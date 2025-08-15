#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage, Image
import cv2
import numpy as np
from cv_bridge import CvBridge

class ImageConverter(Node):
    def __init__(self):
        super().__init__('image_converter')
        
        # 创建CV bridge
        self.bridge = CvBridge()
        
        # 创建发布者和订阅者
        self.subscription = self.create_subscription(
            CompressedImage,
            '/left_camera/image/compressed',
            self.image_callback,
            10
        )
        
        self.publisher = self.create_publisher(
            Image,
            '/left_camera/image/raw',
            10
        )
        
        self.get_logger().info('图像转换节点已启动')
    
    def image_callback(self, msg):
        try:
            # 解码压缩图像
            np_arr = np.frombuffer(msg.data, np.uint8)
            cv_image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            
            if cv_image is not None:
                # 转换为ROS Image消息
                ros_image = self.bridge.cv2_to_imgmsg(cv_image, "bgr8")
                ros_image.header = msg.header
                
                # 发布原始图像
                self.publisher.publish(ros_image)
                self.get_logger().debug('图像转换成功')
            else:
                self.get_logger().warn('无法解码压缩图像')
                
        except Exception as e:
            self.get_logger().error(f'图像转换错误: {str(e)}')

def main(args=None):
    rclpy.init(args=args)
    node = ImageConverter()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main() 