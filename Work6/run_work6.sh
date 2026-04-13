#!/usr/bin/env bash
set -eo pipefail

source /opt/ros/noetic/setup.bash
source /home/zyz/catkin_ws/devel/setup.bash

export ROS_MASTER_URI="${ROS_MASTER_URI:-http://localhost:11311}"

roslaunch image_pkg work6_all.launch "$@"
