:::info
3D 彩色点云的生成原理：基于针孔相机模型，以深度图为载体，通过相机内参将每个像素的2D坐标与深度值反投影为3D空间坐标，再将彩色图中对应像素的RGB颜色信息绑定到该3D点上，最终形成带颜色的3D点集合。

:::

#### `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`原理`</font>`

`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`RGB-D 相机可同时输出`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`彩色图像（RGB）与深度图像（Depth）`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`，通过相机内参（焦距、光心）对每个像素进行三维坐标反投影，即可将二维像素坐标转换为相机坐标系下的三维空间坐标，再将像素颜色信息与三维坐标绑定，生成带颜色的三维点云，这是机器人视觉、三维重建的基础。`</font>`

#### `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`算法关键`</font>`

##### `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">` 数据订阅与格式适配`</font>`

+ `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`订阅相机话题：`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">/kinect2/hd/image_color_rect</font>``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`（彩色图，`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">bgr8</font>``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">` 编码）、`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">/kinect2/sd/image_depth_rect</font>``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`（深度图，`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">16UC1</font>``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">` 编码）、`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">/kinect2/sd/camera_info</font>``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`（相机内参）`</font>`
+ `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`采用 `</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">cv_bridge</font>``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">` 实现 ROS 图像消息与 OpenCV 格式的互转，适配 Kinect2 仿真数据格式`</font>`

##### `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`三维坐标计算`</font>`

`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`基于针孔相机模型，遍历像素计算三维坐标：`</font>`

`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);"></font>`$ z = \frac{1000.0}{\text{depth}}, \quad x = \frac{(u - c_x) \cdot z}{f_x}, \quad y = \frac{(c_y - v) \cdot z}{f_y} $

`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`其中 `</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`fx,fy`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">` 为相机焦距，`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`cx,cy`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">` 为光心坐标，`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`depth`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">` 为深度值（单位：毫米，转换为米），修正 y 轴方向以适配 RViz 显示。`</font>`

##### `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`颜色编码与点云发布`</font>`

+ `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`颜色编码：将 OpenCV 读取的 `</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">bgr8</font>``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">` 格式颜色，按 `</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">r/g/b/alpha</font>``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">` 顺序打包为 `</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">uint32</font>``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">` 格式，适配 RViz `</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">RGB8</font>``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">` 颜色转换器；`</font>`
+ `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`点云发布：通过 `</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">sensor_msgs.point_cloud2.create_cloud</font>``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">` 构建 `</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">PointCloud2</font>``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">` 消息，发布到 `</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">/pointcloud_output</font>``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">` 话题，坐标系设为 `</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">kinect2_camera_frame</font>``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`，实现 RViz 实时可视化。`</font>`

##### `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`工程优化`</font>`

 工程优化是保证机器人视觉程序**`<font style="color:rgb(31, 35, 41);background-color:rgba(0, 0, 0, 0);">`稳定运行、高效执行、适配实际硬件环境`</font>`**的关键步骤。在 RGB-D 转点云的实现中，通过降采样减少点云数量、过滤无效深度数据、控制程序运行频率、优化消息队列等方式，可以显著降低 CPU 与内存的占用，避免节点卡顿、死机或数据阻塞，同时提升点云质量与系统实时性。

合理的工程优化能让算法从理论验证阶段走向可靠的实际应用，使程序在机器人平台上高效、稳定、可持续运行，是开发实用化 ROS 节点的必要环节。

:::danger
请注意：RViz 自带的点云，是 Kinect2 官方经过 C++ 深度优化过代码，点云密度极高，颜色完全对齐，深度无噪声，发布频率 30Hz。由于硬件条件有限，我们这里了解算法原理，并用 Python 演示，在性能、精度、对齐上，与官方驱动不可比拟。请通过实验感受这一点。

如果你有兴趣做相关的研究，可以尝试从以下几方面对代码进行优化：

