:::color2
**实验内容：**

1. 点云分割、特征提取基础方法的原理与实现；
2. 实操训练：基于PCL+ROS，完成桌面物品点云采集、滤波、分割，提取目标点云特征。

**考察目标：**

1. 能设计基础点云处理流程，完成核心操作；
2. 能实现ROS与PCL的数据传输；
3. 能分析处理问题，提出基础优化方案。

:::

#### 三维视觉：

**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`二维视觉让机器人 “看见”，三维视觉让机器人 “看懂空间”`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`。我们生活在三维世界里，用 RGB 相机互获得的二维视觉只能看到平面，无法感知深度、距离、空间形状，这会影响到机器人的安全、精准地行动和操作。`</font>`

[此处为语雀卡片，点击链接查看](https://www.yuque.com/shellcore/zkttvr/qcdkfrsvyevz9xu7#UcFz4)

`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`机器人需要三维视觉，获得“空间感知能力”，主要用途有：`</font>`

1. **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`获取深度信息，知道 “远近高低”。`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`二维图像只有长和宽，不知道物体离自己多远、有多厚、有没有高低差。三维视觉（双目、结构光、激光雷达等）能测出`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`距离、深度、体积`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`，让机器人分清前后、上下、立体层次。`</font>`

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1775466898944-caa0689a-5b4a-431f-9feb-05e331b6aca8.png" width="520.4000244140625" title="" crop="0,0,1,1" id="u2f7cbb3a" class="ne-image">

