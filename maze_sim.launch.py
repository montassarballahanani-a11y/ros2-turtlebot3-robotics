#!/usr/bin/env python3
"""ROS 2 Humble / Gazebo Classic TurtleBot3 Waffle maze simulation."""
import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    here = os.path.dirname(os.path.abspath(__file__))
    gazebo_share = get_package_share_directory('gazebo_ros')
    tb3_gazebo = get_package_share_directory('turtlebot3_gazebo')
    tb3_description = get_package_share_directory('turtlebot3_description')
    model_file = os.path.join(tb3_gazebo, 'models', 'turtlebot3_waffle', 'model.sdf')
    urdf_file = os.path.join(tb3_description, 'urdf', 'turtlebot3_waffle.urdf')
    with open(urdf_file, encoding='utf-8') as f:
        robot_description = f.read()
    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(gazebo_share, 'launch', 'gazebo.launch.py')),
            launch_arguments={'world': os.path.join(here, 'maze.world'), 'verbose': 'false'}.items()
        ),
        Node(package='robot_state_publisher', executable='robot_state_publisher',
             name='robot_state_publisher', output='screen',
             parameters=[{'robot_description': robot_description, 'use_sim_time': True}]),
        Node(package='gazebo_ros', executable='spawn_entity.py',
             arguments=['-entity', 'turtlebot3_waffle', '-file', model_file,
                        '-x', '-3.25', '-y', '-2.0', '-z', '0.01'], output='screen'),
    ])
