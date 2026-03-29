#!/usr/bin/env python3
"""Publish random Twist commands for multiple balls in simulation."""

import random
from typing import Dict

import rospy
from geometry_msgs.msg import Twist


class MoveBallRandom:
    """Drive multiple balls with piecewise-random velocities."""

    def __init__(self):
        rospy.init_node("move_ball_random", anonymous=True)

        self.publish_rate = float(rospy.get_param("~publish_rate", 20.0))
        self.change_interval_min = float(rospy.get_param("~change_interval_min", 0.8))
        self.change_interval_max = float(rospy.get_param("~change_interval_max", 2.2))

        self.max_linear_x = float(rospy.get_param("~max_linear_x", 0.45))
        self.max_linear_y = float(rospy.get_param("~max_linear_y", 0.45))
        self.max_angular_z = float(rospy.get_param("~max_angular_z", 1.2))

        self.ball_topics = rospy.get_param(
            "~ball_topics",
            {
                "red_ball": "/red_ball/cmd_vel",
                "green_ball": "/green_ball/cmd_vel",
                "blue_ball": "/blue_ball/cmd_vel",
                "orange_ball": "/orange_ball/cmd_vel",
            },
        )

        if not isinstance(self.ball_topics, dict) or not self.ball_topics:
            raise ValueError("~ball_topics must be a non-empty dict")

        self.publishers: Dict[str, rospy.Publisher] = {}
        self.current_twists: Dict[str, Twist] = {}
        self.next_change_time: Dict[str, rospy.Time] = {}

        for ball_name, topic_name in self.ball_topics.items():
            self.publishers[ball_name] = rospy.Publisher(topic_name, Twist, queue_size=10)
            self.current_twists[ball_name] = Twist()
            self.next_change_time[ball_name] = rospy.Time(0)

        rospy.on_shutdown(self.on_shutdown)
        rospy.loginfo("move_ball_random started with balls: %s", list(self.ball_topics.keys()))

    def random_twist(self) -> Twist:
        msg = Twist()
        msg.linear.x = random.uniform(-self.max_linear_x, self.max_linear_x)
        msg.linear.y = random.uniform(-self.max_linear_y, self.max_linear_y)
        msg.angular.z = random.uniform(-self.max_angular_z, self.max_angular_z)
        return msg

    def random_interval(self) -> rospy.Duration:
        dt = random.uniform(self.change_interval_min, self.change_interval_max)
        return rospy.Duration.from_sec(max(0.1, dt))

    def step_ball(self, ball_name: str, now: rospy.Time):
        if now >= self.next_change_time[ball_name]:
            self.current_twists[ball_name] = self.random_twist()
            self.next_change_time[ball_name] = now + self.random_interval()
        self.publishers[ball_name].publish(self.current_twists[ball_name])

    def stop_all(self):
        zero = Twist()
        for pub in self.publishers.values():
            pub.publish(zero)

    def run(self):
        rate = rospy.Rate(self.publish_rate)
        while not rospy.is_shutdown():
            now = rospy.Time.now()
            for ball_name in self.publishers:
                self.step_ball(ball_name, now)
            rate.sleep()

    def on_shutdown(self):
        try:
            self.stop_all()
        except rospy.ROSException:
            pass


def main():
    try:
        node = MoveBallRandom()
        node.run()
    except rospy.ROSInterruptException:
        pass


if __name__ == "__main__":
    main()
