#!/usr/bin/env python3
"""Unit tests for the shared mecanum control math."""

import sys
import unittest
from pathlib import Path


SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from mecanum_logic import (
    apply_deadzone,
    ball_position_to_cmd,
    pixel_position_to_normalized,
    twist_to_wheel_velocities,
)


class MecanumLogicTests(unittest.TestCase):
    """Test the pure functions used by the ROS nodes."""

    def assert_tuple_close(self, actual, expected, places=6):
        for current, target in zip(actual, expected):
            self.assertAlmostEqual(current, target, places=places)

    def test_center_position_stops_robot(self):
        self.assert_tuple_close(
            ball_position_to_cmd(0.0, 0.0, 1.0, 0.12, 0.12),
            (0.0, 0.0, 0.0),
        )

    def test_cardinal_directions_have_expected_signs(self):
        self.assert_tuple_close(
            ball_position_to_cmd(0.0, -1.0, 1.0, 0.0, 0.0),
            (1.0, 0.0, 0.0),
        )
        self.assert_tuple_close(
            ball_position_to_cmd(0.0, 1.0, 1.0, 0.0, 0.0),
            (-1.0, 0.0, 0.0),
        )
        self.assert_tuple_close(
            ball_position_to_cmd(-1.0, 0.0, 1.0, 0.0, 0.0),
            (0.0, 1.0, 0.0),
        )
        self.assert_tuple_close(
            ball_position_to_cmd(1.0, 0.0, 1.0, 0.0, 0.0),
            (0.0, -1.0, 0.0),
        )

    def test_corner_position_generates_diagonal_motion(self):
        self.assert_tuple_close(
            ball_position_to_cmd(-1.0, -1.0, 1.0, 0.0, 0.0),
            (1.0, 1.0, 0.0),
        )
        self.assert_tuple_close(
            ball_position_to_cmd(1.0, 1.0, 1.0, 0.0, 0.0),
            (-1.0, -1.0, 0.0),
        )

    def test_deadzone_scales_after_boundary(self):
        self.assertAlmostEqual(apply_deadzone(0.09, 0.1), 0.0)
        self.assertAlmostEqual(apply_deadzone(-0.1, 0.1), 0.0)
        self.assertAlmostEqual(apply_deadzone(0.55, 0.1), 0.5)
        self.assertAlmostEqual(apply_deadzone(-0.55, 0.1), -0.5)

    def test_pixel_position_to_normalized_center(self):
        self.assert_tuple_close(
            pixel_position_to_normalized(320, 240, 640, 480),
            (0.0, 0.0),
        )

    def test_pixel_position_to_normalized_corners(self):
        self.assert_tuple_close(
            pixel_position_to_normalized(0, 0, 640, 480),
            (-1.0, -1.0),
        )
        self.assert_tuple_close(
            pixel_position_to_normalized(639, 479, 640, 480),
            (0.996875, 0.9958333333333333),
        )

    def test_forward_twist_to_wheels(self):
        self.assert_tuple_close(
            twist_to_wheel_velocities(1.0, 0.0, 0.0, 1.0, 0.5, 0.4),
            (1.0, 1.0, 1.0, 1.0),
        )

    def test_strafe_twist_to_wheels(self):
        self.assert_tuple_close(
            twist_to_wheel_velocities(0.0, 1.0, 0.0, 1.0, 0.5, 0.4),
            (-1.0, 1.0, 1.0, -1.0),
        )

    def test_diagonal_twist_to_wheels(self):
        self.assert_tuple_close(
            twist_to_wheel_velocities(1.0, 1.0, 0.0, 1.0, 0.5, 0.4),
            (0.0, 2.0, 2.0, 0.0),
        )


if __name__ == "__main__":
    unittest.main()
