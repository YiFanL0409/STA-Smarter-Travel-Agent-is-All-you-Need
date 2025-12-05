from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("DASHSCOPE_API_KEY") or os.getenv("OPENAI_API_KEY")
base_url = (
    os.getenv("DASHSCOPE_BASE_URL")
    or os.getenv("OPENAI_BASE_URL")
    or "https://dashscope.aliyuncs.com/compatible-mode/v1"
)
model = os.getenv("QWEN_MODEL") or "qwen-plus"

llm = ChatOpenAI(model=model, api_key=api_key, base_url=base_url, temperature=0.55)
