 本示例的思路是**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`利用二值蒙版（Mask）从图像中将颜色一致的目标小球提取出来`</font>`**。程序先将图像从 RGB 颜色空间转换到 HSV 颜色空间，再通过设定合适的色相、饱和度与明度阈值范围，生成一幅黑白二值掩膜：满足目标颜色条件的区域被标记为白色，背景及其他无关区域则被标记为黑色，从而实现目标区域与背景的分离。

在图像处理与机器视觉任务中，将图像由 RGB 颜色空间转换为 HSV 颜色空间，是因为于 RGB 空间中**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`颜色信息与亮度信息相互耦合`</font>`**，易受光照强度变化干扰，难以通过固定阈值实现稳定的颜色分割与目标识别；而 HSV 空间将颜色分解为**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`色相（H）、饱和度（S）、明度（V）三个独立分量，实现了颜色特征与亮度信息的有效分离`</font>`**，光实现了颜色特征与亮度信息的有效解耦。光照变化主要影响明度通道，对色相通道的影响很小，因此可以显著提升颜色识别的鲁棒性，简化阈值选取过程，且更符合人眼对色彩的感知规律，在目标检测、颜色分割、视觉跟踪等视觉任务中得到了广泛应用。

** HSV **颜色空间中，**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`色相 H`</font>`**决定颜色的种类，对应红、黄、绿、蓝等基本色彩，取值范围为 0～179；**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`饱和度 S`</font>`**表示颜色的鲜艳与纯净程度，数值越高色彩越浓郁，越低则越接近灰色，范围为 0～255；**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`明度 V`</font>`**反映图像的明暗程度，数值越高图像越亮，越低则越暗。

<img src="https://cdn.nlark.com/yuque/0/2026/jpeg/54556538/1774880739831-afc3429e-f429-4623-96e3-af34ca3f3ac9.jpeg" width="1236.8" title="" crop="0,0,1,1" id="u4aa32372" class="ne-image">

在视觉图像处理中，通过颜色阈值生成的二值掩膜（Mask），其工作原理与 Photoshop 中的图层蒙版高度相似。二者均以黑白灰度信息为控制依据，实现对图像内容的选择性保留与剔除：在 Photoshop 蒙版中，白色区域表示内容可见，黑色区域表示内容被隐藏，灰色区域可实现半透明过渡；而在基于 HSV 的阈值分割流程中，白色像素代表需要识别与追踪的目标区域，黑色像素代表需要忽略的背景区域。二者的核心逻辑完全一致，都是通过一张辅助的黑白图像控制 “哪些区域保留、哪些区域舍弃”。二者的主要区别在于，Photoshop 蒙版多用于图像编辑，支持灰度渐变以实现柔和过渡；而机器视觉中的掩膜多为严格的黑白二值图像，目标与背景分界清晰，主要服务于目标提取、轮廓检测、位置定位等自动化分析任务。

#### 创建功能包 image_pkg和脚本文件夹scripts

```bash
cd ~/catkin_ws/src
catkin_create_pkg image_pkg rospy roscpp std_msgs image_transport cv_bridge
cd image_pkg
mkdir -p scripts && cd scripts
```

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1774879718751-059a85ff-18da-4664-af50-cfbe8ae4e9ca.png" width="1047.2" title="" crop="0,0,1,1" id="ud9e715a4" class="ne-image">

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1774879861753-f39fe4d4-68c1-43e8-959a-aa90b13834ac.png" width="612.8" title="" crop="0,0,1,1" id="u6e203d89" class="ne-image">

#### 在颜色空间转换RGB->HSV

在脚本文件夹中新建脚本 hsv_node.py:

```c
cd catkin_ws/src/image_pkg/scripts/
touch hsv_node.py
chmod +x hsv_node.py 
```

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1774881128415-58437992-6e53-4026-ab11-de4b23e64cf4.png" width="615.2" title="" crop="0,0,1,1" id="ubacc5196" class="ne-image">

参考代码:

