import os
import base64
import requests
from dotenv import load_dotenv

# 加载 .env 文件里的密码本
load_dotenv()

API_KEY = os.getenv("ALIYUN_API_KEY")
BASE_URL = os.getenv("ALIYUN_BASE_URL")
# ⚠️ 这里填入你在百炼控制台看到的模型名称，比如 qwen-vl-max
API_KEY = os.getenv("ALIYUN_API_KEY")
BASE_URL = os.getenv("ALIYUN_BASE_URL")

# ---> 在这里临时加一行，看看代码有没有读到正确的值 <---
print(f"当前读取到的Key是: [{API_KEY}]") 
print(f"当前读取到的URL是: [{BASE_URL}]")
MODEL_NAME = "glm-4v-flash" 

# 准备一张本地测试图片 (随便找一张你电脑里的图片，改一下下面的路径)
# 建议放在你的 ai_job 文件夹下，命名为 test.jpg
image_path = "test.jpg"

def encode_image(image_path):
    """把图片转成 base64 字符串"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def ask_vlm_about_image(image_path, prompt_text):
    """把图片发给云端大模型"""
    base64_image = encode_image(image_path)
    
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
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 256
    }
    
    print("正在请求云端大模型...")
    response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ 云端回复：")
        print(result['choices'][0]['message']['content'])
    else:
        print(f"\n❌ 请求失败，状态码：{response.status_code}")
        print(response.text)

if __name__ == "__main__":
    # 确保你的电脑里有一张名为 test.jpg 的图片，和这个脚本放在同一个目录
    if os.path.exists(image_path):
        ask_vlm_about_image(image_path, "请详细描述这张图片里的内容。")
    else:
        print(f"找不到图片：{image_path}。请随便找一张图片重命名为 test.jpg 放到同级目录下。")