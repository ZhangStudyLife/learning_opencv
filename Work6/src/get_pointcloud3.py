#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RGB-D 图像转彩色点云，并在退出时保存最后一帧 PCD。"""

from __future__ import annotations

import os
import struct
import subprocess
from typing import List, Sequence, Tuple

import numpy as np
import rospy
import sensor_msgs.point_cloud2 as pcl2
from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import CameraInfo, Image, PointCloud2, PointField
from std_msgs.msg import Header


FIELDS = [
    PointField("x", 0, PointField.FLOAT32, 1),
    PointField("y", 4, PointField.FLOAT32, 1),
    PointField("z", 8, PointField.FLOAT32, 1),
    PointField("rgb", 12, PointField.UINT32, 1),
]


class RGBD2PointCloud:
    def __init__(self) -> None:
        rospy.init_node("rgbd_to_pointcloud", anonymous=False)

        self.rgb_topic = rospy.get_param("~rgb_topic", "/kinect2/hd/image_color_rect")
        self.depth_topic = rospy.get_param("~depth_topic", "/kinect2/sd/image_depth_rect")
        self.camera_info_topic = rospy.get_param("~camera_info_topic", "/kinect2/sd/camera_info")
        self.pointcloud_topic = rospy.get_param("~pointcloud_topic", "/pointcloud_output")
        self.frame_id = rospy.get_param("~frame_id", "kinect2_camera_frame")
        self.publish_rate = max(0.1, float(rospy.get_param("~publish_rate", 10.0)))
        self.step = max(1, int(rospy.get_param("~step", 4)))
        self.min_depth_m = self._depth_limit_to_m(rospy.get_param("~min_depth_mm", 100))
        self.max_depth_m = self._depth_limit_to_m(rospy.get_param("~max_depth_mm", 5000))
        self.log_interval = max(0.5, float(rospy.get_param("~log_interval", 2.0)))
        self.save_on_shutdown = bool(rospy.get_param("~save_on_shutdown", True))
        self.pcd_output_path = rospy.get_param("~pcd_output_path", "output/pointcloud/output_cloud.pcd")

        self.bridge = CvBridge()
        self.rgb_image = None
        self.depth_image = None
        self.camera_info = None
        self.last_points_xyz: List[Tuple[float, float, float]] = []

        rospy.Subscriber(self.rgb_topic, Image, self.cb_rgb, queue_size=1, buff_size=2**26)
        rospy.Subscriber(self.depth_topic, Image, self.cb_depth, queue_size=1, buff_size=2**24)
        rospy.Subscriber(self.camera_info_topic, CameraInfo, self.cb_info, queue_size=1)
        self.publisher = rospy.Publisher(self.pointcloud_topic, PointCloud2, queue_size=1)
        self.timer = rospy.Timer(rospy.Duration(1.0 / self.publish_rate), self.publish_cloud)
        rospy.on_shutdown(self.on_shutdown)

        rospy.loginfo(
            "get_pointcloud3.py 已启动: rgb=%s depth=%s camera_info=%s output=%s",
            self.rgb_topic,
            self.depth_topic,
            self.camera_info_topic,
            self.pointcloud_topic,
        )

    def cb_rgb(self, msg: Image) -> None:
        try:
            self.rgb_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except CvBridgeError as exc:
            rospy.logwarn_throttle(self.log_interval, "彩色图转换失败: %s", exc)

    def cb_depth(self, msg: Image) -> None:
        try:
            self.depth_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding="passthrough")
        except CvBridgeError as exc:
            rospy.logwarn_throttle(self.log_interval, "深度图转换失败: %s", exc)

    def cb_info(self, msg: CameraInfo) -> None:
        self.camera_info = msg

    def publish_cloud(self, _event) -> None:
        if self.rgb_image is None or self.depth_image is None or self.camera_info is None:
            rospy.logwarn_throttle(self.log_interval, "等待 RGB、Depth 和 CameraInfo 数据。")
            return

        colored_points, pcd_points = self.build_points()
        if not colored_points:
            rospy.logwarn_throttle(self.log_interval, "当前没有可发布的彩色点云。")
            return

        self.last_points_xyz = pcd_points

        header = Header()
        header.stamp = rospy.Time.now()
        header.frame_id = self.frame_id
        cloud = pcl2.create_cloud(header, FIELDS, colored_points)
        self.publisher.publish(cloud)
        rospy.loginfo_throttle(self.log_interval, "发布彩色点云 %d 个点", len(colored_points))

    def build_points(self) -> Tuple[List[List[float]], List[Tuple[float, float, float]]]:
        rgb = self.rgb_image
        depth = self.depth_image
        info = self.camera_info

        fx = float(info.K[0])
        fy = float(info.K[4])
        cx = float(info.K[2])
        cy = float(info.K[5])
        if fx <= 0.0 or fy <= 0.0:
            rospy.logwarn_throttle(self.log_interval, "相机内参非法，fx/fy 不能为 0。")
            return [], []

        height_d, width_d = depth.shape
        height_rgb, width_rgb = rgb.shape[:2]
        colored_points: List[List[float]] = []
        pcd_points: List[Tuple[float, float, float]] = []

        for v in range(0, height_d, self.step):
            for u in range(0, width_d, self.step):
                z = self._depth_value_to_m(depth[v, u])
                if z is None:
                    continue
                if z < self.min_depth_m or z > self.max_depth_m:
                    continue

                x = (float(u) - cx) * z / fx
                y = (cy - float(v)) * z / fy

                u_rgb = min(width_rgb - 1, max(0, int(float(u) * width_rgb / width_d)))
                v_rgb = min(height_rgb - 1, max(0, int(float(v) * height_rgb / height_d)))
                b, g, r = [int(channel) for channel in rgb[v_rgb, u_rgb]]
                rgb_packed = struct.unpack("<I", struct.pack("BBBB", b, g, r, 255))[0]

                colored_points.append([x, y, z, rgb_packed])
                pcd_points.append((x, y, z))

        return colored_points, pcd_points

    def on_shutdown(self) -> None:
        if self.save_on_shutdown:
            self.save_pcd(self.last_points_xyz)

    def resolve_output_path(self) -> str:
        configured = self.pcd_output_path
        if os.path.isabs(configured):
            return configured

        package_root = self.find_package_root()
        if package_root:
            return os.path.join(package_root, configured)
        return os.path.abspath(configured)

    def find_package_root(self) -> str:
        try:
            return subprocess.check_output(["rospack", "find", "image_pkg"], text=True).strip()
        except Exception:
            return ""

    def save_pcd(self, points: Sequence[Tuple[float, float, float]]) -> None:
        if not points:
            rospy.logwarn("没有点云数据，跳过 PCD 保存。")
            return

        output_path = self.resolve_output_path()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        header = "\n".join(
            [
                "# .PCD v0.7 - Point Cloud Data file format",
                "VERSION 0.7",
                "FIELDS x y z",
                "SIZE 4 4 4",
                "TYPE F F F",
                "COUNT 1 1 1",
                "WIDTH %d" % len(points),
                "HEIGHT 1",
                "VIEWPOINT 0 0 0 1 0 0 0",
                "POINTS %d" % len(points),
                "DATA ascii",
            ]
        )

        try:
            with open(output_path, "w", encoding="ascii") as handle:
                handle.write(header)
                handle.write("\n")
                for x, y, z in points:
                    handle.write("%.6f %.6f %.6f\n" % (x, y, z))
        except OSError as exc:
            rospy.logerr("PCD 保存失败 %s: %s", output_path, exc)
            return

        rospy.loginfo("PCD 保存成功: %s，点数=%d", output_path, len(points))

    def _depth_limit_to_m(self, value) -> float:
        value = float(value)
        return value / 1000.0 if value > 20.0 else value

    def _depth_value_to_m(self, value):
        if not np.isfinite(value):
            return None
        value = float(value)
        if value <= 0.0:
            return None
        return value / 1000.0 if value > 20.0 else value


if __name__ == "__main__":
    try:
        RGBD2PointCloud()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
