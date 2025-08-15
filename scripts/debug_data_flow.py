#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CompressedImage, PointCloud2, Imu
from livox_ros_driver2.msg import CustomMsg
from std_msgs.msg import Header
import time
from datetime import datetime
import threading
from collections import deque

class DataFlowDebugger(Node):
    def __init__(self):
        super().__init__('data_flow_debugger')
        
        # 存储数据统计
        self.data_stats = {
            'livox_raw': {'count': 0, 'last_time': None, 'first_time': None},
            'image_compressed': {'count': 0, 'last_time': None, 'first_time': None},
            'imu': {'count': 0, 'last_time': None, 'first_time': None},
            'pointcloud2': {'count': 0, 'last_time': None, 'first_time': None},
            'image_raw': {'count': 0, 'last_time': None, 'first_time': None}
        }
        
        # 订阅原始话题
        self.livox_sub = self.create_subscription(
            CustomMsg, '/livox/lidar', self.livox_callback, 10)
        self.image_compressed_sub = self.create_subscription(
            CompressedImage, '/left_camera/image/compressed', self.image_compressed_callback, 10)
        self.imu_sub = self.create_subscription(
            Imu, '/livox/imu', self.imu_callback, 10)
        
        # 订阅转换后的话题
        self.pointcloud2_sub = self.create_subscription(
            PointCloud2, '/livox/lidar/pointcloud2', self.pointcloud2_callback, 10)
        self.image_raw_sub = self.create_subscription(
            Image, '/left_camera/image/raw', self.image_raw_callback, 10)
        
        # 创建定时器，每5秒打印一次统计信息
        self.timer = self.create_timer(5.0, self.print_stats)
        
        self.get_logger().info('数据流调试器已启动')
        
    def livox_callback(self, msg):
        """Livox原始数据回调"""
        timestamp = msg.header.stamp.sec + msg.header.stamp.nanosec / 1e9
        self.data_stats['livox_raw']['count'] += 1
        if self.data_stats['livox_raw']['first_time'] is None:
            self.data_stats['livox_raw']['first_time'] = timestamp
        self.data_stats['livox_raw']['last_time'] = timestamp
        
        # 检查点云数据
        if hasattr(msg, 'point_num'):
            self.get_logger().info(f'Livox数据: {msg.point_num} 个点, 时间戳: {timestamp:.6f}')
        else:
            self.get_logger().warn(f'Livox数据缺少point_num字段')
        
    def image_compressed_callback(self, msg):
        """压缩图像回调"""
        timestamp = msg.header.stamp.sec + msg.header.stamp.nanosec / 1e9
        self.data_stats['image_compressed']['count'] += 1
        if self.data_stats['image_compressed']['first_time'] is None:
            self.data_stats['image_compressed']['first_time'] = timestamp
        self.data_stats['image_compressed']['last_time'] = timestamp
        
        self.get_logger().info(f'压缩图像: 格式={msg.format}, 时间戳: {timestamp:.6f}')
        
    def imu_callback(self, msg):
        """IMU数据回调"""
        timestamp = msg.header.stamp.sec + msg.header.stamp.nanosec / 1e9
        self.data_stats['imu']['count'] += 1
        if self.data_stats['imu']['first_time'] is None:
            self.data_stats['imu']['first_time'] = timestamp
        self.data_stats['imu']['last_time'] = timestamp
        
    def pointcloud2_callback(self, msg):
        """转换后点云回调"""
        timestamp = msg.header.stamp.sec + msg.header.stamp.nanosec / 1e9
        self.data_stats['pointcloud2']['count'] += 1
        if self.data_stats['pointcloud2']['first_time'] is None:
            self.data_stats['pointcloud2']['first_time'] = timestamp
        self.data_stats['pointcloud2']['last_time'] = timestamp
        
        self.get_logger().info(f'转换后点云: {msg.width}x{msg.height} 点, 时间戳: {timestamp:.6f}')
        
    def image_raw_callback(self, msg):
        """转换后图像回调"""
        timestamp = msg.header.stamp.sec + msg.header.stamp.nanosec / 1e9
        self.data_stats['image_raw']['count'] += 1
        if self.data_stats['image_raw']['first_time'] is None:
            self.data_stats['image_raw']['first_time'] = timestamp
        self.data_stats['image_raw']['last_time'] = timestamp
        
        self.get_logger().info(f'转换后图像: {msg.width}x{msg.height}, 编码={msg.encoding}, 时间戳: {timestamp:.6f}')
        
    def print_stats(self):
        """打印统计信息"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n=== 数据流统计报告 ({current_time}) ===")
        
        for topic, stats in self.data_stats.items():
            print(f"📊 {topic:20}:")
            print(f"    消息数量: {stats['count']}")
            if stats['first_time'] is not None:
                print(f"    首次时间: {stats['first_time']:.6f}")
            if stats['last_time'] is not None:
                print(f"    最后时间: {stats['last_time']:.6f}")
                if stats['first_time'] is not None:
                    duration = stats['last_time'] - stats['first_time']
                    if duration > 0:
                        freq = stats['count'] / duration
                        print(f"    平均频率: {freq:.2f} Hz")
            print()
        
        # 检查数据流问题
        print("🔍 数据流问题诊断:")
        
        # 检查是否有数据
        no_data_topics = []
        for topic, stats in self.data_stats.items():
            if stats['count'] == 0:
                no_data_topics.append(topic)
        
        if no_data_topics:
            print(f"    ⚠️  无数据的话题: {', '.join(no_data_topics)}")
        else:
            print("    ✅ 所有话题都有数据")
        
        # 检查时间同步
        if all(stats['last_time'] is not None for stats in self.data_stats.values()):
            times = [stats['last_time'] for stats in self.data_stats.values()]
            max_time = max(times)
            min_time = min(times)
            time_diff = max_time - min_time
            
            if time_diff > 1.0:
                print(f"    ⚠️  时间同步问题: 最大时间差 {time_diff:.3f}秒")
            else:
                print(f"    ✅ 时间同步良好: 最大时间差 {time_diff:.3f}秒")
        
        print("=" * 50)

def main(args=None):
    rclpy.init(args=args)
    debugger = DataFlowDebugger()
    
    try:
        rclpy.spin(debugger)
    except KeyboardInterrupt:
        print("\n数据流调试器已停止")
    finally:
        debugger.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main() 