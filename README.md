# FAST-LIVO2 ROS2

## 🛠️ 环境配置

### 系统要求
- **操作系统**: Ubuntu 22.04 LTS (Jammy Jellyfish)
- **ROS2版本**: ROS2 Humble
- **Python版本**: Python 3.10+

### 1. 基础依赖安装

```bash
# 更新系统包
sudo apt update

# 安装基础开发工具
sudo apt install -y \
  build-essential \
  cmake \
  git \
  wget \
  curl \
  unzip \
  pkg-config

# 安装ROS2 Humble基础包
sudo apt install -y \
  ros-humble-ament-cmake-auto \
  ros-humble-ament-cmake-clang-format \
  ros-humble-ament-lint-auto \
  ros-humble-ament-cmake-copyright \
  ros-humble-ament-cmake-cppcheck \
  ros-humble-ament-cmake-cpplint \
  ros-humble-ament-cmake-lint-cmake \
  ros-humble-ament-cmake-xmllint
```

### 2. 核心库安装

```bash
# 安装PCL、Eigen3、OpenCV
sudo apt install -y \
  libpcl-dev \
  libeigen3-dev \
  libopencv-dev

# 安装图像传输插件（解决RViz兼容性问题）
sudo apt install -y \
  ros-humble-image-transport-plugins \
  ros-humble-compressed-image-transport \
  ros-humble-compressed-depth-image-transport

# 安装其他ROS2依赖
sudo apt install -y \
  ros-humble-tf2-ros \
  ros-humble-tf2-geometry-msgs \
  ros-humble-pcl-conversions \
  ros-humble-cv-bridge \
  ros-humble-image-transport \
  ros-humble-nav-msgs \
  ros-humble-sensor-msgs \
  ros-humble-geometry-msgs \
  ros-humble-visualization-msgs
```

### 3. Sophus库安装

```bash
# 克隆Sophus库
git clone https://github.com/strasdat/Sophus.git
cd Sophus
git checkout a621ff

# 修改so2.cpp文件（解决编译问题）
# 在 Sophus/sophus/so2.cpp 中添加：
# SO2::SO2()
# {
#   unit_complex_.real(1.);
#   unit_complex_.imag(0.);
# }

# 编译安装
mkdir build && cd build
cmake ..
make -j$(nproc)
sudo make install
```

### 4. Livox-SDK2安装

```bash
# 克隆Livox-SDK2
git clone https://github.com/Livox-SDK/Livox-SDK2.git
cd Livox-SDK2

# 编译安装
mkdir build && cd build
cmake .. && make -j$(nproc)
sudo make install
```

**注意**: 对于Ubuntu 24.04，需要在以下文件中添加 `#include <cstdint>`:
- `Livox-SDK2/sdk_core/logger_handler/file_manager.h`
- `Livox-SDK2/sdk_core/comm/define.h`

### 5. livox_ros_driver2安装

#### Ubuntu 22.04 (推荐)
```bash
# 安装PCL ROS包
sudo apt install -y libpcl-dev ros-humble-pcl-ros

# 创建工作空间并克隆驱动
mkdir -p ~/catkin_ws/src
cd ~/catkin_ws/src/
git clone https://github.com/Livox-SDK/livox_ros_driver2.git
cd livox_ros_driver2

# 编译安装
./build.sh humble
```

#### Ubuntu 24.04
```bash
# 安装PCL ROS包
sudo apt install -y libpcl-dev ros-jazzy-pcl-ros

# 创建工作空间并克隆驱动
mkdir -p ~/catkin_ws/src
cd ~/catkin_ws/src/
git clone https://github.com/Livox-SDK/livox_ros_driver2.git
cd livox_ros_driver2

# 编译安装
./build.sh humble
```

### 6. 环境配置验证

```bash
# 检查ROS2环境
ros2 --version

# 检查关键依赖
pkg-config --modversion eigen3
pkg-config --modversion opencv4
pkg-config --modversion pcl_common

# 检查图像传输插件
ros2 run image_transport list_transports
```

## 🚀 快速开始

### 使用方法
```bash
./scripts/run_offline_dataset.sh [dataset_path] [visualization_type]
```

### 参数说明
- `dataset_path`: 数据集目录路径（必需）
- `visualization_type`: 可视化类型（可选，默认：rviz）
  - `rviz`: 纯RViz可视化（仅显示原始数据）
  - `full`: 完整FAST-LIVO2系统（SLAM + RViz）
  - `quick`: 快速测试（仅FAST-LIVO2，无可视化）

### 使用示例
```bash
# RViz可视化（默认）
./scripts/run_offline_dataset.sh ~/ros2_dataset

# 完整FAST-LIVO2系统
./scripts/run_offline_dataset.sh ~/ros2_dataset full

# 快速测试
./scripts/run_offline_dataset.sh ~/ros2_dataset quick
```

## 📊 支持的数据集格式

- **LiDAR**: `/livox/lidar` (livox_ros_driver2/msg/CustomMsg)
- **Camera**: `/left_camera/image/compressed` (sensor_msgs/msg/CompressedImage)
- **IMU**: `/livox/imu` (sensor_msgs/msg/Imu)

## 🔧 可视化模式说明

### rviz 模式
- 仅启动RViz显示原始传感器数据
- 自动转换Livox消息为PointCloud2格式
- 自动转换压缩图像为原始图像
- 不运行FAST-LIVO2 SLAM算法
- 适合数据检查和调试

### full 模式
- 启动完整的FAST-LIVO2 SLAM系统
- 包含RViz可视化
- 运行SLAM算法进行建图和定位
- 适合完整的SLAM评估

### quick 模式
- 仅运行FAST-LIVO2 SLAM算法
- 无GUI可视化
- 适合性能测试和算法调试

## ⚠️ 注意事项

1. 确保ROS2环境已正确设置
2. 确保livox_ros_driver2已安装
3. 数据集目录必须包含.db3文件
4. RViz模式需要GUI环境
5. 首次运行可能需要较长时间编译依赖

## 🎯 预期结果

- **rviz模式**: 显示原始点云和图像数据
- **full模式**: 显示SLAM建图结果和轨迹
- **quick模式**: 终端输出SLAM处理信息