+ `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`采用降采样降低计算量，平衡实时性与精度`</font>`
+ `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`过滤无效深度值，提升点云质量`</font>`
+ `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`优化订阅队列与循环频率，避免节点阻塞`</font>`

:::

---

#### `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`RGB-D 相机的输出`</font>`

在 ROS 中，RGB-D相机先将采集到的原始 RGB 图像、深度图像封装为标准的图像消息发布，我们需要将这些二维的图像数据转换为点云数据。

之前的课程我们讲解过，Kinect2相机输出的数据有 `sensor_msgs/PointCloud2`消息格式进行传输，这一格式正是连接 ROS 生态与三维点云处理库（PCL）的核心桥梁。

| **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`特性`</font>`**     | **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`普通 RGB 相机 (Camera)`</font>`**                                                     | **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`RGB-D 深度相机 (Kinect)`</font>`**                                                                                                                                                                         |
| ----------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`核心能力`</font>`** | `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`二维彩色成像`</font>`                                                                         | `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`二维彩色成像 + 三维深度测量`</font>`                                                                                                                                                                               |
| **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`深度信息`</font>`** | `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`❌`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">` 无`</font>` | `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`✅`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">` 有`</font>`                                                                                                                      |
| **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`数据输出`</font>`** | `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">sensor_msgs/Image</font>`                                                                        | `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">sensor_msgs/Image</font>``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">` + `</font>**<font style="color:#DF2A3F;background-color:rgba(0, 0, 0, 0);">sensor_msgs/PointCloud2</font>**` |

#### 创建脚本文件 get_pointcloud.py

```python
roscd image_pkg
cd scripts
touch get_pointcloud.py
chmod +x get_pointcloud.py 
```

#### 参考代码

