cmake_minimum_required(VERSION 3.0.2)
project(work4)

find_package(catkin REQUIRED COMPONENTS
  cv_bridge
  geometry_msgs
  rospy
  sensor_msgs
  std_msgs
)

catkin_package(
  CATKIN_DEPENDS cv_bridge geometry_msgs rospy sensor_msgs std_msgs
)

catkin_install_python(PROGRAMS
  src/move_ball_random.py
  src/kinect_color_tracker.py
  src/ball_chase_controller.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

install(DIRECTORY launch config doc
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)
