#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""深度图转三维点云，只发布 xyz 点云。"""

from __future__ import annotations

from typing import List

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
]


class Depth2PointCloud:
    def __init__(self) -> None:
        rospy.init_node("depth_to_pointcloud", anonymous=False)

        self.depth_topic = rospy.get_param("~depth_topic", "/kinect2/sd/image_depth_rect")
        self.camera_info_topic = rospy.get_param("~camera_info_topic", "/kinect2/sd/camera_info")
        self.pointcloud_topic = rospy.get_param("~pointcloud_topic", "/pointcloud_output")
        self.frame_id = rospy.get_param("~frame_id", "kinect2_camera_frame")
        self.publish_rate = max(0.1, float(rospy.get_param("~publish_rate", 10.0)))
        self.step = max(1, int(rospy.get_param("~step", 4)))
        self.min_depth_m = self._depth_limit_to_m(rospy.get_param("~min_depth_mm", 100))
        self.max_depth_m = self._depth_limit_to_m(rospy.get_param("~max_depth_mm", 5000))
        self.log_interval = max(0.5, float(rospy.get_param("~log_interval", 2.0)))

        self.bridge = CvBridge()
        self.depth_image = None
        self.camera_info = None

        rospy.Subscriber(self.depth_topic, Image, self.cb_depth, queue_size=1, buff_size=2**24)
        rospy.Subscriber(self.camera_info_topic, CameraInfo, self.cb_info, queue_size=1)
        self.publisher = rospy.Publisher(self.pointcloud_topic, PointCloud2, queue_size=1)
        self.timer = rospy.Timer(rospy.Duration(1.0 / self.publish_rate), self.publish_cloud)

        rospy.loginfo(
            "get_pointcloud.py 已启动: depth=%s camera_info=%s output=%s",
            self.depth_topic,
            self.camera_info_topic,
            self.pointcloud_topic,
        )

    def cb_depth(self, msg: Image) -> None:
        try:
            self.depth_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding="passthrough")
        except CvBridgeError as exc:
            rospy.logwarn_throttle(self.log_interval, "深度图转换失败: %s", exc)

    def cb_info(self, msg: CameraInfo) -> None:
        self.camera_info = msg

    def publish_cloud(self, _event) -> None:
        if self.depth_image is None or self.camera_info is None:
            rospy.logwarn_throttle(self.log_interval, "等待深度图和相机内参。")
            return

        points = self.build_points()
        if not points:
            rospy.logwarn_throttle(self.log_interval, "当前没有可发布的有效点云。")
            return

        header = Header()
        header.stamp = rospy.Time.now()
        header.frame_id = self.frame_id
        cloud = pcl2.create_cloud(header, FIELDS, points)
        self.publisher.publish(cloud)
        rospy.loginfo_throttle(self.log_interval, "发布基础点云 %d 个点", len(points))

    def build_points(self) -> List[List[float]]:
        depth = self.depth_image
        info = self.camera_info
        fx = float(info.K[0])
        fy = float(info.K[4])
        cx = float(info.K[2])
        cy = float(info.K[5])
        if fx <= 0.0 or fy <= 0.0:
            rospy.logwarn_throttle(self.log_interval, "相机内参非法，fx/fy 不能为 0。")
            return []

        height, width = depth.shape
        points: List[List[float]] = []
        for v in range(0, height, self.step):
            for u in range(0, width, self.step):
                z = self._depth_value_to_m(depth[v, u])
                if z is None:
                    continue
                if z < self.min_depth_m or z > self.max_depth_m:
                    continue

                x = (float(u) - cx) * z / fx
                y = (cy - float(v)) * z / fy
                points.append([x, y, z])
        return points

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
        Depth2PointCloud()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