在本次实验中，我们在生成 3D点云数据时，仅用深度图的数据：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深度图转三维点云（只用深度图，无彩色）
"""

import rospy
import cv2
import numpy as np
from sensor_msgs.msg import Image, PointCloud2, PointField, CameraInfo
from cv_bridge import CvBridge
import sensor_msgs.point_cloud2 as pcl2

# ===================== 点云格式定义（只用x,y,z，无rgb）=====================
FIELDS = [
    PointField('x',  0, PointField.FLOAT32, 1),
    PointField('y',  4, PointField.FLOAT32, 1),
    PointField('z',  8, PointField.FLOAT32, 1),
]

class Depth2PointCloud:
    def __init__(self):
        rospy.init_node('depth_to_pointcloud')
        self.bridge = CvBridge()
      
        self.depth = None
        self.info = None

        # ===================== 只订阅深度图和内参，不订阅彩色图 =====================
        self.sub_depth = rospy.Subscriber(
            "/kinect2/sd/image_depth_rect", Image, self.cb_depth
        )
        self.sub_info = rospy.Subscriber(
            "/kinect2/sd/camera_info", CameraInfo, self.cb_info
        )

        self.pub = rospy.Publisher("/pointcloud_output", PointCloud2, queue_size=1)
        rospy.loginfo("✅ 只用深度图的点云节点已启动")

    def cb_depth(self, msg):
        try:
            self.depth = self.bridge.imgmsg_to_cv2(msg, "16UC1")
        except Exception as e:
            rospy.logerr(f"深度图转换失败: {e}")

    def cb_info(self, msg):
        self.info = msg

    def run(self):
        rate = rospy.Rate(10)  # 降低到10Hz，避免卡顿
      
        while not rospy.is_shutdown():
            # ✅ 检查深度图和内参
            if self.depth is None or self.info is None:
                rate.sleep()
                continue

            h, w = self.depth.shape
            fx, fy = self.info.K[0], self.info.K[4]
            cx, cy = self.info.K[2], self.info.K[5]
          
            points = []
            step = 4  # ✅ 加降采样，避免卡顿

            for v in range(0, h, step):
                for u in range(0, w, step):
                    d = self.depth[v, u]
                  
                    # ✅ 过滤d=0，不过滤其他值
                    if d == 0:
                        continue
                  
                    # ✅ 适配深度数据，单位是米
                    z = d / 1.0
                  
                    # ✅ Y轴方向适配RViz，点云不会倒立
                    x = (u - cx) * z / fx
                    y = -(v - cy) * z / fy
                  
                    points.append([x, y, z])

            rospy.loginfo(f"📊 本次生成点云数量：{len(points)} 个")

            if len(points) > 0:
                header = rospy.Header()
                header.stamp = rospy.Time.now()
                header.frame_id = "kinect2_camera_frame"  
              
                cloud = pcl2.create_cloud(header, FIELDS, points)
                self.pub.publish(cloud)

            rate.sleep()

if __name__ == '__main__':
    try:
        Depth2PointCloud().run()
    except rospy.ROSInterruptException:
        pass
```

#### 实验

##### 启动 wpr_bottles.launch 场景

```bash
roslaunch wpr_simulation wpr_bottles.launch
```

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1775479873196-d3b13664-8414-4c86-92ab-8c095ffc93a4.png" width="1172" title="" crop="0,0,1,1" id="wUsJe" class="ne-image">

##### 启动 get_pointcloud.py 节点

```bash
rosrun image_pkg get_pointcloud.py
```

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1775483184946-4c2c5efa-347a-46a6-8ed1-648194e53616.png" width="736" title="" crop="0,0,1,1" id="JNJ89" class="ne-image">

##### 启动 RViz观察

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1775504141176-5fcc838f-ed72-4ec7-858b-b367dd070f8e.png" width="1056.8" title="" crop="0,0,1,1" id="u5ec029a2" class="ne-image">

在演示效果时，点的渲染样式建议选择 Points，像素大小设置为 3 ：若点大小设置过大，点云会出现膨胀、重叠与变形；若点大小过小，则点云难以观察，甚至会丢失颜色信息，导致无法正常显示彩色效果。

在 ROS 环境中，虽然可以通过 RViz 实时查看三维点云，但手动调整观测视角较为繁琐，且点大小、渲染方式等参数不易控制。因此，我们将生成的三维点云数据保存为 PCD 格式文件，再使用 PCL 可视化工具进行离线查看，便于更清晰、稳定地观察点云效果。

#### 安装 PCL工具

```bash
sudo apt update
sudo apt install pcl-tools
```

##### 运行代码，并用PCL Visualizer观察

修改代码，比如 get_pointcloud3.py

```python
roscd image_pkg
cd scripts
touch get_pointcloud3.py
chmod +x get_pointcloud3.py 
```

参考代码：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深度图转三维点云 + 保存PCD文件
✅ 只用深度图，无彩色
✅ 按Ctrl+C自动保存最后一帧为output_cloud.pcd
"""

import rospy
import cv2
import numpy as np
from sensor_msgs.msg import Image, PointCloud2, PointField, CameraInfo
from cv_bridge import CvBridge
import sensor_msgs.point_cloud2 as pcl2
import atexit  # 用于程序退出时自动保存PCD

# ===================== 点云格式定义 =====================
FIELDS = [
    PointField('x',  0, PointField.FLOAT32, 1),
    PointField('y',  4, PointField.FLOAT32, 1),
    PointField('z',  8, PointField.FLOAT32, 1),
]

