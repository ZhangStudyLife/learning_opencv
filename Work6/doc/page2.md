    通过 RViz 可视化，我们来验证 RGB-D 相机能够输出 RGB 图像、深度图像，以及 3D点云图像。

在 ROS 中，RGB-D相机先将采集到的原始 RGB 图像、深度图像封装为标准的图像消息发布，之前的课程我们讲解过，Kinect2相机输出的数据有 `sensor_msgs/PointCloud2`消息格式进行传输，这一格式正是连接 ROS 生态与三维点云处理库（PCL）的核心桥梁。

| **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`特性`</font>`**     | **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`普通 RGB 相机 (Camera)`</font>`**                                                     | **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`RGB-D 深度相机 (Kinect)`</font>`**                                                                                                                                                                         |
| ----------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`核心能力`</font>`** | `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`二维彩色成像`</font>`                                                                         | `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`二维彩色成像 + 三维深度测量`</font>`                                                                                                                                                                               |
| **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`深度信息`</font>`** | `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`❌`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">` 无`</font>` | `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`✅`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">` 有`</font>`                                                                                                                      |
| **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`数据输出`</font>`** | `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">sensor_msgs/Image</font>`                                                                        | `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">sensor_msgs/Image</font>``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">` + `</font>**<font style="color:#DF2A3F;background-color:rgba(0, 0, 0, 0);">sensor_msgs/PointCloud2</font>**` |

#### 场景设计

首先，我们先来设计一个场景：

    - 打开 Gazebo 仿真环境；
    - 加载桌子、红瓶子、绿瓶子；
    - 生成带机械臂的机器人 wpb_home_mani；
    - 启动控制器、抓取服务等。

如图所示：

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1775479873196-d3b13664-8414-4c86-92ab-8c095ffc93a4.png?x-oss-process=image%2Fformat%2Cwebp" width="1465" title="" crop="0,0,1,1" id="k2HzJ" class="ne-image">

编写wpb_bottles.lauch 脚本：

```bash
roscd wpr_simulation
cd launch
touch wpr_bottles.launch
```

参考脚本：

```python
<launch>
  <!-- 启动 Gazebo -->
  <include file="$(find gazebo_ros)/launch/empty_world.launch">
    <arg name="world_name" value="$(find wpr_simulation)/worlds/simple.world"/>
    <arg name="paused" value="false"/>
    <arg name="use_sim_time" value="true"/>
    <arg name="gui" value="true"/>
    <arg name="recording" value="false"/>
    <arg name="debug" value="false"/>
  </include>

  <!-- 生成桌子 -->
  <node name="table" pkg="gazebo_ros" type="spawn_model" args="-file $(find wpr_simulation)/models/table.model -x 1.2 -y 0.0 -z 0 -Y 0 -urdf -model table" />

  <!-- 生成瓶子（修正高度，红瓶/绿瓶均稳定在桌面） -->
  <node name="red_bottle" pkg="gazebo_ros" type="spawn_model" args="-file $(find wpr_simulation)/models/bottles/red_bottle.model -x 1.15 -y 0.3 -z 0.75 -Y 0 -urdf -model red_bottle" />
  <node name="green_bottle" pkg="gazebo_ros" type="spawn_model" args="-file $(find wpr_simulation)/models/bottles/green_bottle.model -x 1.15 -y -0.2 -z 0.75 -Y 0 -urdf -model green_bottle" />

  <!-- 生成机器人 -->
  <node name="spawn_urdf" pkg="gazebo_ros" type="spawn_model" args="-file $(find wpr_simulation)/models/wpb_home_mani.model -urdf -model wpb_home_mani" />

  <!-- 加载控制器 -->
  <include file="$(find wpr_simulation)/launch/wpb_home_controllers.launch"/>

</launch>
```

#### 启动 wpr_bottles.launch 场景

