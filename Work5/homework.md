# Work5 作业说明

## 1. 作业目标

在机器人足球场仿真环境中，完成以下三项视觉任务：

1. 基于 HSV 阈值分割识别指定颜色小球，并实时显示质心。
2. 基于同一套 HSV 分割结果控制机器人跟随目标小球。
3. 使用 Haar 级联检测人脸，控制机器人对准并靠近目标，自动保存 3 张照片。

## 2. 包与目录约定

- 目录名保持为 `Work5`
- ROS 包名正式切换为 `image_pkg`
- 不修改 `Work4`
- 运行时统一使用 `rosrun image_pkg ...` 或 `roslaunch image_pkg ...`

## 3. 当前实现内容

### 3.1 可执行节点

- `hsv_node.py`
  - 默认订阅 `/kinect2/sd/image_color_rect`
  - 完成 `BGR -> HSV -> inRange -> 开/闭运算 -> moments 质心计算`
  - 提供 6 个 HSV 滑块
  - 支持鼠标点击打印 HSV 取样值
  - 显示原图、HSV 视图、Mask 结果

- `follow_node.py`
  - 直接订阅图像并在节点内部完成 HSV 分割
  - 检测到目标时输出固定线速度和比例角速度
  - 丢失目标时立即停止
  - 调试画面叠加目标中心、图像中心线、偏差和当前速度

- `face_capture_node.py`
  - 使用 OpenCV Haar 级联检测人脸
  - 默认选择最大的人脸作为目标
  - 按水平偏差比例转向，按人脸宽度决定是否继续前进
  - 目标稳定进入中心区域后自动保存 3 张照片

- `move_ball_random.py`
  - 保留为辅助节点
  - 可选在跟球演示时与 `follow_node.py` 一起启动

### 3.2 配置文件

- `config/hsv_green_ball.yaml`
- `config/follow_green_ball.yaml`
- `config/face_capture.yaml`
- `config/ball_motion.yaml`

### 3.3 Launch 入口

- `launch/hsv_demo.launch`
- `launch/follow_ball.launch`
- `launch/face_capture.launch`

## 4. 推荐验收流程

### 4.1 构建

```bash
source /opt/ros/noetic/setup.bash
cd /home/zyz/catkin_ws
catkin_make
source /home/zyz/catkin_ws/devel/setup.bash
rospack find image_pkg
```

### 4.2 HSV 取球演示

终端 1：

```bash
source /opt/ros/noetic/setup.bash
source /home/zyz/catkin_ws/devel/setup.bash
roslaunch wpr_simulation wpb_balls.launch
```

终端 2：

```bash
source /opt/ros/noetic/setup.bash
source /home/zyz/catkin_ws/devel/setup.bash
roslaunch image_pkg hsv_demo.launch
```

### 4.3 跟球演示

终端 1：

```bash
source /opt/ros/noetic/setup.bash
source /home/zyz/catkin_ws/devel/setup.bash
roslaunch wpr_simulation wpb_balls.launch
```

终端 2：

```bash
source /opt/ros/noetic/setup.bash
source /home/zyz/catkin_ws/devel/setup.bash
roslaunch image_pkg follow_ball.launch run_ball_motion:=true
```

### 4.4 人脸拍照加分项

终端 1：

```bash
source /opt/ros/noetic/setup.bash
source /home/zyz/catkin_ws/devel/setup.bash
roslaunch wpr_simulation wpb_single_face.launch
```

终端 2：

```bash
source /opt/ros/noetic/setup.bash
source /home/zyz/catkin_ws/devel/setup.bash
roslaunch image_pkg face_capture.launch
```

## 5. 验收关注点

- `hsv_node.py` 能看到实时原图、HSV 视图和 Mask 结果。
- 目标存在时日志输出中心坐标；目标消失时明确提示未检测到。
- `follow_node.py` 目标偏左/偏右时，角速度方向正确。
- 目标接近图像中心时，角速度逐渐减小。
- 丢失目标时 `/cmd_vel` 回到 0。
- `face_capture_node.py` 能稳定框出最大人脸。
- 机器人能朝人脸转向并适当前进。
- 达到居中稳定条件后自动保存 3 张照片。

## 6. 输出目录

默认照片保存目录：

```bash
$(rospack find image_pkg)/output/face_capture
```

如需修改，可在 `face_capture.launch` 中覆盖 `save_dir` 参数。
