#!/usr/bin/env bash
set -eo pipefail

for session in work6_rviz work6_detection work6_pointcloud work6_scene work6_core; do
  tmux has-session -t "$session" 2>/dev/null && tmux kill-session -t "$session" || true
done

echo "Work6 tmux 会话已停止。"
