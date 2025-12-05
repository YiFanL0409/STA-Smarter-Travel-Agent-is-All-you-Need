import asyncio
import os
import uuid
from datetime import datetime
from openai import OpenAI
import time
import gradio as gr
try:
    from TAgent.my_llm import llm
except ModuleNotFoundError:
    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
    from TAgent.my_llm import llm

MCP_SERVERS = {
    "fetch_mcp_server_config": {
        "url": os.getenv("MCP_FETCH_URL", ""),
        "transport": "streamable_http",
    },
    "noname_mcp_server_config": {
        "url": os.getenv("MCP_NONAME_URL", ""),
        "transport": "sse",
    },
    "fetch_mcp_server_config_2": {
        "url": os.getenv("MCP_FETCH2_URL", ""),
        "transport": "sse",
    },
    "Transport_mcp_server_config": {
        "url": os.getenv("MCP_TRANSPORT_URL", ""),
        "transport": "sse",
    },
    "Aviation_mcp_server_config": {
        "url": os.getenv("MCP_AVIATION_URL", ""),
        "transport": "sse",
    },
    "Bing_mcp_server_config": {
        "url": os.getenv("MCP_BING_URL", ""),
        "transport": "sse",
    },
    "Zhipu_mcp_server_config": {
        "url": os.getenv("MCP_ZHIPU_URL", ""),
        "transport": "sse",
    },
    "Chart_mcp_server_config": {
        "url": os.getenv("MCP_CHART_URL", ""),
        "transport": "streamable_http",
    },
}

def _load_mcp_tools():
    if (os.getenv("ENABLE_MCP") or os.getenv("DASHSCOPE_ENABLE_MCP")) not in ("1", "true", "True"):
        return []
    try:
        from langgraph.prebuilt import create_react_agent
        from langchain_mcp_adapter import MultiServerMCPClient
    except Exception:
        return []
    try:
        client = MultiServerMCPClient(MCP_SERVERS)
        tools = asyncio.run(client.get_tools())
        return tools
    except Exception:
        return []

TOOLS = _load_mcp_tools()
AGENT = None
# 强制启用 MCP 路径（即使没有工具也尝试按 MCP 方式调用，失败后回退）
MCP_ENABLED = True

SYSTEM_PROMPT = f"今天日期：{datetime.now().strftime('%Y-%m-%d')}; 你是旅行规划助理，回答需准确、简洁，涉及实时价格/班次/天气等必须调用 MCP 工具检索，避免臆测。"

