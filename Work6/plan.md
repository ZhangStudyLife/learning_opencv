# Work6 完整部署与演示增强计划

## 1. 计划目的

本计划用于指导 `Work6` 从“基础作业可运行”升级到“演示效果完整、部署链路一键化、界面配置自动完成”的状态。

本次计划不仅覆盖老师 `Work6/homework.md` 里的基础要求，还补上你根据参考视频和截图提出的增强需求，目标是让最终效果更接近同学演示：

1. Gazebo 场景一键启动，桌子、红瓶、绿瓶、机器人全部自动加载。
2. Kinect2 的彩色图、深度图、相机内参自动接入。
3. 自动生成并发布彩色点云。
4. 自动保存最后一帧点云为 `PCD` 文件。
5. 自动打开 RViz，并预配置好左侧面板、图像显示、点云显示、展开状态、颜色模式、大小等参数。
6. 新增绿色瓶检测，支持在彩色画面中显示绿色框。
7. 新增绿色掩膜黑白窗口，用于演示颜色阈值分割效果。
8. 支持机器人运动时继续识别绿色瓶，并持续输出距离。
9. 整个流程尽量压缩成一个一键脚本启动，不靠手工在 RViz 里乱点。

---

## 2. 需求来源与约束

### 2.1 老师原始作业要求

`Work6/homework.md` 给出的最低目标是：

> 请搭建实验场景，利用 RGB-D 相机获取彩色图像与深度图像，将其转换为 3D 点云数据，并保存为 PCD 格式文件，完成演示。

也就是说，老师的硬性目标是：

1. 场景搭建
2. RGB-D 数据获取
3. 3D 点云生成
4. PCD 保存
5. 可演示

### 2.2 你新增的增强要求

根据 `Work6/doc/运动检测小球.mp4` 和 `Work6/doc/0356783c3f34b652cfcb36bd913deb27.jpg`，你希望最终方案额外具备以下效果：

1. 识别目标从“红瓶”切换为“绿瓶”。
2. 在 RGB 图像中给绿色瓶子画出明显的绿色矩形框。
3. 能单独显示绿色阈值掩膜的黑白图窗口。
4. 机器人运动过程中仍能稳定识别绿色瓶并输出距离。
5. RViz 左侧 `Displays` 面板里的项目、展开状态和勾选项提前配好。
6. RViz 里除了自定义点云，还要能看到更密、更清楚的高密度点云效果。
7. 尽量通过命令行和配置文件解决，不再靠手工点 RViz。

### 2.3 本次计划的边界

本计划优先保证“部署完整”和“演示效果逼近参考视频”，但仍然坚持下面几个约束：

1. 不去改 `Work5`。
2. 不引入复杂的深度学习模型。
3. 不重写成 C++。
4. 不做与本次演示无关的大规模重构。
5. 继续基于 ROS Noetic + Python3 + OpenCV + 现有 Gazebo 仿真环境。

---

## 3. 当前状态复盘

当前 `Work6` 已经具备以下基础：

1. `wpr_bottles.launch` 已能起 Gazebo 场景。
2. `get_pointcloud.py` 和 `get_pointcloud3.py` 已能生成自定义点云。
3. `get_pointcloud3.py` 已支持退出时保存 `PCD`。
4. `run_work6.sh` 已支持检查工作区并自动 `catkin_make` 后启动。
5. `work6_pointcloud.rviz` 已有基础的 `PointCloud2` 显示配置。

但当前仍然有几个明显短板：

1. 检测节点还是 `red_bottle_smart.py`，目标颜色不对。
2. 没有参考视频里的 `RGB Detection` 和 `Green Mask` 窗口。
3. RViz 只显示一个 `PointCloud2`，左侧内容不够丰富。
4. 默认 RViz 看的还是 `/pointcloud_output`，点云稀疏感比较明显。
5. 没有把 `/kinect2/sd/points` 原生高密度点云作为主要演示资源。
6. 没有把“运动识别绿色瓶”的完整链路收进一键启动脚本。

结论很直接：现有工程已经能交最基础作业，但离“像别人视频里那样好看、好演示、自动化程度高”还差一截。

---

## 4. 最终交付目标