```python
#!/usr/bin/env python3
#coding=utf-8
import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import cv2
import numpy as np

# HSV阈值
hue_min = 20
hue_max = 60
saturation_min = 50
saturation_max = 255
value_min = 50
value_max = 255

# 全局转换器
bridge = CvBridge()

# 图像回调函数
def Cam_RGB_Callback(msg):
    global hue_min, hue_max, saturation_min, saturation_max, value_min, value_max

    # 转换ROS图像为OpenCV格式
    try:
        cv_image = bridge.imgmsg_to_cv2(msg, "bgr8")
    except CvBridgeError as e:
        rospy.logerr(f"转换失败: {e}")
        return
   
    # HSV颜色空间转换
    hsv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
  
    """
    # 亮度均衡化
    h, s, v = cv2.split(hsv_image)
    v = cv2.equalizeHist(v)
    hsv_eq = cv2.merge((h, s, v))  
    # 用均衡化后的图像做二值化，虚拟环境中不均衡化反而更好
    # 实测均衡化后目标反而更难检测到，可能是因为环境光线较为稳定，均衡化反而引入了噪声
    """
  
    th_image = cv2.inRange(hsv_image, (hue_min, saturation_min, value_min), (hue_max, saturation_max, value_max))
  
    # 形态学去噪
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    th_image = cv2.morphologyEx(th_image, cv2.MORPH_OPEN, kernel)
    th_image = cv2.morphologyEx(th_image, cv2.MORPH_CLOSE, kernel)

    # ✅ 图像矩计算中心
    M = cv2.moments(th_image)
    pix_count = int(M["m00"])

    if pix_count > 50:
        # 计算目标中心
        cx = int(M["m10"] / pix_count)
        cy = int(M["m01"] / pix_count)
        rospy.loginfo(f"目标中心：({cx}, {cy}) | 像素数：{pix_count}")
        # 绘制十字
        cv2.drawMarker(cv_image, (cx, cy), (0,255,0), cv2.MARKER_CROSS, 15, 2)
    else:
        rospy.loginfo("未检测到目标")

    # 显示结果，调试用
    cv2.imshow("RGB Camera", cv_image)
    cv2.imshow("HSV Image", hsv_eq)
    cv2.imshow("Mask Result", th_image)
    cv2.waitKey(1) 

# 主函数
if __name__ == '__main__':
    rospy.init_node("hsv_color_detector")
    rospy.loginfo("✅ 节点启动成功，等待图像数据...")

    # 订阅Kinect图像话题
    rospy.Subscriber("/kinect2/qhd/image_color_rect", Image, Cam_RGB_Callback, queue_size=1)

    # HSV滑块调节窗口
    cv2.namedWindow("HSV Adjust", cv2.WINDOW_AUTOSIZE)
    cv2.createTrackbar("H Min", "HSV Adjust", hue_min, 179, lambda x: None)
    cv2.createTrackbar("H Max", "HSV Adjust", hue_max, 179, lambda x: None)
    cv2.createTrackbar("S Min", "HSV Adjust", saturation_min, 255, lambda x: None)
    cv2.createTrackbar("S Max", "HSV Adjust", saturation_max, 255, lambda x: None)
    cv2.createTrackbar("V Min", "HSV Adjust", value_min, 255, lambda x: None)
    cv2.createTrackbar("V Max", "HSV Adjust", value_max, 255, lambda x: None)

    # 主循环
    rate = rospy.Rate(30)
    while not rospy.is_shutdown():
        # 实时读取滑块值
        hue_min = cv2.getTrackbarPos("H Min", "HSV Adjust")
        hue_max = cv2.getTrackbarPos("H Max", "HSV Adjust")
        saturation_min = cv2.getTrackbarPos("S Min", "HSV Adjust")
        saturation_max = cv2.getTrackbarPos("S Max", "HSV Adjust")
        value_min = cv2.getTrackbarPos("V Min", "HSV Adjust")
        value_max = cv2.getTrackbarPos("V Max", "HSV Adjust")
        rate.sleep()

    cv2.destroyAllWindows()
```

#### 二值化，分割提取目标物

#### 计算目标物的质心坐标

#### 静态场景测试

##### `<font style="color:rgb(38, 38, 38);">`运行看带有小球的场景`</font>`

`<font style="color:rgb(38, 38, 38);">`开启第 1 个终端，运行：`</font>`

