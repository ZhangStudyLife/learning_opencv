接下来两周，我们将在 ROS 平台中，让 wpr机器人通过 Kinect2 深度相机获取场景图像数据，并结合之前学习的 OpenCV 图像处理技术与 Haar 特征分类器，实现人脸等目标的检测，最终让机器人完成目标识别与自动追踪。

1比较

| 特性``     | 普通 RGB 相机 (Camera)``   | RGB-D 深度相机 (Kinect)``                            |
| ----------------- | --------------------------------- | ----------------------------------------------------------- |
| 核心能力`` | 二维彩色成像``             | 二维彩色成像 + 三维深度测量``                        |
| 深度信息`` | ❌无``                     | ✅有``                                               |
| 数据输出`` | sensor_msgs/Image``        | sensor_msgs/Image``+sensor_msgs/PointCloud2`` |
| 典型原理`` | 针孔成像``                 | 结构光 / ToF / 双目视觉``                            |
| 核心优势`` | 成本低、色彩好、分辨率高`` | 三维空间感知能力``                                   |
| 主要局限`` | 无法测距``                 | 易受环境光干扰、成本较高``                           |
| 典型应用`` | 人脸识别、颜色追踪``       | 避障、导航、三维建模、物体抓取``                     |

2第二代深度相机 Kinect2
Kinect 2（Kinect for Windows v2 / Kinect for Xbox One）是微软推出的多模态 ToF 深度相机/体感传感器，集成多组件的感知单元：
1基本配置：采用间接 ToF 技术，红外发射器投射调制红外光，红外相机检测反射光相位差计算深度。
2获取图像：不仅能获取和普通相机一样的彩色图像，还有深度图、红外图模式：
a彩色图（RGB） 1080p@30fps RGB 彩色相机；
b深度图（Depth）512×424@30fps 深度，每个像素带距离信息，可以用来做 3D 感知、避障、人体识别；
c红外图（IR）黑夜也能看清，不受光照影响。
这款相机自 2014 年推出，最初是 Xbox One 体感外设，常用于体感交互、3D 点云采集、人体骨架追踪，在机器人视觉、VR/AR、动作捕捉等领域应用广泛。
如果你有 kinect2 实物可以通过：
●驱动包：libfreenect2 + ROS 封装（如 iai_kinect2/freenect2_camera）
●启动命令：roslaunch freenect2 freenect2.launch

3ROS摄像头去和数据接口

3.1kinect2 功能包中的话题和服务

| 分类``       | 名称``                                      | 类型``                            | 描述``                                          |
| ------------------- | -------------------------------------------------- | ---------------------------------------- | ------------------------------------------------------ |
| Topic 发布`` | /kinect2/sd/camera_info``                   | sensor_msgs/CameraInfo``          | 标清（SD）相机校准信息（内参、畸变系数）``      |
|                     | /kinect2/sd/image_color_rect``              | sensor_msgs/Image``               | 校正后的标清彩色图像数据（BGR8 格式）``         |
|                     | /kinect2/sd/image_depth_rect``              | sensor_msgs/Image``               | 校正后的标清深度图像数据（16UC1，单位：毫米）`` |
|                     | /kinect2/sd/image_ir_rect``                 | sensor_msgs/Image``               | 校正后的标清红外图像数据``                      |
|                     | /kinect2/sd/points``                        | sensor_msgs/PointCloud2``         | 彩色 + 深度融合的 3D 点云数据``                 |
|                     | /kinect2/qhd/camera_info``                  | sensor_msgs/CameraInfo``          | 四分之一高清（QHD）相机校准信息``               |
|                     | /kinect2/qhd/image_color_rect``             | sensor_msgs/Image``               | 校正后的 QHD 彩色图像数据``                     |
|                     | /kinect2/hd/camera_info``                   | sensor_msgs/CameraInfo``          | 高清（HD）相机校准信息``                        |
|                     | /kinect2/hd/image_color_rect``              | sensor_msgs/Image``               | 校正后的 HD 彩色图像数据``                      |
|                     | /kinect2/sd/image_color_rect/compressed``   | sensor_msgs/CompressedImage``     | 标清彩色图像的压缩版（降低带宽）``              |
|                     | /kinect2/sd/image_color_rect/theora``       | theora_image_transport/Packet``   | 标清彩色图像的 Theora 编码视频流``              |
|                     | /kinect2/sd/image_ir_rect/compressedDepth`` | sensor_msgs/CompressedImage``     | 标清红外 / 深度图像的压缩版``                   |
|                     | /diagnostics``                              | diagnostic_msgs/DiagnosticArray`` | Kinect v2 传感器运行状态诊断信息``              |
| Services``   | /kinect2/sd/set_camera_info``               | sensor_msgs/SetCameraInfo``       | 设置标清相机的校准信息``                        |
|                     | /kinect2/qhd/set_camera_info``              | sensor_msgs/SetCameraInfo``       | 设置 QHD 相机的校准信息``                       |
|                     | /kinect2/hd/set_camera_info``               | sensor_msgs/SetCameraInfo``       | 设置 HD 相机的校准信息``                        |

