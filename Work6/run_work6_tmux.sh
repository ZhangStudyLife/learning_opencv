#!/usr/bin/env bash
set -eo pipefail

source /opt/ros/noetic/setup.bash
source /home/zyz/catkin_ws/devel/setup.bash

export ROS_MASTER_URI="${ROS_MASTER_URI:-http://localhost:11311}"

for session in work6_core work6_scene work6_pointcloud work6_detection work6_rviz; do
  tmux has-session -t "$session" 2>/dev/null && tmux kill-session -t "$session" || true
done

tmux new-session -d -s work6_core "bash -lc 'source /opt/ros/noetic/setup.bash && roscore'"
sleep 5

tmux new-session -d -s work6_scene "bash -lc 'source /opt/ros/noetic/setup.bash && source /home/zyz/catkin_ws/devel/setup.bash && export ROS_MASTER_URI=http://localhost:11311 && roslaunch --wait image_pkg wpr_bottles.launch'"
sleep 8

tmux new-session -d -s work6_pointcloud "bash -lc 'source /opt/ros/noetic/setup.bash && source /home/zyz/catkin_ws/devel/setup.bash && export ROS_MASTER_URI=http://localhost:11311 && roslaunch --wait image_pkg work6_pointcloud.launch'"
sleep 3

tmux new-session -d -s work6_detection "bash -lc 'source /opt/ros/noetic/setup.bash && source /home/zyz/catkin_ws/devel/setup.bash && export ROS_MASTER_URI=http://localhost:11311 && roslaunch --wait image_pkg work6_detection.launch'"
sleep 2

tmux new-session -d -s work6_rviz "bash -lc 'source /opt/ros/noetic/setup.bash && source /home/zyz/catkin_ws/devel/setup.bash && export ROS_MASTER_URI=http://localhost:11311 && roslaunch --wait image_pkg work6_rviz.launch'"

echo "Work6 tmux 会话已启动："
tmux ls
