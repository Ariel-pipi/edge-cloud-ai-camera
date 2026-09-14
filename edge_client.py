import cv2
import requests
from ultralytics import YOLO

# 1. 加载 YOLO 模型
print("正在加载 YOLO 模型...")
model = YOLO("yolo11n.pt")

# 2. 打开摄像头
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("无法打开摄像头")
    exit()

print("✅ 摄像头已打开！按 'q' 键退出。")

# FastAPI 服务地址 (本地启动)
API_URL = "http://127.0.0.1:8000/analyze"

last_cloud_call = 0

while True:
    ret, frame = cap.read()
    if not ret: break

    # 本地 YOLO 推理
    results = model(frame, verbose=False)
    annotated_frame = results[0].plot()

    boxes = results[0].boxes
    if len(boxes) > 0:
        current_time = cv2.getTickCount() / cv2.getTickFrequency()
        if current_time - last_cloud_call > 3.0:
            box = boxes[0].xyxy[0].cpu().numpy()
            x1, y1, x2, y2 = map(int, box)
            cropped_img = frame[y1:y2, x1:x2]
            
            if cropped_img.size > 0:
                print("\n检测到物体，正在发送给 FastAPI 服务端...")
                
                # 把 OpenCV 的图像压缩成 jpg 字节流
                _, img_encoded = cv2.imencode('.jpg', cropped_img)
                img_bytes = img_encoded.tobytes()
                
                # 构造 multipart/form-data 请求发送给 FastAPI
                files = {'file': ('image.jpg', img_bytes, 'image/jpeg')}
                
                try:
                    # 调用本地 FastAPI 接口
                    response = requests.post(API_URL, files=files, timeout=15)
                    if response.status_code == 200:
                        result = response.json()
                        print(f"✅ 服务端返回: {result.get('description')}")
                    else:
                        print(f"❌ 服务端错误: {response.status_code}")
                except Exception as e:
                    print(f"❌ 无法连接到 FastAPI 服务: {e}")
                    
                last_cloud_call = current_time

    cv2.imshow("Edge Client (Press 'q' to quit)", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()