本次最终交付，不是单纯交一个能跑的节点，而是一整套“可部署、可展示、可验收”的 Work6 演示工程。

### 4.1 最终用户体验目标

执行一条命令后，应当自动完成：

1. 检查 `catkin_ws` 与 `image_pkg -> Work6` 的映射。
2. 编译工作区。
3. 启动 Gazebo 场景。
4. 启动点云生成节点。
5. 启动绿色瓶检测节点。
6. 启动 RViz。
7. 自动加载 RViz 配置，不需要手工 Add、勾选、展开。
8. 自动打开检测窗口，显示彩色检测图和绿色掩膜图。

### 4.2 最终演示窗口组成

最终演示应至少包含以下 4 类可视化结果：

1. Gazebo 仿真场景
2. RViz 三维显示
3. `RGB Detection` 彩色检测窗口
4. `Green Mask` 黑白掩膜窗口

### 4.3 最终点云展示策略

为了同时兼顾“作业要求”和“演示效果”，点云采用双轨方案：

1. `/pointcloud_output`
   - 由我们自己的 Python 节点生成
   - 用于作业说明、PCD 保存和自主实现证明
2. `/kinect2/sd/points`
   - 由 Kinect2 仿真直接提供的原生高密度点云
   - 用于 RViz 里展示更密、更清楚的点云现象

这个方案最务实。否则你硬拿 Python 降采样点云去跟仿真原生点云比密度，纯属给自己找不痛快。

---

## 5. 整体架构设计

### 5.1 功能模块划分

整个 Work6 分为 5 个子系统：

1. 仿真场景子系统
2. RGB-D 数据获取与点云子系统
3. 绿色瓶检测子系统
4. RViz 自动展示子系统
5. 一键部署启动子系统

### 5.2 数据流

#### 主线 A：作业主任务

`Gazebo + Kinect2 -> RGB/Depth/CameraInfo -> 自定义点云节点 -> /pointcloud_output -> 保存 output_cloud.pcd`

#### 主线 B：高密度演示点云

`Gazebo + Kinect2 -> 原生 /kinect2/sd/points -> RViz`

#### 主线 C：绿色瓶检测

`RGB 图 -> HSV 阈值分割 -> 最大绿色轮廓 -> 绿色框绘制 -> 深度坐标映射 -> 距离输出`

#### 主线 D：图像演示

`RGB 图 -> 检测结果窗口`

`HSV Mask -> 黑白掩膜窗口`

### 5.3 设计原则

1. 作业主线与演示增强分层，不互相污染。
2. 自定义点云和原生点云同时存在，但用途不同。
3. 所有主要参数放到 `yaml`。
4. 所有展示项尽量放到 `launch` 与 `rviz` 配置中自动完成。
5. 默认入口尽量一键启动，单节点调试入口仍保留。

---

## 6. 目录与文件规划

最终 `Work6` 以如下结构为目标：

```text
Work6/
├─ package.xml
├─ CMakeLists.txt
├─ homework.md
├─ plan.md
├─ run_work6.sh
├─ run_work6_tmux.sh
├─ stop_work6_tmux.sh
├─ doc/
│  ├─ page1.md
│  ├─ page2.md
│  ├─ page3.md
│  ├─ page4.md
│  ├─ 运动检测小球.mp4
│  └─ 0356783c3f34b652cfcb36bd913deb27.jpg
├─ launch/
│  ├─ wpr_bottles.launch
│  ├─ work6_pointcloud.launch
│  ├─ work6_detection.launch
│  ├─ work6_rviz.launch
│  ├─ work6_demo.launch
│  └─ work6_all.launch
├─ config/
│  ├─ pointcloud.yaml
│  ├─ nearest_obstacle.yaml
│  ├─ green_bottle.yaml
│  └─ work6_pointcloud.rviz
├─ src/
│  ├─ get_pointcloud.py
│  ├─ get_pointcloud3.py
│  ├─ nearest_obstacle_final.py
│  └─ green_bottle_tracker.py
└─ output/
   ├─ pointcloud/
   │  └─ output_cloud.pcd
   └─ reference_frames/
```

说明：

