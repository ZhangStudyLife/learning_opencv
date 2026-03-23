#!/usr/bin/env python3
"""ROS node that converts red ball position into /cmd_vel for a mecanum robot."""

import sys
from pathlib import Path

import rospy
from geometry_msgs.msg import Point, Twist
from std_msgs.msg import Bool


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from mecanum_logic import ball_position_to_cmd, smooth_command, zero_small_command


class MecanumController:
    """Subscribe to ball detection topics and publish smoothed mecanum commands."""

    def __init__(self):
        rospy.init_node("mecanum_controller", anonymous=True)

        self.max_linear_speed = rospy.get_param("~max_linear_speed", 1.0)
        self.deadzone_x = rospy.get_param("~deadzone_x", 0.12)
        self.deadzone_y = rospy.get_param("~deadzone_y", 0.12)
        self.lost_timeout = rospy.get_param("~lost_timeout", 0.35)
        self.smoothing_alpha = rospy.get_param("~smoothing_alpha", 0.25)
        self.publish_rate = rospy.get_param("~publish_rate", 30.0)

        self.latest_ball_pos = None
        self.ball_detected = False
        self.last_detection_time = 0.0

        self.target_cmd = (0.0, 0.0, 0.0)
        self.current_cmd = (0.0, 0.0, 0.0)

        self.cmd_pub = rospy.Publisher("/cmd_vel", Twist, queue_size=10)
        rospy.Subscriber("/ball_position", Point, self.ball_position_callback, queue_size=1)
        rospy.Subscriber("/ball_detected", Bool, self.ball_detected_callback, queue_size=1)

        rospy.on_shutdown(self.shutdown)

        rospy.loginfo("Mecanum controller started")
        rospy.loginfo(
            "max_linear_speed=%.3f deadzone_x=%.3f deadzone_y=%.3f lost_timeout=%.3f smoothing_alpha=%.3f",
            self.max_linear_speed,
            self.deadzone_x,
            self.deadzone_y,
            self.lost_timeout,
            self.smoothing_alpha,
        )

    def ball_position_callback(self, msg: Point):
        """Store the latest normalized ball position."""
        self.latest_ball_pos = (msg.x, msg.y, msg.z)
        self.last_detection_time = rospy.get_time()

    def ball_detected_callback(self, msg: Bool):
        """Store the latest ball detection state."""
        self.ball_detected = msg.data
        if msg.data:
            self.last_detection_time = rospy.get_time()

    def has_recent_detection(self) -> bool:
        """Check whether the detector is currently providing usable data."""
        if not self.ball_detected or self.latest_ball_pos is None:
            return False

        age = rospy.get_time() - self.last_detection_time
        return age <= self.lost_timeout

    def compute_target_command(self):
        """Compute the target velocity from the latest ball position."""
        if not self.has_recent_detection():
            return 0.0, 0.0, 0.0

        norm_x, norm_y, _ = self.latest_ball_pos
        return ball_position_to_cmd(
            norm_x=norm_x,
            norm_y=norm_y,
            max_linear_speed=self.max_linear_speed,
            deadzone_x=self.deadzone_x,
            deadzone_y=self.deadzone_y,
        )

    def publish_cmd(self, cmd):
        """Publish a Twist message."""
        msg = Twist()
        msg.linear.x = cmd[0]
        msg.linear.y = cmd[1]
        msg.angular.z = cmd[2]
        self.cmd_pub.publish(msg)

    def run(self):
        """Main control loop."""
        rate = rospy.Rate(self.publish_rate)

        while not rospy.is_shutdown():
            self.target_cmd = self.compute_target_command()
            self.current_cmd = smooth_command(
                self.current_cmd,
                self.target_cmd,
                self.smoothing_alpha,
            )
            self.current_cmd = zero_small_command(self.current_cmd)
            self.publish_cmd(self.current_cmd)
            rate.sleep()

    def shutdown(self):
        """Stop the robot when the node exits."""
        self.current_cmd = (0.0, 0.0, 0.0)
        try:
            self.publish_cmd(self.current_cmd)
        except rospy.ROSException:
            pass


def main():
    try:
        controller = MecanumController()
        controller.run()
    except rospy.ROSInterruptException:
        pass


if __name__ == "__main__":
    main()
