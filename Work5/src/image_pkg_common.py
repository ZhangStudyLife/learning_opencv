"""image_pkg 共用的图像处理工具函数。"""

from __future__ import annotations

import os
from typing import Dict, Optional, Tuple

import cv2
import numpy as np
import rospy
from sensor_msgs.msg import Image as RosImage


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def ensure_odd_kernel(size: int) -> int:
    size = int(size)
    if size <= 1:
        return 0
    return size if size % 2 == 1 else size + 1


def build_hsv_bounds(
    h_min: int,
    h_max: int,
    s_min: int,
    s_max: int,
    v_min: int,
    v_max: int,
) -> Tuple[np.ndarray, np.ndarray]:
    h_low, h_high = sorted((int(clamp(h_min, 0, 179)), int(clamp(h_max, 0, 179))))
    s_low, s_high = sorted((int(clamp(s_min, 0, 255)), int(clamp(s_max, 0, 255))))
    v_low, v_high = sorted((int(clamp(v_min, 0, 255)), int(clamp(v_max, 0, 255))))
    lower = np.array([h_low, s_low, v_low], dtype=np.uint8)
    upper = np.array([h_high, s_high, v_high], dtype=np.uint8)
    return lower, upper


def apply_morphology(mask: np.ndarray, open_kernel: int, close_kernel: int) -> np.ndarray:
    result = mask
    open_kernel = ensure_odd_kernel(open_kernel)
    close_kernel = ensure_odd_kernel(close_kernel)

    if open_kernel > 1:
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (open_kernel, open_kernel))
        result = cv2.morphologyEx(result, cv2.MORPH_OPEN, kernel)
    if close_kernel > 1:
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (close_kernel, close_kernel))
        result = cv2.morphologyEx(result, cv2.MORPH_CLOSE, kernel)
    return result


def detect_mask_centroid(mask: np.ndarray, min_white_pixels: int) -> Optional[Dict[str, object]]:
    white_pixels = int(cv2.countNonZero(mask))
    if white_pixels < int(min_white_pixels):
        return None

    moments = cv2.moments(mask, binaryImage=True)
    if moments["m00"] <= 0:
        return None

    cx = int(moments["m10"] / moments["m00"])
    cy = int(moments["m01"] / moments["m00"])
    return {
        "center": (cx, cy),
        "white_pixels": white_pixels,
    }


def draw_cross_marker(
    image: np.ndarray,
    center: Tuple[int, int],
    color: Tuple[int, int, int] = (0, 255, 0),
    size: int = 20,
    thickness: int = 2,
) -> None:
    cv2.drawMarker(image, center, color, cv2.MARKER_CROSS, int(size), int(thickness))


def ensure_directory(path: str) -> str:
    os.makedirs(path, exist_ok=True)
    return path


def resolve_image_topic(preferred_topic: str, candidates=None, wait_timeout: float = 1.5) -> str:
    candidate_topics = []
    preferred_topic = (preferred_topic or "").strip()

    if preferred_topic and preferred_topic.lower() not in ("auto", "default"):
        candidate_topics.append(preferred_topic)

    for topic in candidates or []:
        topic = str(topic).strip()
        if topic and topic not in candidate_topics:
            candidate_topics.append(topic)

    if not candidate_topics:
        candidate_topics.append("/kinect2/qhd/image_color_rect")

    for topic in candidate_topics:
        try:
            rospy.wait_for_message(topic, RosImage, timeout=float(wait_timeout))
            rospy.loginfo("检测到活动图像话题: %s", topic)
            return topic
        except rospy.ROSException:
            rospy.logwarn("图像话题 %s 在 %.1f 秒内没有收到消息。", topic, wait_timeout)

    fallback_topic = candidate_topics[0]
    rospy.logwarn("没有探测到活动图像话题，回退到配置值: %s", fallback_topic)
    return fallback_topic


class DisplayManager:
    """统一处理 OpenCV 窗口，避免无显示环境直接炸掉。"""

    def __init__(self, enabled: bool):
        self.enabled = bool(enabled)
        self._warned = False

    def _disable(self, reason: str) -> None:
        if self.enabled and not self._warned:
            rospy.logwarn("%s，后续关闭图像窗口显示。", reason)
            self._warned = True
        self.enabled = False

    def create_window(self, name: str, flags: int = cv2.WINDOW_NORMAL) -> bool:
        if not self.enabled:
            return False
        try:
            cv2.namedWindow(name, flags)
            return True
        except cv2.error as exc:
            self._disable("OpenCV 创建窗口失败: %s" % exc)
            return False

    def create_trackbar(self, name: str, window: str, value: int, maximum: int, callback) -> bool:
        if not self.enabled:
            return False
        try:
            cv2.createTrackbar(name, window, int(value), int(maximum), callback)
            return True
        except cv2.error as exc:
            self._disable("OpenCV 创建滑块失败: %s" % exc)
            return False

    def get_trackbar_pos(self, name: str, window: str) -> int:
        if not self.enabled:
            return 0
        try:
            return int(cv2.getTrackbarPos(name, window))
        except cv2.error as exc:
            self._disable("OpenCV 读取滑块失败: %s" % exc)
            return 0

    def set_mouse_callback(self, name: str, callback) -> None:
        if not self.enabled:
            return
        try:
            cv2.setMouseCallback(name, callback)
        except cv2.error as exc:
            self._disable("OpenCV 设置鼠标回调失败: %s" % exc)

    def show(self, name: str, image: np.ndarray) -> None:
        if not self.enabled:
            return
        try:
            cv2.imshow(name, image)
        except cv2.error as exc:
            self._disable("OpenCV 显示窗口失败: %s" % exc)

    def poll(self, delay_ms: int = 1) -> int:
        if not self.enabled:
            return -1
        try:
            return cv2.waitKey(int(delay_ms)) & 0xFF
        except cv2.error as exc:
            self._disable("OpenCV 刷新窗口失败: %s" % exc)
            return -1

    def destroy_all(self) -> None:
        try:
            cv2.destroyAllWindows()
        except cv2.error:
            pass