1. `red_bottle_smart.py` 将被替换或重命名为绿色版本实现。
2. `green_bottle.yaml` 用于承接绿色检测参数。
3. `work6_demo.launch` 用于强化演示模式。
4. `run_work6.sh` 作为默认一键入口。

---

## 7. 逐文件改造计划

### 7.1 `src/get_pointcloud.py`

角色：基础版深度点云节点。

保留原因：

1. 方便老师追问“只用深度图时怎么转点云”。
2. 方便单独验证深度坐标反投影逻辑。

本文件改造要求：

1. 保留当前结构。
2. 继续支持只订阅深度图和相机内参。
3. 保留 `step`、`min_depth_mm`、`max_depth_mm` 参数。
4. 不承担主要演示任务。

### 7.2 `src/get_pointcloud3.py`

角色：作业主点云节点。

本文件改造要求：

1. 继续订阅：
   - `/kinect2/hd/image_color_rect`
   - `/kinect2/sd/image_depth_rect`
   - `/kinect2/sd/camera_info`
2. 继续发布 `/pointcloud_output`。
3. 继续退出时保存 `Work6/output/pointcloud/output_cloud.pcd`。
4. 调整参数使点云更细一些：
   - 默认 `step` 从 `4` 下降到 `2` 或保留可配置
   - 发布频率维持在机器能扛住的范围
5. 保证 PCD 文件头合法，便于 `pcl_viewer` 直接打开。

### 7.3 `src/nearest_obstacle_final.py`

角色：保留扩展测距节点。

本文件改造要求：

1. 继续作为附加展示功能保留。
2. 不作为默认演示主窗口。
3. 可在 `tmux` 或扩展 launch 中保留。

### 7.4 `src/green_bottle_tracker.py`

角色：新的绿色瓶演示检测主节点。

这是本次增强的核心节点，职责如下：

1. 订阅 RGB 图像。
2. 订阅深度图像。
3. 在 HSV 空间中提取绿色区域。
4. 做适度形态学开运算/闭运算去噪。
5. 选择面积最大的绿色轮廓作为目标。
6. 在 RGB 图上画绿色矩形框。
7. 在目标中心点处画十字或圆点。
8. 将 RGB 坐标映射到深度图坐标。
9. 读取该点深度值，转换为米。
10. 在图像左上角叠加距离文本。
11. 弹出两个窗口：
    - `RGB Detection`
    - `Green Mask`
12. 控制台输出绿色瓶距离，便于验收。
13. 节点退出时自动关闭 OpenCV 窗口。

这个节点必须直接对齐你给的视频效果，不准再扯成红瓶。

---

## 8. 配置文件详细规划

### 8.1 `config/pointcloud.yaml`

职责：统一管理自定义点云节点参数。

建议参数：

```yaml
rgb_topic: /kinect2/hd/image_color_rect
depth_topic: /kinect2/sd/image_depth_rect
camera_info_topic: /kinect2/sd/camera_info
pointcloud_topic: /pointcloud_output
frame_id: kinect2_camera_frame
publish_rate: 10.0
step: 2
min_depth_mm: 100
max_depth_mm: 5000
pcd_output_path: output/pointcloud/output_cloud.pcd
save_on_shutdown: true
log_interval: 2.0
```

重点：

1. 默认 `step` 要比现在更细，优先尝试 `2`。
2. 若性能不够，再退回 `4`。
3. 路径必须固定到 `Work6/output/pointcloud/output_cloud.pcd`。

### 8.2 `config/green_bottle.yaml`

职责：统一管理绿色检测节点参数。

建议参数：

```yaml
rgb_topic: /kinect2/hd/image_color_rect
depth_topic: /kinect2/sd/image_depth_rect
publish_rate: 10.0
min_area: 400
change_threshold_m: 0.05
depth_min_m: 0.1
depth_max_m: 10.0
show_windows: true
show_mask_window: true
show_detection_window: true
kernel_size: 5
h_min: 35
h_max: 90
s_min: 60
s_max: 255
v_min: 60
v_max: 255
```

重点：

1. 颜色阈值直接针对绿色，不再保留红色双区间逻辑。
2. `show_windows` 要能控制是否弹出窗口，方便远程环境调试。
3. 面积阈值先设中等，不要小得满屏乱框。

