:::color2

+ `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`你告诉机器人：去那个点（`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`Goal`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`）`</font>`
+ **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`move_base`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">` 负责：`</font>`
  1. `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`看地图，规划大致路线`</font>`
  2. `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`看传感器，躲避障碍物`</font>`
  3. `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`看里程计，知道自己走到哪了`</font>`
  4. `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`不断输出速度，让机器人稳稳走到终点`</font>`
+ `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`最终输出：`</font>**<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">/cmd_vel</font>**``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`（线速度 + 角速度）`</font>`

:::

在未知环境中实现机器人的自主导航是一个复杂的任务，涉及多个关键技术与功能模块的协同。在开始学习之前，我们先通过一幅漫画了解机器人自主导航的实现过程：

<img src="https://cdn.nlark.com/yuque/0/2025/png/54556538/1744095895968-831124cc-f8e0-4beb-8c7e-2b81148dda43.png?x-oss-process=image%2Fcrop%2Cx_0%2Cy_0%2Cw_1525%2Ch_1020" width="753" title="" crop="0,0,1,0.994" id="FDBon" class="ne-image">

`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`这张图是 ROS 社区广为流传的梗图， 用来直观讲解`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`导航栈`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`的工作原理，你可能会在 ROS 教学中经常看到它。2009年Willow Garage 邀请了《PhD Comics》创作者 Jorge Cham 绘制了一系列 ROS 主题漫画，用来推广 ROS 生态`</font>`

#### `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`画面内容：`</font>`

+ `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`在起点 A、B 处，一个机器人走出了`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`极其蜿蜒、绕圈、完全不最优`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`的红色路径，还兴奋地举着机械臂 “炫耀”，旁边两个机器人围观。`</font>`
+ `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`图下的配文：`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`"His `</font>`****`<font style="color:#DF2A3F;background-color:rgba(0, 0, 0, 0);">`path-planning`</font>`****`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">` may be sub-optimal, but it's got flair."  意思是`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`：”他的路径规划虽然不是最优的，但姿势很帅！~“`</font>`

#### `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`内涵：`</font>`

+ **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`ROS 导航框架的逻辑`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`：ROS 集成的路径规划（Path Planner）算法“能到就行，不一定最短或是最快”。在地图上搜索可行路径，但如果参数调得不好、地图有误差、或者局部避障逻辑过分“有效”，就会出现这种 “绕大弯、画蛇形” 的奇葩路径。`</font>`
+ **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`行业梗`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`：机器人开发的工程师，几乎都遇到过机器人“不走直线、疯狂绕路、原地画圈” 的调试噩梦，这个漫画戳中了开发者的共同痛点，用自嘲的方式让技术变得有趣。`</font>`
+ **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`关于 Willow Garage `</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`：右下角标注了`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">www.willowgarage.com</font>``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`，大名鼎鼎的柳树仓库，是创造 ROS 的公司，漫画里的机器人原型就是 PR2，是柳树仓库的代表作。`</font>`

#### `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`ROS Navigation Stack（导航功能包集） `</font>`