def main():
    css = ".gradio-container{color:#666;font-style:italic}.gr-chatbot{height:500px}.gr-chatbot .message,.gr-chatbot .message-content{white-space:pre}"
    with gr.Blocks(title="Travel Agent") as demo:
        gr.HTML(f"<style>{css}</style>")
        chat = gr.Chatbot(height=500, render_markdown=True)
        # 工具调用面板（置于聊天框下方，可点击展开查看全部，最大高度200）
        with gr.Accordion("工具调用（最近两个）", open=False):
            tool_recent = gr.Markdown(visible=True)
            tool_all = gr.HTML(visible=True)
        inp = gr.Textbox(placeholder="输入消息", lines=1)
        with gr.Row():
            send = gr.Button("发送")
            clear = gr.Button("清空对话")
        state = gr.State([])

        async def stream_fn(history, message):
            h = history or []
            h.append({"role": "user", "content": message})
            h.append({"role": "assistant", "content": "..."})
            tool_trace = []
            def status_text():
                if not tool_trace:
                    return ""
                tail = " → ".join(tool_trace[-2:])
                return f"工具调用：{tail}"
            # 初始：关闭旧面板，显示占位符“...”
            recent_md = status_text()
            all_html = "<div style=\"max-height:200px;overflow:auto\"></div>"
            yield h, h, "", recent_md, all_html
            acc = ""

            sys_msg = {"role": "system", "content": SYSTEM_PROMPT}
            user_msg = {"role": "user", "content": message}
            messages_for_model = [sys_msg] + h[:-1]

            if MCP_ENABLED:
                try:
                    api_key = os.getenv("DASHSCOPE_API_KEY") or os.getenv("OPENAI_API_KEY")
                    base_url = os.getenv("DASHSCOPE_BASE_URL") or os.getenv("OPENAI_BASE_URL") or "https://dashscope.aliyuncs.com/compatible-mode/v1"
                    model = os.getenv("QWEN_MODEL", "qwen-plus")
                    client = OpenAI(api_key=api_key, base_url=base_url)

                    mcp_tools = []
                    for label, cfg in MCP_SERVERS.items():
                        url = cfg.get("url")
                        if not url:
                            continue
                        mcp_tools.append({
                            "type": "mcp",
                            "server_label": label,
                            "server_url": url,
                        })

                    # Streaming via OpenAI Responses with MCP tools
                    try:
                        stream = client.responses.stream(
                            model=model,
                            input=messages_for_model,
                            tools=mcp_tools,
                        )
                        with stream as s:
                            start = time.time()
                            timeout_s = float(os.getenv("MCP_STREAM_TIMEOUT", "8"))
                            events_seen = 0
                            for event in s:
                                events_seen += 1
                                # 提取工具调用名（尽力兼容不同事件结构）
                                tool_name = None
                                ed = getattr(event, "data", None)
                                if isinstance(ed, dict):
                                    tool_name = ed.get("tool_name") or ed.get("tool") or ed.get("name")
                                    if isinstance(ed.get("tool"), dict):
                                        tool_name = ed["tool"].get("name") or tool_name
                                else:
                                    tool_name = (
                                        getattr(event, "tool_name", None)
                                        or getattr(event, "name", None)
                                    )
                                # 再尝试从事件类型里推断工具调用
                                evt_type = (
                                    getattr(event, "event", None)
                                    or getattr(event, "type", None)
                                    or ""
                                )
                                if isinstance(evt_type, str) and ("tool" in evt_type.lower() or "mcp" in evt_type.lower()):
                                    if not tool_name and isinstance(ed, dict):
                                        tool_name = ed.get("name") or ed.get("tool_name")
                                if isinstance(tool_name, str):
                                    tool_trace.append(tool_name)
                                    recent_md = status_text()
                                    all_html = "<div style=\"max-height:200px;overflow:auto\"><ul>" + "".join(
                                        f"<li>{t}</li>" for t in tool_trace
                                    ) + "</ul></div>"
                                    yield h, h, "", recent_md, all_html

                                text = (
                                    getattr(event, "delta", None)
                                    or (isinstance(ed, dict) and ed.get("delta"))
                                )
                                if not text:
                                    # 若长时间没有文本增量，触发超时回退
                                    if (time.time() - start) > timeout_s and acc == "":
                                        raise TimeoutError("MCP stream timeout without delta")
                                    continue
                                acc += text
                                h[-1] = {"role": "assistant", "content": acc}
                                recent_md = status_text()
                                all_html = "<div style=\"max-height:200px;overflow:auto\"><ul>" + "".join(
                                    f"<li>{t}</li>" for t in tool_trace
                                ) + "</ul></div>"
                                yield h, h, "", recent_md, all_html
                                start = time.time()  # 每次收到增量刷新超时计时
                            final = s.get_final_response()
                            final_text = getattr(final, "output_text", None) or acc
                            if final_text and final_text != acc:
                                acc = final_text
                                h[-1] = {"role": "assistant", "content": acc}
                                recent_md = status_text()
                                all_html = "<div style=\"max-height:200px;overflow:auto\"><ul>" + "".join(
                                    f"<li>{t}</li>" for t in tool_trace
                                ) + "</ul></div>"
                                yield h, h, "", recent_md, all_html
                    except Exception:
                        # Fallback to non-stream create
                        resp = client.responses.create(
                            model=model,
                            input=messages_for_model,
                            tools=mcp_tools,
                        )
                        final_text = getattr(resp, "output_text", None) or acc
                        if final_text:
                            acc = final_text
                            h[-1] = {"role": "assistant", "content": acc}
                            recent_md = status_text()
                            all_html = "<div style=\"max-height:200px;overflow:auto\"><ul>" + "".join(
                                f"<li>{t}</li>" for t in tool_trace
                            ) + "</ul></div>"
                            yield h, h, "", recent_md, all_html
                except Exception:
                    pass

            for chunk in llm.stream(messages_for_model):
                text = (
                    getattr(chunk, "content", None)
                    or getattr(getattr(chunk, "message", None) or object(), "content", None)
                    or getattr(chunk, "text", None)
                    or (isinstance(chunk, str) and chunk)
                )
                if not text:
                    continue
                acc += text
                h[-1] = {"role": "assistant", "content": acc}
                recent_md = status_text()
                all_html = "<div style=\"max-height:200px;overflow:auto\"><ul>" + "".join(
                    f"<li>{t}</li>" for t in tool_trace
                ) + "</ul></div>"
                yield h, h, "", recent_md, all_html

            

        send.click(stream_fn, inputs=[state, inp], outputs=[chat, state, inp, tool_recent, tool_all])
        inp.submit(stream_fn, inputs=[state, inp], outputs=[chat, state, inp, tool_recent, tool_all])
        clear.click(lambda: ([], [], "", "", "<div style=\"max-height:200px;overflow:auto\"></div>"), outputs=[chat, state, inp, tool_recent, tool_all])
    port = int(os.getenv("GRADIO_SERVER_PORT", "7860"))
    try:
        demo.queue().launch(server_name="127.0.0.1", server_port=port, share=False)
        print(f"http://127.0.0.1:{port}/")
    except OSError:
        launched = False
        for p in range(port + 1, port + 20):
            try:
                demo.queue().launch(server_name="127.0.0.1", server_port=p, share=False)
                print(f"http://127.0.0.1:{p}/")
                launched = True
                break
            except OSError:
                pass
        if not launched:
            demo.queue().launch(server_name="127.0.0.1", share=False)

if __name__ == "__main__":
    main()
