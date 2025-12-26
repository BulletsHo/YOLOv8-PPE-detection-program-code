# SmartSafety PPE检测系统 - 摄像头开启解决方案

## 问题分析
当前系统显示"Demo Mode - No Camera"，原因是：
- 容器环境中没有检测到物理摄像头设备（/dev/video* 不存在）
- 系统缺少视频4linux工具支持
- 运行在虚拟化环境中，无法直接访问主机摄像头

## 解决方案

### 方案1：使用虚拟摄像头（推荐）
安装v4l2loopback创建虚拟摄像头设备：

```bash
# 安装v4l2loopback
sudo apt-get update
sudo apt-get install v4l2loopback-dkms v4l2loopback-utils

# 创建虚拟摄像头
sudo modprobe v4l2loopback devices=1 video_nr=10 card_label="Virtual Camera"

# 使用GStreamer或FFmpeg向虚拟摄像头推送视频
# 示例：推送测试视频
gst-launch-1.0 videotestsrc ! v4l2sink device=/dev/video10

# 或者推送本地视频文件
gst-launch-1.0 filesrc location=test_video.mp4 ! decodebin ! videoconvert ! v4l2sink device=/dev/video10
```

### 方案2：修改代码支持文件输入
修改app.py支持视频文件输入：

```python
# 在app.py中添加文件输入支持
VIDEO_SOURCE = "test_video.mp4"  # 可以是文件路径或URL
camera = cv2.VideoCapture(VIDEO_SOURCE)
```

### 方案3：使用网络摄像头
支持RTSP/HTTP网络摄像头流：

```python
# RTSP摄像头
camera = cv2.VideoCapture("rtsp://username:password@ip:port/stream")

# HTTP摄像头
camera = cv2.VideoCapture("http://ip:port/video")
```

### 方案4：使用USB摄像头（物理环境）
如果在物理机器上运行：

```bash
# 检查USB设备
lsusb

# 检查视频设备
ls -la /dev/video*

# 给予权限
sudo chmod 666 /dev/video0
```

## 快速实施步骤

### 步骤1：创建虚拟摄像头
```bash
sudo apt-get update
sudo apt-get install v4l2loopback-dkms
sudo modprobe v4l2loopback devices=1 video_nr=10
```

### 步骤2：准备测试视频
创建一个简单的测试视频或使用现有视频文件。

### 步骤3：修改代码配置
修改app.py中的摄像头索引：
```python
camera = cv2.VideoCapture(10)  # 使用虚拟摄像头
```

### 步骤4：重启应用
```bash
python app.py
```

## 验证步骤
1. 检查虚拟摄像头是否创建成功：`ls -la /dev/video10`
2. 检查视频流是否正常：使用`v4l2-ctl --device=/dev/video10 --all`
3. 在Web界面查看是否显示实时画面而非demo模式

## 故障排除
- 如果modprobe失败，检查内核模块是否可用
- 确保用户有权限访问视频设备
- 检查是否有其他程序占用了摄像头
- 验证视频文件格式是否被OpenCV支持