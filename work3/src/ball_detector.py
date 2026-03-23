#!/usr/bin/env python3
"""ROS node that publishes a virtual red ball from video or mouse input."""

import sys
from pathlib import Path

import cv2
import numpy as np
import rospy
from cv_bridge import CvBridge
from geometry_msgs.msg import Point
from sensor_msgs.msg import Image
from std_msgs.msg import Bool


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from mecanum_logic import pixel_position_to_normalized


class BallDetector:
    """Produce ball position topics from either video frames or mouse hover input."""

    def __init__(self):
        rospy.init_node("ball_detector", anonymous=True)

        self.input_mode = rospy.get_param("~input_mode", "video").strip().lower()
        self.camera_id = rospy.get_param("~camera_id", 0)
        self.video_path = rospy.get_param("~video_path", "")
        self.frame_width = rospy.get_param("~frame_width", 640)
        self.frame_height = rospy.get_param("~frame_height", 480)
        self.publish_rate = rospy.get_param("~publish_rate", 30.0)
        self.mouse_window_name = rospy.get_param("~mouse_window_name", "work3 mouse pad")
        self.mouse_ball_radius = rospy.get_param("~mouse_ball_radius", 24)

        self.lower_red1 = np.array(rospy.get_param("~lower_red1", [0, 100, 100]), dtype=np.uint8)
        self.upper_red1 = np.array(rospy.get_param("~upper_red1", [10, 255, 255]), dtype=np.uint8)
        self.lower_red2 = np.array(rospy.get_param("~lower_red2", [160, 100, 100]), dtype=np.uint8)
        self.upper_red2 = np.array(rospy.get_param("~upper_red2", [180, 255, 255]), dtype=np.uint8)

        self.erode_kernel = rospy.get_param("~erode", 2)
        self.dilate_kernel = rospy.get_param("~dilate", 2)
        self.min_radius = rospy.get_param("~min_radius", 10)
        self.min_area = rospy.get_param("~min_area", 100)

        self.kalman = self.create_kalman_filter()
        self.kalman_initialized = False
        self.bridge = CvBridge()

        self.pos_pub = rospy.Publisher("/ball_position", Point, queue_size=10)
        self.detected_pub = rospy.Publisher("/ball_detected", Bool, queue_size=10)
        self.image_pub = rospy.Publisher("/camera/image_processed", Image, queue_size=10)

        self.cap = None
        self.mouse_position = (self.frame_width // 2, self.frame_height // 2)
        self.mouse_window_created = False

        self.validate_mode()
        if self.input_mode == "video":
            self.cap = self.open_video_source()
        else:
            self.setup_mouse_window()

        rospy.on_shutdown(self.shutdown)
        rospy.loginfo("Ball detector started with input_mode=%s", self.input_mode)

    def validate_mode(self):
        """Validate the requested input mode."""
        valid_modes = {"video", "mouse"}
        if self.input_mode not in valid_modes:
            raise ValueError(f"Unsupported input_mode: {self.input_mode}")

    @staticmethod
    def create_kalman_filter():
        """Create a simple constant-velocity Kalman filter."""
        kalman = cv2.KalmanFilter(4, 2)
        kalman.transitionMatrix = np.array(
            [[1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0], [0, 0, 0, 1]],
            dtype=np.float32,
        )
        kalman.measurementMatrix = np.array(
            [[1, 0, 0, 0], [0, 1, 0, 0]],
            dtype=np.float32,
        )
        kalman.processNoiseCov = np.eye(4, dtype=np.float32) * 0.01
        kalman.measurementNoiseCov = np.eye(2, dtype=np.float32) * 0.1
        kalman.errorCovPost = np.eye(4, dtype=np.float32)
        return kalman

    def setup_mouse_window(self):
        """Create the mouse joystick pad window."""
        cv2.namedWindow(self.mouse_window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.mouse_window_name, self.frame_width, self.frame_height)
        cv2.setMouseCallback(self.mouse_window_name, self.on_mouse_event)
        self.mouse_window_created = True

    def on_mouse_event(self, event, x, y, _flags, _userdata):
        """Track the current mouse position inside the virtual joystick pad."""
        if event in (cv2.EVENT_MOUSEMOVE, cv2.EVENT_LBUTTONDOWN, cv2.EVENT_LBUTTONUP):
            clamped_x = int(min(max(x, 0), self.frame_width - 1))
            clamped_y = int(min(max(y, 0), self.frame_height - 1))
            self.mouse_position = (clamped_x, clamped_y)

    def open_camera(self):
        """Open the camera and configure capture size."""
        cap = cv2.VideoCapture(self.camera_id)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
        return cap

    def open_video_source(self):
        """Prefer a video file and fall back to a camera when needed."""
        if self.video_path:
            video_file = Path(self.video_path).expanduser()
            cap = cv2.VideoCapture(str(video_file))
            if cap.isOpened():
                self.video_path = str(video_file)
                rospy.loginfo("Using video file: %s", self.video_path)
                return cap
            rospy.logwarn("Cannot open video file %s, fallback to camera %s", self.video_path, self.camera_id)

        cap = self.open_camera()
        if not cap.isOpened():
            raise RuntimeError("Failed to open both video file and camera")

        self.video_path = ""
        rospy.loginfo("Using camera: %s", self.camera_id)
        return cap

    def read_frame(self):
        """Read the next frame and loop when using a video file."""
        ret, frame = self.cap.read()
        if ret:
            return True, frame

        if self.video_path:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()
            if ret:
                return True, frame

        return False, None

    def create_mask(self, frame):
        """Create a binary mask for red pixels."""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask1 = cv2.inRange(hsv, self.lower_red1, self.upper_red1)
        mask2 = cv2.inRange(hsv, self.lower_red2, self.upper_red2)
        mask = cv2.bitwise_or(mask1, mask2)

        if self.erode_kernel > 0:
            kernel = np.ones((self.erode_kernel, self.erode_kernel), np.uint8)
            mask = cv2.erode(mask, kernel, iterations=1)
        if self.dilate_kernel > 0:
            kernel = np.ones((self.dilate_kernel, self.dilate_kernel), np.uint8)
            mask = cv2.dilate(mask, kernel, iterations=1)

        return mask

    def detect_ball_from_video(self, frame):
        """Detect the red ball from a video frame."""
        mask = self.create_mask(frame)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        best_circle = None
        best_score = 0.0

        for contour in contours:
            area = cv2.contourArea(contour)
            if area < self.min_area:
                continue

            (x, y), radius = cv2.minEnclosingCircle(contour)
            if radius < self.min_radius:
                continue

            perimeter = cv2.arcLength(contour, True)
            if perimeter <= 0.0:
                continue

            circularity = 4.0 * np.pi * area / (perimeter ** 2)
            score = area * circularity
            if score > best_score:
                best_score = score
                best_circle = (int(x), int(y), int(radius))

        vis_frame = frame.copy()
        self.draw_video_overlay(vis_frame, mask, best_circle)
        return best_circle, vis_frame

    def draw_video_overlay(self, frame, mask, best_circle):
        """Draw detector overlays on the video image."""
        if best_circle:
            x, y, radius = best_circle
            cv2.circle(frame, (x, y), radius, (0, 255, 0), 2)
            cv2.circle(frame, (x, y), 3, (255, 0, 0), -1)
            text = f"source=video ball=({x}, {y}) r={radius}"
            color = (0, 255, 0)
        else:
            text = "source=video ball=not detected"
            color = (0, 0, 255)

        cv2.putText(frame, text, (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.65, color, 2)

        mask_bgr = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        mask_small = cv2.resize(mask_bgr, (160, 120))
        frame[10:130, 10:170] = mask_small
        cv2.rectangle(frame, (10, 10), (170, 130), (255, 255, 255), 1)

    def create_mouse_pad_frame(self):
        """Create the virtual joystick pad image."""
        frame = np.full((self.frame_height, self.frame_width, 3), 245, dtype=np.uint8)
        grid_color = (175, 175, 175)

        cv2.line(frame, (self.frame_width // 3, 0), (self.frame_width // 3, self.frame_height), grid_color, 1)
        cv2.line(frame, (self.frame_width * 2 // 3, 0), (self.frame_width * 2 // 3, self.frame_height), grid_color, 1)
        cv2.line(frame, (0, self.frame_height // 3), (self.frame_width, self.frame_height // 3), grid_color, 1)
        cv2.line(frame, (0, self.frame_height * 2 // 3), (self.frame_width, self.frame_height * 2 // 3), grid_color, 1)

        center_x = self.frame_width // 2
        center_y = self.frame_height // 2
        cv2.line(frame, (center_x - 20, center_y), (center_x + 20, center_y), (110, 110, 110), 2)
        cv2.line(frame, (center_x, center_y - 20), (center_x, center_y + 20), (110, 110, 110), 2)

        mouse_x, mouse_y = self.mouse_position
        cv2.circle(frame, (mouse_x, mouse_y), self.mouse_ball_radius, (0, 0, 255), -1)
        cv2.circle(frame, (mouse_x, mouse_y), self.mouse_ball_radius + 2, (30, 30, 30), 2)

        norm_x, norm_y = pixel_position_to_normalized(mouse_x, mouse_y, self.frame_width, self.frame_height)
        cv2.putText(frame, "source=mouse", (15, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (50, 50, 50), 2)
        cv2.putText(
            frame,
            f"mouse=({mouse_x}, {mouse_y}) norm=({norm_x:+.2f}, {norm_y:+.2f})",
            (15, 58),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (70, 70, 70),
            2,
        )
        cv2.putText(
            frame,
            "Hover mouse to control the red ball | Q/Esc to exit",
            (15, self.frame_height - 18),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (90, 90, 90),
            1,
        )
        return frame, norm_x, norm_y

    def update_kalman(self, measured_x, measured_y):
        """Filter the detected position for smoother control."""
        measurement = np.array([[np.float32(measured_x)], [np.float32(measured_y)]])

        if not self.kalman_initialized:
            self.kalman.statePost = np.array(
                [[measured_x], [measured_y], [0], [0]],
                dtype=np.float32,
            )
            self.kalman_initialized = True

        prediction = self.kalman.predict()
        self.kalman.correct(measurement)
        return int(prediction[0]), int(prediction[1])

    def publish_ball_state(self, norm_x, norm_y, radius, detected, vis_frame):
        """Publish the standard detector topics."""
        self.detected_pub.publish(Bool(data=detected))

        if detected:
            pos_msg = Point()
            pos_msg.x = norm_x
            pos_msg.y = norm_y
            pos_msg.z = radius
            self.pos_pub.publish(pos_msg)

        try:
            image_msg = self.bridge.cv2_to_imgmsg(vis_frame, "bgr8")
            self.image_pub.publish(image_msg)
        except Exception as exc:  # pylint: disable=broad-except
            rospy.logwarn_throttle(2.0, "Failed to publish processed image: %s", exc)

    def handle_video_mode(self):
        """Read a frame, detect the ball, and publish ROS messages."""
        ret, frame = self.read_frame()
        if not ret or frame is None:
            rospy.logwarn_throttle(2.0, "Failed to read a frame from the video source")
            return

        best_circle, vis_frame = self.detect_ball_from_video(frame)
        detected = best_circle is not None

        if detected:
            x, y, radius = best_circle
            filtered_x, filtered_y = self.update_kalman(x, y)
            norm_x, norm_y = pixel_position_to_normalized(filtered_x, filtered_y, frame.shape[1], frame.shape[0])
            cv2.circle(vis_frame, (filtered_x, filtered_y), 5, (255, 0, 0), -1)
            cv2.putText(
                vis_frame,
                f"norm=({norm_x:+.2f}, {norm_y:+.2f})",
                (10, 155),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 0),
                2,
            )
            self.publish_ball_state(norm_x, norm_y, radius, True, vis_frame)
        else:
            self.publish_ball_state(0.0, 0.0, 0.0, False, vis_frame)

    def handle_mouse_mode(self):
        """Render the mouse pad and publish it as the virtual red ball state."""
        frame, norm_x, norm_y = self.create_mouse_pad_frame()
        self.publish_ball_state(norm_x, norm_y, float(self.mouse_ball_radius), True, frame)

        cv2.imshow(self.mouse_window_name, frame)
        key = cv2.waitKey(1) & 0xFF
        if key in (ord("q"), 27):
            rospy.signal_shutdown("Mouse pad closed by user")

    def run(self):
        """Main detector loop."""
        rate = rospy.Rate(self.publish_rate)

        while not rospy.is_shutdown():
            if self.input_mode == "mouse":
                self.handle_mouse_mode()
            else:
                self.handle_video_mode()
            rate.sleep()

    def shutdown(self):
        """Release resources on exit."""
        if self.cap is not None:
            self.cap.release()
        if self.mouse_window_created:
            try:
                cv2.destroyWindow(self.mouse_window_name)
            except cv2.error:
                pass


def main():
    try:
        detector = BallDetector()
        detector.run()
    except rospy.ROSInterruptException:
        pass


if __name__ == "__main__":
    main()