```bash
roslaunch wpr_simulation wpr_bottles.launch
```

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1775479873196-d3b13664-8414-4c86-92ab-8c095ffc93a4.png" width="1172" title="" crop="0,0,1,1" id="u1318c13d" class="ne-image">

#### `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`启动 RViz 显示深度相机彩色图与深度图`</font>`

**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`RViz（ROS Visualization）`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">` 是 ROS 系统中官方提供的`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`三维可视化工具`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`，用于实时显示机器人传感器数据、坐标变换、地图、点云、模型等信息。它可以直观呈现机器人所处环境与自身状态，是调试机器人感知、定位、导航等功能必不可少的工具。`</font>`

`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`在本实验中，RViz 主要用于：`</font>`

+ `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`显示 RGB-D 相机生成的`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`三维彩色点云`</font>`**
+ `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`验证点云坐标、形状、颜色是否正确`</font>`
+ `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`通过交互式视角观察三维场景结构`</font>`

:::danger
请注意：`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`RViz 可视化配置（关键设置）`</font>`

+ **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`设置坐标系`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`将 RViz 左上角 `</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`Fixed Frame`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">` 设置为 `</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">kinect2_camera_frame</font>``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`，保证点云与相机坐标系正确对齐。`</font>`
+ **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`添加点云显示插件`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`点击左下角 `</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`Add`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`，选择 `</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`PointCloud2`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">` 插件并确认。`</font>`
+ **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`选择点云话题`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`在新建的 PointCloud2 插件中，将 `</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`Topic`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">` 设置为 `</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">/pointcloud_output</font>``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`。`</font>`
+ **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`设置显示样式`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`将 `</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`Style`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">` 设置为 `</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">Points</font>``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`，避免使用 `</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">Flat Squares</font>``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">` 以获得更清晰的点效果。`</font>`
+ **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`调整点大小`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`将 `</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`Size (Pixels)`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">` 设置为 `</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`5～8`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`，适当放大点云，提升显示清晰度。`</font>`
+ **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`开启彩色显示`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`将 `</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`Color Transformer`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">` 设置为 `</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">RGB8</font>``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`，启用点云彩色渲染模式。`</font>`
+ **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`视角操作`</font>`**
  - `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`鼠标左键拖动：旋转视角`</font>`
  - `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`鼠标滚轮：缩放视图`</font>`
  - `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`鼠标中键拖动：平移视图通过以上操作可从多角度观察三维点云结构。`</font>`

:::

##### `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`启动 RViz`</font>`

`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`首先，启动 RViz 工具，`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`在终端中输入以下命令，启动 RViz 可视化工具：`</font>`

```bash
rviz 
```

`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`在 RViz 中，`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`Fixed Frame（固定坐标系）`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">` 是所有可视化数据的参考基准。本实验基于机器人与相机仿真，`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`未构建地图`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`，因此不存在 `</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">map</font>``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">` 坐标系。将 Fixed Frame 修改为`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`相机或机器人本体坐标系`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`，才能正常显示传感器数据。`</font>`

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1775475113224-6a9d5550-5167-4fdd-bda6-15734d2ad6fa.png?x-oss-process=image%2Fcrop%2Cx_62%2Cy_48%2Cw_1215%2Ch_895" width="973" title="" crop="0.0241,0.0333,0.4989,0.6546" id="sTlgx" class="ne-image">

##### `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`修改 Fixed Frame`</font>`

`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`由于本实验使用深度相机采集数据，将 Fixed Frame 修改为相机自身坐标系 `</font>**<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">kinect2_camera_frame</font>**``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`。这时，RViz 的三维视图将`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`切换到 Kinect2 相机的第一人称视角`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`，所有图像、点云等传感器数据都会以相机为中心进行渲染，与相机拍摄视角保持一致，便于直观观察场景内容与传感器输出效果。`</font>`

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1775474511312-888f43c6-362d-4314-8f40-834f0ef90a63.png?x-oss-process=image%2Fcrop%2Cx_0%2Cy_0%2Cw_371%2Ch_255" width="297" title="" crop="0,0,1,0.8226" id="ufbd2c480" class="ne-image">

