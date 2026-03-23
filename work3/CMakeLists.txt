cmake_minimum_required(VERSION 3.0.2)
project(work3)

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
  src/ball_detector.py
  src/mecanum_controller.py
  src/mecanum_driver.py
  src/mecanum_visualizer.py
  src/mecanum_logic.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

install(DIRECTORY launch config urdf rviz
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)
