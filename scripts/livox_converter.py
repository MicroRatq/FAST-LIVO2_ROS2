#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from livox_ros_driver2.msg import CustomMsg
from sensor_msgs.msg import PointCloud2, PointField
import numpy as np
import struct

class LivoxConverter(Node):
    def __init__(self):
        super().__init__('livox_converter')
        
        # 创建发布者和订阅者
        self.subscription = self.create_subscription(
            CustomMsg,
            '/livox/lidar',
            self.livox_callback,
            10
        )
        
        self.publisher = self.create_publisher(
            PointCloud2,
            '/livox/lidar/pointcloud2',
            10
        )
        
        self.get_logger().info('Livox转换节点已启动')
    
    def livox_callback(self, msg):
        try:
            # 创建PointCloud2消息
            cloud_msg = PointCloud2()
            cloud_msg.header = msg.header
            cloud_msg.header.frame_id = "camera_init"  # 设置frame_id
            
            # 设置点云字段
            cloud_msg.fields = [
                PointField(name='x', offset=0, datatype=PointField.FLOAT32, count=1),
                PointField(name='y', offset=4, datatype=PointField.FLOAT32, count=1),
                PointField(name='z', offset=8, datatype=PointField.FLOAT32, count=1),
                PointField(name='intensity', offset=12, datatype=PointField.FLOAT32, count=1),
            ]
            cloud_msg.point_step = 16  # 4 bytes per field * 4 fields
            cloud_msg.row_step = cloud_msg.point_step * len(msg.points)
            cloud_msg.is_dense = True
            
            # 转换点云数据
            point_data = []
            for point in msg.points:
                # 添加x, y, z, intensity
                point_data.extend(struct.pack('ffff', point.x, point.y, point.z, point.reflectivity))
            
            cloud_msg.data = point_data
            cloud_msg.height = 1
            cloud_msg.width = len(msg.points)
            
            # 发布转换后的点云
            self.publisher.publish(cloud_msg)
            self.get_logger().debug(f'转换了 {len(msg.points)} 个点')
            
        except Exception as e:
            self.get_logger().error(f'Livox转换错误: {str(e)}')

def main(args=None):
    rclpy.init(args=args)
    node = LivoxConverter()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main() 