# 端云协同实时视觉分析系统 (Edge-Cloud Collaborative Visual Analysis System)

## 📖 项目简介
本项目是一个基于“端侧轻量推理 + 云端多模态大模型理解”的端云协同 AI 系统。旨在解决传统纯云端AI推理带来的高延迟、高带宽成本问题。

系统架构采用客户端-服务端（C/S）分离模式。端侧（客户端）通过摄像头捕捉画面，利用轻量级目标检测模型 YOLO11n 在本地进行毫秒级推理，仅将检测到的有效主体（如猫、香蕉等）裁剪并上传至后端。云端（服务端）基于 FastAPI 接收图像，通过异步请求调用多模态大模型（GLM-4V），实现对图像内容的深度理解并生成自然语言反馈。

## 🚀 核心功能
- **端侧实时检测**：基于 YOLO11n (仅6MB) 实现本地超低延迟目标检测，减少原始视频流带宽消耗。
- **数据管道传输**：端侧自动裁剪检测主体，通过 HTTP POST 请求（multipart/form-data）上传至 FastAPI 后端。
- **云端多模态推理**：后端通过 HTTPX 异步调用云端多模态大模型（GLM-4V），实现图像到文字的智能描述。
- **系统限流与防刷**：端侧实现防刷限流策略（3秒间隔限制），有效控制云端 API 调用成本。
- **密钥安全隔离**：使用 `.env` 文件隔离敏感 API Key，确保代码开源安全。

## 🛠️ 技术栈
- **端侧（Edge）**：Python, OpenCV, Ultralytics YOLO11n, Requests
- **后端（Backend）**：FastAPI, Uvicorn, HTTPX, Python-Multipart
- **云端模型（Cloud LLM）**：智谱 GLM-4V (多模态大模型 API)
- **工具与架构**：Git, Dotenv, 客户端-服务端 (C/S) 架构

## 🏗️ 系统架构图
```text
[摄像头] 
   ↓ (画面流)
[端侧 YOLO11n 推理] ——> 检测到物体，截取主体
   ↓ (HTTP POST /analyze，上传图片)
[FastAPI 后端服务] ——> 异步请求
   ↓ (HTTPX 异步调用)
[云端 GLM-4V 多模态大模型] 
   ↓ (返回文字描述)
[FastAPI 后端服务] ——> 返回 JSON
   ↓ (HTTP Response)
[端侧终端展示结果]
##运行效果
<img width="1324" height="1126" alt="image" src="https://github.com/user-attachments/assets/e18483eb-5d2d-4511-b80a-969d8ba3b771" />
