# Work6 OpenCV + ROS 项目计划

## 1. 作业目标

基于老师给出的 `Work6/doc` 和 `Work6/homework.md`，完成一个可运行的 RGB-D 视觉作业工程，达到下面效果：

1. 在 Gazebo 中搭建桌子、红瓶、绿瓶、机械臂机器人场景。
2. 从 Kinect2 获取彩色图像、深度图像和相机内参。
3. 将深度图/彩色图转换为 3D 点云，并发布到 ROS 话题中。
4. 将最后一帧点云保存为 PCD 文件。
5. 实现最近障碍物距离检测。
6. 实现红色瓶子的识别与距离测量。
7. 优先保证“现象跑通”，不做展示文档、美化和额外封装。

---

## 2. 总体实现策略

### 2.1 包组织方式

`Work6` 独立补成一个新的 ROS 包，包名继续使用 `image_pkg`。

原因：
- 不污染 `Work5`
- 方便单独构建和验收
- 结构上和前面作业保持一致
- 后续只需要把 `/home/zyz/catkin_ws/src/image_pkg` 切换到 `Work6` 即可运行

### 2.2 命名策略

按老师课件命名优先，脚本和 launch 尽量贴老师文档，降低验收沟通成本。

### 2.3 实现原则

- 先保证主流程通，再做 page4 扩展功能
- 先做独立节点，再通过 launch 串联
- 不做过度工程化
- 参数尽量放到 yaml，避免全部写死
- 重点保证 ROS 话题链路正确、现象稳定

---

## 3. 目录规划

建议 `Work6` 最终结构如下：

```text
Work6/
├─ package.xml
├─ CMakeLists.txt
├─ homework.md
├─ plan.md
├─ doc/
│  ├─ page1.md
│  ├─ page2.md
│  ├─ page3.md
│  └─ page4.md
├─ launch/
│  ├─ wpr_bottles.launch
│  ├─ work6_pointcloud.launch
│  ├─ work6_detection.launch
│  └─ work6_all.launch
├─ config/
│  ├─ pointcloud.yaml
│  ├─ nearest_obstacle.yaml
│  └─ red_bottle.yaml
├─ src/
│  ├─ get_pointcloud.py
│  ├─ get_pointcloud3.py
│  ├─ nearest_obstacle_final.py
│  └─ red_bottle_smart.py
└─ output/
   └─ pointcloud/
```

---

## 4. 需要实现的文件与职责

### 4.1 ROS 包基础文件

#### `package.xml`
声明依赖：
- `rospy`
- `sensor_msgs`
- `std_msgs`
- `cv_bridge`

运行依赖：
- `python3-opencv`
- `python3-numpy`

#### `CMakeLists.txt`
完成以下事情：
- 注册 Python 节点安装
- 安装 `launch/config/output/doc`
- 不写 C++ 编译目标

---

### 4.2 场景启动文件

#### `launch/wpr_bottles.launch`
负责启动老师要求的仿真场景：

- 启动 Gazebo 空世界
- 加载 `simple.world`
- 生成桌子
- 生成红瓶
- 生成绿瓶
- 生成 `wpb_home_mani`
- 加载控制器

模型位置按老师文档固定，不做动态生成。

---

### 4.3 点云相关节点

#### `src/get_pointcloud.py`
功能：
- 订阅深度图 `/kinect2/sd/image_depth_rect`
- 订阅内参 `/kinect2/sd/camera_info`
- 将深度图转换为 3D 点云
- 发布到 `/pointcloud_output`

特点：
- 只用深度图
- 不做彩色点云
- 作为第一阶段基础验证节点

#### `src/get_pointcloud3.py`
功能：
- 订阅彩色图 `/kinect2/hd/image_color_rect`
- 订阅深度图 `/kinect2/sd/image_depth_rect`
- 订阅内参 `/kinect2/sd/camera_info`
- 生成彩色点云
- 发布到 `/pointcloud_output`
- 程序退出时自动保存最后一帧为 `output_cloud.pcd`

这是最终主节点，作业主流程以它为准。

---

### 4.4 检测节点

#### `src/nearest_obstacle_final.py`
功能：
- 只订阅深度图
- 过滤无效深度值
- 输出最近障碍物距离

