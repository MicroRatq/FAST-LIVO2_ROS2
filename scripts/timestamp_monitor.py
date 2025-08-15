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

class TimestampMonitor(Node):
    def __init__(self):
        super().__init__('timestamp_monitor')
        
        # 存储最新的时间戳
        self.latest_timestamps = {
            'livox_raw': None,
            'image_compressed': None,
            'imu': None,
            'pointcloud2': None,
            'image_raw': None
        }
        
        # 存储时间戳历史（用于分析）
        self.timestamp_history = {
            'livox_raw': deque(maxlen=100),
            'image_compressed': deque(maxlen=100),
            'imu': deque(maxlen=100),
            'pointcloud2': deque(maxlen=100),
            'image_raw': deque(maxlen=100)
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
        
        # 创建定时器，每秒打印一次时间戳信息
        self.timer = self.create_timer(1.0, self.print_timestamps)
        
        self.get_logger().info('时间戳监控节点已启动')
        
    def livox_callback(self, msg):
        """Livox原始数据回调"""
        timestamp = msg.header.stamp.sec + msg.header.stamp.nanosec / 1e9
        self.latest_timestamps['livox_raw'] = timestamp
        self.timestamp_history['livox_raw'].append(timestamp)
        
    def image_compressed_callback(self, msg):
        """压缩图像回调"""
        timestamp = msg.header.stamp.sec + msg.header.stamp.nanosec / 1e9
        self.latest_timestamps['image_compressed'] = timestamp
        self.timestamp_history['image_compressed'].append(timestamp)
        
    def imu_callback(self, msg):
        """IMU数据回调"""
        timestamp = msg.header.stamp.sec + msg.header.stamp.nanosec / 1e9
        self.latest_timestamps['imu'] = timestamp
        self.timestamp_history['imu'].append(timestamp)
        
    def pointcloud2_callback(self, msg):
        """转换后点云回调"""
        timestamp = msg.header.stamp.sec + msg.header.stamp.nanosec / 1e9
        self.latest_timestamps['pointcloud2'] = timestamp
        self.timestamp_history['pointcloud2'].append(timestamp)
        
    def image_raw_callback(self, msg):
        """转换后图像回调"""
        timestamp = msg.header.stamp.sec + msg.header.stamp.nanosec / 1e9
        self.latest_timestamps['image_raw'] = timestamp
        self.timestamp_history['image_raw'].append(timestamp)
        
    def print_timestamps(self):
        """打印时间戳信息"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n=== 时间戳监控报告 ({current_time}) ===")
        
        # 打印最新时间戳
        print("📊 最新时间戳:")
        for topic, timestamp in self.latest_timestamps.items():
            if timestamp is not None:
                print(f"  {topic:20}: {timestamp:.6f}")
            else:
                print(f"  {topic:20}: 无数据")
        
        # 计算时间差
        print("\n⏱️  时间戳同步性分析:")
        if all(timestamp is not None for timestamp in self.latest_timestamps.values()):
            # 以图像时间戳为基准
            base_time = self.latest_timestamps['image_compressed']
            
            for topic, timestamp in self.latest_timestamps.items():
                if topic != 'image_compressed':
                    diff = timestamp - base_time
                    print(f"  {topic:20} 与图像时间差: {diff:+.3f}秒")
                    
                    # 检查时间差是否过大
                    if abs(diff) > 1.0:
                        print(f"    ⚠️  警告: 时间差过大!")
                    elif abs(diff) > 0.1:
                        print(f"    ⚠️  注意: 时间差较大")
                    else:
                        print(f"    ✅ 时间同步良好")
        else:
            print("  无法进行同步性分析 - 缺少某些传感器数据")
        
        # 统计信息
        print("\n📈 数据统计:")
        for topic, history in self.timestamp_history.items():
            if len(history) > 0:
                print(f"  {topic:20}: 收到 {len(history)} 条消息")
                if len(history) > 1:
                    # 计算频率
                    time_span = history[-1] - history[0]
                    if time_span > 0:
                        freq = (len(history) - 1) / time_span
                        print(f"    📊 频率: {freq:.2f} Hz")
            else:
                print(f"  {topic:20}: 无数据")
        
        print("=" * 50)

def main(args=None):
    rclpy.init(args=args)
    monitor = TimestampMonitor()
    
    try:
        rclpy.spin(monitor)
    except KeyboardInterrupt:
        print("\n时间戳监控已停止")
    finally:
        monitor.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main() 