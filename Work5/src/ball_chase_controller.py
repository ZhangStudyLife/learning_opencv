#!/usr/bin/env python3
"""Drive robot to chase detected target ball."""

import rospy
from geometry_msgs.msg import Point, Twist
from std_msgs.msg import Bool


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def smooth(prev: float, target: float, alpha: float) -> float:
    alpha = clamp(alpha, 0.0, 1.0)
    return alpha * target + (1.0 - alpha) * prev


class BallChaseController:
    """Convert visual target position into /cmd_vel."""

    def __init__(self):
        rospy.init_node("ball_chase_controller", anonymous=True)

        self.cmd_topic = rospy.get_param("~cmd_topic", "/cmd_vel")
        self.image_width = float(rospy.get_param("~image_width", 640.0))

        self.control_rate = float(rospy.get_param("~control_rate", 20.0))
        self.lost_timeout = float(rospy.get_param("~lost_timeout", 0.6))

        self.kp_angular = float(rospy.get_param("~kp_angular", 1.4))
        self.kp_linear = float(rospy.get_param("~kp_linear", 2.6))

        self.max_linear_x = float(rospy.get_param("~max_linear_x", 0.35))
        self.max_angular_z = float(rospy.get_param("~max_angular_z", 1.5))

        self.deadband_x = float(rospy.get_param("~deadband_x", 0.05))
        self.deadband_size = float(rospy.get_param("~deadband_size", 0.006))
        self.target_area_ratio = float(rospy.get_param("~target_area_ratio", 0.020))

        self.smooth_alpha = float(rospy.get_param("~smooth_alpha", 0.35))
        self.search_angular_z = float(rospy.get_param("~search_angular_z", 0.0))

        self.detected = False
        self.last_detection_time = rospy.Time(0)
        self.target_u = -1.0
        self.target_v = -1.0
        self.target_area = 0.0

        self.cur_linear_x = 0.0
        self.cur_angular_z = 0.0

        self.cmd_pub = rospy.Publisher(self.cmd_topic, Twist, queue_size=10)
        rospy.Subscriber("/ball_detected", Bool, self.detected_callback, queue_size=1)
        rospy.Subscriber("/ball_position", Point, self.position_callback, queue_size=1)

        rospy.on_shutdown(self.on_shutdown)
        rospy.loginfo("ball_chase_controller publishing %s", self.cmd_topic)

    def detected_callback(self, msg: Bool):
        self.detected = bool(msg.data)
        if self.detected:
            self.last_detection_time = rospy.Time.now()

    def position_callback(self, msg: Point):
        self.target_u = float(msg.x)
        self.target_v = float(msg.y)
        self.target_area = float(msg.z)
        if self.target_u >= 0.0 and self.target_v >= 0.0:
            self.last_detection_time = rospy.Time.now()

    def has_target(self) -> bool:
        if not self.detected:
            return False
        dt = (rospy.Time.now() - self.last_detection_time).to_sec()
        return dt <= self.lost_timeout and self.target_u >= 0.0 and self.target_v >= 0.0

    def compute_cmd(self):
        if not self.has_target():
            return 0.0, self.search_angular_z

        x_err = (self.target_u - 0.5 * self.image_width) / max(1.0, 0.5 * self.image_width)
        size_err = self.target_area_ratio - self.target_area

        if abs(x_err) < self.deadband_x:
            x_err = 0.0
        if abs(size_err) < self.deadband_size:
            size_err = 0.0

        linear_x = clamp(self.kp_linear * size_err, -self.max_linear_x, self.max_linear_x)
        angular_z = clamp(-self.kp_angular * x_err, -self.max_angular_z, self.max_angular_z)
        return linear_x, angular_z

    def publish_cmd(self, linear_x: float, angular_z: float):
        cmd = Twist()
        cmd.linear.x = linear_x
        cmd.angular.z = angular_z
        self.cmd_pub.publish(cmd)

    def run(self):
        rate = rospy.Rate(self.control_rate)
        while not rospy.is_shutdown():
            target_linear, target_angular = self.compute_cmd()
            self.cur_linear_x = smooth(self.cur_linear_x, target_linear, self.smooth_alpha)
            self.cur_angular_z = smooth(self.cur_angular_z, target_angular, self.smooth_alpha)
            self.publish_cmd(self.cur_linear_x, self.cur_angular_z)
            rate.sleep()

    def on_shutdown(self):
        try:
            self.publish_cmd(0.0, 0.0)
        except rospy.ROSException:
            pass


if __name__ == "__main__":
    try:
        node = BallChaseController()
        node.run()
    except rospy.ROSInterruptException:
        pass
