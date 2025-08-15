#!/bin/bash

# FAST-LIVO2 离线数据集测试脚本
# 使用方法: ./run_offline_dataset.sh [dataset_path] [visualization_type]
# visualization_type: rviz/full/quick

# 设置颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查参数
if [ $# -lt 1 ]; then
    echo -e "${RED}错误: 缺少参数${NC}"
    echo -e "${YELLOW}使用方法: $0 [dataset_path] [visualization_type]${NC}"
    echo -e "${YELLOW}visualization_type: rviz/full/quick (默认: rviz)${NC}"
    echo -e "${YELLOW}示例: $0 ~/ros2_dataset rviz${NC}"
    exit 1
fi

# 参数解析
DATASET_DIR="$1"
VISUALIZATION_TYPE=${2:-"rviz"}  # 默认为rviz

echo -e "${BLUE}=== FAST-LIVO2 离线数据集测试 ===${NC}"
echo -e "${GREEN}数据集目录: ${DATASET_DIR}${NC}"
echo -e "${GREEN}可视化类型: ${VISUALIZATION_TYPE}${NC}"

# 检查数据集目录是否存在
if [ ! -d "${DATASET_DIR}" ]; then
    echo -e "${RED}错误: 找不到数据集目录 ${DATASET_DIR}${NC}"
    exit 1
fi

# 检查目录中是否有.db3文件
DB3_FILE=$(find "${DATASET_DIR}" -name "*.db3" | head -1)
if [ -z "$DB3_FILE" ]; then
    echo -e "${RED}错误: 在目录 ${DATASET_DIR} 中找不到.db3文件${NC}"
    exit 1
fi

echo -e "${GREEN}找到数据集文件: ${DB3_FILE}${NC}"

# 设置ROS2环境
echo -e "${BLUE}设置ROS2环境...${NC}"
source /opt/ros/humble/setup.sh
source ~/livox_ws/install/setup.sh
source ~/catkin_ws/install/setup.sh

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 根据可视化类型选择启动方式
case $VISUALIZATION_TYPE in
    "rviz")
        echo -e "${GREEN}启动RViz可视化模式...${NC}"
        
        # 启动TF发布节点
        echo "启动TF发布节点..."
        python3 "${SCRIPT_DIR}/tf_publisher.py" &
        TF_PID=$!
        
        # 启动图像转换节点
        echo "启动图像转换节点..."
        python3 "${SCRIPT_DIR}/image_converter.py" &
        CONVERTER_PID=$!
        
        # 启动Livox转换节点
        echo "启动Livox转换节点..."
        python3 "${SCRIPT_DIR}/livox_converter.py" &
        LIVOX_PID=$!
        
        # 等待转换节点启动
        sleep 3
        
        # 启动bag播放
        echo "启动bag播放..."
        ros2 bag play "${DATASET_DIR}" --rate 0.5 &
        BAG_PID=$!
        
        # 等待bag开始播放
        sleep 3
        
        # 检查topic
        echo "检查topic:"
        ros2 topic list
        
        # 启动时间戳监控节点
        echo "启动时间戳监控节点..."
        python3 "${SCRIPT_DIR}/timestamp_monitor.py" &
        TIMESTAMP_MONITOR_PID=$!
        
        # 启动数据流调试节点
        echo "启动数据流调试节点..."
        python3 "${SCRIPT_DIR}/debug_data_flow.py" &
        DATA_FLOW_DEBUG_PID=$!
        
        # 启动RViz
        echo "启动RViz..."
        ros2 run rviz2 rviz2 -d "${SCRIPT_DIR}/../rviz_cfg/dataset.rviz" &
        RVIZ_PID=$!
        
        echo -e "${GREEN}RViz已启动，使用预配置的dataset.rviz配置文件${NC}"
        echo "配置已包含:"
        echo "- Fixed Frame: camera_init"
        echo "- PointCloud2: /livox/lidar/pointcloud2 (Decay Time: 30秒)"
        echo "- Image: /left_camera/image/raw"
        echo ""
        echo "时间戳监控正在后台运行，请查看终端输出"
        echo "按Ctrl+C停止测试"
        
        # 等待用户中断
        wait
        
        # 清理进程
        kill $BAG_PID $RVIZ_PID $CONVERTER_PID $TF_PID $LIVOX_PID $TIMESTAMP_MONITOR_PID $DATA_FLOW_DEBUG_PID 2>/dev/null || true
        ;;
        
    "full")
        echo -e "${GREEN}启动完整FAST-LIVO2模式...${NC}"
        
        # 启动FAST-LIVO2 + RViz
        ros2 launch fast_livo mapping_avia.launch.py dataset_dir:="${DATASET_DIR}" &
        LAUNCH_PID=$!
        
        # 等待一下让系统启动
        sleep 5
        
        # 启动bag播放
        echo "启动bag播放..."
        ros2 bag play "${DATASET_DIR}" &
        BAG_PID=$!
        
        echo -e "${GREEN}完整FAST-LIVO2系统已启动${NC}"
        echo "按Ctrl+C停止测试"
        
        # 等待用户中断
        wait
        
        # 清理进程
        kill $LAUNCH_PID $BAG_PID 2>/dev/null || true
        ;;
        
    "quick")
        echo -e "${GREEN}启动快速测试模式...${NC}"
        
        # 启动FAST-LIVO2（无RViz）
        ros2 launch fast_livo mapping_avia_simple.launch.py dataset_dir:="${DATASET_DIR}" &
        LAUNCH_PID=$!
        
        # 等待一下让系统启动
        sleep 5
        
        # 启动bag播放
        echo "启动bag播放..."
        ros2 bag play "${DATASET_DIR}" &
        BAG_PID=$!
        
        echo -e "${GREEN}快速测试模式已启动${NC}"
        echo "按Ctrl+C停止测试"
        
        # 等待用户中断
        wait
        
        # 清理进程
        kill $LAUNCH_PID $BAG_PID 2>/dev/null || true
        ;;
        
    *)
        echo -e "${RED}错误: 未知的可视化类型 '${VISUALIZATION_TYPE}'${NC}"
        echo -e "${YELLOW}支持的类型: rviz, full, quick${NC}"
        exit 1
        ;;
esac

echo -e "${GREEN}测试完成${NC}" 