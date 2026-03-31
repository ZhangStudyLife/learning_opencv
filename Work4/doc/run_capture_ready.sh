#!/usr/bin/env bash
set -u

source /opt/ros/noetic/setup.bash
source /home/zyz/catkin_ws/devel/setup.bash

# 1) 清理旧进程，避免端口和节点冲突
pkill -f "roslaunch wpr_simulation wpb_balls.launch" || true
pkill -f "roslaunch work4 work4_pipeline.launch" || true
pkill -f "rosrun image_view image_view" || true
pkill -f gzserver || true
pkill -f gzclient || true
sleep 2

# 2) 确保 roscore 在线
if ! rostopic list >/dev/null 2>&1; then
  nohup roscore >/tmp/work4_roscore.log 2>&1 &
  sleep 3
fi

# 3) 启动仿真场景
nohup roslaunch wpr_simulation wpb_balls.launch >/tmp/work4_scene.log 2>&1 &
sleep 8

# 4) 启动 Work4 管线
nohup roslaunch work4 work4_pipeline.launch >/tmp/work4_pipeline.log 2>&1 &
sleep 8

# 5) 拉起实时画面窗口
nohup rosrun image_view image_view image:=/kinect2/sd/image_color_rect >/tmp/work4_image_view.log 2>&1 &
sleep 3

# 6) 生成可截图证据文件
mkdir -p /tmp/work4_capture

{
  echo "===== [A] rostopic list (关键话题筛选) ====="
  rostopic list | grep -E "kinect2|ball_vel|ball_detected|ball_position|cmd_vel" || true
  echo
  echo "===== [B] 图像话题状态 ====="
  timeout 6s rostopic info /kinect2/sd/image_color_rect || true
  echo
  echo "===== [C] 图像话题频率 ====="
  timeout 6s rostopic hz /kinect2/sd/image_color_rect || true
  echo
  echo "===== [D] 四个小球速度话题频率（至少一项有频率即可截图） ====="
  timeout 6s rostopic hz /red_ball_vel || true
  timeout 6s rostopic hz /green_ball_vel || true
  timeout 6s rostopic hz /blue_ball_vel || true
  timeout 6s rostopic hz /orange_ball_vel || true
  echo
  echo "===== [E] 检测与控制输出 ====="
  timeout 6s rostopic echo -n 5 /ball_detected || true
  timeout 6s rostopic echo -n 5 /ball_position || true
  timeout 6s rostopic echo -n 5 /cmd_vel || true
} | tee /tmp/work4_capture/report_terminal_output.txt

cat <<'EOF'

已进入“可截图”状态，请按下面清单截图：
1) Gazebo 场景窗口（有四个球运动）
2) image_view 窗口（/kinect2/sd/image_color_rect）
3) 终端输出文件：/tmp/work4_capture/report_terminal_output.txt

如果要再次一键重来：
bash /home/zyz/learning_opencv/Work4/doc/run_capture_ready.sh
EOF
