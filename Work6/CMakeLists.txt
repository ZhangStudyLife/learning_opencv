cmake_minimum_required(VERSION 3.0.2)
project(image_pkg)

find_package(catkin REQUIRED COMPONENTS
  cv_bridge
  rospy
  sensor_msgs
  std_msgs
)

catkin_package(
  CATKIN_DEPENDS cv_bridge rospy sensor_msgs std_msgs
)

catkin_install_python(PROGRAMS
  src/get_pointcloud.py
  src/get_pointcloud3.py
  src/nearest_obstacle_final.py
  src/red_bottle_smart.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

install(DIRECTORY launch config doc output
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)
