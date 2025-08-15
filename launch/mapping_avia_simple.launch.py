#!/usr/bin/env python3

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # Get the package directory
    pkg_share = FindPackageShare('fast_livo')
    
    # Launch arguments
    dataset_dir_arg = DeclareLaunchArgument(
        'dataset_dir',
        default_value='',
        description='Dataset directory path'
    )
    
    # Load parameters
    avia_config = PathJoinSubstitution([
        pkg_share, 'config', 'avia.yaml'
    ])
    
    camera_config = PathJoinSubstitution([
        pkg_share, 'config', 'camera_pinhole.yaml'
    ])
    
    # Main node
    fastlivo_node = Node(
        package='fast_livo',
        executable='fastlivo_mapping',
        name='laserMapping',
        output='screen',
        parameters=[
            avia_config,
            camera_config
        ]
    )
    
    return LaunchDescription([
        dataset_dir_arg,
        fastlivo_node
    ]) 