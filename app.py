from flask import Flask, Response, render_template, send_from_directory, request, jsonify
from dotenv import load_dotenv
from ultralytics import YOLO
import datetime
import time
import cv2
import subprocess
import numpy as np
import db
import fs
import threading
import socket
import signal
import sys
import os

SAMBA_MOUNT_POINT = '/mnt/samba'
load_dotenv()

# Create temporary directory for screenshots
os.makedirs('screenshots', exist_ok=True)

app = Flask(__name__)

# Camera configuration options
CAMERA_SOURCES = {
    'default': 0,           # Default camera
    'virtual': 10,          # Virtual camera (v4l2loopback)
    'file': 'test_video.mp4',  # Video file
    'usb': 1,               # USB camera
    'rtsp': 'rtsp://username:password@ip:port/stream',  # RTSP stream
    'http': 'http://ip:port/video'  # HTTP stream
}

# Try different camera sources
camera = None
camera_available = False
current_camera_source = None  # 添加缺失的全局变量
width, height, fps = 640, 480, 30

# Priority order for camera sources
camera_attempts = [
    ('default', CAMERA_SOURCES['default']),
    ('virtual', CAMERA_SOURCES['virtual']),
    ('file', CAMERA_SOURCES['file']),
]

print("Attempting to initialize camera...")

for source_name, source_value in camera_attempts:
    try:
        if source_name == 'file':
            # Check if file exists
            if not os.path.exists(source_value):
                print(f"Video file {source_value} not found, skipping...")
                continue
            camera = cv2.VideoCapture(source_value)
            print(f"Trying video file: {source_value}")
        else:
            camera = cv2.VideoCapture(source_value)
            print(f"Trying {source_name} camera (index: {source_value})")
        
        if camera.isOpened():
            # reduce buffer size
            camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            # Frame dimensions
            width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = camera.get(cv2.CAP_PROP_FPS)
            if fps == 0:  # Some sources return 0 FPS
                fps = 30
            
            print(f"✓ Camera initialized successfully!")
            print(f"  Source: {source_name}")
            print(f"  Frame dimensions: {width}x{height}, FPS: {fps}")
            camera_available = True
            break
        else:
            camera.release()
            camera = None
            print(f"✗ {source_name} camera failed to open")
            
    except Exception as e:
        print(f"✗ {source_name} camera error: {e}")
        if camera:
            camera.release()
            camera = None

if not camera_available:
    print("✗ All camera sources failed")
    print("Running in demo mode without camera")
    camera = None

# Load YOLO model (using a lightweight model for demo)
try:
    model = YOLO('yolov8n.pt')  # Using nano model for demo
    print("YOLO model loaded successfully")
except:
    print("Warning: YOLO model not found, using mock detection")
    model = None

now = datetime.datetime.now()
show_live_camera = True  # Flag to toggle between live camera and uploaded content
last_screenshot_time = time.time()  # Variable to track the last screenshot time
screenshot_interval = 5  # Set the interval for taking screenshots (in seconds)