```c
roslaunchwpr_simulationwpb_balls.launch
```

##### 运行功能包 image_pkg 中的节点 hsv_node.py

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1774886652075-e68ae6c5-98bb-4d3c-8227-d0079a3ed1d9.png" width="625.6" title="" crop="0,0,1,1" id="u1b46d485" class="ne-image">

##### 运行结果：

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1774886768508-78613036-936f-43aa-b925-ef273daf94a8.png" width="1817.6" title="" crop="0,0,1,1" id="u33af00f0" class="ne-image">

 在当前 HSV 阈值区间内，程序将绿色小球识别为追踪目标；通过滑动条调整阈值范围，可自定义需要追踪的小球颜色。

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1774888230497-3e29a579-a18f-4985-8d3f-8bf0e5b7c26c.png" width="519.3999938964844" title="" crop="0,0,1,1" id="u27b19c9e" class="ne-image"> <img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1774888255925-a3e493fc-5a46-4c86-8cf8-1261ee464c81.png" width="215.60000610351562" title="" crop="0,0,1,1" id="ue5c893ac" class="ne-image">

---

#### 结果分析

##### 如何确定 HSV 阈值区间？

    -**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`先固定 `</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`饱和度`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`S ≥ 100（`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`越低越灰色`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`），`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`明度`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`V ≥ 100`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`过滤掉灰色、阴影（越低越黑）`</font>`
    - **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`只调 H`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`找到你要的颜色区间，参考值：`</font>`
        * `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`0 ~ 10 → 红`</font>`
        * `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`10 ~ 40 → 黄`</font>`
        * `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`40 ~ 80 → 绿`</font>`
        * `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`90 ~ 130 → 蓝`</font>`
    - **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`再微调 S、V`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`让目标更干净`</font>`

##### `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`方法 1：手动滑块调参法`</font>`

**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`粗调 H 范围`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`：拖动`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">H Min</font>``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`/`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">H Max</font>``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`，实时观察`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">Mask Result</font>``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`窗口，直到目标颜色完整显示为白色、背景尽量为黑色。比如找绿色：先把 H 拉到`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">20-60</font>``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`，蓝色：先把 H 拉到`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">90-120</font>``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`，看对应颜色的球是否完整。在`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`细调 S/V`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`：如果目标颜色还有缺失，就降低`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">S Min</font>``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`/`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">V Min</font>``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`（比如从 100 降到 50）；如果背景出现杂色，就提高`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">S Min</font>``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`/`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">V Min</font>``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`。`</font>`

##### `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`方法 2：颜色拾取 + 直方图法（更精准）`</font>`

`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`用鼠标拾取目标色值：在代码中添加鼠标回调，点击目标球后打印该点的`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">H/S/V</font>``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`，比如 python 运行：`</font>`

```python
def mouse_click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        h, s, v = hsv_image[y, x]
        print(f"当前点 H:{h}, S:{s}, V:{v}")
cv2.setMouseCallback("RGB Camera", mouse_click)
```

**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`看直方图分布`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`：用`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">cv2.calcHist</font>``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`计算 H/V 通道直方图，看目标颜色的像素集中在哪个区间，以此确定阈值范围。`</font>`

**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`留余量`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`：比如拾取到多个点的 H 在`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">90-110</font>``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`、S 在`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">120-200</font>``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`、V 在`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">150-230</font>``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`，就把阈值设为`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">H:85-115</font>``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`、`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">S:110-210</font>``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`、`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">V:140-240</font>``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`，避免光照微小波动导致目标丢失。`</font>`

`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);"></font>`

`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`💡`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">` `</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`阈值没有 “绝对标准答案”，`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`以「目标完整显示、背景尽量干净」为最终标准`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`：`</font>`

+ `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`✅`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">` 目标在 Mask 里是完整的白色区域`</font>`
+ `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`❌`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">` 背景尽量为黑色，无明显杂色`</font>`
+ `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`模拟环境下，参考值 + 微调就能满足需求；真实环境下需要更宽的阈值或光照补偿。`</font>`

`<font style="color:rgb(108, 108, 108);background-color:rgb(250, 250, 250);">`1 `</font>`
