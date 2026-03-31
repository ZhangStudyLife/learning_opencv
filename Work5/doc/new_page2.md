
:::danger
**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`思路`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`：`</font>`

1. `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`算出小球和画面中心的`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`水平偏差`</font>`**
2. `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`用`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`比例控制`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`：偏差越大，转向越快`</font>`
3. `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`检测到小球 → 前进 + 转向；没检测到 → 停止`</font>`

:::

#### `<font style="color:rgb(38, 38, 38);">`创建脚本文件 follow_node.py`</font>`

```python
roscd image_pkg
cd scripts
touch follow_node.py
chmod +x follow_node.py 
```

#### 参考代码：

```python
#! /usr/bin/env python3
#coding=utf-8
import rospy
import cv2
import numpy as np
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
from geometry_msgs.msg import Twist

# ===================== 全局参数定义 =====================
# HSV阈值参数
hue_min = 20
hue_max = 80
saturation_min = 100
saturation_max = 255
value_min = 80
value_max = 255

# 速度控制与图像转换
vel_cmd = Twist()
vel_pub = None
bridge = CvBridge()

# ===================== 图像回调与目标跟随函数 =====================
def Cam_RGB_Callback(msg):
    global vel_cmd, vel_pub
    global hue_min, hue_max, saturation_min, saturation_max, value_min, value_max

    # 1. ROS图像转换为OpenCV格式
    try:
        cv_image = bridge.imgmsg_to_cv2(msg, "bgr8")
    except CvBridgeError as e:
        rospy.logerr(f"图像转换失败: {e}")
        return
  
    # 2. 转换为HSV颜色空间
    hsv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
  
    # 3. HSV阈值分割，生成二值蒙版
    th_image = cv2.inRange(hsv_image, (hue_min, saturation_min, value_min), (hue_max, saturation_max, value_max))
  
    # 4. 形态学操作，去除噪点
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    th_image = cv2.morphologyEx(th_image, cv2.MORPH_OPEN, kernel)
    th_image = cv2.morphologyEx(th_image, cv2.MORPH_CLOSE, kernel)  
  
    # 5. 图像矩计算目标中心
    M = cv2.moments(th_image)
    pix_count = int(M["m00"])
    img_h, img_w = cv_image.shape[:2]  # 获取图像宽高
    center_x = img_w // 2  # 图像水平中心点

    if pix_count > 50:
        # 计算目标中心坐标
        cx = int(M["m10"] / pix_count)
        cy = int(M["m01"] / pix_count)
        rospy.loginfo(f"目标中心：({cx}, {cy}) | 像素数：{pix_count}")
      
        # 绘制目标十字标记
        cv2.drawMarker(cv_image, (cx, cy), (0, 255, 0), cv2.MARKER_CROSS, 15, 2)
     
        # 6. 核心：根据目标位置实现机器人跟随
        error = cx - center_x  # 水平偏差
        vel_cmd.linear.x = 0.2    # 前进速度（固定值，可调节）
        vel_cmd.angular.z = -error * 0.002  # 转向速度（比例控制）
      
    else:
        rospy.loginfo("未检测到目标，机器人停止")
        vel_cmd.linear.x = 0
        vel_cmd.angular.z = 0
  
    # 7. 发布速度指令
    vel_pub.publish(vel_cmd)
    rospy.loginfo(f"线速度={vel_cmd.linear.x:.2f}, 角速度={vel_cmd.angular.z:.2f}")

    # 8. 显示图像窗口
    cv2.imshow("RGB Camera", cv_image)
    cv2.imshow("Mask Result", th_image)
    cv2.waitKey(1)  

# ===================== 主函数 =====================  
if __name__ == '__main__':
    # 初始化ROS节点（修复拼写错误）
    rospy.init_node('color_follow_node', anonymous=True)
    rospy.loginfo("颜色追踪跟随节点已启动")
  
    # 订阅Kinect2图像话题
    rgb_sub = rospy.Subscriber('/kinect2/qhd/image_color_rect', Image, Cam_RGB_Callback, queue_size=1)
    # 发布机器人速度指令
    vel_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
  
    # 创建HSV参数调节滑块
    cv2.namedWindow("HSV Threshold")
    cv2.createTrackbar("Hue Min", "HSV Threshold", hue_min, 179, lambda x: None)
    cv2.createTrackbar("Hue Max", "HSV Threshold", hue_max, 179, lambda x: None)
    cv2.createTrackbar("S Min", "HSV Threshold", saturation_min, 255, lambda x: None)
    cv2.createTrackbar("S Max", "HSV Threshold", saturation_max, 255, lambda x: None)
    cv2.createTrackbar("V Min", "HSV Threshold", value_min, 255, lambda x: None)  
    cv2.createTrackbar("V Max", "HSV Threshold", value_max, 255, lambda x: None)
  
    # 主循环，实时更新滑块参数
    rate = rospy.Rate(30)
    while not rospy.is_shutdown():
        hue_min = cv2.getTrackbarPos("Hue Min", "HSV Threshold")
        hue_max = cv2.getTrackbarPos("Hue Max", "HSV Threshold")
        saturation_min = cv2.getTrackbarPos("S Min", "HSV Threshold")
        saturation_max = cv2.getTrackbarPos("S Max", "HSV Threshold")
        value_min = cv2.getTrackbarPos("V Min", "HSV Threshold")
        value_max = cv2.getTrackbarPos("V Max", "HSV Threshold")
      
        rate.sleep()
  
    # 关闭窗口
    cv2.destroyAllWindows()
```

#### 运行

[此处为语雀卡片，点击链接查看](https://www.yuque.com/shellcore/zkttvr/fpgm9ckfg5qfwmxa#TaMzt)

#### 验收：测试：

启动终端，让小车能够跟随指定小球移动。

#### 加分项：人脸识别

在终端中，运行仿真环境：

```python
roslaunch wpr_simulation wpb_single_face.launch 
```

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1774890938236-54791cee-df9b-40a9-b1bd-edf1c6f286f1.png" width="1128" title="" crop="0,0,1,1" id="uadea9e8c" class="ne-image">

    请编写代码，控制小车移动，识别出帅哥的脸部，并为他拍几张写真吧~
