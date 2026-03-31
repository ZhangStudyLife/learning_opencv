在机器人足球场仿真场景中，一台搭载 Kinect2 深度相机的移动机器人需要实现对场景内彩色小球的自主识别、定位与追踪运动。请参考课件内容，完成工作空间搭建、仿真环境部署、节点编程、话题通信、视觉图像处理与运动控制等流程，最终实现机器人可以自主运动、指定颜色小球也可以自主运动的功能。

二、实验环境与工具* wpr_simulation 机器人仿真功能包

* Kinect2 相机驱动
* 三、任务要求

任务 1：ROS 工作空间与仿真环境搭建1. 创建 catkin 工作空间，完成编译与环境变量配置。

1. 下载 `wpr_simulation`、`wpb_home`、`waterplus_map_tools` 源码包。
2. 执行依赖安装脚本，完成环境配置。
3. 编译工作空间，解决编译错误。

任务 2：启动足球场仿真场景1. 启动带 Kinect2 相机与彩色小球的 Gazebo 仿真场景。

1. 使用 `rostopic list` 查看所有话题，记录 Kinect2 图像话题与小球速度话题。
2. 使用 `rqt_graph` 查看节点与话题关系，写出核心节点（gazebo、kinect2）的功能。

任务 3：小球自动运动控制1. 编写 / 使用 `move_ball_random.py` 节点，实现小球随机运动功能。

1. 能够分别控制 red_ball、green_ball、blue_ball、orange_ball 运动。
2. 理解小球速度话题格式（`Twist` 消息）。

任务 4：Kinect2 相机图像获取1. 订阅 Kinect2 标清彩色图像话题：`/kinect2/sd/image_color_rect`。

1. 使用 `image_view` 查看实时相机画面。
