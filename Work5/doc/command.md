# Work5 / image_pkg 启动命令

本文件统一记录 `Work5` 的运行方式。目录名仍然是 `Work5`，但 ROS 包名已经改为 `image_pkg`。

## 0. 推荐：一条命令直接拉起 HSV 调试

先执行这一条，别再手敲两终端那套了：

```bash
bash /home/zyz/learning_opencv/Work5/doc/run_capture_ready.sh
```

说明：

- 默认就是 `hsv` 模式，等价于 `bash /home/zyz/learning_opencv/Work5/doc/run_capture_ready.sh hsv`
- 脚本会自动清理旧 ROS/Gazebo 进程、必要时检查工作空间、后台启动无 GUI 的球场景、自动探测真正有图像的 `kinect2` 话题，并拉起 `hsv_demo` + `image_view`
- 终端里会直接打印诊断信息，同时把完整输出保存到 `/tmp/image_pkg_capture/report_terminal_output.txt`
- 你执行完以后，把“终端输出 + 实际窗口现象”一起发回来

常用一键模式：

```bash
bash /home/zyz/learning_opencv/Work5/doc/run_capture_ready.sh hsv
bash /home/zyz/learning_opencv/Work5/doc/run_capture_ready.sh follow
bash /home/zyz/learning_opencv/Work5/doc/run_capture_ready.sh face
```

## 1. 编译

```bash
source /opt/ros/noetic/setup.bash
cd /home/zyz/catkin_ws
catkin_make
source /home/zyz/catkin_ws/devel/setup.bash
rospack find image_pkg
```

## 2. 手动方式：HSV 取球演示

```bash
source /opt/ros/noetic/setup.bash
source /home/zyz/catkin_ws/devel/setup.bash
roslaunch image_pkg wpb_balls_headless.launch
roslaunch image_pkg hsv_demo.launch image_topic:=/kinect2/qhd/image_color_rect
```

可选验证：

```bash
rostopic info /kinect2/qhd/image_color_rect
rostopic hz /kinect2/qhd/image_color_rect
```

## 3. 手动方式：跟球演示

```bash
source /opt/ros/noetic/setup.bash
source /home/zyz/catkin_ws/devel/setup.bash
roslaunch image_pkg wpb_balls_headless.launch
roslaunch image_pkg follow_ball.launch image_topic:=/kinect2/qhd/image_color_rect run_ball_motion:=true
```

可选验证：

```bash
rostopic hz /red_ball_vel
rostopic echo -n 5 /cmd_vel
```

## 4. 手动方式：人脸拍照演示

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

查看照片：

```bash
source /opt/ros/noetic/setup.bash
source /home/zyz/catkin_ws/devel/setup.bash
ls "$(rospack find image_pkg)/output/face_capture"
```

## 5. 常用参数覆盖

切换图像话题：

```bash
roslaunch image_pkg hsv_demo.launch config:=/home/zyz/custom_hsv.yaml
roslaunch image_pkg follow_ball.launch config:=/home/zyz/custom_follow.yaml
roslaunch image_pkg face_capture.launch config:=/home/zyz/custom_face.yaml
```

关闭随机小球运动：

```bash
roslaunch image_pkg follow_ball.launch run_ball_motion:=false
```

覆盖拍照保存目录：

```bash
roslaunch image_pkg face_capture.launch save_dir:=/home/zyz/face_capture_output
```

## 6. 一键停止

```bash
pkill -f "roslaunch image_pkg wpb_balls_headless.launch" || true
pkill -f "roslaunch image_pkg hsv_demo.launch" || true
pkill -f "roslaunch image_pkg follow_ball.launch" || true
pkill -f "roslaunch image_pkg face_capture.launch" || true
pkill -f "roslaunch wpr_simulation wpb_balls.launch" || true
pkill -f "roslaunch wpr_simulation wpb_single_face.launch" || true
pkill -f "rosrun image_view image_view" || true
```
