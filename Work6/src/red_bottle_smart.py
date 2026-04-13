#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""识别红色瓶子，并输出其距离。"""

from __future__ import annotations

import cv2
import numpy as np
import rospy
from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import Image


class RedBottleSmart:
    def __init__(self) -> None:
        rospy.init_node("red_bottle_smart", anonymous=False)

        self.rgb_topic = rospy.get_param("~rgb_topic", "/kinect2/hd/image_color_rect")
        self.depth_topic = rospy.get_param("~depth_topic", "/kinect2/sd/image_depth_rect")
        self.publish_rate = max(0.1, float(rospy.get_param("~publish_rate", 10.0)))
        self.min_area = max(1, int(rospy.get_param("~min_area", 500)))
        self.change_threshold_m = max(0.01, float(rospy.get_param("~change_threshold_m", 0.1)))
        self.depth_min_m = float(rospy.get_param("~depth_min_m", 0.1))
        self.depth_max_m = float(rospy.get_param("~depth_max_m", 10.0))
        self.log_interval = max(0.5, float(rospy.get_param("~log_interval", 2.0)))

        self.lower_red_1 = np.array(
            [
                int(rospy.get_param("~h1_min", 0)),
                int(rospy.get_param("~s1_min", 120)),
                int(rospy.get_param("~v1_min", 70)),
            ],
            dtype=np.uint8,
        )
        self.upper_red_1 = np.array(
            [
                int(rospy.get_param("~h1_max", 10)),
                int(rospy.get_param("~s1_max", 255)),
                int(rospy.get_param("~v1_max", 255)),
            ],
            dtype=np.uint8,
        )
        self.lower_red_2 = np.array(
            [
                int(rospy.get_param("~h2_min", 170)),
                int(rospy.get_param("~s2_min", 120)),
                int(rospy.get_param("~v2_min", 70)),
            ],
            dtype=np.uint8,
        )
        self.upper_red_2 = np.array(
            [
                int(rospy.get_param("~h2_max", 180)),
                int(rospy.get_param("~s2_max", 255)),
                int(rospy.get_param("~v2_max", 255)),
            ],
            dtype=np.uint8,
        )

        self.bridge = CvBridge()
        self.rgb_image = None
        self.depth_image = None
        self.last_distance = None

        rospy.Subscriber(self.rgb_topic, Image, self.cb_rgb, queue_size=1, buff_size=2**26)
        rospy.Subscriber(self.depth_topic, Image, self.cb_depth, queue_size=1, buff_size=2**24)
        rospy.loginfo("red_bottle_smart.py 已启动: rgb=%s depth=%s", self.rgb_topic, self.depth_topic)

    def cb_rgb(self, msg: Image) -> None:
        try:
            self.rgb_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except CvBridgeError as exc:
            rospy.logwarn_throttle(2.0, "彩色图转换失败: %s", exc)

    def cb_depth(self, msg: Image) -> None:
        try:
            self.depth_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding="passthrough")
        except CvBridgeError as exc:
            rospy.logwarn_throttle(2.0, "深度图转换失败: %s", exc)

    def detect_red_bottle(self):
        if self.rgb_image is None:
            return None

        hsv = cv2.cvtColor(self.rgb_image, cv2.COLOR_BGR2HSV)
        mask1 = cv2.inRange(hsv, self.lower_red_1, self.upper_red_1)
        mask2 = cv2.inRange(hsv, self.lower_red_2, self.upper_red_2)
        mask = cv2.bitwise_or(mask1, mask2)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None

        max_contour = max(contours, key=cv2.contourArea)
        if cv2.contourArea(max_contour) < self.min_area:
            return None

        if self.depth_image is None or np.all(self.depth_image == 0):
            return 999.0

        moments = cv2.moments(max_contour)
        if moments["m00"] == 0:
            return None

        cx = int(moments["m10"] / moments["m00"])
        cy = int(moments["m01"] / moments["m00"])

        height_rgb, width_rgb = self.rgb_image.shape[:2]
        height_d, width_d = self.depth_image.shape[:2]
        cx_d = int(float(cx) * width_d / width_rgb)
        cy_d = int(float(cy) * height_d / height_rgb)
        cx_d = int(np.clip(cx_d, 0, width_d - 1))
        cy_d = int(np.clip(cy_d, 0, height_d - 1))

        raw_depth = self.depth_image[cy_d, cx_d]
        if not np.isfinite(raw_depth):
            return 888.0
        distance_m = float(raw_depth)
        if distance_m > 20.0:
            distance_m /= 1000.0
        if distance_m < self.depth_min_m or distance_m > self.depth_max_m:
            return 888.0

        return distance_m

    def run(self) -> None:
        rate = rospy.Rate(self.publish_rate)
        while not rospy.is_shutdown():
            current_distance = self.detect_red_bottle()
            if current_distance is not None:
                if self.last_distance is None:
                    rospy.loginfo("红瓶初始距离：%.2f 米", current_distance)
                    self.last_distance = current_distance
                elif abs(current_distance - self.last_distance) > self.change_threshold_m:
                    rospy.loginfo("红瓶距离更新：%.2f 米", current_distance)
                    self.last_distance = current_distance
                else:
                    rospy.loginfo_throttle(self.log_interval, "红瓶当前距离：%.2f 米", current_distance)
            rate.sleep()


if __name__ == "__main__":
    try:
        node = RedBottleSmart()
        node.run()
    except rospy.ROSInterruptException:
        pass
