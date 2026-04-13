cmake_minimum_required(VERSION 3.0.2)
project(image_pkg)

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
  src/hsv_node.py
  src/follow_node.py
  src/face_capture_node.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

install(FILES
  src/image_pkg_common.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

install(DIRECTORY launch config doc output
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)
