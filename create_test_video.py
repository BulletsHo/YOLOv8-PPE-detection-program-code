#!/usr/bin/env python3
"""
创建测试视频文件用于PPE检测系统
当没有物理摄像头时，可以使用这个视频文件作为输入源
"""

import cv2
import numpy as np
import os

def create_test_video():
    """创建一个包含模拟工作场景的测试视频"""
    
    # 视频参数
    width, height = 640, 480
    fps = 30
    duration = 60  # 60秒
    total_frames = fps * duration
    
    # 创建视频写入器
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter('test_video.mp4', fourcc, fps, (width, height))
    
    print("正在创建测试视频...")
    
    for frame_num in range(total_frames):
        # 创建空白帧
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # 添加背景渐变
        for y in range(height):
            color = int(50 + (y / height) * 100)
            frame[y, :] = [color, color, color + 20]
        
        # 添加模拟人物轮廓（简单矩形表示）
        person_x, person_y = width // 2 - 50, height // 2 - 100
        person_w, person_h = 100, 200
        
        # 人物身体
        cv2.rectangle(frame, (person_x, person_y), (person_x + person_w, person_y + person_h), (200, 150, 100), -1)
        
        # 安全帽（周期性显示）
        if (frame_num // 90) % 2 == 0:  # 每3秒切换一次
            cv2.ellipse(frame, (person_x + person_w//2, person_y - 10), (person_w//2, 20), 0, 0, 360, (255, 200, 0), -1)
            cv2.putText(frame, "Helmet: ON", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "Helmet: OFF", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # 反光背心（周期性显示）
        if (frame_num // 120) % 2 == 0:  # 每4秒切换一次
            cv2.rectangle(frame, (person_x + 20, person_y + 50), (person_x + person_w - 20, person_y + 100), (0, 255, 255), -1)
            cv2.putText(frame, "Vest: ON", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "Vest: OFF", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # 防护眼镜（周期性显示）
        if (frame_num // 150) % 2 == 0:  # 每5秒切换一次
            cv2.ellipse(frame, (person_x + person_w//2 - 15, person_y + 30), (15, 10), 0, 0, 360, (100, 200, 255), -1)
            cv2.ellipse(frame, (person_x + person_w//2 + 15, person_y + 30), (15, 10), 0, 0, 360, (100, 200, 255), -1)
            cv2.putText(frame, "Glasses: ON", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "Glasses: OFF", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # 添加时间戳
        timestamp = f"Frame: {frame_num}/{total_frames}"
        cv2.putText(frame, timestamp, (10, height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # 添加场景信息
        cv2.putText(frame, "Construction Site - Zone A", (width - 200, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # 写入帧
        out.write(frame)
        
        # 显示进度
        if frame_num % 30 == 0:
            print(f"进度: {frame_num}/{total_frames} 帧 ({100*frame_num/total_frames:.1f}%)")
    
    # 释放资源
    out.release()
    print("✓ 测试视频创建完成: test_video.mp4")
    print(f"  分辨率: {width}x{height}")
    print(f"  时长: {duration}秒")
    print(f"  帧率: {fps}fps")

if __name__ == "__main__":
    create_test_video()