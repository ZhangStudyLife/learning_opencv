#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Haar 人脸检测、对准跟随与自动拍照节点。"""

from __future__ import annotations

import datetime as dt
import os
import sys
from typing import Optional, Tuple

import cv2
import rospy
from cv_bridge import CvBridge, CvBridgeError
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Image

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from image_pkg_common import DisplayManager, clamp, ensure_directory, resolve_image_topic


class FaceCaptureNode:
    def __init__(self):
        rospy.init_node("face_capture_node", anonymous=True)

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
        self.show_windows = bool(rospy.get_param("~show_windows", True))
        self.log_interval = float(rospy.get_param("~log_interval", 1.0))

        self.scale_factor = float(rospy.get_param("~scale_factor", 1.1))
        self.min_neighbors = int(rospy.get_param("~min_neighbors", 5))
        self.min_face_size = int(rospy.get_param("~min_face_size", 60))

        self.linear_x = float(rospy.get_param("~linear_x", 0.12))
        self.kp_angular = float(rospy.get_param("~kp_angular", 1.2))
        self.max_angular_z = float(rospy.get_param("~max_angular_z", 0.8))
        self.center_deadband = float(rospy.get_param("~center_deadband", 0.03))
        self.center_tolerance = float(rospy.get_param("~center_tolerance", 0.08))
        self.target_face_width = int(rospy.get_param("~target_face_width", 180))
        self.capture_face_width = int(rospy.get_param("~capture_face_width", self.target_face_width))
        self.capture_count = int(rospy.get_param("~capture_count", 3))
        self.capture_interval = float(rospy.get_param("~capture_interval", 1.0))
        self.stable_duration = float(rospy.get_param("~stable_duration", 0.8))
        self.save_dir = ensure_directory(rospy.get_param("~save_dir", os.path.join(os.getcwd(), "face_capture")))
        self.save_prefix = rospy.get_param("~save_prefix", "face_capture")

        cascade_path = rospy.get_param("~cascade_path", "")
        if not cascade_path:
            cascade_path = os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml")
        self.cascade_path = cascade_path
        self.face_cascade = cv2.CascadeClassifier(self.cascade_path)
        if self.face_cascade.empty():
            raise RuntimeError("Haar 分类器加载失败: %s" % self.cascade_path)

        self.bridge = CvBridge()
        self.display = DisplayManager(self.show_windows)
        self.cmd_pub = rospy.Publisher(self.cmd_topic, Twist, queue_size=10)
        self.image_topic = resolve_image_topic(preferred_topic, self.image_topic_candidates, self.topic_probe_timeout)

        self.window_view = rospy.get_param("~window_view", "Face Capture - View")
        if self.display.enabled:
            self.display.create_window(self.window_view)

        self.centered_since: Optional[rospy.Time] = None
        self.last_capture_time: Optional[rospy.Time] = None
        self.captured_images = 0
        self.capture_complete = False

        rospy.Subscriber(self.image_topic, Image, self.image_callback, queue_size=1, buff_size=2**24)
        rospy.on_shutdown(self.on_shutdown)
        rospy.loginfo("face_capture_node 已启动，图像话题=%s，保存目录=%s", self.image_topic, self.save_dir)

    def publish_cmd(self, linear_x: float, angular_z: float) -> None:
        cmd = Twist()
        cmd.linear.x = linear_x
        cmd.angular.z = angular_z
        self.cmd_pub.publish(cmd)

    def pick_largest_face(self, faces) -> Optional[Tuple[int, int, int, int]]:
        if len(faces) == 0:
            return None
        return max(faces, key=lambda rect: rect[2] * rect[3])

    def maybe_capture(self, frame, ready: bool, now: rospy.Time) -> None:
        if self.capture_complete:
            return

        if not ready:
            self.centered_since = None
            return

        if self.centered_since is None:
            self.centered_since = now
            return

        stable_time = (now - self.centered_since).to_sec()
        if stable_time < self.stable_duration:
            return

        if self.last_capture_time is not None:
            elapsed = (now - self.last_capture_time).to_sec()
            if elapsed < self.capture_interval:
                return

        timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = "%s_%02d_%s.jpg" % (self.save_prefix, self.captured_images + 1, timestamp)
        file_path = os.path.join(self.save_dir, filename)
        if cv2.imwrite(file_path, frame):
            self.captured_images += 1
            self.last_capture_time = now
            rospy.loginfo("已保存照片 %d/%d: %s", self.captured_images, self.capture_count, file_path)
        else:
            rospy.logwarn("照片保存失败: %s", file_path)

        if self.captured_images >= self.capture_count:
            self.capture_complete = True
            rospy.loginfo("人脸拍照任务完成，已保存 %d 张照片。", self.captured_images)

    def image_callback(self, msg: Image) -> None:
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except CvBridgeError as exc:
            rospy.logwarn_throttle(1.0, "图像转换失败: %s", exc)
            return

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=self.scale_factor,
            minNeighbors=self.min_neighbors,
            minSize=(self.min_face_size, self.min_face_size),
        )
        target_face = self.pick_largest_face(faces)

        vis = frame.copy()
        img_h, img_w = vis.shape[:2]
        center_x = img_w // 2
        cv2.line(vis, (center_x, 0), (center_x, img_h), (255, 255, 0), 1)

        linear_x = 0.0
        angular_z = 0.0
        status_color = (0, 0, 255)
        status_text = "face=none"
        ready_for_capture = False

        if target_face is not None:
            x, y, w, h = target_face
            face_center_x = x + w // 2
            error_norm = float(face_center_x - center_x) / float(max(1, center_x))
            control_error = 0.0 if abs(error_norm) < self.center_deadband else error_norm
            angular_z = clamp(-self.kp_angular * control_error, -self.max_angular_z, self.max_angular_z)
            linear_x = 0.0 if (w >= self.target_face_width or self.capture_complete) else self.linear_x

            ready_for_capture = abs(error_norm) <= self.center_tolerance and w >= self.capture_face_width
            cv2.rectangle(vis, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.circle(vis, (face_center_x, y + h // 2), 4, (0, 255, 0), -1)

            status_color = (0, 255, 0)
            status_text = "face=(%d,%d,%d,%d) err=%.3f width=%d" % (x, y, w, h, error_norm, w)
            rospy.loginfo_throttle(
                self.log_interval,
                "检测到人脸，偏差=%.3f 宽度=%d 线速度=%.3f 角速度=%.3f"
                % (error_norm, w, linear_x, angular_z),
            )
        else:
            self.centered_since = None
            rospy.loginfo_throttle(self.log_interval, "未检测到人脸，/cmd_vel 已置零。")

        now = rospy.Time.now()
        self.maybe_capture(frame, ready_for_capture, now)
        if self.capture_complete:
            linear_x = 0.0
            angular_z = 0.0

        self.publish_cmd(linear_x, angular_z)

        cv2.putText(vis, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, status_color, 2)
        cv2.putText(
            vis,
            "linear=%.3f angular=%.3f capture=%d/%d"
            % (linear_x, angular_z, self.captured_images, self.capture_count),
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            status_color,
            2,
        )
        cv2.putText(
            vis,
            "save_dir=%s" % self.save_dir,
            (10, 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            1,
        )

        self.display.show(self.window_view, vis)
        self.display.poll(1)

    def on_shutdown(self) -> None:
        try:
            self.publish_cmd(0.0, 0.0)
        except rospy.ROSException:
            pass
        self.display.destroy_all()


if __name__ == "__main__":
    try:
        FaceCaptureNode()
        rospy.spin()
    except (rospy.ROSInterruptException, RuntimeError) as exc:
        rospy.logerr("%s", exc)