2. **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`精准抓取与操作，不抓空、不抓坏。`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`工业机械臂分拣零件、服务机器人端水杯、仓储机器人码垛，都需要知道物体的`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`3D 位置、姿态、轮廓`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`。没有三维视觉，机器人只能对准平面，很容易抓偏、抓空，或对不规则物体完全无法操作。`</font>`

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1775466849172-db2cc65c-e493-4b7f-bbdc-d497a0302a46.png" width="1474.4" title="" crop="0,0,1,1" id="u2af53aef" class="ne-image">

3. **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`自主导航与避障，避免碰撞。`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`移动机器人（AGV、送餐机器人、自动驾驶、巡检机器人）需要识别立体障碍：台阶、悬空管道、凸起物、行人等。二维视觉只能看到平面色块，三维视觉才能判断障碍物的空间位置，规划安全路径。`</font>`
4. **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`识别立体物体与复杂形态。`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`二维只能看轮廓，三维能识别物体的`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`立体形状、结构、姿态`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`。比如分拣异形工件、检测产品凹陷 / 变形、农业机器人判断果实位置、医疗机器人定位病灶，都依赖三维形态感知。`</font>`
5. **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`人机安全协作，避免伤人。`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`协作机器人与人同场工作时，三维视觉能实时感知人的肢体位置、运动轨迹，一旦有人靠近就减速 / 停止，杜绝碰撞风险，这是二维视觉做不到的。`</font>`
6. **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`环境三维重建，适应未知场景。`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`救援机器人、测绘机器人、家庭服务机器人，可通过三维视觉扫描环境，搭建`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`3D 地图`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`，适配废墟、陌生室内等无预设场景，完成搜救、清扫、巡检等任务。`</font>`

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1775467142680-b1b97d87-9738-4427-92e7-4258818a7c7c.png" width="563" title="" crop="0,0,1,1" id="ufbb31135" class="ne-image">

需要注意的是，当前深度相机在实践应用中仍存在一些不足，其中最核心的是深度缺失与深度不准问题，具体主要体现在以下几个场景：

一是受材料、光照条件及物体边缘特性的影响。当拍摄物体为**强反光、透明材质**，或处于**强光直射、弱光昏暗等极端光照环境**时，深度相机的传感器难以准确捕捉深度信息，易出现**深度值跳变、缺失**的情况；而物体边缘处因像素过渡陡峭，也容易产生深度计算偏差，导致边缘区域的深度数据不准确。

二是**人体头发**的深度采集难题。头发具有纤细、松散、透光性强的特点，深度相机的红外光线或结构光易穿透发丝间隙，无法有效反射并捕捉深度信号，导致头发区域常常出现深度缺失，无法准确还原头发的三维形态，这对涉及人体感知的机器人应用（如服务机器人、协作机器人）影响较为明显。

三是**玻璃等透明材质**的深度采集问题。玻璃具有高透明、强反光双重特性，一方面大部分光线会穿透玻璃，无法被传感器接收以计算深度；另一方面玻璃表面的反光会干扰传感器的信号识别，导致玻璃区域要么无法采集到有效深度数据，要么深度值出现严重偏差，这也是机器人在复杂环境中感知时需要重点解决的问题。

#### 常用的深度相机

`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`随着微软 Kinect 、英特尔Realsense和国内的 奥比中光Orbbec（国内3D视觉第一股）这类RGB-D相机的大量普及，依托结构光、ToF、双目等多技术路线，在三维重建、人体姿态、机器人感知、SLAM 等三维视觉算法上实现全面突破，形成了百花齐放的产业格局。`</font>`

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1775467192649-f7ec9cbf-e5b4-4173-9886-6a17d7a308d8.png?x-oss-process=image%2Fcrop%2Cx_35%2Cy_30%2Cw_892%2Ch_190" width="714" title="" crop="0.0375,0.1368,0.9906,1" id="u4dde2c24" class="ne-image">

##### 不同相机获得深度信息的原理也不同

| **几种常用相机型号** | **深度原理**                                                               |
| -------------------------- | -------------------------------------------------------------------------------- |
| **Kinect v1**        | 红外结构光（投射斑点图案）                                                       |
| **Kinect2**          | **Time-of-Flight (****ToF****)** —— 发射红外光，测量往返时间 |
| RealSense D400             | 主动红外立体（双目+结构光）                                                      |
| RealSense L515             | ToF                                                                              |

⚠️本实验中，我们使用的是Kinect2 ，采用的是 ToF 原理获得深度信息。

`<font style="color:rgb(31, 35, 41);background-color:rgba(0, 0, 0, 0);">`RGB-D 相机能够同时获取场景`</font>`**`<font style="color:rgb(31, 35, 41);background-color:rgba(0, 0, 0, 0);">`彩色信息`</font>`**`<font style="color:rgb(31, 35, 41);background-color:rgba(0, 0, 0, 0);">`与`</font>`**`<font style="color:rgb(31, 35, 41);background-color:rgba(0, 0, 0, 0);">`深度信息`</font>`**`<font style="color:rgb(31, 35, 41);background-color:rgba(0, 0, 0, 0);">`，输出两种相互配准的图像数据：一种是与普通相机一致的`</font>`**`<font style="color:rgb(31, 35, 41);background-color:rgba(0, 0, 0, 0);">`RGB 彩色图像`</font>`**`<font style="color:rgb(31, 35, 41);background-color:rgba(0, 0, 0, 0);">`，记录场景的色彩与纹理；另一种是`</font>`**`<font style="color:rgb(31, 35, 41);background-color:rgba(0, 0, 0, 0);">`深度图像（Depth Map）`</font>`**`<font style="color:rgb(31, 35, 41);background-color:rgba(0, 0, 0, 0);">`，每个像素值代表对应空间点到相机光心的直线距离，看上去像灰度亮度。`</font>`

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1775468027542-9a8220dc-b7b6-4743-aaa4-e8cf765c0b5e.png?x-oss-process=image%2Fformat%2Cwebp" width="881" title="" crop="0,0,1,1" id="J2cv9" class="ne-image">

#### `<font style="color:rgb(31, 35, 41);background-color:rgba(0, 0, 0, 0);">`针孔相机模型`</font>`（Pinhole Camera Model）

RGB‑D 相机获取的原始数据是二维图像像素，以及**`<font style="color:rgb(31, 35, 41);background-color:rgba(0, 0, 0, 0);">`像素坐标 `</font>`****`<font style="color:rgb(31, 35, 41);background-color:rgba(0, 0, 0, 0);">`(u,v)`</font>`****`<font style="color:rgb(31, 35, 41);background-color:rgba(0, 0, 0, 0);">` 与对应空间点深度值 `</font>`****`<font style="color:rgb(31, 35, 41);background-color:rgba(0, 0, 0, 0);">`Z`</font>`** 之间的一一对应关系。其中，RGB 通道记录像素的颜色信息，深度通道记录该像素在三维空间中到相机光心的距离信息。结合针孔相机模型，利用已知的相机内参与每个像素的$ （u,v,Z） $，即可反推出该点在相机坐标系下的三维坐标 $ (x,y,Z) $，进而将整幅图像转换为三维点云数据。

<img src="https://cdn.nlark.com/yuque/0/2026/jpeg/54556538/1775469924717-254c4e4b-da3f-4c53-8b58-afb66ec4edcc.jpeg" width="538.4000244140625" title="" crop="0,0,1,1" id="u3a640ecb" class="ne-image">

<img src="https://cdn.nlark.com/yuque/0/2026/jpeg/54556538/1775467047561-85db17e6-ee33-486d-86be-d44fc1c668af.jpeg" width="494.3999938964844" title="针孔成像模型" crop="0,0,1,1" id="u2ea6cd0c" class="ne-image">

**深度值**$ Z
 $ 如何转换为三维坐标？

首先，通过** 针孔成像模型**与**相机内参**$ (f_x, f_y, c_x, c_y) $，将像素坐标转换为相机坐标系下的三维坐标点：

$ u = f_x \cdot \frac{X}{Z} + c_x, \quad v = f_y \cdot \frac{Y}{Z} + c_y $

其中：

+ $ (u, v) $：像素坐标
+ $ Z $：深度值（单位：米）
+ $ (f_x, f_y, c_x, c_y) $：相机内参（由标定获得）

| **参数** | **计算公式**                           | **说明**                   |
| -------------- | -------------------------------------------- | -------------------------------- |
| $ c_x $      | $ \frac{width}{2} $                        | 图像宽度的一半，光学中心的横坐标 |
| $ c_y $      | $ \frac{height}{2} $                       | 图像高度的一半，光学中心的纵坐标 |
| $ f_x $      | $ \frac{width}{sensor\_width} \times f $   | 焦距×分辨率比例                 |
| $ f_y $      | $ \frac{height}{sensor\_height} \times f $ | 焦距×分辨率比例                 |

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1775471405549-5c63a41c-637f-499e-ab42-677c911e4323.png" width="504.20001220703125" title="" crop="0,0,1,1" id="ub58eda75" class="ne-image">

    当图像中所有像素完成这一坐标变换后，就形成了由大量三维坐标点构成的集合——点云数据。点云不只是 “一堆坐标点”，还能给每个点加额外信息，比如颜色、物体表面的朝向等信息。比如 RGB-D 相机拍出来的点云，既有三维位置，又有颜色，拼出来的立体画面就我们眼睛看到的大致一样

#### 本节实验：

`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`通过本节实验，我们将会了解三维视觉相机采集的数据是以什么形式存在于 ROS 中，以及如何转换成三维点云库（PCL）的数据格式，如何使用 PCL工具对点云数据进行处理，获得距离、深度、体积等信息 `</font>`
