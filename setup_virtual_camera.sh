#!/bin/bash

# SmartSafety PPE检测系统 - 虚拟摄像头设置脚本
# 这个脚本帮助用户设置虚拟摄像头设备

set -e

echo "=== SmartSafety 虚拟摄像头设置 ==="
echo

# 检查是否以root权限运行
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  需要root权限来加载内核模块"
    echo "请使用: sudo bash setup_virtual_camera.sh"
    exit 1
fi

# 检查系统是否支持v4l2loopback
echo "1. 检查系统环境..."
if ! command -v modprobe &> /dev/null; then
    echo "❌ modprobe 命令不可用"
    exit 1
fi

# 检查v4l2loopback模块是否可用
if ! modinfo v4l2loopback &> /dev/null; then
    echo "❌ v4l2loopback 内核模块未找到"
    echo "正在尝试安装..."
    
    # 尝试安装v4l2loopback
    if command -v apt-get &> /dev/null; then
        echo "使用 apt-get 安装..."
        apt-get update
        apt-get install -y v4l2loopback-dkms v4l2loopback-utils
    elif command -v yum &> /dev/null; then
        echo "使用 yum 安装..."
        yum install -y v4l2loopback
    else
        echo "❌ 无法自动安装v4l2loopback"
        echo "请手动安装v4l2loopback内核模块"
        exit 1
    fi
fi

# 卸载已存在的模块
echo "2. 清理现有模块..."
modprobe -r v4l2loopback 2>/dev/null || true

# 加载v4l2loopback模块
echo "3. 加载虚拟摄像头模块..."
modprobe v4l2loopback devices=1 video_nr=10 card_label="SmartSafety_Virtual_Camera" exclusive_caps=1

# 验证模块是否加载成功
if lsmod | grep -q v4l2loopback; then
    echo "✓ v4l2loopback 模块加载成功"
else
    echo "❌ v4l2loopback 模块加载失败"
    exit 1
fi

# 检查虚拟设备是否创建
if [ -e /dev/video10 ]; then
    echo "✓ 虚拟摄像头设备已创建: /dev/video10"
else
    echo "❌ 虚拟摄像头设备未创建"
    exit 1
fi

# 显示设备信息
echo
echo "4. 设备信息:"
v4l2-ctl --device=/dev/video10 --all 2>/dev/null || echo "v4l2-ctl 不可用，跳过详细信息"

# 创建测试视频流（可选）
echo
echo "5. 创建测试视频流..."
if command -v ffmpeg &> /dev/null; then
    echo "使用ffmpeg创建测试视频流..."
    # 创建一个简单的测试图案
    ffmpeg -f lavfi -i testsrc=duration=60:size=640x480:rate=30 -f v4l2 /dev/video10 &
    FFMPEG_PID=$!
    echo "✓ 测试视频流已启动 (PID: $FFMPEG_PID)"
    echo "  要停止测试流，请运行: kill $FFMPEG_PID"
else
    echo "⚠️  ffmpeg 未安装，跳过测试视频流创建"
    echo "  您可以手动安装: apt-get install ffmpeg"
fi

echo
echo "=== 设置完成 ==="
echo "✓ 虚拟摄像头已准备就绪"
echo "✓ 设备路径: /dev/video10"
echo "✓ 标签: SmartSafety_Virtual_Camera"
echo
echo "使用说明:"
echo "1. 在Web界面中选择'虚拟摄像头 (v4l2loopback)'"
echo "2. 点击'切换视频源'按钮"
echo "3. 系统应该能够检测到虚拟摄像头"
echo
echo "故障排除:"
echo "- 如果切换失败，请检查dmesg日志"
echo "- 确保没有其他程序占用虚拟设备"
echo "- 重启系统后需要重新运行此脚本"