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
    rviz_arg = DeclareLaunchArgument(
        'rviz',
        default_value='true',
        description='Whether to launch RViz'
    )
    
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
    
    rviz_config = PathJoinSubstitution([
        pkg_share, 'rviz_cfg', 'fast_livo2.rviz'
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
    
    # RViz node
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz',
        arguments=['-d', rviz_config]
    )
    
    # Image transport republish node
    republish_node = Node(
        package='image_transport',
        executable='republish',
        name='republish',
        arguments=['compressed', 'in:=/left_camera/image', 'raw', 'out:=/left_camera/image'],
        output='screen',
        respawn=True
    )
    
    return LaunchDescription([
        rviz_arg,
        dataset_dir_arg,
        fastlivo_node,
        rviz_node,
        republish_node
    ]) 