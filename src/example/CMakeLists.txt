cmake_minimum_required(VERSION 3.0.2)
project(example)
find_package(catkin REQUIRED COMPONENTS
  rospy
  std_msgs
  utils
)

catkin_package(
#  INCLUDE_DIRS include
)

include_directories(
# include
  ${catkin_INCLUDE_DIRS}
)

file(GLOB PYTHON_FILES_TASK_1 "src/example/project_1/task_1/*.py")
file(GLOB PYTHON_FILES_TASK_2 "src/example/project_1/task_2/*.py")
file(GLOB PYTHON_FILES_TASK_3 "src/example/project_1/task_3/*.py")
file(GLOB PYTHON_FILES_TASK_4 "src/example/project_1/task_4/*.py")

list(APPEND ALL_PYTHON_FILES ${PYTHON_FILES_TASK_1} ${PYTHON_FILES_TASK_2} ${PYTHON_FILES_TASK_3} ${PYTHON_FILES_TASK_4})

catkin_install_python(PROGRAMS ${ALL_PYTHON_FILES} DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION})
