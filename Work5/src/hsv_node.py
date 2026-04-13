#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HSV 取球调参与质心检测节点。"""

from __future__ import annotations

import os
import sys

import cv2
import rospy
from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import Image

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from image_pkg_common import (
    DisplayManager,
    apply_morphology,
    build_hsv_bounds,
    detect_mask_centroid,
    draw_cross_marker,
    resolve_image_topic,
)


class HsvNode:
    def __init__(self):
        rospy.init_node("hsv_node", anonymous=True)

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
        self.min_white_pixels = int(rospy.get_param("~min_white_pixels", 400))
        self.open_kernel = int(rospy.get_param("~open_kernel", 5))
        self.close_kernel = int(rospy.get_param("~close_kernel", 5))
        self.crosshair_size = int(rospy.get_param("~crosshair_size", 20))
        self.show_windows = bool(rospy.get_param("~show_windows", True))
        self.log_interval = float(rospy.get_param("~log_interval", 1.0))

        self.window_rgb = rospy.get_param("~window_rgb", "HSV Detector - RGB")
        self.window_hsv = rospy.get_param("~window_hsv", "HSV Detector - HSV")
        self.window_mask = rospy.get_param("~window_mask", "HSV Detector - Mask")
        self.window_trackbar = rospy.get_param("~window_trackbar", "HSV Detector - Adjust")

        self.h_min = int(rospy.get_param("~h_min", 35))
        self.h_max = int(rospy.get_param("~h_max", 85))
        self.s_min = int(rospy.get_param("~s_min", 80))
        self.s_max = int(rospy.get_param("~s_max", 255))
        self.v_min = int(rospy.get_param("~v_min", 60))
        self.v_max = int(rospy.get_param("~v_max", 255))

        self.bridge = CvBridge()
        self.display = DisplayManager(self.show_windows)
        self.latest_hsv = None
        self.image_topic = resolve_image_topic(preferred_topic, self.image_topic_candidates, self.topic_probe_timeout)

        self._setup_windows()
        rospy.Subscriber(self.image_topic, Image, self.image_callback, queue_size=1, buff_size=2**24)
        rospy.on_shutdown(self.on_shutdown)
        rospy.loginfo("hsv_node 已启动，订阅图像话题: %s", self.image_topic)

    def _setup_windows(self) -> None:
        if not self.display.enabled:
            return

        for name in (self.window_rgb, self.window_hsv, self.window_mask, self.window_trackbar):
            self.display.create_window(name)
        if not self.display.enabled:
            return

        self.display.create_trackbar("H Min", self.window_trackbar, self.h_min, 179, lambda _: None)
        self.display.create_trackbar("H Max", self.window_trackbar, self.h_max, 179, lambda _: None)
        self.display.create_trackbar("S Min", self.window_trackbar, self.s_min, 255, lambda _: None)
        self.display.create_trackbar("S Max", self.window_trackbar, self.s_max, 255, lambda _: None)
        self.display.create_trackbar("V Min", self.window_trackbar, self.v_min, 255, lambda _: None)
        self.display.create_trackbar("V Max", self.window_trackbar, self.v_max, 255, lambda _: None)
        self.display.set_mouse_callback(self.window_rgb, self.on_mouse_click)

    def _read_trackbars(self) -> None:
        if not self.display.enabled:
            return
        self.h_min = self.display.get_trackbar_pos("H Min", self.window_trackbar)
        self.h_max = self.display.get_trackbar_pos("H Max", self.window_trackbar)
        self.s_min = self.display.get_trackbar_pos("S Min", self.window_trackbar)
        self.s_max = self.display.get_trackbar_pos("S Max", self.window_trackbar)
        self.v_min = self.display.get_trackbar_pos("V Min", self.window_trackbar)
        self.v_max = self.display.get_trackbar_pos("V Max", self.window_trackbar)

    def on_mouse_click(self, event, x, y, _flags, _param) -> None:
        if event != cv2.EVENT_LBUTTONDOWN or self.latest_hsv is None:
            return
        if y >= self.latest_hsv.shape[0] or x >= self.latest_hsv.shape[1]:
            return
        h, s, v = self.latest_hsv[y, x]
        rospy.loginfo("鼠标取样坐标=(%d,%d) HSV=(%d,%d,%d)", x, y, int(h), int(s), int(v))

    def image_callback(self, msg: Image) -> None:
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except CvBridgeError as exc:
            rospy.logwarn_throttle(1.0, "图像转换失败: %s", exc)
            return

        self._read_trackbars()
        hsv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        self.latest_hsv = hsv_image

        lower, upper = build_hsv_bounds(self.h_min, self.h_max, self.s_min, self.s_max, self.v_min, self.v_max)
        mask = cv2.inRange(hsv_image, lower, upper)
        mask = apply_morphology(mask, self.open_kernel, self.close_kernel)
        detection = detect_mask_centroid(mask, self.min_white_pixels)

        vis = frame.copy()
        h, w = vis.shape[:2]
        draw_cross_marker(vis, (w // 2, h // 2), color=(255, 255, 0), size=16, thickness=1)

        if detection is not None:
            cx, cy = detection["center"]
            draw_cross_marker(vis, (cx, cy), size=self.crosshair_size)
            cv2.putText(
                vis,
                "target=(%d,%d) white=%d" % (cx, cy, detection["white_pixels"]),
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
            )
            rospy.loginfo_throttle(
                self.log_interval,
                "检测到目标中心=(%d,%d)，白色像素=%d" % (cx, cy, detection["white_pixels"]),
            )
        else:
            cv2.putText(
                vis,
                "target=none white<threshold",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2,
            )
            rospy.loginfo_throttle(self.log_interval, "未检测到目标，当前白色像素不足阈值。")

        hsv_vis = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)
        self.display.show(self.window_rgb, vis)
        self.display.show(self.window_hsv, hsv_vis)
        self.display.show(self.window_mask, mask)
        self.display.poll(1)

    def on_shutdown(self) -> None:
        self.display.destroy_all()


if __name__ == "__main__":
    try:
        HsvNode()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
