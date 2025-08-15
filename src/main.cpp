#include "LIVMapper.h"
#include <rclcpp/rclcpp.hpp>
#include <image_transport/image_transport.hpp>

int main(int argc, char **argv)
{
  rclcpp::init(argc, argv);
  auto node = std::make_shared<rclcpp::Node>("laserMapping");
  image_transport::ImageTransport it(node);
  LIVMapper mapper(node); 
  mapper.initializeSubscribersAndPublishers(node, it);
  std::cout << "LIVMapper initialized" << std::endl;
  mapper.run();
  rclcpp::shutdown();
  return 0;
}