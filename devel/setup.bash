#!/usr/bin/env bash
# generated from catkin/cmake/templates/setup.bash.in

CATKIN_SHELL=bash

# source setup.sh from same directory as this file
_CATKIN_SETUP_DIR=$(builtin cd "`dirname "${BASH_SOURCE[0]}"`" > /dev/null && pwd)
. "$_CATKIN_SETUP_DIR/setup.sh"


export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:/home/eric/project-status-1/src/models>
export ROS_PACKAGE_PATH=$ROS_PACKAGE_PATH:/home/eric/project-status-1/src
