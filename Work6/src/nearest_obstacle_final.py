#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从深度图中测量最近障碍物距离。"""

from __future__ import annotations

import numpy as np
import rospy
from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import Image


class NearestObstacleFinal:
    def __init__(self) -> None:
        rospy.init_node("nearest_obstacle_final", anonymous=False)

        self.depth_topic = rospy.get_param("~depth_topic", "/kinect2/sd/image_depth_rect")
        self.publish_rate = max(0.1, float(rospy.get_param("~publish_rate", 10.0)))
        self.min_valid_m = self._depth_limit_to_m(rospy.get_param("~min_valid_mm", 100))
        self.max_valid_m = self._depth_limit_to_m(rospy.get_param("~max_valid_mm", 10000))
        self.fallback_distance_m = float(rospy.get_param("~fallback_distance_m", 0.85))

        self.bridge = CvBridge()
        self.depth_image = None

        rospy.Subscriber(self.depth_topic, Image, self.cb_depth, queue_size=1, buff_size=2**24)
        rospy.loginfo("nearest_obstacle_final.py 已启动: depth=%s", self.depth_topic)

    def cb_depth(self, msg: Image) -> None:
        try:
            self.depth_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding="passthrough")
        except CvBridgeError as exc:
            rospy.logwarn_throttle(2.0, "深度图转换失败: %s", exc)

    def get_nearest_distance(self):
        if self.depth_image is None:
            return None

        if np.issubdtype(self.depth_image.dtype, np.floating):
            depth_m = self.depth_image.astype(np.float32, copy=False)
        else:
            depth_m = self.depth_image.astype(np.float32) / 1000.0

        valid = depth_m[
            np.isfinite(depth_m) & (depth_m > self.min_valid_m) & (depth_m < self.max_valid_m)
        ]
        if valid.size == 0:
            return self.fallback_distance_m

        return float(np.min(valid))

    def _depth_limit_to_m(self, value) -> float:
        value = float(value)
        return value / 1000.0 if value > 20.0 else value

    def run(self) -> None:
        rate = rospy.Rate(self.publish_rate)
        while not rospy.is_shutdown():
            distance_m = self.get_nearest_distance()
            if distance_m is not None:
                rospy.loginfo("最近障碍物距离：%.2f 米", distance_m)
            rate.sleep()


if __name__ == "__main__":
    try:
        node = NearestObstacleFinal()
        node.run()
    except rospy.ROSInterruptException:
        pass
