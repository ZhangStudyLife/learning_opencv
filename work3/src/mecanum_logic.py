#!/usr/bin/env python3
"""Core math helpers for the work3 mecanum project."""

from typing import Tuple


def clamp(value: float, lower: float, upper: float) -> float:
    """Clamp a value into a closed interval."""
    return max(lower, min(upper, value))


def apply_deadzone(value: float, deadzone: float) -> float:
    """
    Scale a normalized axis value with a center deadzone.

    Input and output are both in [-1, 1]. Values inside the deadzone become 0.
    Values outside the deadzone are re-scaled to preserve the full output range.
    """
    value = clamp(value, -1.0, 1.0)
    deadzone = clamp(deadzone, 0.0, 0.99)

    magnitude = abs(value)
    if magnitude <= deadzone:
        return 0.0

    scaled = (magnitude - deadzone) / (1.0 - deadzone)
    return clamp((1.0 if value >= 0.0 else -1.0) * scaled, -1.0, 1.0)


def ball_position_to_cmd(
    norm_x: float,
    norm_y: float,
    max_linear_speed: float,
    deadzone_x: float,
    deadzone_y: float,
) -> Tuple[float, float, float]:
    """
    Convert normalized ball coordinates into a mecanum command.

    Mapping is fixed by the project requirement:
      linear.x = -norm_y * max_linear_speed
      linear.y = -norm_x * max_linear_speed
      angular.z = 0
    """
    scaled_x = apply_deadzone(norm_x, deadzone_x)
    scaled_y = apply_deadzone(norm_y, deadzone_y)

    linear_x = -scaled_y * max_linear_speed
    linear_y = -scaled_x * max_linear_speed
    angular_z = 0.0
    return linear_x, linear_y, angular_z


def pixel_position_to_normalized(
    pixel_x: float,
    pixel_y: float,
    frame_width: int,
    frame_height: int,
) -> Tuple[float, float]:
    """Convert a pixel position into normalized coordinates in [-1, 1]."""
    if frame_width <= 0 or frame_height <= 0:
        raise ValueError("frame size must be positive")

    norm_x = (pixel_x - frame_width / 2.0) / (frame_width / 2.0)
    norm_y = (pixel_y - frame_height / 2.0) / (frame_height / 2.0)
    return clamp(norm_x, -1.0, 1.0), clamp(norm_y, -1.0, 1.0)


def smooth_command(
    current_cmd: Tuple[float, float, float],
    target_cmd: Tuple[float, float, float],
    alpha: float,
) -> Tuple[float, float, float]:
    """Apply first-order low-pass smoothing to a velocity command."""
    alpha = clamp(alpha, 0.0, 1.0)
    return tuple(
        alpha * target + (1.0 - alpha) * current
        for current, target in zip(current_cmd, target_cmd)
    )


def zero_small_command(
    cmd: Tuple[float, float, float],
    epsilon: float = 1e-3,
) -> Tuple[float, float, float]:
    """Remove tiny residual values after smoothing."""
    return tuple(0.0 if abs(value) < epsilon else value for value in cmd)


def twist_to_wheel_velocities(
    vx: float,
    vy: float,
    omega: float,
    wheel_radius: float,
    wheel_base_length: float,
    wheel_base_width: float,
    max_wheel_speed: float = None,
) -> Tuple[float, float, float, float]:
    """Convert robot twist to mecanum wheel angular velocities."""
    if wheel_radius <= 0.0:
        raise ValueError("wheel_radius must be positive")

    turn_scale = (wheel_base_length + wheel_base_width) / 2.0

    v_fl = vx - vy - omega * turn_scale
    v_fr = vx + vy + omega * turn_scale
    v_rl = vx + vy - omega * turn_scale
    v_rr = vx - vy + omega * turn_scale

    wheel_speeds = (
        v_fl / wheel_radius,
        v_fr / wheel_radius,
        v_rl / wheel_radius,
        v_rr / wheel_radius,
    )

    if max_wheel_speed is None:
        return wheel_speeds

    return tuple(
        clamp(speed, -max_wheel_speed, max_wheel_speed) for speed in wheel_speeds
    )