##### 点 “Add”添加话题，这里有两种方法，在 By display type 中选择“Image”：

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1775475290116-b77f1d61-4c97-4986-a571-9fca1259033e.png" width="748.8" title="" crop="0,0,1,1" id="u45a876aa" class="ne-image">

+ 点“Image Topic”选择话题，这里有4个话题：

`<font style="background-color:#CEF5F7;">`/kinect2/hd/image_color_rect: HD 分辨率下`</font>`**`<font style="background-color:#CEF5F7;">`校正后彩色图像`</font>`**`<font style="background-color:#CEF5F7;">`的话题`</font>`

`<font style="background-color:#CEF5F7;">`/kinect2/qhd/image_color_rect: QHD 分辨率下`</font>`**`<font style="background-color:#CEF5F7;">`校正后彩色图像`</font>`**`<font style="background-color:#CEF5F7;">`的话题`</font>`

`<font style="background-color:#FBDE28;">`/kinect2/sd/image_depth_rect: HD 分辨率下`</font>`**`<font style="background-color:#FBDE28;">`深度图`</font>`**`<font style="background-color:#FBDE28;">`的话题`</font>`

/kinect2/sd/image_irr_rect ：SD 分辨率下**校正后红外图像**的话题

:::danger
**注意这里有个坑：**

+ `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`深度图是 SD的，分辨率是：512×424`</font>`
+ `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`彩色图是 HD的，分辨率是：1920×1080`</font>`

:::

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1775475462851-07a4be9e-6bf6-49e8-88fd-bcecfedcd94b.png?x-oss-process=image%2Fcrop%2Cx_1221%2Cy_281%2Cw_1215%2Ch_902" width="972" title="" crop="0.477,0.1953,0.9518,0.8214" id="ufff104e8" class="ne-image">

##### 分别观察：

    **RGB 图像 **是包含红、绿、蓝三个颜色通道的普通彩色图像，能够呈现场景的色彩、纹理与外观信息；

**深度图像 **则是一种记录场景中各点到相机距离的**灰度图像**，像素值代表实际空间距离，可提供场景的三维结构信息。

在 RGB-D 视觉处理中，通常将两者结合，利用深度信息恢复三维坐标，利用 RGB 信息赋予点云颜色，从而实现三维彩色点云的构建，如图3.5节所示。

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1775475891258-e4cc4c35-3a0e-4693-b780-895f45b5d3c1.png" width="284.8" title="RGB图像" crop="0,0,1,1" id="u59af8d26" class="ne-image"> <img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1775475869404-a643b613-2995-4ab4-ba37-68af5259679a.png" width="291.2" title="深度图像" crop="0,0,1,1" id="u9af7dd9d" class="ne-image">

##### `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`添加 3D点云图像`</font>`

`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`类似地，我们可通过 RViz 实现深度相机三维点云数据的可视化：点击左下角 `</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`Add`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">` 按钮，在弹出的插件列表中选择 `</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`PointCloud2`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">` 并确认添加；展开左侧新增的 `</font>**<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">PointCloud2</font>**``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">` 插件，在 `</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`Topic`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">` 下拉菜单中选择深度相机的点云话题 `</font>**<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">/kinect2/sd/points</font>**``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`。`</font>`

`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`配置完成后，RViz 主界面将以 `</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">kinect2_camera_frame</font>``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">` 为基准，渲染出相机采集的三维点云数据，呈现出场景中桌子、物体等目标的三维空间结构，直观展示深度相机对场景可见表面的采样结果。`</font>`

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1775476247663-771e2999-a931-49f4-97e3-504a4209b240.png" width="748" title="" crop="0,0,1,1" id="u2673c668" class="ne-image">

##### 观察

`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`可以通过 `</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`鼠标滚轮 `</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`向前滚放大，向后滚缩小；`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`按住鼠标右键拖动`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`，旋转视角，绕着点云看；`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`按住鼠标中键拖动`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">` 平移视角，把点云移到屏幕中间。`</font>`

