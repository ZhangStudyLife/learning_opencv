# work3：OpenCV 虚拟红球控制麦克纳姆小车

## 项目目标

`work3` 通过 OpenCV 产生一个“虚拟红色小球”，再把小球相对画面中心的归一化坐标映射成麦克纳姆小车的 `/cmd_vel`，最终在 Gazebo 中实时观察小车运动。

当前支持两种输入模式：

- `video`：读取 MP4 文件或摄像头画面，识别里面的红色小球
- `mouse`：打开一个鼠标操控台，鼠标悬停位置就是虚拟红球位置

控制公式固定为：

```text
linear.x = -norm_y * max_linear_speed
linear.y = -norm_x * max_linear_speed
angular.z = 0
```

## 节点结构

```text
video/mp4 或 mouse pad
    -> ball_detector.py
        -> /ball_position
        -> /ball_detected
        -> /camera/image_processed
    -> mecanum_controller.py
        -> /cmd_vel
    -> gazebo_ros_planar_move
        -> /odom + Gazebo base motion
    -> mecanum_visualizer.py
        -> OpenCV 监视窗口
```

## 运行方式

### 1. Gazebo 仿真 + MP4 红球控制

```bash
roslaunch work3 mecanum_sim.launch input_mode:=video video_file:=$(rospack find work3)/test_video.mp4
```

### 2. Gazebo 仿真 + 鼠标虚拟摇杆

```bash
roslaunch work3 mecanum_sim.launch input_mode:=mouse
```

鼠标模式说明：

- 会额外弹出一个 `work3 mouse pad` 操控台
- 鼠标停在哪里，红球就在哪里
- 鼠标停在中心附近时，小车会因为死区而接近停止
- 按 `q` 或 `Esc` 可以退出

### 3. 只调试控制链路，不启动 Gazebo

MP4 模式：

```bash
roslaunch work3 ball_control.launch input_mode:=video video_file:=$(rospack find work3)/test_video.mp4
```

鼠标模式：

```bash
roslaunch work3 ball_control.launch input_mode:=mouse
```

## 监视窗口

`work3 monitor` 会显示：

- 左侧：当前输入源图像
  - `video` 模式下是检测后的画面
  - `mouse` 模式下是虚拟操控台画面
- 右侧：麦克纳姆底盘与目标速度箭头
- 顶部：当前输入源、红球检测状态、归一化坐标、`cmd_vel`

## 主要文件

- `src/ball_detector.py`：统一输入源节点，支持 `video` / `mouse`
- `src/mecanum_controller.py`：将 `/ball_position` 映射成 `/cmd_vel`
- `src/mecanum_visualizer.py`：监视窗口
- `src/mecanum_logic.py`：公共纯逻辑函数
- `launch/mecanum_sim.launch`：Gazebo 仿真入口
- `launch/ball_control.launch`：本地调试入口

## 配置文件

### `config/hsv_red_range.yaml`

用于 `video` 模式红球检测：

- 红色 HSV 阈值
- 腐蚀/膨胀参数
- 最小半径
- 最小面积

### `config/control_params.yaml`

控制和显示参数：

- `max_linear_speed`
- `deadzone_x`
- `deadzone_y`
- `lost_timeout`
- `smoothing_alpha`
- `publish_rate`
- `refresh_rate`
- `frame_width`
- `frame_height`
- `mouse_ball_radius`

## 依赖安装

```bash
sudo apt install \
  ros-noetic-gazebo-plugins \
  ros-noetic-robot-state-publisher \
  ros-noetic-joint-state-publisher \
  ros-noetic-rviz \
  ros-noetic-tf
```

Python 依赖：

```bash
pip install -r requirements.txt
```

## 测试

```bash
python3 -m unittest discover -s tests -v
```

## Git 初始化建议

整个项目根目录目前建议作为 Git 仓库根：

```bash
cd ~/learning_opencv
git init
git add .
git commit -m "chore: initialize learning_opencv repository with current OpenCV and ROS baseline"
```

后续鼠标虚拟摇杆功能的提交信息建议：

```text
feat(work3): add mouse joystick mode for virtual red ball control
```
