import streamlit as st
import requests
from PIL import Image
import io

# 1. 设置网页标题和配置
st.set_page_config(page_title="端云协同AI视觉系统", page_icon="🤖")
st.title("📸 端云协同AI视觉分析系统")
st.write("基于 FastAPI + 多模态大模型 (GLM-4V)。请在下方拍照或上传图片，体验云端AI的深度理解能力。")

# FastAPI 后端地址
API_URL = "http://127.0.0.1:8000/analyze"

# 2. 提供两种上传方式：浏览器拍照 或 上传本地图片
option = st.radio("选择输入方式：", ("使用浏览器摄像头拍照", "上传本地图片"))

image_file = None
if option == "使用浏览器摄像头拍照":
    image_file = st.camera_input("请对准物体拍照")
else:
    image_file = st.file_uploader("上传一张图片", type=["jpg", "jpeg", "png"])

# 3. 如果用户提供了图片，就发送给 FastAPI 后端
if image_file is not None:
    # 将上传的文件转换成 OpenCV/PIL 能读的格式
    image = Image.open(image_file)
    
    # 显示用户输入的图片
    st.image(image, caption="原始输入图片", use_container_width=True)
    
    # 把图片转成字节流，准备发送给后端
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG')
    img_bytes = img_byte_arr.getvalue()
    
    # 构造 multipart/form-data 请求
    files = {'file': ('image.jpg', img_bytes, 'image/jpeg')}
    
    with st.spinner("正在通过 FastAPI 发送给云端大模型分析，请稍候..."):
        try:
            # 调用 FastAPI 后端接口
            response = requests.post(API_URL, files=files, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "success":
                    st.success("分析成功！")
                    # 用醒目的大字显示云端返回的文本
                    st.markdown(f"### 🤖 云端大模型反馈：\n**{result.get('description')}**")
                else:
                    st.error(f"云端分析出错：{result.get('message')}")
            else:
                st.error(f"请求后端失败，状态码：{response.status_code}")
        except Exception as e:
            st.error(f"无法连接到 FastAPI 后端，请确认后端服务是否已启动。错误信息：{e}")

# 4. 页面底部的小提示
st.markdown("---")
st.caption("架构说明：Streamlit (前端 UI) ➡️ FastAPI (本地后端) ➡️ 智谱 GLM-4V (云端大模型)")