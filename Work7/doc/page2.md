:::color2
在机器人利用 **move_base** 节点进行自主导航之前，我们先要完成 2 项工作：**构建一张环境地图，同时让机器人在该地图中的进行自主定位。**

没有地图，机器人将无法知晓周围环境；而在地图上准确定位自身位置，让机器人明确“我在哪”。只有具备了环境先验信息与自身位姿，`**<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">move_base</font>**`才能根据目标点规划出合理可行的路径。

:::

#### 什么是 SLAM

SLAM（Simultaneous Localization and Mapping）即同时定位与地图构建，在机器人和智能驾驶领域， SLAM技术起到了至关重要的作用。如机器人巡逻、无人车自动驾驶、室内自主导航等领域 ，**`<font style="color:#DF2A3F;">`机器人通过传感器获取环境信息，同时利用这些信息进行自身定位，以构建地图。`</font>`**

<img src="https://cdn.nlark.com/yuque/0/2025/gif/54556538/1743920868868-0b77b763-214d-445f-ae2c-0367f7126457.gif" width="1193" title="" crop="0,0,1,1" id="JV8CS" class="ne-image">

根据感知环境的传感器，常用的 SLAM 算法有：

+ 基于** 激光雷达** 的 SLAM算法，如 `<font style="color:#DF2A3F;">`gmapping`</font>`、hector和 Google的 `<font style="color:#DF2A3F;">`Cartographer`</font>`等；
+ 基于 **视觉** 的 SLAM算法，如`<font style="color:#DF2A3F;">` ORB-SLAM`</font>`、PTAM、DVO
+ **多传感器融合算法**，常用的传感器融合的SLAM算法，有 VINS-Mono、 LIO-SAM、MSCKF等。在地图构建和定位过程中，还要考虑传感器的准确性和精度 、机器人本身的运动 等影响。 通过融合多种传感器的数据，相互印证和纠正 ，可以在一定程度上避免测量误差，构建出更加精确和完整的环境地图 。

不同的算法适用于不同的场景和应用需求，本节实验中，我们以 gmapping功能包为例，介绍基于激光雷达的 SLAM 算法功能包， 是如何构建地图和定位的。

<img src="https://cdn.nlark.com/yuque/0/2025/png/54556538/1743921563740-8785f1be-c6ba-4332-acb8-2cf802b7fb2d.png?x-oss-process=image%2Fcrop%2Cx_25%2Cy_28%2Cw_1049%2Ch_810" width="1049" title="" crop="0.0228,0.0323,0.9759,0.9644" id="ua04588a8" class="ne-image">

:::color2
`<font style="color:rgb(6, 6, 7);">`与`</font>`**`<font style="color:rgb(6, 6, 7);">`视觉 SLAM相比`</font>`**`<font style="color:rgb(6, 6, 7);">`，`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">` 激光 SLAM `</font>`**`<font style="color:rgb(6, 6, 7);">`构建地图具有`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`数据稳定、抗干扰强、栅格地图直接可用、与 move_base 导航体系高度适配`</font>`**`<font style="color:rgb(6, 6, 7);">`等优势，更适合实现稳定可靠的机器人导航任务。  `</font>`

:::

#### `<font style="color:rgb(6, 6, 7);">`常用激光 SLAM算法比较`</font>`

`<font style="color:rgb(6, 6, 7);">`关于GMapping、Hector和Cartographer三种激光SLAM算法的比较：`</font>`

**`<font style="color:rgb(6, 6, 7);background-color:#FBF5CB;">`GMapping`</font>`**

+ **`<font style="color:rgb(6, 6, 7);background-color:#FBF5CB;">`优点`</font>`**`<font style="color:rgb(6, 6, 7);background-color:#FBF5CB;">`：可以实时构建室内地图，在构建小场景地图时所需的计算量较小且精度较高。有效利用了车轮里程计信息，对激光雷达频率要求较低`</font>`
+ **`<font style="color:rgb(6, 6, 7);background-color:#FBF5CB;">`缺点`</font>`**`<font style="color:rgb(6, 6, 7);background-color:#FBF5CB;">`：随着场景增大所需的粒子增加，构建大地图时所需内存和计算量都会增加。并且没有回环检测，在回环闭合时可能会造成地图错位`</font>`

**`<font style="color:rgb(6, 6, 7);">`Hector`</font>`**

+ **`<font style="color:rgb(6, 6, 7);">`优点`</font>`**`<font style="color:rgb(6, 6, 7);">`：主要用于救灾等地面不平坦的情况，不需要里程计信息`</font><font style="color:rgb(6, 6, 7);">`。适合空中无人机及地面小车在不平坦区域建图`</font><font style="color:rgb(6, 6, 7);">`。`</font>`
+ **`<font style="color:rgb(6, 6, 7);">`缺点`</font>`**`<font style="color:rgb(6, 6, 7);">`：需要激光雷达的更新频率较高且测量噪声小`</font><font style="color:rgb(6, 6, 7);">`。在里程计数据比较精确的时候，无法有效利用里程计信息`</font><font style="color:rgb(6, 6, 7);">`。`</font>`

**`<font style="color:rgb(6, 6, 7);">`Cartographer`</font>`**

+ **`<font style="color:rgb(6, 6, 7);">`优点`</font>`**`<font style="color:rgb(6, 6, 7);">`：是用于手持激光雷达完成的SLAM过程，没有里程计信息可用`</font><font style="color:rgb(6, 6, 7);">`。基于优化框架的SLAM算法，相当于地图中只用一个粒子，因此存储空间会小很多，可以构建巨大的场景地图`</font><font style="color:rgb(6, 6, 7);">`。`</font>`
+ **`<font style="color:rgb(6, 6, 7);">`缺点`</font>`**`<font style="color:rgb(6, 6, 7);">`：需要复杂的矩阵运算，计算量大`</font><font style="color:rgb(6, 6, 7);">`。不进行优化时，笔记本电脑根本就跑不动`</font><font style="color:rgb(6, 6, 7);">`。`</font>`

:::color2
`<font style="color:rgb(6, 6, 7);">`综上所述，`</font>`**`<font style="color:#DF2A3F;">`GMapping适合小场景地图构建`</font>`**`<font style="color:rgb(6, 6, 7);">`，Hector适合地面不平坦场景，Cartographer适合大场景地图构建，但对计算资源要求较高。`</font>`

:::
