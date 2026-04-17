#!/usr/bin/env bash
set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CATKIN_WS="/home/zyz/catkin_ws"
PACKAGE_LINK="${CATKIN_WS}/src/image_pkg"

source /opt/ros/noetic/setup.bash

if [[ ! -d "${CATKIN_WS}/src" ]]; then
  echo "未找到 catkin 工作区: ${CATKIN_WS}" >&2
  exit 1
fi

if [[ ! -e "${PACKAGE_LINK}" ]]; then
  echo "未找到 ROS 包链接: ${PACKAGE_LINK}" >&2
  exit 1
fi

PACKAGE_REALPATH="$(readlink -f "${PACKAGE_LINK}")"
if [[ "${PACKAGE_REALPATH}" != "${SCRIPT_DIR}" ]]; then
  echo "image_pkg 当前未指向 Work6: ${PACKAGE_REALPATH}" >&2
  echo "期望路径: ${SCRIPT_DIR}" >&2
  exit 1
fi

echo "[Work6] 开始编译 catkin 工作区..."
cd "${CATKIN_WS}"
catkin_make

source "${CATKIN_WS}/devel/setup.bash"

export ROS_MASTER_URI="${ROS_MASTER_URI:-http://localhost:11311}"

echo "[Work6] 启动作业主流程: Gazebo + 彩色点云 + RViz"
roslaunch image_pkg work6_all.launch "$@"