class Depth2PointCloud:
    def __init__(self):
        rospy.init_node('depth_to_pointcloud')
        self.bridge = CvBridge()
      
        self.depth = None
        self.info = None
        self.last_points = []  # 存储最后一帧点云数据，用于保存PCD

        # 订阅话题
        self.sub_depth = rospy.Subscriber(
            "/kinect2/sd/image_depth_rect", Image, self.cb_depth
        )
        self.sub_info = rospy.Subscriber(
            "/kinect2/sd/camera_info", CameraInfo, self.cb_info
        )

        self.pub = rospy.Publisher("/pointcloud_output", PointCloud2, queue_size=1)
      
        # 注册退出函数：程序停止时自动保存PCD
        atexit.register(self.save_pcd)
      
        rospy.loginfo("✅ 点云节点已启动，按Ctrl+C停止并自动保存PCD")

    def cb_depth(self, msg):
        try:
            self.depth = self.bridge.imgmsg_to_cv2(msg, "16UC1")
        except Exception as e:
            rospy.logerr(f"深度图转换失败: {e}")

    def cb_info(self, msg):
        self.info = msg

    def save_pcd(self):
        """程序退出时自动保存最后一帧为PCD文件（文本格式，无需额外库）"""
        if len(self.last_points) == 0:
            rospy.logwarn("没有点云数据，跳过保存")
            return
      
        filename = "output_cloud.pcd"
        rospy.loginfo(f"💾 正在保存点云到 {filename} ...")
      
        # 生成PCD文件头（文本格式，ASCII编码）
        pcd_header = f"""# .PCD v.7 - Point Cloud Data file format
VERSION .7
FIELDS x y z
SIZE 4 4 4
TYPE F F F
COUNT 1 1 1
WIDTH {len(self.last_points)}
HEIGHT 1
VIEWPOINT 0 0 0 1 0 0 0
POINTS {len(self.last_points)}
DATA ascii
"""
      
        # 写入文件
        with open(filename, 'w') as f:
            f.write(pcd_header)
            # 逐点写入x y z坐标
            for point in self.last_points:
                f.write(f"{point[0]:.6f} {point[1]:.6f} {point[2]:.6f}\n")
      
        rospy.loginfo(f"✅ 点云保存成功！共 {len(self.last_points)} 个点")

    def run(self):
        rate = rospy.Rate(10)
      
        while not rospy.is_shutdown():
            if self.depth is None or self.info is None:
                rate.sleep()
                continue

            h, w = self.depth.shape
            fx, fy = self.info.K[0], self.info.K[4]
            cx, cy = self.info.K[2], self.info.K[5]

            # 修改step = 2，点云会变稠密，保存更多细节
            points = []
            step = 4

            for v in range(0, h, step):
                for u in range(0, w, step):
                    d = self.depth[v, u]
                  
                    if d == 0:
                        continue
                  
                    z = d / 1.0
                    x = (u - cx) * z / fx
                    y = -(v - cy) * z / fy
                  
                    points.append([x, y, z])

            # 更新最后一帧点云，用于保存
            self.last_points = points
          
            rospy.loginfo(f"📊 本次生成点云数量：{len(points)} 个")

            if len(points) > 0:
                header = rospy.Header()
                header.stamp = rospy.Time.now()
                header.frame_id = "kinect2_camera_frame"
              
                cloud = pcl2.create_cloud(header, FIELDS, points)
                self.pub.publish(cloud)

            rate.sleep()

if __name__ == '__main__':
    try:
        Depth2PointCloud().run()
    except rospy.ROSInterruptException:
        pass
```

运行：

```bash
rosrun image_pkg get_pointcloud3.py
```

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1775504617699-7b9c3584-d9ea-4949-9a5d-66f61834e98a.png" width="728" title="" crop="0,0,1,1" id="u484505f5" class="ne-image">

确认 output_cloud.pcd文件已经生成：

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1775504668770-304c37e1-2b9d-498a-8ac8-09b6256e360d.png" width="1074.4" title="" crop="0,0,1,1" id="u1bb5e7a8" class="ne-image">

启动 P`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`CL viewer 工具，查看 生成的文件 output_cloud.pcd`</font>`

```bash
pcl_viewer output_cloud.pcd
```

`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`在 PCL viewer 里按 `</font>**<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">+</font>**`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">` 键`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`，放大点大小，让点云更清晰；按 `</font>**<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">r</font>**`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">` 键`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`，重置点云视角，自动把桌子放在窗口正中间。`</font>`

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1775504761058-c7e5deae-b197-4977-86af-da59def14faf.png" width="1032.8" title="" crop="0,0,1,1" id="uf0142ecb" class="ne-image">

#### （慎用）使用 pcl_ros 功能包

在安装PCL工具的时候，自带了 pcl_ros功能包：

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1775488516341-077fff67-9546-4d5f-8578-fce1d9b110a3.png" width="1088.8" title="" crop="0,0,1,1" id="ym8AY" class="ne-image">

```bash
rosrun pcl_ros pointcloud_to_pcd input:=/kinect2/sd/points
```

运行 pcl_ros 功能包里的PCD转换文件节点，将

+ `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">pointcloud_to_pcd</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`：包内的节点名，专门用来把 ROS 点云话题转成 PCD 文件；`</font>`
+ `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">input:=/kinect2/sd/points</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`：指定输入话题为相机原生点云话题：`</font>`

