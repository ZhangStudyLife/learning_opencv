#!/bin/bash
# Test script to send cmd_vel commands manually

echo "Testing cmd_vel - Forward"
rostopic pub /cmd_vel geometry_msgs/Twist "linear:
  x: 1.0
  y: 0.0
  z: 0.0
angular:
  x: 0.0
  y: 0.0
  z: 0.0" -r 10 &
sleep 3
kill %1

echo "Testing cmd_vel - Left"
rostopic pub /cmd_vel geometry_msgs/Twist "linear:
  x: 0.0
  y: 1.0
  z: 0.0
angular:
  x: 0.0
  y: 0.0
  z: 0.0" -r 10 &
sleep 3
kill %1

echo "Testing cmd_vel - Stop"
rostopic pub /cmd_vel geometry_msgs/Twist "linear:
  x: 0.0
  y: 0.0
  z: 0.0
angular:
  x: 0.0
  y: 0.0
  z: 0.0" -r 10 &
sleep 1
kill %1

echo "Done"
