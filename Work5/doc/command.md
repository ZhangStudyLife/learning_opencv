# Work4 启动命令（修复版）

本文件给出两种启动方式：
- 方式 A：分终端前台启动（最稳，推荐）
- 方式 B：单命令后台启动（便捷）

## 0) 编译（只需偶尔执行）

```bash
source /opt/ros/noetic/setup.bash
cd /home/zyz/catkin_ws
catkin_make
```

## 1) 方式 A：分终端前台启动（推荐）

先做一次预检（任意终端执行）：

```bash
source /opt/ros/noetic/setup.bash
rosnode list
```

- 如果 `rosnode list` 能返回节点列表，说明 ROS 主控已经在线：跳过“终端 1”，直接执行“终端 2”。
- 如果报错（如无法连接 master），再执行“终端 1”启动 roscore。

### 终端 1

```bash
source /opt/ros/noetic/setup.bash
roscore
```

### 终端 2

```bash
source /opt/ros/noetic/setup.bash
source /home/zyz/catkin_ws/devel/setup.bash
roslaunch wpr_simulation wpb_balls.launch
```

### 终端 3

```bash
source /opt/ros/noetic/setup.bash
source /home/zyz/catkin_ws/devel/setup.bash
roslaunch work4 work4_pipeline.launch
```

### 终端 4（实时画面验证）

```bash
source /opt/ros/noetic/setup.bash
rosrun image_view image_view image:=/kinect2/sd/image_color_rect
```

## 2) 方式 B：单命令后台启动

```bash
pkill -f roslaunch || true
pkill -f roscore || true
pkill -f rosmaster || true
pkill -f gzserver || true
pkill -f gzclient || true
sleep 2

source /opt/ros/noetic/setup.bash
source /home/zyz/catkin_ws/devel/setup.bash

nohup roscore >/tmp/work4_roscore.log 2>&1 &
sleep 2
nohup roslaunch wpr_simulation wpb_balls.launch >/tmp/work4_scene.log 2>&1 &
sleep 6
nohup roslaunch work4 work4_pipeline.launch >/tmp/work4_pipeline.log 2>&1 &
```

## 3) 启动后快速验证

```bash
source /opt/ros/noetic/setup.bash
timeout 6s rostopic info /kinect2/sd/image_color_rect
timeout 6s rostopic hz /kinect2/sd/image_color_rect
timeout 6s rostopic hz red_ball_vel
timeout 6s rostopic echo -n 10 /ball_detected
timeout 6s rostopic echo -n 10 /ball_position
timeout 6s rostopic echo -n 10 /cmd_vel
```

判定标准：
- `/kinect2/sd/image_color_rect` 有发布者和订阅者（至少有 image_view）
- 图像话题有帧率（通常约 20Hz）
- `red_ball_vel` 有帧率
- `/ball_detected` 能看到 True
- `/cmd_vel` 不是全 0

## 4) 一键停止

```bash
pkill -f "roslaunch wpr_simulation wpb_balls.launch" || true
pkill -f "roslaunch work4 work4_pipeline.launch" || true
pkill -f "rosrun image_view image_view" || true
pkill -f roscore || true
pkill -f rosmaster || true
pkill -f gzserver || true
pkill -f gzclient || true
```

## 5) 常见误解（重要）

1. `timeout` 命令结束后返回码通常是 124，不代表失败。
2. `rostopic hz` 在超时退出时常显示非 0 退出码，只要有频率输出就算成功。
3. `roscore` 如果提示 "already running"，说明主控已在线，不是项目失败；此时不要重启 roscore，继续执行后续终端命令即可。
4. 多次联调后如果状态混乱，先执行“4) 一键停止”，再从“1) 方式 A”按顺序重启。
