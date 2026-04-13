#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""基于 HSV 的直接跟球节点。"""

from __future__ import annotations

import os
import sys

import cv2
import rospy
from cv_bridge import CvBridge, CvBridgeError
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Image

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from image_pkg_common import (
    DisplayManager,
    apply_morphology,
    build_hsv_bounds,
    clamp,
    detect_mask_centroid,
    draw_cross_marker,
    resolve_image_topic,
)


class FollowNode:
    def __init__(self):
        rospy.init_node("follow_node", anonymous=True)

        preferred_topic = rospy.get_param("~image_topic", "auto")
        self.image_topic_candidates = rospy.get_param(
            "~image_topic_candidates",
            [
                "/kinect2/qhd/image_color_rect",
                "/kinect2/hd/image_color_rect",
                "/kinect2/sd/image_color_rect",
            ],
        )
        self.topic_probe_timeout = float(rospy.get_param("~topic_probe_timeout", 1.5))
        self.cmd_topic = rospy.get_param("~cmd_topic", "/cmd_vel")
        self.min_white_pixels = int(rospy.get_param("~min_white_pixels", 400))
        self.open_kernel = int(rospy.get_param("~open_kernel", 5))
        self.close_kernel = int(rospy.get_param("~close_kernel", 5))
        self.linear_x = float(rospy.get_param("~linear_x", 0.18))
        self.kp_angular = float(rospy.get_param("~kp_angular", 1.2))
        self.max_angular_z = float(rospy.get_param("~max_angular_z", 0.8))
        self.center_deadband = float(rospy.get_param("~center_deadband", 0.03))
        self.show_windows = bool(rospy.get_param("~show_windows", True))
        self.log_interval = float(rospy.get_param("~log_interval", 1.0))

        self.window_view = rospy.get_param("~window_view", "Ball Follow - View")
        self.window_mask = rospy.get_param("~window_mask", "Ball Follow - Mask")

        self.h_min = int(rospy.get_param("~h_min", 35))
        self.h_max = int(rospy.get_param("~h_max", 85))
        self.s_min = int(rospy.get_param("~s_min", 80))
        self.s_max = int(rospy.get_param("~s_max", 255))
        self.v_min = int(rospy.get_param("~v_min", 60))
        self.v_max = int(rospy.get_param("~v_max", 255))

        self.bridge = CvBridge()
        self.display = DisplayManager(self.show_windows)
        self.cmd_pub = rospy.Publisher(self.cmd_topic, Twist, queue_size=10)
        self.image_topic = resolve_image_topic(preferred_topic, self.image_topic_candidates, self.topic_probe_timeout)

        if self.display.enabled:
            self.display.create_window(self.window_view)
            self.display.create_window(self.window_mask)

        rospy.Subscriber(self.image_topic, Image, self.image_callback, queue_size=1, buff_size=2**24)
        rospy.on_shutdown(self.on_shutdown)
        rospy.loginfo("follow_node 已启动，图像话题=%s，速度话题=%s", self.image_topic, self.cmd_topic)

    def publish_cmd(self, linear_x: float, angular_z: float) -> None:
        msg = Twist()
        msg.linear.x = linear_x
        msg.angular.z = angular_z
        self.cmd_pub.publish(msg)

    def image_callback(self, msg: Image) -> None:
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except CvBridgeError as exc:
            rospy.logwarn_throttle(1.0, "图像转换失败: %s", exc)
            return

        hsv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower, upper = build_hsv_bounds(self.h_min, self.h_max, self.s_min, self.s_max, self.v_min, self.v_max)
        mask = cv2.inRange(hsv_image, lower, upper)
        mask = apply_morphology(mask, self.open_kernel, self.close_kernel)
        detection = detect_mask_centroid(mask, self.min_white_pixels)

        vis = frame.copy()
        img_h, img_w = vis.shape[:2]
        center_x = img_w // 2
        cv2.line(vis, (center_x, 0), (center_x, img_h), (255, 255, 0), 1)

        linear_x = 0.0
        angular_z = 0.0

        if detection is not None:
            cx, cy = detection["center"]
            error_norm = float(cx - center_x) / float(max(1, center_x))
            if abs(error_norm) < self.center_deadband:
                error_norm = 0.0

            linear_x = self.linear_x
            angular_z = clamp(-self.kp_angular * error_norm, -self.max_angular_z, self.max_angular_z)
            draw_cross_marker(vis, (cx, cy), size=20)
            rospy.loginfo_throttle(
                self.log_interval,
                "跟球目标中心=(%d,%d) 偏差=%.3f 线速度=%.3f 角速度=%.3f"
                % (cx, cy, error_norm, linear_x, angular_z),
            )
            status_color = (0, 255, 0)
            status_text = "target=(%d,%d) err=%.3f" % (cx, cy, error_norm)
        else:
            rospy.loginfo_throttle(self.log_interval, "未检测到目标，/cmd_vel 已置零。")
            status_color = (0, 0, 255)
            status_text = "target=none err=nan"

        self.publish_cmd(linear_x, angular_z)
        cv2.putText(vis, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
        cv2.putText(
            vis,
            "linear=%.3f angular=%.3f white=%d"
            % (linear_x, angular_z, 0 if detection is None else detection["white_pixels"]),
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            status_color,
            2,
        )

        self.display.show(self.window_view, vis)
        self.display.show(self.window_mask, mask)
        self.display.poll(1)

    def on_shutdown(self) -> None:
        try:
            self.publish_cmd(0.0, 0.0)
        except rospy.ROSException:
            pass
        self.display.destroy_all()


if __name__ == "__main__":
    try:
        FollowNode()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
