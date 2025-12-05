# Travel Agent - 旅行规划助手

一个基于 Gradio 的智能旅行规划助手，支持通过 MCP (Model Context Protocol) 工具调用获取实时旅行信息，包括交通、航班、天气等数据。

## 功能特性

- 🤖 智能对话：基于大语言模型的自然语言交互
- 🛫 实时信息：通过 MCP 工具获取实时航班、交通、天气等信息
- 🌐 Web 界面：基于 Gradio 的友好用户界面
- 🔧 工具调用：支持多个 MCP 服务器，可扩展性强
- 📊 可视化：实时显示工具调用过程和结果

## 快速开始

### 前置要求

- Python 3.9 或更高版本
- DashScope API Key 或 OpenAI API Key

### 安装步骤

1. **克隆仓库**
```bash
git clone <repository-url>
cd Agent_V1.0
```

2. **创建虚拟环境**
```bash
python -m venv venv
```

3. **激活虚拟环境**

Windows:
```bash
venv\Scripts\activate
```

Linux/Mac:
```bash
source venv/bin/activate
```

4. **安装依赖**
```bash
pip install -r requirements.txt
```

5. **配置环境变量**

复制 `.env.example` 文件并重命名为 `.env`：
```bash
copy .env.example .env  # Windows
# 或
cp .env.example .env    # Linux/Mac
```

编辑 `.env` 文件，填入你的 API 密钥：
```env
DASHSCOPE_API_KEY=your_api_key_here
```

6. **运行应用**
```bash
python TAgent/agent.py
```

或者：
```bash
python -m TAgent.agent
```

7. **访问应用**

应用启动后，在浏览器中打开显示的地址（默认：http://127.0.0.1:7860）

## 配置说明

### 必需配置

- `DASHSCOPE_API_KEY` 或 `OPENAI_API_KEY`：API 密钥（至少配置一个）

### 可选配置

#### API 配置
- `DASHSCOPE_BASE_URL`：DashScope API 基础 URL（默认：https://dashscope.aliyuncs.com/compatible-mode/v1）
- `OPENAI_BASE_URL`：OpenAI API 基础 URL
- `QWEN_MODEL`：使用的模型名称（默认：qwen-plus）

#### MCP 服务器配置
如需启用 MCP 工具调用，需要配置以下环境变量：

- `ENABLE_MCP` 或 `DASHSCOPE_ENABLE_MCP`：设置为 `1` 或 `true` 启用 MCP
- `MCP_STREAM_TIMEOUT`：MCP 流式响应超时时间（秒，默认：8）

MCP 服务器 URL（根据需要配置）：
- `MCP_FETCH_URL`：数据获取服务器
- `MCP_NONAME_URL`：未命名服务器
- `MCP_FETCH2_URL`：数据获取服务器 2
- `MCP_TRANSPORT_URL`：交通信息服务器
- `MCP_AVIATION_URL`：航空信息服务器
- `MCP_BING_URL`：Bing 搜索服务器
- `MCP_ZHIPU_URL`：智谱服务器
- `MCP_CHART_URL`：图表服务器

#### 服务器配置
- `GRADIO_SERVER_PORT`：Gradio 服务器端口（默认：7860）

## 使用方法

1. 启动应用后，在浏览器中打开显示的地址
2. 在输入框中输入你的旅行相关问题，例如：
   - "帮我规划一次北京到上海的旅行"
   - "查询明天北京到上海的航班"
   - "北京今天的天气怎么样？"
3. 点击"发送"按钮或按 Enter 键
4. 查看助手回复和工具调用信息

## 项目结构

```
Agent_V1.0/
├── main.py                 # 主入口文件
├── TAgent/                 # 核心模块目录
│   ├── __init__.py
│   ├── agent.py           # 主应用逻辑
│   └── my_llm.py          # LLM 配置
├── requirements.txt        # 依赖列表
├── .env.example           # 环境变量示例
├── .gitignore             # Git 忽略文件
└── README.md              # 项目说明文档
```

## 依赖说明

主要依赖包：
- `openai`：OpenAI API 客户端
- `gradio`：Web UI 框架
- `langchain-openai`：LangChain OpenAI 集成
- `python-dotenv`：环境变量管理
- `langgraph`：LangGraph 工具（可选，用于 MCP）
- `langchain-mcp-adapter`：MCP 适配器（可选）

## 注意事项

1. **API 密钥安全**：请勿将 `.env` 文件提交到版本控制系统
2. **虚拟环境**：建议使用虚拟环境运行项目
3. **MCP 服务器**：MCP 功能需要配置相应的服务器 URL 才能使用
4. **端口占用**：如果默认端口被占用，应用会自动尝试其他端口

## 故障排除

### 端口被占用
如果 7860 端口被占用，应用会自动尝试 7861-7879 端口，或使用随机端口。

### MCP 工具无法使用
- 检查 `ENABLE_MCP` 或 `DASHSCOPE_ENABLE_MCP` 是否设置为 `1` 或 `true`
- 确认相应的 MCP 服务器 URL 已正确配置
- 检查网络连接和服务器可访问性

### API 调用失败
- 确认 API 密钥正确且有效
- 检查 API 基础 URL 是否正确
- 确认账户余额充足（如适用）


## 贡献

欢迎提交 Issue 和 Pull Request！

