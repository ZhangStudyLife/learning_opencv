ROS 标准图像消息 sensor_msgs/Image的数据结构

1先看一个例子
（来源：[https://www.yuque.com/shellcore/hob75t/cinq06mo0l2z1yni](https://www.yuque.com/shellcore/hob75t/cinq06mo0l2z1yni) ）
在gazebo物理环境中，控制小车运动，观察小车摄像头采集到的视频信息。

<video preload="metadata" playsinline="" poster="https://img.alicdn.com/imgextra/i1/6000000002122/O1CN01dVSu981RXvUiPbijX_!!6000000002122-0-tbvideo.jpg"></video>

![play](https://gw.alipayobjects.com/zos/bmw-prod/b805f4eb-90d6-4436-83c9-db779654f71a.svg)

**0:00**/**1:42**

倍速

![volumeUp](https://gw.alipayobjects.com/zos/bmw-prod/550c35db-8b72-44f1-84ff-098d1c8ca62c.svg)

![fullscreen](https://gw.alipayobjects.com/zos/bmw-prod/a687e835-ae61-4f61-92da-cc7d09273133.svg)

![fullscreen](https://gw.alipayobjects.com/zos/bmw-prod/a7574efd-0464-4f4b-8584-2a88eed310fb.svg)

1.1在gazebo中启动带相机的mbot机器人
在mbot_gazebo的功能包中，有带相机 camera、深度相机 kinect、激光雷达 laser 三种机器人

VIEWMBOT_GAZEBO_PLAYGROUND.LAUNCH

VIEWMBOTWITHLASERGAZEBOLAUNCH

VIEW_MBOTGAZEBO_EMPTYWORDLAUNCH

VIEWMBOTGAZEBO_ROOM.AUNCH

MBOTGAZEBO

AUNCH

![image.png](https://cdn.nlark.com/yuque/0/2025/png/54556538/1742882105402-0c037722-c237-401d-834e-b0043d46ba08.png)

1

**roslaunch** **mbot_gazebo** **view_mbot_with_camera_gazebo**.**launch**

LO卡乡N值EA行

大中口小

ERICALCOORDINATE

YIEWWINDOWHELR

INSERTLAYERS

PROPERTY

IS_STATIC

PMROBOT

JERSEY_BARRIER

![image.png](https://cdn.nlark.com/yuque/0/2025/png/54556538/1742745679181-6b0ced26-2e94-4a61-9430-d671d12145a8.png)

切换视角，能够看到相机camera
![image.png](https://cdn.nlark.com/yuque/0/2025/png/54556538/1742745762234-7f3b5d60-eec4-4d57-bafc-2fdf80291748.png)

1.2在第2个终端中开启键盘控制

![image.png]()

仔细阅读键盘控制指令，让小车运动起来，或者：
![image.png]()

手工向小车发布 /cmd_vel 控制指令：
![image.png]()

1.3 在第3个终端中打开 rqt_image_view工具
![image.png]()

订阅话题 /camera/image_raw：![image.png]()

演示视频：

<video preload="metadata" playsinline="" poster="https://img.alicdn.com/imgextra/i3/6000000005894/O1CN01Vkw5aK1tPVSHNq98l_!!6000000005894-0-tbvideo.jpg"></video>

![play](https://gw.alipayobjects.com/zos/bmw-prod/b805f4eb-90d6-4436-83c9-db779654f71a.svg)

**0:00**/**0:19**

倍速

![volumeUp](https://gw.alipayobjects.com/zos/bmw-prod/550c35db-8b72-44f1-84ff-098d1c8ca62c.svg)

![fullscreen](https://gw.alipayobjects.com/zos/bmw-prod/a687e835-ae61-4f61-92da-cc7d09273133.svg)

![fullscreen](https://gw.alipayobjects.com/zos/bmw-prod/a7574efd-0464-4f4b-8584-2a88eed310fb.svg)

2使用真实摄像头
如果是 WSL2 用户，虽然无法使用真实的摄像头，但可以使用 roslaunch 观摩功能包 usb_cam
![image.png]()

然后进入文件夹 launch：
![image.png]()

用 vim 工具查看 usb_cam-test 文件：
![b78c33913f41621ff66f346b1cc2c42e.png]()

如果你使用的是双系统或虚拟机，摄像头可以正常使用，可以运行：

2.1 启动 usb_cam 功能包

2.2图像数据
相机采集的图像数据，通过 /usb_cam/image_raw 话题进行传输，消息载体为 sensor_msgs/Image）
![17612aba61e6b325b69a41ff94fb7eb5.png]()

2.3 查看当前系统中可用的话题
执行命令 rostopic list：
![image.png]()

2.4同样，打开 rqt_image_view工具
订阅 2.3 话题，看到图片信息：
![image.png]()

2.5执行命令 rostopic info [话题名称]
![image.png]()

3ROS标准图像消息sensor_msgs/Image
在上面的例子中，我们可以看到相机采集的图像数据，是通过 /camera/image_raw（仿真） 或 /usb_cam/image_raw（真实相机）的话题进行传输，消息载体都是 sensor_msgs/Image
查看消息的完整数据结构，可以执行命令 rosmsg show [消息类型名称]，通过控制台查看，运行：

![image.png]()

说明：
●Header：消息头，包含消息序号，时间戳和绑定坐标系；
●height：图像的纵向分辨率；
●width：图像的横向分辨率；
●encoding：图像的编码格式，包含 RGB、YUV 等常用格式，不涉及图像压缩编码；
●is_bigendian：图像数据的大小端存储模式；
●step：一行图像数据的字节数量，作为数据的步长参数；
●data：存储图像数据的数组，大小为step*height个字节。

那么，1280*720 分辨率的摄像头产生一帧图像的数据大小是： 3*1280* 720=2764800字节，即 2.7648MB，数据量是相当客观了。
所以，除了 /camera/image_raw（仿真） 或 /usb_cam/image_raw（真实相机）这种原始图像，视觉传感器还提供了压缩过、便于传输的消息：
●/camera/image_raw/compressed：JPEG/PNG 压缩版图像，用于降低网络带宽占用
●/camera/image_raw/theora：Theora 编码的视频流，适合实时视频传输
●带/compressedDepth的话题：若为 RGB-D 相机，则是深度图的压缩版本
稍后，我们来学习深度相机的图像数据格式。

最后，还有一个概念希望大家了解：大小端存储模式
假设一个数值 = 0x1234（2 个字节）
●高字节：0x12
●低字节：0x34
大端存储（先存高字节），内存顺序：1234
小端存储（先存低字节），内存顺序：3412

参考资料：
RGB相机在ROS中的数据接口
 ① 启动 usb_cam 功能包
② 相机采集的图像数据，通过 /usb_cam/image_raw 话题进行传输，消息载体为 sensor_msgs/Image）
③ 查看当前系统中可用的话题：执行命令 rostopic list
④ 查看指定话题的消息类型：执行命令 rostopic info [话题名称]
⑤ 查看消息的完整数据结构：执行命令 rosmsg show [消息类型名称]

[https://www.yuque.com/shellcore/hob75t/cinq06mo0l2z1yni](https://www.yuque.com/shellcore/hob75t/cinq06mo0l2z1yni)
[https://www.yuque.com/shellcore/hob75t/tohh3extnaz2gzzq](https://www.yuque.com/shellcore/hob75t/tohh3extnaz2gzzq)
