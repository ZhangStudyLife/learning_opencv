#!/usr/bin/env python3
"""
Generate a sample video with a moving red ball for work3.
"""

from pathlib import Path
import argparse

import cv2
import numpy as np


WIDTH = 640
HEIGHT = 480
FPS = 30
BALL_RADIUS = 28
FRAMES_PER_ZONE = 30
TRANSITION_FRAMES = 18


def zone_centers(width, height):
    xs = [width // 6, width // 2, width * 5 // 6]
    ys = [height // 6, height // 2, height * 5 // 6]
    return [
        (xs[0], ys[0]), (xs[1], ys[0]), (xs[2], ys[0]),
        (xs[0], ys[1]), (xs[1], ys[1]), (xs[2], ys[1]),
        (xs[0], ys[2]), (xs[1], ys[2]), (xs[2], ys[2]),
    ]


def lerp(p0, p1, t):
    return (
        int(round(p0[0] + (p1[0] - p0[0]) * t)),
        int(round(p0[1] + (p1[1] - p0[1]) * t)),
    )


def draw_grid(frame):
    color = (180, 180, 180)
    cv2.line(frame, (WIDTH // 3, 0), (WIDTH // 3, HEIGHT), color, 1)
    cv2.line(frame, (WIDTH * 2 // 3, 0), (WIDTH * 2 // 3, HEIGHT), color, 1)
    cv2.line(frame, (0, HEIGHT // 3), (WIDTH, HEIGHT // 3), color, 1)
    cv2.line(frame, (0, HEIGHT * 2 // 3), (WIDTH, HEIGHT * 2 // 3), color, 1)


def make_frame(ball_pos, frame_index, label):
    frame = np.full((HEIGHT, WIDTH, 3), 245, dtype=np.uint8)
    draw_grid(frame)

    cv2.circle(frame, ball_pos, BALL_RADIUS, (0, 0, 255), -1)
    cv2.circle(frame, ball_pos, BALL_RADIUS + 3, (20, 20, 20), 2)

    cv2.putText(frame, "work3 red ball sample", (18, 32),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (40, 40, 40), 2)
    cv2.putText(frame, f"zone: {label}", (18, 66),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (30, 80, 30), 2)
    cv2.putText(frame, f"frame: {frame_index:04d}", (18, HEIGHT - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (80, 80, 80), 1)
    return frame


def generate_positions():
    labels = ["LU", "FW", "RU", "LF", "ST", "RT", "LD", "BW", "RD"]
    centers = zone_centers(WIDTH, HEIGHT)

    for idx, center in enumerate(centers):
        label = labels[idx]
        for _ in range(FRAMES_PER_ZONE):
            yield center, label

        next_center = centers[(idx + 1) % len(centers)]
        next_label = labels[(idx + 1) % len(labels)]
        for step in range(1, TRANSITION_FRAMES + 1):
            t = step / TRANSITION_FRAMES
            yield lerp(center, next_center, t), f"{label}->{next_label}"


def create_video(output_path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(
        str(output_path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        FPS,
        (WIDTH, HEIGHT),
    )
    if not writer.isOpened():
        raise RuntimeError(f"Failed to open video writer: {output_path}")

    frame_total = 0
    for frame_total, (pos, label) in enumerate(generate_positions(), start=1):
        writer.write(make_frame(pos, frame_total, label))

    writer.release()
    return frame_total


def main():
    parser = argparse.ArgumentParser(description="Create a sample red ball video.")
    parser.add_argument(
        "--output",
        "-o",
        default=str(Path(__file__).resolve().parents[1] / "test_video.mp4"),
        help="Output video path",
    )
    args = parser.parse_args()

    output_path = Path(args.output).expanduser().resolve()
    frame_total = create_video(output_path)
    duration = frame_total / FPS
    print(f"Created video: {output_path}")
    print(f"Frames: {frame_total}")
    print(f"Duration: {duration:.2f}s")
    print(f"Resolution: {WIDTH}x{HEIGHT} @ {FPS} FPS")


if __name__ == "__main__":
    main()
