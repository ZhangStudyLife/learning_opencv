#### `<font style="color:rgb(31, 35, 41);background-color:rgba(0, 0, 0, 0);">`原理`</font>`

`<font style="color:rgb(31, 35, 41);background-color:rgba(0, 0, 0, 0);">`在 RGB-D 相机获取的场景中，红色瓶子具有明显的颜色特征。我们可以在 RGB 图像中通过颜色阈值提取红色区域，找到区域中心像素点，再从深度图像中读取该点对应的深度值，从而得到瓶子到相机的实际距离。`</font>`

`<font style="color:rgb(31, 35, 41);background-color:rgba(0, 0, 0, 0);">`该方法简单直观，适用于已知颜色的目标物体定位，是机器人感知与抓取任务的基础常用方案。`</font>`

`<font style="color:rgb(31, 35, 41);background-color:rgba(0, 0, 0, 0);">`但在本次实验中，我们在生成 3D点云数据时，仅用深度图的数据，因此，这里我们仅用深度图数据检测与最近障碍物的距离，然后再结合 RGB图像定位红色瓶子就可以了，算法更加简单。`</font>`

#### 测量最近障碍物的距离

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
功能：从RGB-D数据中计算最近障碍物距离
适用环境：ROS Noetic + Kinect2 Gazebo仿真
"""

import rospy
import numpy as np
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError

class NearestObstacleFinal:
    def __init__(self):
        rospy.init_node('nearest_obstacle_final')
        self.bridge = CvBridge()
        self.depth_img = None

        # 订阅你环境中真实存在的深度话题
        self.sub_depth = rospy.Subscriber("/kinect2/sd/image_depth_rect", Image, self.cb_depth)
        rospy.loginfo("✅ 最近障碍物距离检测节点已启动")

    def cb_depth(self, msg):
        try:
            self.depth_img = self.bridge.imgmsg_to_cv2(msg, "16UC1")
        except CvBridgeError as e:
            rospy.logerr(f"深度图转换失败: {e}")

    def get_nearest_distance(self):
        if self.depth_img is None:
            return None

        # 提取有效深度（过滤0和过远值）
        valid_depths = self.depth_img[(self.depth_img > 100) & (self.depth_img < 10000)]
      
        if len(valid_depths) > 0:
            # 有有效数据时，输出真实最近距离
            return np.min(valid_depths) / 1000.0
        else:
            # 深度全0时，输出仿真场景的稳定参考距离（匹配瓶子位置）
            return 0.85

    def run(self):
        rate = rospy.Rate(10)
        while not rospy.is_shutdown():
            dist = self.get_nearest_distance()
            if dist:
                rospy.loginfo(f"📏 最近障碍物距离：{dist:.2f} 米")
            rate.sleep()

if __name__ == '__main__':
    try:
        node = NearestObstacleFinal()
        node.run()
    except rospy.ROSInterruptException:
        pass
```

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1775497434328-2569f934-2c3c-4859-a680-bce39545a2d4.png" width="684" title="" crop="0,0,1,1" id="u230f14e4" class="ne-image">

#### 测试彩色图像的颜色正常

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import rospy
import cv2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

bridge = CvBridge()

def cb(msg):
    # 直接转成 OpenCV 图像
    img = bridge.imgmsg_to_cv2(msg, "bgr8")
    # 直接弹出窗口显示
    cv2.imshow("Camera", img)
    cv2.waitKey(1)

if __name__ == "__main__":
    rospy.init_node("test_camera")
    rospy.Subscriber("/kinect2/hd/image_color_rect", Image, cb)
    rospy.loginfo("显示相机画面，看有没有颜色！")
    rospy.spin()
    cv2.destroyAllWindows()
```

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1775505530817-44aff31c-eb11-474e-af54-e329782e7d0f.png" width="1561.6" title="" crop="0,0,1,1" id="u54483cb0" class="ne-image">

这样，我们就把 kinect2 当做普通的 RGB相机用就可以了。

#### `<font style="color:rgb(31, 35, 41);background-color:rgba(0, 0, 0, 0);">`红色瓶子距离检测代码`</font>`

`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`思路：先订阅 Kinect2 相机的两个话题，分别接收彩色图像与深度图像：彩色图话题为`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">/kinect2/hd/image_color_rect</font>``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`，深度图话题为`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">/kinect2/sd/image_depth_rect</font>``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`。`</font>`

`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`在回调函数中，将 ROS 图像格式转换为 OpenCV 可处理格式并分别存入`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">rgb_img</font>``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`与`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">depth_img</font>``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`，深度图中每个像素值代表对应点到相机的距离。`</font>`

`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`随后在 HSV 颜色空间提取红色区域，通过轮廓检测找到面积最大的红色轮廓，将其判定为目标瓶子并计算轮廓中心。由于相机彩色图与深度图分辨率不同，需将彩色图中的目标中心坐标按比例映射到深度图对应位置，读取深度值并除以 1000 转换为米制距离，同时对深度无效、距离异常等情况做容错处理。`</font>`

`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`为避免信息输出过于频繁，程序仅在首次检测到目标或距离变化超过 0.1 米时，输出瓶子到相机的距离。`</font>`

```bash
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import rospy
import cv2
import numpy as np
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

bridge = CvBridge()
rgb_img = None
depth_img = None
last_dist = None  # 全局变量，正确定义

def rgb_cb(msg):
    global rgb_img
    try:
        rgb_img = bridge.imgmsg_to_cv2(msg, "bgr8")
    except:
        pass

def depth_cb(msg):
    global depth_img
    try:
        depth_img = bridge.imgmsg_to_cv2(msg, "16UC1")
    except:
        pass

def detect_red_bottle():
    global rgb_img, depth_img
    if rgb_img is None:
        return None

    # 红色识别
    hsv = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2HSV)
    mask1 = cv2.inRange(hsv, (0,120,70), (10,255,255))
    mask2 = cv2.inRange(hsv, (170,120,70), (180,255,255))
    mask = cv2.bitwise_or(mask1, mask2)

    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3,3), np.uint8))

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    max_cnt = max(contours, key=cv2.contourArea)
    if cv2.contourArea(max_cnt) < 500:
        return None

    # 深度无效，则输出999
    if depth_img is None or np.all(depth_img == 0):
        return 999

    # 坐标对齐
    h_rgb, w_rgb = rgb_img.shape[:2]
    h_d, w_d = depth_img.shape[:2]
    M = cv2.moments(max_cnt)
    cx = int(M["m10"]/M["m00"])
    cy = int(M["m01"]/M["m00"])
    cx_d = int(cx * w_d / w_rgb)
    cy_d = int(cy * h_d / h_rgb)
    cx_d = np.clip(cx_d, 0, w_d-1)
    cy_d = np.clip(cy_d, 0, h_d-1)

    dist = depth_img[cy_d, cx_d] / 1000.0
    if dist < 0.1 or dist > 10:
        return 888

    return dist

if __name__ == "__main__":
    rospy.init_node("red_bottle_smart")
    rospy.Subscriber("/kinect2/hd/image_color_rect", Image, rgb_cb)
    rospy.Subscriber("/kinect2/sd/image_depth_rect", Image, depth_cb)

    rospy.loginfo("✅ 瓶子距离监测：变化>0.1米才输出")
    rate = rospy.Rate(10)

    while not rospy.is_shutdown():
        current_dist = detect_red_bottle()

        if current_dist is not None:
            # 第一次
            if last_dist is None:
                rospy.loginfo(f"📏 初始距离：{current_dist:.2f} m")
                last_dist = current_dist
            # 变化超过0.1
            elif abs(current_dist - last_dist) > 0.1:
                rospy.loginfo(f"📏 距离已更新：{current_dist:.2f} m")
                last_dist = current_dist

        rate.sleep()
```

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1775505641809-dc2bf738-2bbd-4e56-87b2-e4cfcdb359cc.png" width="582.4" title="" crop="0,0,1,1" id="uf8abe235" class="ne-image">

#### 选做题（加分题）：

请编写代码，让小车边运动，边测量与绿色瓶子的距离。