3.2ROS标准图像消息sensor_msgs/Image
可以通过控制台查看，运行：

KERR2004@KERR-B1DG10:~$RO

STDMSGS/HEADERHEADER

WSENSORMSGS/IMAGE

UIINT8ISBIGENDIAN

STRINGFRAIEID

UINT8LDATA

UINT32WIDTH

UINT32HEIGHT

STRINGENCODING

UINT32STEP

UINT32SEG

TIMESTAMP

ROSMSG

SHOW

![image.png](https://cdn.nlark.com/yuque/0/2026/png/54556538/1774275870749-306598b2-2021-4fbe-96ee-f0ab72a3c67e.png)

说明：
●Header：消息头，包含消息序号，时间戳和绑定坐标系；
●height：图像的纵向分辨率；
●width：图像的横向分辨率；
●encoding：图像的编码格式，包含 RGB、YUV 等常用格式，不涉及图像压缩编码；
●is_bigendian：图像数据的大小端存储模式；
●step：一行图像数据的字节数量，作为数据的步长参数；
●data：存储图像数据的数组，大小为step*height个字节。

3.3ROS 三维点云数据的标sensor_msgs/PointCloud2
sensor_msgs/PointCloud2 是 ROS 中用于表示三维点云数据的标准消息类型，包含了大量三维坐标点的数据包，每个点都带有位置信息（x,y,z），有时还带有颜色（rgb）或其他属性。

| 字段``         | 含义``                                                                                                     |
| --------------------- | ----------------------------------------------------------------------------------------------------------------- |
| header``       | 消息头，包含时间戳（stamp）和坐标系（frame_id），用于同步和定位``                                          |
| height``       | 点云的高度（行数）。若为无序点云，通常为 1``                                                               |
| width``        | 点云的宽度（列数）。总点数 =height * width``                                                               |
| fields``       | 点云中点的数据类型定义数组，描述每个点包含哪些维度的数据（如 x, y, z, rgb）``                              |
| is_bigendian`` | 数据存储的字节顺序（大端 / 小端），通常为False``（小端）``                                          |
| point_step``   | 单个点占用的字节数，即从一个点的起始位置到下一个点的起始位置的字节步长``                                   |
| row_step``     | 一行点云数据占用的总字节数，即width * point_step``                                                         |
| data``         | 存储所有点云数据的字节数组，总大小为row_step * height``                                                    |
| is_dense``     | 点云是否为 “稠密” 的。True``表示所有点都是有效的；False``表示可能存在无效点（如 NaN 值）`` |

4课程示范：
我们在课程中使用的 wpr 机器人的头部就安装了一台 Kinect 2 相机，在之前的实验中，我们已经能够通过 cv_bridge 进行数据转换，那么，请接受挑战吧：)
PENCV的数据格式

ROS的数据格式

SENSORMSGS:IMAGE

机器人头部相机

CV_BRIDGE

CV::IMSHOW

CV::MAT

![9b29750bda3bf94b717a82518f02d230.png](https://cdn.nlark.com/yuque/0/2026/png/54556538/1774275491162-557f12b7-4603-4d8d-a670-4c52a4020241.png)

参考资料：
[https://www.yuque.com/shellcore/hob75t/cinq06mo0l2z1yni](https://www.yuque.com/shellcore/hob75t/cinq06mo0l2z1yni)
[https://www.yuque.com/shellcore/hob75t/tohh3extnaz2gzzq](https://www.yuque.com/shellcore/hob75t/tohh3extnaz2gzzq)
