import os
import base64
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile

# 1. 加载环境变量
load_dotenv()
API_KEY = os.getenv("ALIYUN_API_KEY")
BASE_URL = os.getenv("ALIYUN_BASE_URL")
MODEL_NAME = "glm-4v-flash"

# 2. 创建 FastAPI 应用实例
app = FastAPI(title="端云协同AI后端服务")

# 3. 定义接口 (POST请求，路径为 /analyze)
@app.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    """
    接收端侧上传的图片，调用云端大模型分析，并返回文本结果。
    """
    # 读取上传的图片数据
    image_bytes = await file.read()
    
    # 转成 Base64 格式供 API 使用
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    
    # 构造请求头和数据
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

    # 使用 httpx 发送异步请求给智谱 API
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload, timeout=15.0)
        
        if response.status_code == 200:
            result = response.json()
            text_result = result['choices'][0]['message']['content']
            return {"status": "success", "description": text_result}
        else:
            return {"status": "error", "message": f"云端API错误: {response.status_code}"}
    except Exception as e:
        return {"status": "error", "message": f"网络异常: {str(e)}"}