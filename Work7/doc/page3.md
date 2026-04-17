#### 激光雷达传感器的数学模型

激光雷达是自动驾驶中的重要传感器，它提供高精度的距离测量信息，但价格十分昂贵。常用的激光雷达分为**机械旋转格激光雷达**、**固态激光雷达**，以及混合固态。

机械式激光雷达：可以看成一列以固定频率旋转的激光探头，每个探头能够快速探测外部物体离自身的距离。这些探头没旋转一圈，就可以完成一次对周围场景的扫描。常见的线数包括单线、4线、8线……128线。线数越高，每次扫描得到的点数越多，信息越丰富。然而，即使经过多次降价，32线的高线数机械旋转式激光雷达热仍然是十分昂贵的传感器，其价格甚至是某些车辆的好几倍。

固态激光雷达：并不进行360°扫描，只能探测约60~120°视野范围内的 3D信息。它们与RGBD相机十分类似，而且可以实现图像式扫描。以等效的线数来看，固态激光雷达甚至可以实现200线以上的效果。但固态激光雷达并不一定是以水平的扫描线进行扫描，而是有自己独特的扫描图案。

混合固态激光雷达：这种激光雷达的收发装置保持不动，通过光学扫描结构实现机械旋转。相比机械式激光雷达，混合固态激光雷达的结构更加紧凑，更易于量产，成本也相对较低。

固态激光雷达和机械旋转激光雷达都是激光雷达技术的应用，它们有着各自的优点和缺点。比如固态激光雷达没有运动部件，性能稳定，但是射程和视野范围相对较小；机械旋转激光雷达具有较远的射程和广阔的视野范围，但是需要运动部件，工作时存在旋转带来的误差。根据实际需求选择适合的激光雷达技术是非常重要的。在智能驾驶的实际体验中，算法和软件的重要性不言而喻。尽管各种激光雷达技术在不断进步，但最终的用户体验还是取决于算法的优化程度。

#### 单点测量的 RAE 模型

激光雷达 (Lidar) 的测量模型为距离-方位角-俯仰角模型 (Range-Azimuth-Elevation, RAE) 。其中P是激光雷达 (Lidar) 的观测点，$ r $是P点距离激光雷达(Lidar)传感器的距离，它通过激光脉冲传播的时间乘以光速除以2获得；$ \alpha $ 是方位角(Azimuth)，  $ \epsilon $是俯仰角(Elevation)，$ \alpha $和$ \epsilon $是激光束的发射角度。

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1776101889794-efafe886-552a-4887-9943-2758b6d6c69d.png" width="528.4000244140625" title="单点测量的 RAE 模型" crop="0,0,1,1" id="u47fef2c8" class="ne-image">

激光雷达每旋转一周，会向周围发射数百至数千束激光脉冲，每一束激光脉冲经环境物体反射后，会被雷达接收端捕获，进而计算出激光发射点与反射点之间的距离、方位角等信息，这些离散的、携带空间坐标信息的反射点集合，被称为点云（Point Cloud），而获取完整一圈点云的过程，即为一次扫描（Scan）。

一次扫描所生成的点云，不仅包含了环境中物体的轮廓信息，还能通过激光反射强度的差异，区分不同材质的物体（如金属、塑料、植被等）——反射强度越高，通常对应物体表面越光滑、反射率越高。此外，不同型号的激光雷达，一次扫描的点云数量（即点云密度）存在差异，点云密度越高，对环境细节的还原度就越高，能识别的最小物体尺寸也越小，比如工业级激光雷达的单圈点云数量可达到数千个，而消费级激光雷达则可能在数百个左右。

在ROS（机器人操作系统）等常用开发环境中，激光雷达的一次扫描数据会以特定的消息类型（如**`<font style="color:#DF2A3F;">`sensor_msgs/LaserScan`</font>`**）发布，消息中包含扫描的角度范围（通常为0°~360°，部分激光雷达支持自定义角度范围）、角度分辨率（相邻两个激光点之间的角度差，角度分辨率越小，点云越密集）、每一个激光点的距离数据及反射强度数据等关键信息，这些数据是后续SLAM地图构建、障碍物检测、路径规划等算法的输入。

2D激光雷达的一次扫描仅能获取同一水平面上的环境信息，生成2D点云，而3D激光雷达（如多线激光雷达）则可通过多个激光发射单元的配合，在探头旋转时实现不同高度层面的扫描，一次扫描即可生成包含三维坐标（x、y、z）的3D点云，能更全面地还原三维环境立体结构，适用于更复杂的机器人感知场景。

#### 来自激光雷达的扫描数据 `<font style="color:#DF2A3F;background-color:rgb(243, 245, 250);">sensor_msgs/LaserScan</font>`