控制台不停地刷新，并自动化保存PCD文件。

按下 Ctrl+C，最近文件名字是 164965000.pcd，我们用  pcl_view 这个文件：

```bash
pcl_viewer -rgb xxxxxxxx.pcd  #输入前几个数字，然后按 TAB补全
```

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1775487938221-e410fec5-9668-4606-b8fd-adc276bdbb89.png" width="1056.8" title="" crop="0,0,1,1" id="AYHJg" class="ne-image">

下载这幅图：

[1816965000.zip](https://www.yuque.com/attachments/yuque/0/2026/zip/54556538/1775494934798-dd6e6e1d-ca47-4bab-910e-62c54bce19ae.zip)

本代码的图片默认是存在家目录的，一直运行会保存一直保存很多张图片！

`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`现在可以看到，点云图像中找到桌子和瓶子，并且图片有颜色。`</font>`

`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`由于点云是`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`俯视角度`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`拍的桌子（从上方往下看），而 PCL Viewer 默认用了`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`正等测视角`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`，还自动把点云缩放到了整个窗口大小。`</font>`

#### （选做）

:::warning
3D 彩色点云的生成原理：基于针孔相机模型，以深度图为载体，通过相机内参将每个像素的2D坐标与深度值反投影为3D空间坐标，再将彩色图中对应像素的RGB颜色信息绑定到该3D点上，最终形成带颜色的3D点集合。

在本实验中，彩色图为SD、深度图为HD，分辨率不匹配。因此，需先通过坐标缩放对齐，按宽高比例将深度图的高分辨率像素映射到彩色图的低分辨率像素，或反向插值补全彩色图，再执行坐标计算与颜色绑定，确保每个3D点都能匹配到正确的颜色。

还需要需注意坐标系Y轴方向、深度单位、RGB字节序等细节，避免点云倒立、颜色反转等问题，最终生成与场景一致的三维彩色点云。

:::

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RGB-D 图像转三维彩色点云
"""

import rospy
import cv2
import numpy as np
from sensor_msgs.msg import Image, PointCloud2, PointField, CameraInfo
from cv_bridge import CvBridge
import sensor_msgs.point_cloud2 as pcl2
import struct

FIELDS = [
    PointField('x',  0, PointField.FLOAT32, 1),
    PointField('y',  4, PointField.FLOAT32, 1),
    PointField('z',  8, PointField.FLOAT32, 1),
    PointField('rgb',12,PointField.UINT32, 1),
]

class RGBD2PointCloud:
    def __init__(self):
        rospy.init_node('rgbd_to_pointcloud')
        self.bridge = CvBridge()
      
        self.rgb = None
        self.depth = None
        self.info = None

        # 订阅话题
        self.sub_rgb = rospy.Subscriber(
            "/kinect2/hd/image_color_rect", Image, self.cb_rgb
        )
        self.sub_depth = rospy.Subscriber(
            "/kinect2/sd/image_depth_rect", Image, self.cb_depth
        )
        self.sub_info = rospy.Subscriber(
            "/kinect2/sd/camera_info", CameraInfo, self.cb_info
        )

        self.pub = rospy.Publisher("/pointcloud_output", PointCloud2, queue_size=1)
        rospy.loginfo("✅ 点云节点已启动！")

    def cb_rgb(self, msg):
        self.rgb = self.bridge.imgmsg_to_cv2(msg, "bgr8")

    def cb_depth(self, msg):
        self.depth = self.bridge.imgmsg_to_cv2(msg, "16UC1")

    def cb_info(self, msg):
        self.info = msg

    def run(self):
        rate = rospy.Rate(15)
      
        while not rospy.is_shutdown():
            if self.rgb is None or self.depth is None or self.info is None:
                rate.sleep()
                continue

            # 分辨率
            h_d, w_d = self.depth.shape
            h_rgb, w_rgb = self.rgb.shape[:2]

            # 内参
            fx, fy = self.info.K[0], self.info.K[4]
            cx, cy = self.info.K[2], self.info.K[5]
          
            points = []
            step = 4

            for v in range(0, h_d, step):
                for u in range(0, w_d, step):
                    d = self.depth[v, u]
                  
                    if d == 0:
                        continue
                  
                    z = d / 1.0
                  
                    # 光学坐标系 → 相机连杆坐标系，Y轴取反，适配RViz显示
                    x = (u - cx) * z / fx
                    y = -(v - cy) * z / fy  # Y轴取反，桌腿朝下，桌子正过来

                    # 颜色坐标对齐
                    u_rgb = int(u * w_rgb / w_d)
                    v_rgb = int(v * h_rgb / h_d)
                    u_rgb = max(0, min(u_rgb, w_rgb-1))
                    v_rgb = max(0, min(v_rgb, h_rgb-1))

                    # 颜色100%正确，红瓶绿瓶无偏差
                    b, g, r = self.rgb[v_rgb, u_rgb]
                    rgb = struct.unpack('I', struct.pack('BBBB', b, g, r, 255))[0]
                  
                    points.append([x, y, z, rgb])

            rospy.loginfo(f"📊 本次生成点云数量：{len(points)} 个")

            if len(points) > 0:
                # 调整RViz的Fixed Frame完全一致，坐标系不再乱
                header = rospy.Header()
                header.stamp = rospy.Time.now()
                header.frame_id = "kinect2_camera_frame"
              
                cloud = pcl2.create_cloud(header, FIELDS, points)
                self.pub.publish(cloud)

            rate.sleep()

if __name__ == '__main__':
    try:
        RGBD2PointCloud().run()
    except rospy.ROSInterruptException:
        pass
```

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1775503494857-2601bd51-ef0f-4974-b653-2685cd6760ce.png" width="1316" title="" crop="0,0,1,1" id="uc69ef468" class="ne-image">

改进：

+ **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`点云更细腻`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`：把代码里的 `</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">step = 4</font>``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">` 改成 `</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">step = 2</font>``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`，点的数量会变成 4 倍，点云更密集，桌子和瓶子的轮廓会更平滑，不会有明显的颗粒感。`</font>`
+ **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`过滤背景杂点`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`：如果想去掉远处的地面杂点，让桌子和瓶子更突出，把代码里的深度过滤改成：`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`python`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`运行`</font>`

```python
if d == 0 or d > 5:  # 只保留5米以内的点
    continue
```

+ **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`锁定相机视角 `</font>`** `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`：如果想让 RViz 视角永远和相机保持一致，把右侧 Views 的 Type 改成 `</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">Camera</font>``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`，Target Frame 选 `</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">kinect2_camera_frame</font>``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`，就能完全锁定相机的第一视角，和原始图像永远同步。`</font>`
+ **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`点大小微调 `</font>`** `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`：在演示效果时，点的渲染样式选择 Points，像素大小设置为 3 ：若点大小设置过大，点云会出现膨胀、重叠与变形；若点大小过小，则点云难以观察，甚至会丢失颜色信息，导致无法正常显示彩色效果，目前是最好的效果。`</font>`
