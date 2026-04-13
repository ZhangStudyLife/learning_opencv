#!/usr/bin/env bash
set -eo pipefail

MODE="${1:-hsv}"
WORKSPACE_DIR="/home/zyz/catkin_ws"
REPORT_DIR="/tmp/image_pkg_capture"
ROSCORE_LOG="/tmp/image_pkg_roscore.log"
SCENE_LOG="/tmp/image_pkg_scene.log"
NODE_LOG="/tmp/image_pkg_node.log"
IMAGE_VIEW_LOG="/tmp/image_pkg_image_view.log"
VIEW_TOPIC=""
TOPIC_CANDIDATES=(
  "/kinect2/qhd/image_color_rect"
  "/kinect2/hd/image_color_rect"
  "/kinect2/sd/image_color_rect"
)

safe_source() {
  set +u
  # shellcheck disable=SC1090
  source "$1"
  set -u
}

safe_source /opt/ros/noetic/setup.bash

ensure_workspace_ready() {
  if [[ ! -f "${WORKSPACE_DIR}/devel/setup.bash" ]]; then
    (
      cd "${WORKSPACE_DIR}"
      catkin_make
    )
  fi

  safe_source "${WORKSPACE_DIR}/devel/setup.bash"

  if ! rospack find image_pkg >/dev/null 2>&1; then
    (
      cd "${WORKSPACE_DIR}"
      catkin_make
    )
    safe_source "${WORKSPACE_DIR}/devel/setup.bash"
  fi
}

cleanup() {
  pkill -f "roslaunch image_pkg hsv_demo.launch" || true
  pkill -f "roslaunch image_pkg follow_ball.launch" || true
  pkill -f "roslaunch image_pkg face_capture.launch" || true
  pkill -f "roslaunch image_pkg wpb_balls_headless.launch" || true
  pkill -f "roslaunch wpr_simulation wpb_balls.launch" || true
  pkill -f "roslaunch wpr_simulation wpb_single_face.launch" || true
  pkill -f "rosrun image_view image_view" || true
  pkill -f "hsv_node.py" || true
  pkill -f "follow_node.py" || true
  pkill -f "face_capture_node.py" || true
  pkill -f gzserver || true
  pkill -f gzclient || true
}

detect_active_image_topic() {
  python3 - "$@" <<'PY'
import sys
import rospy
from sensor_msgs.msg import Image

topics = sys.argv[1:]
rospy.init_node("image_pkg_topic_probe", anonymous=True, disable_signals=True)

for topic in topics:
    try:
        rospy.wait_for_message(topic, Image, timeout=3.0)
        print(topic)
        raise SystemExit(0)
    except Exception:
        continue

raise SystemExit(1)
PY
}

ensure_workspace_ready

if ! rostopic list >/dev/null 2>&1; then
  nohup roscore >"${ROSCORE_LOG}" 2>&1 &
  sleep 3
fi

cleanup
sleep 2

case "${MODE}" in
  hsv)
    SCENE_CMD="roslaunch image_pkg wpb_balls_headless.launch"
    NODE_CMD="roslaunch image_pkg hsv_demo.launch"
    ;;
  follow)
    SCENE_CMD="roslaunch image_pkg wpb_balls_headless.launch"
    NODE_CMD="roslaunch image_pkg follow_ball.launch run_ball_motion:=true"
    ;;
  face)
    SCENE_CMD="roslaunch wpr_simulation wpb_single_face.launch"
    NODE_CMD="roslaunch image_pkg face_capture.launch"
    ;;
  *)
    echo "未知模式: ${MODE}"
    echo "用法: bash /home/zyz/learning_opencv/Work5/doc/run_capture_ready.sh [hsv|follow|face]"
    exit 1
    ;;
esac

nohup bash -lc "${SCENE_CMD}" >"${SCENE_LOG}" 2>&1 &
sleep 8

if VIEW_TOPIC="$(detect_active_image_topic "${TOPIC_CANDIDATES[@]}" 2>/dev/null)"; then
  NODE_CMD="${NODE_CMD} image_topic:=${VIEW_TOPIC}"
else
  echo "未探测到活动图像话题，先别继续截图了。"
  echo "场景日志：${SCENE_LOG}"
  tail -n 80 "${SCENE_LOG}" || true
  exit 1
fi

nohup bash -lc "${NODE_CMD}" >"${NODE_LOG}" 2>&1 &
sleep 8

nohup rosrun image_view image_view image:="${VIEW_TOPIC}" >"${IMAGE_VIEW_LOG}" 2>&1 &
sleep 3

mkdir -p "${REPORT_DIR}"

{
  echo "===== [A] mode ====="
  echo "${MODE}"
  echo
  echo "===== [B] active image topic ====="
  echo "${VIEW_TOPIC}"
  echo
  echo "===== [B] rostopic list ====="
  rostopic list | grep -E "kinect2|ball_vel|cmd_vel" || true
  echo
  echo "===== [C] image topic info ====="
  timeout 6s rostopic info "${VIEW_TOPIC}" || true
  echo
  echo "===== [D] image topic hz ====="
  timeout 6s rostopic hz "${VIEW_TOPIC}" || true
  if [[ "${MODE}" != "hsv" ]]; then
    echo
    echo "===== [E] cmd_vel ====="
    timeout 6s rostopic echo -n 5 /cmd_vel || true
  else
    echo
    echo "===== [E] cmd_vel ====="
    echo "hsv 模式不检查 /cmd_vel。"
  fi
  if [[ "${MODE}" == "follow" ]]; then
    echo
    echo "===== [F] ball velocity topics ====="
    timeout 6s rostopic hz /red_ball_vel || true
    timeout 6s rostopic hz /green_ball_vel || true
    timeout 6s rostopic hz /blue_ball_vel || true
    timeout 6s rostopic hz /orange_ball_vel || true
  fi
  echo
  echo "===== [G] scene log tail ====="
  tail -n 40 "${SCENE_LOG}" || true
  echo
  echo "===== [H] node log tail ====="
  tail -n 40 "${NODE_LOG}" || true
  echo
  echo "===== [I] image_view log tail ====="
  tail -n 40 "${IMAGE_VIEW_LOG}" || true
} | tee "${REPORT_DIR}/report_terminal_output.txt"

cat <<EOF

已进入可截图状态，请截图以下内容：
1) image_view 窗口（${VIEW_TOPIC}）
2) HSV Detector 窗口（如果弹出来）
3) 终端输出文件：${REPORT_DIR}/report_terminal_output.txt

重新运行示例：
bash /home/zyz/learning_opencv/Work5/doc/run_capture_ready.sh hsv
bash /home/zyz/learning_opencv/Work5/doc/run_capture_ready.sh follow
bash /home/zyz/learning_opencv/Work5/doc/run_capture_ready.sh face
EOF
