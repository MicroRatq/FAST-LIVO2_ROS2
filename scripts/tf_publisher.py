#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TransformStamped
from tf2_ros import StaticTransformBroadcaster
import math

class TFPublisher(Node):
    def __init__(self):
        super().__init__('tf_publisher')
        
        # 创建静态TF广播器
        self.tf_broadcaster = StaticTransformBroadcaster(self)
        
        # 发布静态TF
        self.publish_static_transforms()
        
        self.get_logger().info('TF发布节点已启动')
    
    def publish_static_transforms(self):
        # 发布map到camera_init的转换
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'map'
        t.child_frame_id = 'camera_init'
        
        # 设置转换参数（单位矩阵）
        t.transform.translation.x = 0.0
        t.transform.translation.y = 0.0
        t.transform.translation.z = 0.0
        t.transform.rotation.x = 0.0
        t.transform.rotation.y = 0.0
        t.transform.rotation.z = 0.0
        t.transform.rotation.w = 1.0
        
        # 发布转换
        self.tf_broadcaster.sendTransform(t)
        self.get_logger().info('发布了map到camera_init的TF转换')

def main(args=None):
    rclpy.init(args=args)
    node = TFPublisher()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main() 