`<font style="color:rgb(6, 6, 7);">`ROS 中`</font><font style="color:#DF2A3F;background-color:rgb(243, 245, 250);">sensor_msgs/LaserScan</font>``<font style="color:rgb(6, 6, 7);">`消息类型的结构：`</font>`

```python
kerr2004@Kerr-Bldg10:~/newbot_ws$ rosmsg show sensor_msgs/LaserScan
```

<img src="https://cdn.nlark.com/yuque/0/2025/png/54556538/1743923193156-cf3b6fee-4fc5-452e-9753-a84eb712baa8.png" width="512" title="" crop="0,0,1,1" id="YU9jw" class="ne-image">

`<font style="color:rgb(6, 6, 7);">`该消息类型的详细字段解释，参考网址：`</font>`[https://github.com/ros2/common_interfaces/blob/humble/sensor_msgs/msg/LaserScan.msg](https://github.com/ros2/common_interfaces/blob/humble/sensor_msgs/msg/LaserScan.msg)

##### `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`消息头 `</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">std_msgs/Header header</font>`

`<font style="color:rgb(0, 0, 0);background-color:#FBF5CB;">`这是 ROS 传感器消息的通用头部，用于`</font>`**`<font style="color:rgb(0, 0, 0);background-color:#FBF5CB;">`时间戳`</font>`**`<font style="color:rgb(0, 0, 0);background-color:#FBF5CB;">`和`</font>`**`<font style="color:rgb(0, 0, 0);background-color:#FBF5CB;">`坐标系`</font>`**`<font style="color:rgb(0, 0, 0);background-color:#FBF5CB;">`的绑定`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`：`</font>`

+ `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">uint32 seq</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`：消息序列号，用于追踪数据顺序，排查丢包`</font>`
+ `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">time stamp</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`：数据采集的时间戳，用于多传感器时间同步`</font>`
+ `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">string frame_id</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`：坐标系的名称，用于指定激光扫描数据的参考坐标系，比如`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">laser_link</font>`

##### `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`角度相关参数`</font>`

`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`定义激光雷达的扫描角度范围与步长：`</font>`

+ `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">float32 angle_min</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`：扫描的起始角度（单位：rad，通常对应正左方）`</font>`
+ `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">float32 angle_max</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`：扫描的结束角度（单位：rad，通常对应正右方）`</font>`
+ `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">float32 angle_increment</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`：相邻两个激光束的`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`角度增量`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`（单位：rad），决定扫描分辨率例：360° 雷达若有 1080 个点，则 `</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">angle_increment = 2π / 1080 ≈ 0.0058rad</font>`
+ `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">float32 time_increment</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`：相邻两个激光测量的`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`时间间隔`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`（单位：s），用于运动畸变校正`</font>`
+ `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">float32 scan_time</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`：扫描周期（单位：s），对应雷达的扫描频率（如 10Hz 雷达则为 0.1s）`</font>`

##### `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`距离相关参数`</font>`

`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`定义激光雷达的测距范围与数据：`</font>`

+ `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">float32 range_min</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`：雷达的最小有效测距（单位：m），小于该值的点视为无效`</font>`
+ `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">float32 range_max</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`：雷达的最大有效测距（单位：m），大于该值的点视为无效`</font>`
+ `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">float32[] ranges</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`：核心数据，存储每个角度对应的距离测量值（单位：m），数组长度 = `</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">(angle_max - angle_min) / angle_increment</font>`
+ `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">float32[] intensities</font><font style="color:rgb(6, 6, 7);">`：强度数组，表示每个测量点的反射强度值。`</font>`

`<font style="color:rgb(6, 6, 7);">`这些字段共同描述了激光扫描数据的结构，包括扫描的参数、时间和测量结果。这些信息对于机器人导航和环境感知非常重要。`</font>`

#### 使用 RViz观测激光雷达获取的数据

##### 启动脚本

```bash
 roslaunch wpr_simulation wpb_simple.launch 
```

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1776103375732-c6fc9773-3423-418a-b47c-8a4c2983014e.png" width="743.2" title="" crop="0,0,1,1" id="u1f91af21" class="ne-image">

场景：

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1776104661180-86ed49eb-532a-4dd8-bd78-0cf672bd5967.png" width="1571.2" title="" crop="0,0,1,1" id="u04432a62" class="ne-image">

##### 在 RViz中观察

修改参考系“Fixed Frame”- >“base_footprint”

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1776104599545-00236ef3-3230-411c-a2b0-dee4c98afd9b.png" width="673.4000244140625" title="" crop="0,0,1,1" id="u350f14d8" class="ne-image">

修改激光雷达的可视化效果：Size(m)从0.01调整到合适大小：

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1776104765803-66d580b7-dc15-42d4-9f47-129cfb7c1926.png" width="674.4" title="" crop="0,0,1,1" id="u08c9b9c8" class="ne-image">

在gazebo中放置几个物理模型，对应的可以观察到激光雷达扫出了新增加物体的轮廓：

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1776105156897-efced153-4913-4bde-80ff-b206d6959c69.png" width="1588.8" title="" crop="0,0,1,1" id="u8b0fb0bd" class="ne-image">

##### 在控制台查看数据

重新开启一个控制台：

```bash
# 包含 ranges 数据
rostopic echo /scan 

# 加上参数 --noarr，避免 ranges 数据刷屏
 rostopic echo /scan --noarr
```

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1776105650052-583e4ea1-6677-4f5d-ab81-173b6bf924c7.png" width="524" title="" crop="0,0,1,1" id="u10d515f4" class="ne-image">

| 参数                      | 数值             | 含义                                                                        |
| ------------------------- | ---------------- | --------------------------------------------------------------------------- |
| `frame_id: "laser"`     | `laser`        | 激光雷达的坐标系名称，与 URDF 中配置一致                                    |
| `angle_min / angle_max` | `-π ~ π`     | 扫描角度范围：**360° 全向扫描**（-180° ~ +180°）                   |
| `angle_increment`       | `≈0.0175 rad` | 角度分辨率：≈**1°**（`π/180 ≈ 0.01745`），共 360 个数据点       |
| `range_min / range_max` | `0.24m ~ 6.0m` | 测距范围：最小测距约 0.24m，最大测距 6.0m，只有在这个数值范围内的距离才有效 |
| `ranges` 数组长度       | `360`          | 每帧扫描 360 个距离数据点，与角度分辨率匹配                                 |
| `intensities` 数组长度  | `360`          | 每帧 360 个反射强度数据，支持 SLAM / 避障算法                               |

<img src="https://cdn.nlark.com/yuque/0/2026/jpeg/54556538/1776106648495-8c5f699b-19f1-4adc-830b-b3d98c0b6b7b.jpeg" width="368.3999938964844" title="测量的角度范围" crop="0,0,1,1" id="u49b49962" class="ne-image">    <img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1776106739400-28d00788-5306-41df-8d58-a16f63b51508.png" width="304.3999938964844" title="测量的距离范围" crop="0,0,1,1" id="u0e60ba74" class="ne-image">

下面是 ROS 激光雷达 `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">/scan</font>` 话题的**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`测距数据数组，`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`1帧有360个距离数据点`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`：`</font>`**

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1776106309116-1928dcc9-c9ec-4e9f-8c5d-5d00ace97608.png" width="810.4" title="" crop="0,0,1,1" id="NHx89" class="ne-image">

`**<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">inf</font>**`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">` 含义`</font>`**：表示该角度无有效测距（超出最大量程 `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">6.0m</font>` 或无障碍物）

##### 例：激光雷达测距

<img src="https://cdn.nlark.com/yuque/0/2026/jpeg/54556538/1776107342648-bc133bfd-3bd6-42d5-8048-b7368fd1fc3b.jpeg" width="609.4000244140625" title="" crop="0,0,1,1" id="u5b504d75" class="ne-image">

:::info
**思路：**

    - 在软件包中新建一个节点文件，命名为 lidarceju_node.py；
    - 在主函数中订阅话题/scan，并设置回调函数LidarCallback( )；
    - 构建回调函数LidarCallback( )，用来接收和处理雷达数据；
    - 调用loginfo()显示雷达检测到的前方障碍物距离。

:::

运行例程 功能包中的wpr_simulation 的节点 demo_lidar_data.py

```bash
rosrun wpr_simulation demo_lidar_data.py
```

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1776106980609-2bca221b-80bf-42f3-a01c-9e702c786c1a.png" width="572.8" title="" crop="0,0,1,1" id="ue9a6ab0d" class="ne-image">

正前方距离在 2.58~2.62 米 区间内微小波动，这属于激光雷达正常噪声，无跳变、无异常值；

数据发布频率稳定，时间戳连续递增，说明 ROS 话题订阅正常，无丢包、无延迟

#### 作业：

 请参考当前仿真场景，编写 ROS 控制脚本，使机器人能够通过激光雷达获取环境信息，实现自动避障功能。

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1776107899632-c22dea06-0ff6-4914-8ec4-5f7d956f3fdc.png" width="593.4000244140625" title="" crop="0,0,1,1" id="u567ac262" class="ne-image">