### 8.3 `config/work6_pointcloud.rviz`

职责：自动把 RViz 配成可演示状态。

最终应包含至少这些显示项：

1. `Grid`
2. `Image`：显示 RGB 图像
3. `Image`：显示深度图像
4. `PointCloud2`：显示 `/kinect2/sd/points`
5. `PointCloud2`：显示 `/pointcloud_output`

推荐显示策略：

1. `/kinect2/sd/points`
   - 默认开启
   - `Color Transformer = RGB8`
   - `Style = Points`
   - `Size (Pixels) = 3`
2. `/pointcloud_output`
   - 默认开启或可选开启
   - 便于证明这是我们自己算出来的点云
3. 左侧 `Displays` 面板中相关项默认展开，尽量接近参考截图的手感。
4. `Fixed Frame` 固定为 `kinect2_camera_frame`。

说明：

你要求的“左边点开很多内容、黑白那些都勾上”，本质上不是命令行 magic，而是把 RViz 配置文件提前写死。
这玩意儿不靠手工点，靠 `.rviz` 配置落地，才是正路。

---

## 9. Launch 文件详细规划

### 9.1 `launch/wpr_bottles.launch`

职责：

1. 启动 Gazebo 空世界。
2. 加载桌子。
3. 加载红瓶。
4. 加载绿瓶。
5. 加载 `wpb_home_mani`。
6. 加载控制器。

要求：

1. 模型坐标继续沿用老师文档。
2. 不在这里掺杂检测逻辑。

### 9.2 `launch/work6_pointcloud.launch`

职责：

1. 启动 `get_pointcloud3.py`。
2. 载入 `pointcloud.yaml`。

要求：

1. 默认用彩色点云版本。
2. 保留切回 `get_pointcloud.py` 的能力用于单独调试。

### 9.3 `launch/work6_detection.launch`

职责：

1. 启动 `green_bottle_tracker.py`
2. 可选启动 `nearest_obstacle_final.py`

建议：

1. 默认主演示只必须起绿色检测节点。
2. 最近障碍物节点作为附加功能，可加参数开关控制。

### 9.4 `launch/work6_rviz.launch`

职责：

1. 启动 RViz。
2. 自动加载 `config/work6_pointcloud.rviz`。

### 9.5 `launch/work6_demo.launch`

职责：

1. include `wpr_bottles.launch`
2. include `work6_pointcloud.launch`
3. include `work6_detection.launch`
4. include `work6_rviz.launch`

用途：

1. 专门用于“增强演示模式”
2. 让绿色检测、点云和 RViz 一起启动

### 9.6 `launch/work6_all.launch`

职责：

1. 作为最终默认总入口
2. 直接切到 `work6_demo.launch`

这样做的好处：

1. 用户执行一条命令就够
2. 各子 launch 保持清晰
3. 后续想拆调试不会把总入口搞成一锅粥

---

## 10. 一键部署脚本规划

### 10.1 `run_work6.sh`

这是最终默认入口。

必须完成以下动作：

1. `source /opt/ros/noetic/setup.bash`
2. 检查 `/home/zyz/catkin_ws/src/image_pkg` 是否存在
3. 检查它是否指向当前 `Work6`
4. 执行 `catkin_make`
5. `source /home/zyz/catkin_ws/devel/setup.bash`
6. 设置 `ROS_MASTER_URI`
7. 启动 `roslaunch image_pkg work6_all.launch`

最终用户命令固定为：

```bash
bash /home/zyz/learning_opencv/Work6/run_work6.sh
```

### 10.2 `run_work6_tmux.sh`

这是调试入口，不是默认入口。

职责：

1. 分别启动 `roscore`
2. 启动 Gazebo
3. 启动点云节点
4. 启动绿色瓶检测节点
5. 启动 RViz
6. 必要时启动最近障碍物节点

要求：

1. 便于分窗口看日志
2. 节点名清晰
3. 默认 session 名称统一

### 10.3 `stop_work6_tmux.sh`

职责：

1. 清理全部 `tmux` 会话
2. 保证演示结束后可以快速收场

---

## 11. 绿色瓶检测算法规划

