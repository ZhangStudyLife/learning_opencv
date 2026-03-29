#!/usr/bin/env python3
"""Track a target color ball from Kinect image stream."""

import cv2
import numpy as np
import rospy
from cv_bridge import CvBridge, CvBridgeError
from geometry_msgs.msg import Point
from sensor_msgs.msg import Image
from std_msgs.msg import Bool


class KinectColorTracker:
    """Detect a target-colored ball and publish image-space position."""

    def __init__(self):
        rospy.init_node("kinect_color_tracker", anonymous=True)

        self.image_topic = rospy.get_param("~image_topic", "/kinect2/sd/image_color_rect")
        self.publish_debug_image = bool(rospy.get_param("~publish_debug_image", True))

        self.lower_color_1 = np.array(rospy.get_param("~lower_color_1", [0, 100, 90]), dtype=np.uint8)
        self.upper_color_1 = np.array(rospy.get_param("~upper_color_1", [12, 255, 255]), dtype=np.uint8)
        self.lower_color_2 = np.array(rospy.get_param("~lower_color_2", [160, 100, 90]), dtype=np.uint8)
        self.upper_color_2 = np.array(rospy.get_param("~upper_color_2", [180, 255, 255]), dtype=np.uint8)

        self.erode_size = int(rospy.get_param("~erode", 2))
        self.dilate_size = int(rospy.get_param("~dilate", 2))
        self.min_area = float(rospy.get_param("~min_area", 140.0))
        self.min_circularity = float(rospy.get_param("~min_circularity", 0.45))

        self.bridge = CvBridge()

        self.pos_pub = rospy.Publisher("/ball_position", Point, queue_size=10)
        self.detected_pub = rospy.Publisher("/ball_detected", Bool, queue_size=10)
        self.debug_pub = rospy.Publisher("/tracker/debug_image", Image, queue_size=2)

        rospy.Subscriber(self.image_topic, Image, self.image_callback, queue_size=1, buff_size=2**24)
        rospy.loginfo("kinect_color_tracker listening on %s", self.image_topic)

    def create_mask(self, frame_bgr: np.ndarray) -> np.ndarray:
        hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
        mask1 = cv2.inRange(hsv, self.lower_color_1, self.upper_color_1)
        mask2 = cv2.inRange(hsv, self.lower_color_2, self.upper_color_2)
        mask = cv2.bitwise_or(mask1, mask2)

        if self.erode_size > 0:
            k1 = np.ones((self.erode_size, self.erode_size), np.uint8)
            mask = cv2.erode(mask, k1, iterations=1)
        if self.dilate_size > 0:
            k2 = np.ones((self.dilate_size, self.dilate_size), np.uint8)
            mask = cv2.dilate(mask, k2, iterations=1)

        return mask

    @staticmethod
    def contour_score(contour) -> float:
        area = cv2.contourArea(contour)
        if area <= 0.0:
            return 0.0
        perimeter = cv2.arcLength(contour, True)
        if perimeter <= 0.0:
            return 0.0
        circularity = 4.0 * np.pi * area / (perimeter * perimeter)
        return area * max(0.0, circularity)

    def detect_target(self, frame_bgr: np.ndarray):
        mask = self.create_mask(frame_bgr)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        best = None
        best_score = 0.0
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < self.min_area:
                continue

            perimeter = cv2.arcLength(contour, True)
            if perimeter <= 0.0:
                continue

            circularity = 4.0 * np.pi * area / (perimeter * perimeter)
            if circularity < self.min_circularity:
                continue

            score = self.contour_score(contour)
            if score > best_score:
                (x, y), radius = cv2.minEnclosingCircle(contour)
                best_score = score
                best = {
                    "center": (int(x), int(y)),
                    "radius": float(radius),
                    "area": float(area),
                }

        return best, mask

    def publish_detection(self, detected: bool, center, area_ratio: float):
        self.detected_pub.publish(Bool(data=detected))

        msg = Point()
        if detected:
            msg.x = float(center[0])
            msg.y = float(center[1])
            msg.z = float(area_ratio)
        else:
            msg.x = -1.0
            msg.y = -1.0
            msg.z = 0.0
        self.pos_pub.publish(msg)

    def draw_overlay(self, frame_bgr: np.ndarray, mask: np.ndarray, target, area_ratio: float):
        vis = frame_bgr.copy()
        _, w = vis.shape[:2]

        if target is not None:
            cx, cy = target["center"]
            radius = int(target["radius"])
            cv2.circle(vis, (cx, cy), radius, (0, 255, 0), 2)
            cv2.circle(vis, (cx, cy), 4, (255, 0, 0), -1)
            cv2.putText(
                vis,
                f"detected center=({cx},{cy}) area_ratio={area_ratio:.4f}",
                (10, 26),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.62,
                (0, 255, 0),
                2,
            )
        else:
            cv2.putText(
                vis,
                "detected=no",
                (10, 26),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.62,
                (0, 0, 255),
                2,
            )

        mask_small = cv2.resize(cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR), (160, 120))
        vis[10:130, max(0, w - 170):max(0, w - 10)] = mask_small
        return vis

    def image_callback(self, msg: Image):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except CvBridgeError as exc:
            rospy.logwarn_throttle(1.0, "CvBridge error: %s", exc)
            return

        h, w = frame.shape[:2]
        target, mask = self.detect_target(frame)

        if target is None:
            self.publish_detection(False, None, 0.0)
            if self.publish_debug_image:
                debug = self.draw_overlay(frame, mask, None, 0.0)
                self.debug_pub.publish(self.bridge.cv2_to_imgmsg(debug, encoding="bgr8"))
            return

        cx, cy = target["center"]
        area_ratio = min(1.0, target["area"] / float(max(1, h * w)))
        self.publish_detection(True, (cx, cy), area_ratio)

        if self.publish_debug_image:
            debug = self.draw_overlay(frame, mask, target, area_ratio)
            self.debug_pub.publish(self.bridge.cv2_to_imgmsg(debug, encoding="bgr8"))


if __name__ == "__main__":
    try:
        KinectColorTracker()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