作用：
- 对应 page4 的最近障碍物测距要求
- 用来证明深度图数据能直接做测距任务

#### `src/red_bottle_smart.py`
功能：
- 订阅彩色图和深度图
- 在 RGB 图中用 HSV 阈值提取红色区域
- 找到最大红色轮廓中心
- 将彩色图坐标映射到深度图
- 读取该点深度，输出红瓶距离

作用：
- 对应 page4 的红色瓶子距离检测要求
- 证明 RGB 与 Depth 能联合完成目标检测和测距

---

## 5. ROS 话题与数据流设计

### 5.1 输入话题

统一使用老师文档中的 Kinect2 话题：

- 彩色图：`/kinect2/hd/image_color_rect`
- 深度图：`/kinect2/sd/image_depth_rect`
- 相机内参：`/kinect2/sd/camera_info`

### 5.2 输出话题

- 点云输出：`/pointcloud_output`

### 5.3 数据流

#### 主线 1：点云生成
`RGB/Depth/CameraInfo -> OpenCV/Numpy -> 3D 点坐标计算 -> PointCloud2 -> RViz`

#### 主线 2：PCD 保存
`PointCloud2 源数据 -> 保存最后一帧点列表 -> 退出时写入 ASCII PCD`

#### 主线 3：最近障碍物检测
`Depth -> 有效深度筛选 -> 最小值 -> 距离输出`

#### 主线 4：红瓶距离检测
`RGB -> HSV 红色提取 -> 轮廓中心 -> 映射到 Depth -> 读取深度 -> 距离输出`

---

## 6. 核心算法设计

### 6.1 深度图转三维点云

使用针孔相机模型：

- `z = depth_mm / 1000.0`
- `x = (u - cx) * z / fx`
- `y = (cy - v) * z / fy`

说明：
- 深度图编码按 `16UC1` 处理
- 深度单位按毫米转米
- `y` 轴取反，保证 RViz 中方向正常
- 遍历深度图像素时做降采样，减少卡顿

### 6.2 彩色映射

由于彩色图和深度图分辨率不同：
- 深度图分辨率：`512 x 424`
- 彩色图分辨率：`1920 x 1080`

采用比例映射：
- `u_rgb = u * w_rgb / w_depth`
- `v_rgb = v * h_rgb / h_depth`

然后从彩色图读取 `(b, g, r)`，打包到点云 `rgb` 字段中。

### 6.3 最近障碍物检测

从深度图中提取有效值：
- 过滤 `0`
- 过滤过近和过远异常值
- 对有效深度取最小值
- 转换成米输出

### 6.4 红瓶检测

流程固定如下：
1. BGR 转 HSV
2. 用双区间提取红色
3. 开运算去噪
4. 查找轮廓
5. 取最大红色轮廓
6. 计算质心
7. 坐标映射到深度图
8. 读取深度值并输出距离

---

## 7. 参数规划

### `config/pointcloud.yaml`
建议包含：
- `rgb_topic`
- `depth_topic`
- `camera_info_topic`
- `pointcloud_topic`
- `frame_id`
- `publish_rate`
- `step`
- `min_depth_mm`
- `max_depth_mm`
- `pcd_output_path`

### `config/nearest_obstacle.yaml`
建议包含：
- `depth_topic`
- `min_valid_mm`
- `max_valid_mm`
- `publish_rate`

### `config/red_bottle.yaml`
建议包含：
- `rgb_topic`
- `depth_topic`
- `publish_rate`
- `hsv_red_1`
- `hsv_red_2`
- `min_area`
- `depth_min_m`
- `depth_max_m`

---

## 8. Launch 规划

### `launch/wpr_bottles.launch`
只负责场景。

### `launch/work6_pointcloud.launch`
负责：
- 启动 `get_pointcloud.py` 或 `get_pointcloud3.py`

### `launch/work6_detection.launch`
负责：
- 启动 `nearest_obstacle_final.py`
- 启动 `red_bottle_smart.py`

### `launch/work6_all.launch`
总入口，负责：
- include `wpr_bottles.launch`
- include `work6_pointcloud.launch`
- include `work6_detection.launch`

这样可以分模块调试，也能一键总启动。

---

## 9. 推荐实现顺序