### 11.1 检测目标

目标物体固定为桌子上的绿色瓶子。

### 11.2 输入数据

1. 彩色图：`/kinect2/hd/image_color_rect`
2. 深度图：`/kinect2/sd/image_depth_rect`

### 11.3 核心流程

1. 将 RGB 图转成 HSV。
2. 用绿色阈值做 `cv2.inRange`。
3. 对掩膜做开运算去掉小噪点。
4. 对掩膜做闭运算补小洞。
5. 提取所有轮廓。
6. 选择面积最大的绿色轮廓。
7. 过滤过小轮廓，避免误检。
8. 计算包围框。
9. 在原图上画绿色矩形框。
10. 计算轮廓中心点。
11. 将中心点从 HD 彩图坐标映射到 SD 深度图坐标。
12. 读取深度值并转换为米。
13. 在图像上绘制距离文本。
14. 在控制台输出距离。

### 11.4 输出形式

图像输出：

1. `RGB Detection` 窗口
2. `Green Mask` 窗口

控制台输出：

```text
绿色瓶距离：1.25 米
```

### 11.5 运动场景适配

为了保证机器人运动时还能识别，节点必须做到：

1. 发布频率不要太低，建议 `10Hz`。
2. 矩形框和距离更新不要只在大变化时才输出。
3. 颜色阈值不要设得太窄。
4. 对单帧无效深度提供容错，例如：
   - 读取中心点失败时，可尝试邻域最小有效深度
   - 不能一碰到 0 就直接废掉整个检测

---

## 12. RViz 完整部署规划

### 12.1 必须自动勾选的显示项

`Displays` 面板应预配置以下项目：

1. `Grid`
2. `RGB Image`
3. `Depth Image`
4. `Native PointCloud`
5. `Custom PointCloud`

推荐命名：

1. `Grid`
2. `RGB Image`
3. `Depth Image`
4. `Native Dense Cloud`
5. `Custom Cloud`

### 12.2 建议具体配置

#### RGB Image

1. Topic：`/kinect2/hd/image_color_rect`
2. Normalize Range：关闭

#### Depth Image

1. Topic：`/kinect2/sd/image_depth_rect`
2. Normalize Range：开启
3. Median window：开启或适中

#### Native Dense Cloud

1. Topic：`/kinect2/sd/points`
2. Style：`Points`
3. Size (Pixels)：`3`
4. Color Transformer：`RGB8`
5. Queue Size：`10`

#### Custom Cloud

1. Topic：`/pointcloud_output`
2. Style：`Points`
3. Size (Pixels)：`3`
4. Color Transformer：`RGB8`

### 12.3 面板布局目标

1. 左侧显示 `Displays`
2. 右侧显示 `Views`
3. 下面显示 `Time`
4. `Displays` 面板默认展开主要条目
5. `PointCloud2`、`Image` 的主要参数展开可见

### 12.4 这样做的目的

1. 你不再需要手工 Add Image / PointCloud2
2. 不再需要手工选 Topic
3. 不再需要手工点开属性
4. 不再需要手工选 `RGB8`
5. 不再需要手工调点大小

一句话总结：把“命令行解决 RViz 配置”的事情，真正落到 `.rviz` 文件，而不是靠嘴说。

---

## 13. 完整部署步骤

### 第 1 步：确认工作区映射

确保：

```bash
readlink -f /home/zyz/catkin_ws/src/image_pkg
```

输出应为：

```bash
/home/zyz/learning_opencv/Work6
```

### 第 2 步：运行一键脚本

执行：

```bash
bash /home/zyz/learning_opencv/Work6/run_work6.sh
```

### 第 3 步：自动完成的内容

脚本启动后，应自动完成：

1. 编译工作区
2. 启动 Gazebo
3. 启动点云节点
4. 启动绿色检测节点
5. 启动 RViz

### 第 4 步：演示时应看到的现象

Gazebo：

1. 桌子
2. 红瓶
3. 绿瓶
4. 机器人

RViz：

1. 左侧有多个显示项
2. RGB 图和深度图可见
3. 原生点云高密度显示
4. 自定义点云也可见

OpenCV 窗口：

1. `RGB Detection`
2. `Green Mask`