def generate_frames():
    global last_screenshot_time
    while True:
        if camera_available and camera:
            # Read a frame from the webcam
            success, frame = camera.read()
            
            # If the camera is open
            if not success:
                # If camera fails, create a demo frame
                frame = create_demo_frame()
            else:
                # Use camera frame
                pass
        else:
            # Create demo frame when camera is not available
            frame = create_demo_frame()
        
        # Run object detection on the frame
        if model:
            results = model.predict(frame, conf=0.6, iou=0.8, imgsz=640, half=True, max_det=10, stream_buffer=True, agnostic_nms=True, vid_stride=12)
            
            # Perform detection
            if results and results[0].boxes:
                current_time = time.time()
                if current_time - last_screenshot_time >= screenshot_interval:
                    screenshot_thread = threading.Thread(target=take_screenshot, args=(results,))
                    screenshot_thread.start()
                    last_screenshot_time = current_time
                
                # Draw bounding boxes and labels on the frame
                detected_frame = results[0].plot()
                print(f"Detected classes: {results[0].boxes.cls.numpy()}")
            else:
                detected_frame = frame
        else:
            # Mock detection for demo
            detected_frame = frame.copy()
            cv2.putText(detected_frame, "Demo Mode - No Model Loaded", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Convert the frame to JPEG format
        ret, buffer = cv2.imencode('.jpg', detected_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        frame_bytes = buffer.tobytes()
        
        # Use a multipart response to continuously send frames
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

def create_demo_frame():
    """Create a demo frame when camera is not available"""
    # Create a blank frame
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Add some demo content
    cv2.rectangle(frame, (50, 50), (590, 430), (255, 255, 255), 2)
    cv2.putText(frame, "SmartSafety PPE Detection", (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, "Demo Mode - No Camera", (120, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
    cv2.putText(frame, "System Ready", (200, 250), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(frame, "Waiting for detections...", (150, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)
    
    # Add timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cv2.putText(frame, timestamp, (10, 470), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    return frame

def take_screenshot(results):
    '''Takes a Screenshot and saves it to a file server and its metadata in a database'''
    # Setting up screenshot and metadata
    hostname = socket.gethostname()
    current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    screenshot_fileLoc = f'screenshots/{hostname}_{current_time}.jpg'
    
    # temporary local storage location
    fileName = screenshot_fileLoc[len('screenshots/'):-len('.jpg')]
    
    # Create an array storing the frequencies of objects (PPE items)
    # For demo: person, bicycle, car, motorcycle, airplane, bus
    completeArr = [0, 1, 2, 3, 5, 7]
    
    if results and results[0].boxes:
        classArray = results[0].boxes.cls.numpy().copy()
        notFoundArr = np.setdiff1d(np.array(completeArr), np.array(classArray)).tolist()
        print("NOTFound" + str(notFoundArr))
        
        # Temporarily stores screenshot to local directory
        cv2.imwrite(screenshot_fileLoc, results[0].plot())
        
        # Add screenshot metadata to Database
        for value in notFoundArr:
            db.upload_metadata(fileName, 'screenshots', hostname, datetime.datetime.now(), int(value + 1))
    else:
        # Mock data for demo
        notFoundArr = [1, 3, 5]  # bicycle, motorcycle, bus not found
        cv2.imwrite(screenshot_fileLoc, np.zeros((480, 640, 3), dtype=np.uint8))
        print("NOTFound" + str(notFoundArr))
        
        # Add mock metadata to Database
        for value in notFoundArr:
            db.upload_metadata(fileName, 'screenshots', hostname, datetime.datetime.now(), int(value + 1))
    
    # Delete Excess Photos from temp directory
    try:
        os.remove(screenshot_fileLoc)
        empty_temp()
    except FileNotFoundError:
        print(f"File '{screenshot_fileLoc}' not found. Skipping removal.")
    except Exception as e:
        print(f"An error occurred: {e}")

def empty_temp():
    """Removes any pictures in temporary folder"""
    try:
        folder_name = "screenshots"
        folder_path = os.path.join(os.path.dirname(__file__), folder_name)
        if os.path.exists(folder_path):
            file_list = os.listdir(folder_path)
            for file_name in file_list:
                file_path = os.path.join(folder_path, file_name)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"Removed: {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

def cleanup():
    empty_temp()
    if camera_available and camera:
        camera.release()
    sys.exit(0)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        # A simple HTML page with an embedded video stream
        return render_template('index.html')
    elif request.method == 'POST':
        data = request.json
        # Process the received data
        print(data)
        return render_template('index.html', data=data), 200
    else:
        # Handle unexpected HTTP methods
        return jsonify({'status': 'failure'}), 405

@app.route('/video_feed')
def video_feed():
    # Stream the video feed as multipart content
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/updates')
def logs():
    try:
        data = db.get_all_detections()
        return render_template('updates.html', data=data)
    except:
        return render_template('updates.html', data=[])

@app.route('/logs')
def update():
    try:
        data = db.get_recent_detections(limit=15)
        return render_template('contents2.html', data=data)
    except:
        return render_template('contents2.html', data=[])

@app.route('/images/<path:filename>')
def serve_image(filename):
    try:
        return send_from_directory('screenshots', filename + ".jpg")
    except:
        return "Image not found", 404

@app.route('/camera_status')
def camera_status():
    """返回当前摄像头状态"""
    global camera_available, current_camera_source
    
    if camera_available and camera and camera.isOpened():
        status = f"摄像头已连接 ({current_camera_source})"
        status_type = "success"
    elif current_camera_source and current_camera_source != "demo":
        status = f"视频源: {current_camera_source}"
        status_type = "info"
    else:
        status = "演示模式 - 无摄像头"
        status_type = "warning"
    
    return jsonify({
        "status": status,
        "type": status_type,
        "source": current_camera_source,
        "available": camera_available
    })

@app.route('/switch_camera', methods=['POST'])
def switch_camera():
    """切换摄像头源"""
    global camera, camera_available, current_camera_source, width, height, fps
    
    try:
        data = request.get_json()
        new_source = data.get('source', 'demo')
        
        # 释放当前摄像头
        if camera and camera.isOpened():
            camera.release()
            camera = None
            camera_available = False
        
        # 根据源类型初始化
        if new_source == "demo":
            # 演示模式
            camera = None
            camera_available = False
            current_camera_source = "demo"
            width, height, fps = 640, 480, 30
            
        elif new_source == "test_video.mp4":
            # 测试视频文件
            if os.path.exists(new_source):
                camera = cv2.VideoCapture(new_source)
                if camera.isOpened():
                    camera_available = True
                    current_camera_source = new_source
                    width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    fps = camera.get(cv2.CAP_PROP_FPS) or 30
                    print(f"✓ 测试视频加载成功: {width}x{height} @ {fps}fps")
                else:
                    camera = None
                    camera_available = False
                    return jsonify({"success": False, "error": "无法打开测试视频文件"})
            else:
                return jsonify({"success": False, "error": "测试视频文件不存在"})
                
        elif new_source == "virtual":
            # 虚拟摄像头 (v4l2loopback)
            camera = cv2.VideoCapture(10)  # 通常虚拟设备在 /dev/video10
            if camera.isOpened():
                camera_available = True
                current_camera_source = "virtual"
                width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = camera.get(cv2.CAP_PROP_FPS) or 30
                print(f"✓ 虚拟摄像头连接成功: {width}x{height} @ {fps}fps")
            else:
                camera = None
                camera_available = False
                return jsonify({"success": False, "error": "无法连接虚拟摄像头，请先创建虚拟设备"})
                
        elif new_source in ["0", "1", "2"]:
            # 物理摄像头
            device_id = int(new_source)
            camera = cv2.VideoCapture(device_id)
            if camera.isOpened():
                camera_available = True
                current_camera_source = f"摄像头{device_id}"
                width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = camera.get(cv2.CAP_PROP_FPS) or 30
                print(f"✓ 物理摄像头连接成功: {width}x{height} @ {fps}fps")
                
                # 设置摄像头参数
                camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            else:
                camera = None
                camera_available = False
                return jsonify({"success": False, "error": f"无法打开摄像头设备{device_id}"})
        else:
            # 网络流或其他URL
            camera = cv2.VideoCapture(new_source)
            if camera.isOpened():
                camera_available = True
                current_camera_source = new_source
                width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = camera.get(cv2.CAP_PROP_FPS) or 30
                print(f"✓ 视频流连接成功: {width}x{height} @ {fps}fps")
            else:
                camera = None
                camera_available = False
                return jsonify({"success": False, "error": "无法连接到指定的视频源"})
        
        return jsonify({
            "success": True,
            "source": current_camera_source,
            "available": camera_available,
            "resolution": f"{width}x{height}",
            "fps": fps
        })
        
    except Exception as e:
        print(f"切换摄像头失败: {e}")
        return jsonify({"success": False, "error": str(e)})

# Run the Flask app
if __name__ == '__main__':
    signal.signal(signal.SIGTERM, cleanup)
    
    try:
        # Initialize database
        db.init_db()
        print("Database initialized")
        
        app.run(debug=True, threaded=True, host='0.0.0.0', port=3000)
    except KeyboardInterrupt:
        cleanup()