import os
import cv2
import base64
import requests
from dotenv import load_dotenv
from ultralytics import YOLO

# 加载 .env 文件
load_dotenv()
API_KEY = os.getenv("ALIYUN_API_KEY")
BASE_URL = os.getenv("ALIYUN_BASE_URL")
MODEL_NAME = "glm-4v-flash" # 你之前测试成功的模型名字

# 加载 YOLO 模型
print("正在加载 YOLO 模型...")
model = YOLO("yolo11n.pt")

# 打开摄像头
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("无法打开摄像头")
    exit()

print("✅ 摄像头已打开！检测到目标后，会自动发送给云端。按 'q' 键退出。")

def ask_cloud_about_image(frame):
    """把帧转成base64，发给云端大模型"""
    # 把图片压缩成 jpg 格式，减少上传带宽
    _, buffer = cv2.imencode('.jpg', frame)
    base64_image = base64.b64encode(buffer).decode('utf-8')

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "你是一个AI视觉助手。请简要描述这张图片里的物体。不超过20个字。"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }
        ],
        "max_tokens": 100
    }

    try:
        # 增加超时时间，因为上传图片需要时间
        response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            return f"云端错误: {response.status_code}"
    except Exception as e:
        return f"网络异常: {str(e)}"

last_cloud_call = 0 # 用来控制云端请求频率，防止刷屏

while True:
    ret, frame = cap.read()
    if not ret: break

    # 本地 YOLO 推理
    results = model(frame, verbose=False)
    annotated_frame = results[0].plot()

    # 检查画面里有没有检测到物体
    boxes = results[0].boxes
    if len(boxes) > 0:
        # 获取当前时间，每 3 秒才允许调用一次云端，避免请求爆炸
        current_time = cv2.getTickCount() / cv2.getTickFrequency()
        if current_time - last_cloud_call > 3.0:
            # 裁剪出检测到的第一个物体
            box = boxes[0].xyxy[0].cpu().numpy()
            x1, y1, x2, y2 = map(int, box)
            cropped_img = frame[y1:y2, x1:x2]
            
            if cropped_img.size > 0:
                print("\n检测到物体，正在上传云端分析...")
                cloud_result = ask_cloud_about_image(cropped_img)
                print(f"云端大模型反馈: {cloud_result}")
                last_cloud_call = current_time

    cv2.imshow("Edge-Cloud AI (Press 'q' to quit)", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()