控制台：

1. 持续输出绿色瓶距离

### 第 5 步：PCD 验证

结束程序后，应检查：

```bash
ls -l /home/zyz/learning_opencv/Work6/output/pointcloud/output_cloud.pcd
```

### 第 6 步：离线查看点云

如已安装 `pcl-tools`，可执行：

```bash
pcl_viewer /home/zyz/learning_opencv/Work6/output/pointcloud/output_cloud.pcd
```

---

## 14. 验收标准

### 14.1 基础作业验收

以下项目必须全部通过：

1. Gazebo 场景正常出现。
2. Kinect2 话题正常存在。
3. `/pointcloud_output` 正常发布。
4. `output_cloud.pcd` 成功生成。
5. RViz 能显示点云。

### 14.2 增强演示验收

以下项目必须尽量达到参考视频效果：

1. 自动识别绿色瓶子。
2. RGB 画面中出现绿色框。
3. 绿色掩膜黑白图能单独显示。
4. 机器人运动时仍能持续检测。
5. RViz 左侧显示项自动配置完成。
6. RViz 中能看到高密度点云。

### 14.3 部署验收

以下项目必须满足：

1. 一条脚本命令即可启动完整演示。
2. 不需要手工在 RViz 中逐项点配置。
3. 代码、配置、launch、脚本都放在 `Work6` 内闭环完成。

---

## 15. 风险与规避方案

### 风险 1：绿色阈值不稳定

问题：

1. 光照或渲染导致绿色瓶颜色偏差
2. 容易漏检或误检

规避：

1. HSV 阈值留足余量
2. 先以仿真环境颜色为准调参
3. 保留 yaml 配置可快速调整

### 风险 2：自定义点云太稀

问题：

1. Python 计算点云性能有限
2. `step` 太大时点云稀疏

规避：

1. 自定义点云用于作业与 PCD 保存
2. RViz 展示主视图采用 `/kinect2/sd/points`

### 风险 3：OpenCV 窗口在某些终端环境打不开

规避：

1. 增加 `show_windows` 开关
2. 默认本地桌面环境开启
3. 远程无图形环境时可关闭，仅保留日志输出

### 风险 4：机器人运动时检测抖动

规避：

1. 适当提高发布频率
2. 对中心点做邻域深度容错
3. 轮廓面积阈值不要太低

### 风险 5：RViz 配置太花，反而难看

规避：

1. 保持显示项有用但不过量
2. 只保留对演示有价值的项目
3. 优先让画面清楚，而不是堆满插件

---

## 16. 实施顺序

建议按下面顺序推进：

### 第一阶段：改检测目标

1. 把红瓶检测逻辑替换为绿瓶检测
2. 跑通矩形框与距离输出

### 第二阶段：补演示窗口

1. 新增 `RGB Detection`
2. 新增 `Green Mask`

### 第三阶段：增强 RViz

1. 在 `.rviz` 中加入 RGB 图、深度图、原生点云、自定义点云
2. 调整默认展开状态、点大小、颜色模式

### 第四阶段：统一 launch

1. 增加 `work6_demo.launch`
2. 让 `work6_all.launch` 指向最终完整模式

### 第五阶段：统一脚本

1. `run_work6.sh` 默认起完整演示
2. `run_work6_tmux.sh` 作为调试入口

### 第六阶段：验收

1. 编译通过
2. 运行通过
3. 检测通过
4. RViz 自动化通过
5. PCD 生成通过

---

## 17. 最终结论

本计划的最终目标，不是只做一个“能交差的 Work6”，而是把它收成一套完整可演示的工程：

1. 基础作业目标全部覆盖
2. 绿色瓶检测补齐参考视频效果
3. RViz 配置自动化
4. 点云显示更密、更清楚
5. 一键启动，一键验收

最终落地后的 Work6 应满足下面这句人话：

> 执行一个脚本，就能自动起 Gazebo、起点云、起绿色瓶检测、起 RViz，屏幕上同时看到三维点云、RGB 检测框、绿色掩膜黑白图，结束后还会自动落盘 PCD 文件。

这才叫“部署好”，不是那种还要你手工去 RViz 里点半天的半吊子玩意儿。
