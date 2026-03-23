#!/usr/bin/env python3
"""ROS monitor window for red ball detection and mecanum wheel motion."""

import math
import sys
from pathlib import Path

import cv2
import numpy as np
import rospy
from cv_bridge import CvBridge
from geometry_msgs.msg import Point, Twist
from sensor_msgs.msg import Image
from std_msgs.msg import Bool


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from mecanum_logic import twist_to_wheel_velocities


class MecanumWheelVisualizer:
    """Render the mecanum chassis and four wheel velocities."""

    def __init__(
        self,
        width=520,
        height=520,
        wheel_radius=0.08,
        wheel_base_length=0.5,
        wheel_base_width=0.4,
        max_wheel_speed=15.0,
    ):
        self.width = width
        self.height = height
        self.wheel_radius = wheel_radius
        self.wheel_base_length = wheel_base_length
        self.wheel_base_width = wheel_base_width
        self.max_wheel_speed = max_wheel_speed

        self.robot_width = 240
        self.robot_height = 300
        self.wheel_draw_radius = 36
        self.center_x = width // 2
        self.center_y = height // 2 + 10

        self.colors = {
            "bg": (18, 18, 18),
            "chassis": (60, 60, 60),
            "chassis_border": (150, 150, 150),
            "text": (240, 240, 240),
            "grid": (40, 40, 40),
            "forward": (0, 220, 0),
            "backward": (0, 0, 220),
            "idle": (110, 110, 110),
            "vector": (0, 220, 220),
        }

    def calculate_wheel_speeds(self, vx, vy, vz):
        """Calculate wheel speeds using the shared mecanum kinematics helper."""
        return twist_to_wheel_velocities(
            vx=vx,
            vy=vy,
            omega=vz,
            wheel_radius=self.wheel_radius,
            wheel_base_length=self.wheel_base_length,
            wheel_base_width=self.wheel_base_width,
            max_wheel_speed=self.max_wheel_speed,
        )

    def draw_wheel(self, canvas, center_x, center_y, speed, label, is_left_side):
        """Draw one mecanum wheel."""
        cv2.circle(canvas, (center_x, center_y), self.wheel_draw_radius, (40, 40, 40), -1)
        cv2.circle(canvas, (center_x, center_y), self.wheel_draw_radius, (110, 110, 110), 2)

        roller_angle = 45 if is_left_side else -45
        roller_color = self.colors["idle"]
        if speed > 0.05:
            roller_color = self.colors["forward"]
        elif speed < -0.05:
            roller_color = self.colors["backward"]

        for offset in (-18, -9, 0, 9, 18):
            angle_rad = math.radians(roller_angle)
            dx = math.cos(angle_rad) * self.wheel_draw_radius * 0.75
            dy = math.sin(angle_rad) * self.wheel_draw_radius * 0.75
            perp_x = -math.sin(angle_rad) * offset
            perp_y = math.cos(angle_rad) * offset

            start = (int(center_x + perp_x - dx), int(center_y + perp_y - dy))
            end = (int(center_x + perp_x + dx), int(center_y + perp_y + dy))
            cv2.line(canvas, start, end, roller_color, 3)
            cv2.line(canvas, start, end, (0, 0, 0), 1)

        cv2.putText(
            canvas,
            label,
            (center_x - 17, center_y + 6),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            self.colors["text"],
            1,
        )
        cv2.putText(
            canvas,
            f"{speed:+.2f}",
            (center_x - 35, center_y + self.wheel_draw_radius + 22),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            roller_color,
            1,
        )

    def draw_chassis(self, canvas, vx, vy, vz):
        """Draw the robot body and motion vectors."""
        half_w = self.robot_width // 2
        half_h = self.robot_height // 2
        corners = np.array(
            [
                [self.center_x - half_w, self.center_y - half_h],
                [self.center_x + half_w, self.center_y - half_h],
                [self.center_x + half_w, self.center_y + half_h],
                [self.center_x - half_w, self.center_y + half_h],
            ],
            dtype=np.int32,
        )

        cv2.fillPoly(canvas, [corners], self.colors["chassis"])
        cv2.polylines(canvas, [corners], True, self.colors["chassis_border"], 2)

        front_marker = np.array(
            [
                [self.center_x, self.center_y - half_h - 12],
                [self.center_x - 14, self.center_y - half_h + 6],
                [self.center_x + 14, self.center_y - half_h + 6],
            ],
            dtype=np.int32,
        )
        cv2.fillPoly(canvas, [front_marker], (0, 180, 255))

        if abs(vx) > 1e-3 or abs(vy) > 1e-3:
            # ROS body frame convention: +x forward, +y left.
            end_x = int(self.center_x - vy * 85)
            end_y = int(self.center_y - vx * 85)
            cv2.arrowedLine(
                canvas,
                (self.center_x, self.center_y),
                (end_x, end_y),
                self.colors["vector"],
                3,
                tipLength=0.25,
            )

        if abs(vz) > 1e-3:
            color = self.colors["forward"] if vz > 0 else self.colors["backward"]
            cv2.ellipse(canvas, (self.center_x, self.center_y), (55, 55), 0, -40, 220, color, 2)

    def create_visualization(self, vx, vy, vz):
        """Create a wheel kinematics panel."""
        canvas = np.full((self.height, self.width, 3), self.colors["bg"], dtype=np.uint8)
        cv2.putText(
            canvas,
            "MECANUM WHEEL VIEW",
            (120, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2,
        )

        wheel_speeds = self.calculate_wheel_speeds(vx, vy, vz)
        self.draw_chassis(canvas, vx, vy, vz)

        offset_x = self.robot_width // 2 + 50
        offset_y = self.robot_height // 2 - 45
        wheel_positions = {
            "FL": (self.center_x - offset_x, self.center_y - offset_y, True, wheel_speeds[0]),
            "FR": (self.center_x + offset_x, self.center_y - offset_y, False, wheel_speeds[1]),
            "RL": (self.center_x - offset_x, self.center_y + offset_y, True, wheel_speeds[2]),
            "RR": (self.center_x + offset_x, self.center_y + offset_y, False, wheel_speeds[3]),
        }

        for label, (center_x, center_y, is_left_side, speed) in wheel_positions.items():
            self.draw_wheel(canvas, center_x, center_y, speed, label, is_left_side)

        cv2.putText(
            canvas,
            f"cmd vx={vx:+.2f} vy={vy:+.2f} wz={vz:+.2f}",
            (60, self.height - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            self.colors["text"],
            1,
        )
        return canvas


class MecanumMonitorNode:
    """Subscribe to detector and controller topics and show a combined monitor window."""

    def __init__(self):
        rospy.init_node("mecanum_visualizer", anonymous=True)

        self.window_name = rospy.get_param("~window_name", "work3 monitor")
        self.input_mode = rospy.get_param("~input_mode", "video")
        self.refresh_rate = rospy.get_param("~refresh_rate", 30.0)
        self.frame_width = rospy.get_param("~frame_width", 640)
        self.frame_height = rospy.get_param("~frame_height", 480)
        self.wheel_radius = rospy.get_param("~wheel_radius", 0.08)
        self.wheel_base_length = rospy.get_param("~wheel_base_length", 0.5)
        self.wheel_base_width = rospy.get_param("~wheel_base_width", 0.4)
        self.max_wheel_speed = rospy.get_param("~max_wheel_speed", 15.0)

        self.bridge = CvBridge()
        self.latest_frame = None
        self.ball_position = None
        self.ball_detected = False
        self.current_cmd = Twist()

        self.wheel_visualizer = MecanumWheelVisualizer(
            wheel_radius=self.wheel_radius,
            wheel_base_length=self.wheel_base_length,
            wheel_base_width=self.wheel_base_width,
            max_wheel_speed=self.max_wheel_speed,
        )

        rospy.Subscriber("/camera/image_processed", Image, self.image_callback, queue_size=1)
        rospy.Subscriber("/ball_position", Point, self.ball_position_callback, queue_size=1)
        rospy.Subscriber("/ball_detected", Bool, self.ball_detected_callback, queue_size=1)
        rospy.Subscriber("/cmd_vel", Twist, self.cmd_vel_callback, queue_size=1)
        rospy.on_shutdown(self.shutdown)

        rospy.loginfo("Mecanum monitor started")

    def image_callback(self, msg: Image):
        """Store the latest processed detector image."""
        try:
            self.latest_frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except Exception as exc:  # pylint: disable=broad-except
            rospy.logwarn_throttle(2.0, "Failed to decode monitor image: %s", exc)

    def ball_position_callback(self, msg: Point):
        """Store the latest normalized ball position."""
        self.ball_position = (msg.x, msg.y, msg.z)

    def ball_detected_callback(self, msg: Bool):
        """Store the latest ball detection state."""
        self.ball_detected = msg.data

    def cmd_vel_callback(self, msg: Twist):
        """Store the latest commanded velocity."""
        self.current_cmd = msg

    def create_placeholder_frame(self):
        """Create a placeholder image before the detector starts publishing."""
        frame = np.full((self.frame_height, self.frame_width, 3), 35, dtype=np.uint8)
        cv2.putText(
            frame,
            "Waiting for /camera/image_processed ...",
            (40, self.frame_height // 2),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (220, 220, 220),
            2,
        )
        return frame

    def overlay_status(self, frame):
        """Draw current control and detection status on top of the image."""
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (frame.shape[1], 85), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)

        state_text = "ball detected" if self.ball_detected else "ball lost"
        state_color = (0, 255, 0) if self.ball_detected else (0, 0, 255)
        cv2.putText(
            frame,
            f"source={self.input_mode} {state_text}",
            (190, 28),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            state_color,
            2,
        )

        if self.ball_position is None:
            ball_text = "norm=(n/a, n/a)"
        else:
            ball_text = f"norm=({self.ball_position[0]:+.2f}, {self.ball_position[1]:+.2f}) r={self.ball_position[2]:.1f}"
        cv2.putText(frame, ball_text, (190, 54), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

        cmd_text = (
            f"cmd vx={self.current_cmd.linear.x:+.2f} "
            f"vy={self.current_cmd.linear.y:+.2f} "
            f"wz={self.current_cmd.angular.z:+.2f}"
        )
        cv2.putText(frame, cmd_text, (190, 78), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (0, 255, 255), 2)
        cv2.putText(
            frame,
            "Press q or Esc to stop",
            (15, frame.shape[0] - 15),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (220, 220, 220),
            1,
        )
        return frame

    def compose_window(self):
        """Create the combined monitor view."""
        frame = self.latest_frame.copy() if self.latest_frame is not None else self.create_placeholder_frame()
        frame = cv2.resize(frame, (self.frame_width, self.frame_height))
        frame = self.overlay_status(frame)

        wheel_panel = self.wheel_visualizer.create_visualization(
            self.current_cmd.linear.x,
            self.current_cmd.linear.y,
            self.current_cmd.angular.z,
        )
        wheel_panel = cv2.resize(wheel_panel, (self.frame_height, self.frame_height))
        return np.hstack([frame, wheel_panel])

    def run(self):
        """Display the monitor window until ROS shuts down."""
        rate = rospy.Rate(self.refresh_rate)

        while not rospy.is_shutdown():
            canvas = self.compose_window()
            cv2.imshow(self.window_name, canvas)
            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):
                rospy.signal_shutdown("Monitor window closed by user")
                break
            rate.sleep()

    def shutdown(self):
        """Close the OpenCV window."""
        cv2.destroyAllWindows()


def main():
    try:
        node = MecanumMonitorNode()
        node.run()
    except rospy.ROSInterruptException:
        pass


if __name__ == "__main__":
    main()