**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`ROS Navigation Stack 导航功能包集`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`提供了移动机器人自主导航的标准架构，主要模块与工作流程可概括如下`</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`：`</font>`

| **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`模块`</font>`**             | **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`核心作用`</font>`**                                                                                              | **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`通俗解释`</font>`**                                                                                                                                                                                                                                                                                                                 |
| ------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`Goal`</font>`**             | `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);"></font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`目标点`</font>`**                 | `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`给机器人下达 “去某个位置” 的指令`</font>`                                                                                                                                                                                                                                                                                                 |
| **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`AMCL`</font>`**             | `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`自适应蒙特卡洛`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`定位`</font>`** | `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`通过激光雷达 / 里程计，在已知地图上确定自己当前的位置`</font>`                                                                                                                                                                                                                                                                              |
| **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`Path Planner`</font>`**     | **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`全局路径规划`</font>`**                                                                                          | `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`机器人的“导航地图 APP”，根据起点、终点和全局地图，规划出一条从 A 到 B 的全局路径（漫画里的蜿蜒红线就是这个模块的输出）`</font>`                                                                                                                                                                                                           |
| **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`move_base`</font>`**        | **`<font style="color:#DF2A3F;background-color:rgba(0, 0, 0, 0);">`导航功能节点`</font>`**                                                                                               | `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`导航的“总指挥”，串联全局规划、局部规划、避障，向底盘下发运动指令`</font>`                                                                                                                                                                                                                                                                 |
| **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`/cmd_vel + /odom`</font>`** | `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`速度指令 + 里程计反馈`</font>`                                                                                           | `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">/cmd_vel</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">` 下发给底盘的线速度 / 角速度指令；`</font>``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">/odom</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">` 是底盘回传的里程计数据，用于闭环控制`</font>` |
| **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`Base Controller`</font>`**  | `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`底盘控制器`</font>`                                                                                                      | `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`机器人的 “司机”，把速度指令转换成底盘电机的控制信号`</font>`                                                                                                                                                                                                                                                                              |
| **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`Motor Speeds`</font>`**     | `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`电机转速`</font>`                                                                                                        | `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`执行：驱动电机转动，让机器人按规划路径移动`</font>`                                                                                                                                                                                                                                                                                         |

#### `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`漫画与流程图的对应关系`</font>`

`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`漫画里的机器人，就是这套导航栈的 “实体化”：`</font>`

+ `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`机器人走的蜿蜒路径，就是`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`Path Planner（路径规划器）`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">` 生成的全局路径；`</font>`
+ `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`配文的 “sub-optimal（非最优）”，精准吐槽了路径规划算法的局限性：算法只保证`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`路径可行（无碰撞）`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`，不保证`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`路径最优（最短 / 最快）`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`；`</font>`
+ `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`整个流程从`</font>`**`<font style="color:#DF2A3F;background-color:rgba(0, 0, 0, 0);">` Goal `</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`到`</font>`**`<font style="color:#DF2A3F;background-color:rgba(0, 0, 0, 0);">` Motor Speeds`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`，完整还原了机器人从 “目标” 到 “执行” 的全过程，这就是ROS Navigation 功能包集的功能，ROS 已经帮我们做好啦！~`</font>`

---

#### 总指挥：功能包 move_base

**`<font style="background-color:#FBF5CB;">`move_base`</font>`**`<font style="background-color:#FBF5CB;">` 是 ROS Navigation Stack 中的核心节点，它整合了`</font>`**`<font style="background-color:#FBF5CB;">`全局路径规划、局部路径规划、代价地图、异常恢复`</font>`**`<font style="background-color:#FBF5CB;">`等多个模块，统一接收地图、传感器、里程计与定位数据，对外输出 /cmd_vel 速度控制指令，驱动机器人实现避障、路径跟踪与自主导航。`</font>`

<img src="https://cdn.nlark.com/yuque/0/2026/jpeg/54556538/1775906605256-6eaee342-c7c2-4ee3-bfc0-1556959b33aa.jpeg" width="5856" title="" crop="0,0,1,1" id="Ij41i" class="ne-image">

| 模块样式                                               | 类型                   | 说明                                                                      |
| ------------------------------------------------------ | ---------------------- | ------------------------------------------------------------------------- |
| 白色椭圆（`move_base`内部）                          | provided node          | 已提供，ROS 导航栈**官方提供的核心算法节点**，开箱即用，只需调参    |
| 灰色矩形（如 `amcl`、`map_server`）                | optional provided node | 可选，ROS 官方提供的**可选配套节点**，是导航的常用依赖              |
| 蓝色矩形（如 `sensor sources`、`base controller`） | platform specific node | 自定义，**平台 / 硬件相关节点**，需要开发者根据自己的机器人硬件实现 |

#### `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`模块与数据流向`</font>`

`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`我们按照 “感知 → 规划 → 执行” 的逻辑，来理解机器人进行自主导航的工作流程：`</font>`