**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`右侧 Views 面板的： `</font>`****`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`Orbit 视角 `</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`是 RViz 的`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`自由轨道视角`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`，你可以按住鼠标左键 360° 旋转，从任意角度观察点云的立体结构，能清晰看到桌子的侧面、深度，适合检查点云的 3D 形状是否正确、有没有变形。`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`XYOrbit`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`等不同视角，你可以尝试着切换观察角度，把点云摆正——和左下角原始图像的相机第一视角一致：桌腿朝下、桌面朝上，红瓶在左、绿瓶在右。`</font>`

`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`点击 `</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`Zero`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">` 按钮，可以重置视角。`</font>`

`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`请多多尝试！`</font>`

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1775476666541-19714c2c-9f11-45b5-aa0c-c5ba877bbd0c.png" width="967.2" title="" crop="0,0,1,1" id="u0b28692f" class="ne-image">

:::danger
当放大时，可以看到，桌子腿是不完整，这是为什么呢？

`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`点云显示的“桌子腿”是通过`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`深度相机在当前视角下对可见表面的采样结果`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`。深度相机只能捕获它视野范围内、未被遮挡的区域，`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`视野外或被自身结构遮挡的区域`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`。你可以控制小车前后左右移动，随着视角缩小或重新对焦，这种不完整感会改善。在实际应用中，点云的显示精度与视野范围完全由相机成像与视角变换决定。`</font>`

:::

```bash
rosrun wpr_simulation keyboard_vel_ctrl
```

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1775477247523-64f368b7-208d-4237-a0ca-77e71eb227a0.png" width="595.2" title="" crop="0,0,1,1" id="u928e0fcb" class="ne-image">

移动观察，桌腿是否完整了呢？

[此处为语雀卡片，点击链接查看](https://www.yuque.com/shellcore/zkttvr/zc2guof2dnc5vtg0#cD8Rj)

`<font style="background-color:#FBE4E7;">` 通过 RViz 可视化，我们验证了 RGB-D 相机能够输出 RGB 图像、深度图像，并可将其转换为三维点云、重建三维场景。接下来我们将通过编程实现`</font>`**`<font style="color:rgb(0, 0, 0);background-color:#FBE4E7;">`RGB 图像与深度图像到三维点云的转换`</font>`**`<font style="background-color:#FBE4E7;">`，掌握像素坐标到空间坐标的映射逻辑。  `</font>`

#### 获取相机内参

重新开一个终端，输入：

```bash
 rostopic echo /kinect2/sd/camera_info
```

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1775499844082-8a886410-6f60-4190-a859-989bcacde3d1.png" width="754.4" title="" crop="0,0,1,1" id="u72453fdb" class="ne-image">

**相机内参矩阵 K **

$ K=
\begin{bmatrix}
f_x & 0 & c_x \\
0 & f_y & c_y \\
0 & 0 & 1
\end{bmatrix} $

**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`从中可以就看出：`</font>`**

**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`焦距 (focal length)`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`：`</font>`

+ `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`f`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`x`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`=`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`365.606`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`（x 方向像素焦距）`</font>`
+ `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`f`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`y`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`=`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`365.606`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`（y 方向像素焦距，和 fx 相等，说明是正方形像素）`</font>`

**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`主点 (principal point / 光心)`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`：`</font>`

+ `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`c`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`x`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`=`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`256.5`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`（图像 x 方向中心，对应图像宽度 512 的中点：512/2=256）`</font>`
+ `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`cy=212.5（图像 y 方向中心，对应图像高度 424 的中点：424/2=212）`</font>`

**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`图像尺寸`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`：`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">height: 424</font>``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`，`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">width: 512</font>``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`，对应 Kinect 2 红外相机的原生分辨率  `</font>`

**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`坐标系：kinect2_ir_optical_frame`</font>`**

`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);"></font>`