### 第一阶段：搭场景
先完成：
- `package.xml`
- `CMakeLists.txt`
- `wpr_bottles.launch`

验收目标：
- Gazebo 中能看到桌子、红瓶、绿瓶、机器人

### 第二阶段：打通点云主链路
先写：
- `get_pointcloud.py`

验收目标：
- `/pointcloud_output` 有数据
- RViz 能看到基本点云

### 第三阶段：完成 PCD 保存
再写：
- `get_pointcloud3.py`

验收目标：
- 停止节点后生成 `output_cloud.pcd`

### 第四阶段：完成 page4 检测功能
再写：
- `nearest_obstacle_final.py`
- `red_bottle_smart.py`

验收目标：
- 能输出最近障碍物距离
- 能输出红瓶距离

### 第五阶段：统一 launch
最后补：
- `work6_pointcloud.launch`
- `work6_detection.launch`
- `work6_all.launch`

验收目标：
- 一套命令可完整跑通

---

## 10. 运行流程规划

### 10.1 准备
1. 将 `Work6` 补成 `image_pkg`
2. 将 `/home/zyz/catkin_ws/src/image_pkg` 指向 `Work6`
3. 执行 `catkin_make`
4. `source devel/setup.bash`

### 10.2 场景启动
运行：
- `roslaunch image_pkg wpr_bottles.launch`

### 10.3 点云验证
运行：
- `rosrun image_pkg get_pointcloud.py`

验证：
- RViz 中显示 `/pointcloud_output`

### 10.4 PCD 保存验证
运行：
- `rosrun image_pkg get_pointcloud3.py`

停止后验证：
- `output/pointcloud/output_cloud.pcd` 已生成

### 10.5 检测验证
分别运行：
- `rosrun image_pkg nearest_obstacle_final.py`
- `rosrun image_pkg red_bottle_smart.py`

验证：
- 控制台持续输出最近障碍物距离
- 控制台输出红瓶距离

---

## 11. 验收标准

最终以以下结果作为完成标准：

### 主任务
- Gazebo 场景正常启动
- Kinect2 相关话题存在
- 点云节点成功发布 `/pointcloud_output`
- RViz 中能看到桌子和瓶子的 3D 点云
- 停止节点后能保存 `PCD` 文件

### 扩展任务
- 最近障碍物距离可以稳定输出
- 红色瓶子距离可以稳定输出

### 工程要求
- 所有脚本都能 `rosrun image_pkg ...`
- 所有 launch 都能 `roslaunch image_pkg ...`
- 代码只依赖 ROS Noetic + Python + OpenCV
- 不修改 `Work5`

---

## 12. 风险点与规避方案

### 风险 1：彩色图和深度图分辨率不同
处理方式：
- 使用比例映射，不做复杂标定对齐

### 风险 2：深度图大量 0 值
处理方式：
- 过滤 `0`
- 设置最小/最大深度阈值

### 风险 3：Python 点云生成太慢
处理方式：
- `step = 4` 做降采样
- 发布频率控制在 `10Hz` 左右

### 风险 4：PCD 保存位置混乱
处理方式：
- 固定输出到 `Work6/output/pointcloud/output_cloud.pcd`

### 风险 5：老师代码示例里公式和单位有不严谨地方
处理方式：
- 实现时统一按 `depth_mm / 1000.0` 转米
- 保证实际现象正确，不照抄有问题的公式写法

---

## 13. 本次明确不做的内容

以下内容不纳入本次作业实现重点：

- 展示文档排版
- README 美化
- 点云滤波、分割、特征提取的深入 PCL 算法
- C++ 重写优化
- 复杂参数动态调节界面
- page4 之外的加分移动抓取联动功能

---

## 14. 最终结论

本项目按“老师命名优先、现象优先、模块分步实现”的策略推进。

最终交付应当是一个独立的 `Work6/image_pkg` ROS 包，包含：
- 1 个场景 launch
- 3 个功能 launch
- 4 个 Python 节点
- 3 个配置文件
- 1 个固定输出目录

主线先完成：
- 场景
- 点云
- PCD

再完成：
- 最近障碍物距离检测
- 红瓶距离检测

这样做最贴合老师文档，最容易验收，也最适合你现在这次作业目标。