##### `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`感知`</font>`

move_base 的数据源可分为 4 类，但这些信息并非全部必需，机器人可根据任务场景灵活配置。例如，在已知环境中，可借助地图实现全局路径规划；在未知环境下，仅依靠环境感知与自身状态反馈，也能完成避障与自主运动。

+ **地图服务：**由 map_server 加载并发布预先构建的栅格地图，为全局路径规划提供环境信息；
+ **外部环境感知数据：**机器人通过激光雷达、深度相机等传感器获取的实时环境信息，典型的数据包括 sensor_msgs/PointCloud2 点云数据与 sensor_msgs/LaserScan 激光扫描数据。
+ **自身状态测量数据：**即里程计（odometry source），用于获取机器人自身的实时位姿、速度等运动信息。
+ **自主定位信息：**综合激光数据、里程计与静态地图，通过自适应蒙特卡洛定位算法（AMCL）实现机器人在全局地图中的精确定位，解决 “我在哪” 的问题，是实现全局导航的重要前提。

##### 规划

`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">move_base</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`是内部包括了 5 个子模块（`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`白色椭圆`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`），完成从目标到运动控制指令的发布：`</font>`

###### `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`全局代价地图 global_costmap`</font>`

`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`以 `</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">map_server</font>``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">` 提供的静态地图为基础，结合传感器观测信息，构建全局环境的代价模型。地图中每个栅格会被赋予代价值，用于表示该区域的通行风险，为全局路径规划提供环境约束。`</font>`

###### `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`全局路径规划器 global_planner`</font>`

`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`根据机器人当前定位、目标点与全局代价地图，使用路径搜索算法（如 A*、Dijkstra）规划出一条从起点到终点的`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`全局最优路径`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`。该路径保证无碰撞、可达性强，但不负责实时避障。`</font>`

###### `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`局部代价地图 local_costmap`</font>`

`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`以机器人自身为中心，构建局部范围内的动态环境代价地图。它主要依赖激光雷达、深度相机等实时传感器数据更新，能够快速响应动态障碍物，是局部避障的基础。`</font>`

###### `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`局部路径规划器 local_planner`</font>`

`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`跟踪全局路径，并结合局部代价地图与里程计信息，实时生成平滑、安全的运动轨迹，输出速度控制指令 `</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">/cmd_vel</font>``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`。常用算法包括 DWA、TEB 等，兼顾跟踪精度与避障能力。`</font>`

###### `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`恢复行为 recovery_behaviors`</font>`

`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`当机器人陷入卡死、定位丢失、路径阻塞等异常状态时，自动触发恢复策略，例如原地旋转、清除局部代价地图、重新规划路径等，使导航系统重新恢复正常工作，提升系统鲁棒性。`</font>`

---

#### 相关话题和服务`<img src="https://cdn.nlark.com/yuque/0/2025/png/54556538/1744095989236-ded9e096-04ba-4f5d-b14e-f88e06c73daa.png" width="756.8" title="" crop="0,0,1,1" id="X4Ly5" class="ne-image">`

---

#### `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`(延伸)：为什么会出现 “非最优路径”？`</font>`

`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`漫画里的奇葩路径，在实际开发中非常常见，可能原因有：`</font>`

+ **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`全局规划器参数问题 `</font>`** `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`：比如 A * 算法的启发函数权重设置不当，或者代价地图（costmap）的障碍物膨胀半径过大，导致机器人不敢走直线，只能绕远路。`</font>`
+ **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`局部避障干扰 `</font>`** `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`：局部路径规划器（如 DWA）为了避障，会频繁修正全局路径，导致轨迹蛇形。`</font>`
+ **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`定位误差 `</font>`** `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`：AMCL 定位不准，机器人 “以为自己在别的位置”，规划出错误路径。`</font>`
+ **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`地图精度问题 `</font>`** `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`：建图时的误差、障碍物标注错误，导致规划器绕开 “不存在的障碍”。`</font>`
