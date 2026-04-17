### GMapping算法的功能

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1776109399145-2588725c-ba09-4de1-ba35-e4752aa24b10.png" width="469.60003662109375" title="" crop="0,0,1,1" id="ub218e1d7" class="ne-image">

参考资料：[https://wiki.ros.org/gmapping](https://wiki.ros.org/gmapping)

+ **数据订阅**：订阅机器人关节变换话题 `/tf`和激光雷达扫描数据话题 `/scan`、里程计话题题 `/odom`等
+ **地图发布**：发布栅格地图话题 `/map_gmapping`

<img src="https://cdn.nlark.com/yuque/0/2025/png/54556538/1744096407620-2637deea-9b67-4944-af27-e8f59e343d7a.png?x-oss-process=image%2Fformat%2Cwebp" width="679.4000244140625" title="" crop="0,0,1,1" id="IDsOc" class="ne-image">

演示视频：

[此处为语雀卡片，点击链接查看](https://www.yuque.com/shellcore/zkttvr/wqlyt0ql5odp93kd#rzths)

### GMapping算法的基本流程

1. **环境扫描**：机器人通过激光雷达不断地扫描周围环境，获取当前位置的测量数据。
2. **运动估算**：将当前位置的测量数据提供给里程计，根据机器人的运动数据，估算机器人的实际运动轨迹。
3. **位置纠正**：将当前位置的测量数据和估算的实际运动轨迹提供给SLAM算法，通过Scan-Matching等方法，对机器人在局部地图中的位置进行估算和纠正。
4. **地图更新**：在对机器人的局部位置进行修正后，将当前位置和局部地图更新到全局地图中。
5. **循环执行**：重复执行上述步骤，不断更新机器人在全局地图中的位置和环境地图。
6. **区域扩展**：当机器人探测到新的未知区域时，扩大局部地图的大小，不断探测这个区域，并且将探测到的数据和估算的位置信息增量地添加到全局地图中。
7. **自主定位与探索**：最终，通过不断地扫描和更新地图，机器人就可以实现自主定位和探索未知区域的功能。

#### 关键点总结

+ **数据依赖**：依赖激光雷达数据和里程计数据。
+ **核心方法**：利用Scan-Matching等方法进行位置纠正。
+ **地图更新机制**：通过增量更新实现地图的动态构建。
+ **适用场景**：适合室内等小场景的实时地图构建和自主定位。

### 实验

##### 安装GMapping、navigation、map-server

本项目已安装，请忽略。

```basic
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install ros-noetic-gmapping
sudo apt-get install ros-noetic-navigation
sudo apt-get install ros-noetic-map-server
sudo apt-get install ros-noetic-joint-state-publisher
sudo apt-get install ros-noetic-tf2-geometry-msgs
sudo apt-get install ros-noetic-tf2-sensor-msgs
sudo apt-get install ros-noetic-move-base-msgs
```

##### 启动场景

```bash
roslaunch wpr_simulation wpb_stage_robocup.launch
```

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1776109200366-40e08003-12f0-4bd0-847b-de4a619672bc.png" width="1584" title="" crop="0,0,1,1" id="uf1ff2173" class="ne-image">

##### 启动gmapping功能包中的slam_gmapping 节点

先安装 tf2 工具，查看 tf树是否正确配置：

```bash
# 安装 tf2_tools（若未安装）
sudo apt install ros-noetic-tf2-tools

# 执行新版 view_frames，生成 frames.pdf
rosrun tf2_tools view_frames.py
```

+ 坐标树文件 frames.pdf 默认保存在家目录下；

```bash
rosrun gmapping slam_gmapping
```

<img src="https://cdn.nlark.com/yuque/0/2026/jpeg/54556538/1776110345286-1385ae17-336c-4030-b26b-9e484522adad.jpeg" width="666" title="" crop="0,0,1,1" id="VGqG3" class="ne-image">

+ slam_gmapping 节点已运行。

##### 在rviz中观察

```bash
rosrun rviz rviz
```

添加 机器人模型、激光雷达数据显示：

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1776110691628-b7ccb69a-fd1c-4aa6-8912-6cb3c8f28b3a.png" width="961.6" title="" crop="0,0,1,1" id="u9c96e753" class="ne-image">

添加地图和话题/map，并调整与gazebo一致的视角：

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1776110799857-24cc6130-f67c-457a-9379-b846a3f3611c.png" width="963.2" title="" crop="0,0,1,1" id="uf607ac59" class="ne-image">

##### 启动键盘控制节点，开车跑图

```bash
rosrun wpr_simulation keyboard_vel_ctrl 
```

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1776110993629-6c3f24b2-e5e8-4f1b-8481-c3ebaeab8486.png" width="472" title="" crop="0,0,1,1" id="ucc8c322f" class="ne-image">

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1776111490230-8a834053-ae1d-4c4e-8644-09c719c5fc75.png" width="1647.2" title="" crop="0,0,1,1" id="ud009be05" class="ne-image">

##### 保存地图

```bash
rosrun map_server map_saver -f eg1_map
```

[https://wiki.ros.org/map_server](https://wiki.ros.org/map_server)

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1776112943067-0b2a3564-c071-486f-aa79-23c8c0b98231.png" width="652.4000244140625" title="" crop="0,0,1,1" id="uad6d4285" class="ne-image">

默认保存在家目录下。

### 看看地图

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1776113332044-760db3b0-00da-4c20-80b1-78863d187f02.png" width="1147.2" title="eg1_map.yaml                                        eg1_map.pgm" crop="0,0,1,1" id="PQTud" class="ne-image">

其中.yam是配置信息，.pgm 保存着由图像文件还原实际地图数据：

| 字段                | 取值                                     | 含义                                   | 说明                                                                                                   |
| ------------------- | ---------------------------------------- | -------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| `image`           | `eg1_map.pgm`                          | 栅格地图图像文件                       | 与 `.yaml` 同目录下的 PGM 格式地图图像，存储了每个栅格的占用状态                                     |
| `resolution`      | `0.050000`                             | 地图分辨率（米 / 像素）                | 每个像素代表实际物理尺寸 0.05m（5cm），是 GMapping 启动参数 `delta: 0.05` 的直接对应                 |
| `origin`          | `[-100.000000, -100.000000, 0.000000]` | 地图原点（左下角）在世界坐标系下的位姿 | 格式为 `[x, y, θ]`，单位：米、弧度。当前表示地图左下角像素对应世界坐标 `(-100, -100)`，航向角 0° |
| `negate`          | `0`                                    | 颜色反转开关                           | `0`：白色 = 自由区域，黑色 = 占用区域（ROS 标准）；`1`：反转颜色含义                               |
| `occupied_thresh` | `0.65`                                 | 占用阈值                               | 栅格概率值 > 0.65 时，判定为**占用**（障碍物）                                                   |
| `free_thresh`     | `0.196`                                | 自由阈值                               | 栅格概率值 < 0.196 时，判定为**自由**（可通行区域）                                              |

### 作业：

请大家在下节课前，跑出完美的地图：

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1776114223794-4be7e44d-a8e4-40c0-b1d6-6c1464724b53.png" width="439.4000244140625" title="" crop="0,0,1,1" id="u02b1cc85" class="ne-image">
