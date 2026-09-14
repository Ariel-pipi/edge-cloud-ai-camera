import cv2
from ultralytics import YOLO

# 1. 加载 YOLO11n 模型 
print("正在加载 YOLO11n 模型...")
model = YOLO("yolo11n.pt") 

# 2. 打开电脑默认摄像头 (0代表默认摄像头)
print("正在打开摄像头...")
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ 无法打开摄像头，请检查是否被其他程序（如微信、腾讯会议）占用！")
    exit()

print("✅ 摄像头已打开，按 'q' 键退出画面。")

while True:
    # 3. 读取一帧画面
    ret, frame = cap.read()
    if not ret:
        print("无法获取画面，退出...")
        break

    # 4. 本地端侧推理 (让 YOLO 检测画面)
    results = model(frame, verbose=False)

    # 5. 把检测框和类别画在画面上
    annotated_frame = results[0].plot()

    # 6. 在屏幕上显示画面
    cv2.imshow("Edge YOLO Detection (Press 'q' to quit)", annotated_frame)

    # 7. 监听键盘，如果按下 'q' 键就退出循环
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 8. 释放摄像头并关闭窗口
cap.release()
cv2.destroyAllWindows()