#!/bin/bash

# SmartSafety PPE检测系统 - 摄像头快速启动脚本
# 这个脚本帮助用户快速设置和启动摄像头

set -e

echo "=== SmartSafety 摄像头快速启动向导 ==="
echo

# 检查当前摄像头状态
echo "1. 检查当前摄像头状态..."
if ls /dev/video* &>/dev/null; then
    echo "✓ 发现摄像头设备:"
    ls /dev/video* | sed 's/^/  /'
else
    echo "⚠️  未发现物理摄像头设备"
fi

# 检查测试视频文件
if [ -f "test_video.mp4" ]; then
    echo "✓ 测试视频文件已存在: test_video.mp4"
else
    echo "⚠️  测试视频文件不存在，正在创建..."
    python3 create_test_video.py
fi

# 提供选项
echo
echo "2. 选择摄像头解决方案:"
echo "   1) 使用测试视频文件 (推荐 - 无需额外设置)"
echo "   2) 设置虚拟摄像头 (需要root权限)"
echo "   3) 检查物理摄像头连接"
echo "   4) 查看详细解决方案"
echo "   5) 退出"
echo

read -p "请选择 (1-5): " choice

case $choice in
    1)
        echo "✓ 选择使用测试视频文件"
        echo "  请在Web界面中选择'测试视频文件'选项"
        echo "  然后点击'切换视频源'按钮"
        ;;
    2)
        echo "设置虚拟摄像头..."
        if [ "$EUID" -ne 0 ]; then 
            echo "⚠️  需要root权限，正在使用sudo..."
            sudo bash setup_virtual_camera.sh
        else
            bash setup_virtual_camera.sh
        fi
        ;;
    3)
        echo "检查物理摄像头连接..."
        echo "  1. 检查USB摄像头是否插入"
        echo "  2. 检查摄像头驱动是否加载"
        echo "  3. 检查权限设置"
        echo
        echo "运行诊断命令..."
        echo "--- USB设备列表 ---"
        lsusb | grep -i camera || echo "未发现USB摄像头设备"
        echo
        echo "--- 视频设备 ---"
        ls -la /dev/video* 2>/dev/null || echo "无视频设备"
        echo
        echo "--- 内核模块 ---"
        lsmod | grep -E "(uvcvideo|videodev)" || echo "相关内核模块未加载"
        ;;
    4)
        echo "查看详细解决方案..."
        if [ -f "CAMERA_SOLUTIONS.md" ]; then
            cat CAMERA_SOLUTIONS.md
        else
            echo "解决方案文档不存在"
        fi
        ;;
    5)
        echo "退出向导"
        exit 0
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo
echo "=== 启动建议 ==="
echo "1. 启动Flask应用: python3 app.py"
echo "2. 打开Web界面: http://localhost:3000"
echo "3. 在'摄像头设置'中选择合适的视频源"
echo "4. 点击'切换视频源'按钮"
echo
echo "如果仍然遇到问题，请查看CAMERA_SOLUTIONS.md获取详细帮助。"