#!/usr/bin/env python3
"""ROS node that converts /cmd_vel into four wheel velocities."""

import sys
from pathlib import Path

import rospy
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from mecanum_logic import twist_to_wheel_velocities


class MecanumDriver:
    """Drive four mecanum wheel velocity controllers from /cmd_vel."""

    def __init__(self):
        rospy.init_node("mecanum_driver", anonymous=True)

        self.wheel_radius = rospy.get_param("~wheel_radius", 0.08)
        self.wheel_base_length = rospy.get_param("~wheel_base_length", 0.5)
        self.wheel_base_width = rospy.get_param("~wheel_base_width", 0.4)
        self.max_wheel_speed = rospy.get_param("~max_wheel_speed", 15.0)
        self.publish_rate = rospy.get_param("~publish_rate", 50.0)

        self.vx = 0.0
        self.vy = 0.0
        self.omega = 0.0

        self.pub_fl = rospy.Publisher("/front_left_wheel_velocity_controller/command", Float64, queue_size=10)
        self.pub_fr = rospy.Publisher("/front_right_wheel_velocity_controller/command", Float64, queue_size=10)
        self.pub_rl = rospy.Publisher("/rear_left_wheel_velocity_controller/command", Float64, queue_size=10)
        self.pub_rr = rospy.Publisher("/rear_right_wheel_velocity_controller/command", Float64, queue_size=10)

        rospy.Subscriber("/cmd_vel", Twist, self.cmd_vel_callback, queue_size=1)
        rospy.on_shutdown(self.shutdown)

        rospy.loginfo("Mecanum driver started")

    def current_wheel_speeds(self):
        """Convert the current Twist command into wheel angular velocities."""
        return twist_to_wheel_velocities(
            vx=self.vx,
            vy=self.vy,
            omega=self.omega,
            wheel_radius=self.wheel_radius,
            wheel_base_length=self.wheel_base_length,
            wheel_base_width=self.wheel_base_width,
            max_wheel_speed=self.max_wheel_speed,
        )

    def publish_wheel_speeds(self, speeds):
        """Publish the four wheel velocities."""
        self.pub_fl.publish(Float64(data=speeds[0]))
        self.pub_fr.publish(Float64(data=speeds[1]))
        self.pub_rl.publish(Float64(data=speeds[2]))
        self.pub_rr.publish(Float64(data=speeds[3]))

    def cmd_vel_callback(self, msg: Twist):
        """Store the latest commanded body velocity."""
        self.vx = msg.linear.x
        self.vy = msg.linear.y
        self.omega = msg.angular.z
        self.publish_wheel_speeds(self.current_wheel_speeds())

    def run(self):
        """Keep publishing the current command so controllers stay fed."""
        rate = rospy.Rate(self.publish_rate)
        while not rospy.is_shutdown():
            self.publish_wheel_speeds(self.current_wheel_speeds())
            rate.sleep()

    def shutdown(self):
        """Stop all wheel controllers when exiting."""
        self.vx = 0.0
        self.vy = 0.0
        self.omega = 0.0
        try:
            self.publish_wheel_speeds((0.0, 0.0, 0.0, 0.0))
        except rospy.ROSException:
            pass


def main():
    try:
        driver = MecanumDriver()
        driver.run()
    except rospy.ROSInterruptException:
        pass


if __name__ == "__main__":
    main()
