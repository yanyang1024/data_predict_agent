# OpenAI Chat Completions 兼容网关（FastAPI）

这个示例把“先创建会话，再基于会话 ID 走 V2 SSE 聊天”的后端服务，包装成一个兼容 `/v1/chat/completions` 的 FastAPI 网关。

## 已覆盖的兼容点

- 接收 OpenAI 风格 `messages`
- 支持 `stream=true`，向客户端输出 OpenAI 风格 SSE chunk
- 支持 `tool` role 消息，把 tool message 直接拼接进后端 `Query`
- 支持 `assistant.tool_calls` 历史消息，把结构化 tool call 转成文本拼接进 `Query`
- 支持多模态 `messages[].content = [{type:text}, {type:image_url}]`
- 对 `data:image/...;base64,...` 自动落盘并桥接为可访问 URL
- 按请求生成完整 trace 日志，便于排查

## 目录结构

```text
openai_compat_fastapi/
├── app/
│   ├── backend_adapter.py
│   ├── config.py
│   ├── image_bridge.py
│   ├── main.py
│   ├── schemas.py
│   ├── service.py
│   ├── session_store.py
│   ├── sse_parser.py
│   └── trace_logger.py
├── tests/
│   └── test_gateway.py
├── README.md
└── requirements.txt
```

## 运行

```bash
cd openai_compat_fastapi
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export USE_MOCK_BACKEND=true
export PUBLIC_BASE_URL="http://127.0.0.1:8000"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 接入真实后端函数

编辑 `app/backend_adapter.py`，把占位函数替换成你项目里的真实实现。

### 方式 A：你已有函数已经支持 query_extends

```python
from your_backend_module import create_conversation
from your_backend_module import chat_query_v2_sse
```

并保证真实函数支持：

```python
def chat_query_v2_sse(user_id: str, app_conversation_id: str, content: str, query_extends: dict | None = None):
    ...
```

### 方式 B：你现有函数仍然只有三个参数

保留原函数：

```python
from your_backend_module import create_conversation
from your_backend_module import chat_query_v2_sse as raw_chat_query_v2_sse


def chat_query_v2_sse(user_id: str, app_conversation_id: str, content: str, query_extends: dict | None = None):
    # 如果你能改原始 HTTP 调用，推荐在这里把 QueryExtends 一起发下去。
    # 如果一时改不了，兼容网关会自动 fallback，把 QueryExtends 作为文本附加到 Query。
    return raw_chat_query_v2_sse(user_id=user_id, app_conversation_id=app_conversation_id, content=content)
```

更推荐的做法是：**在你自己的 `chat_query_v2_sse` 包装里补一个 `query_extends` 参数，真实向后端发 `QueryExtends`**，这样图片链路才是完整的。

## 多模态图片桥接说明

如果 OpenAI 请求里图片是：

- 远程 URL：直接透传为 `QueryExtends.Files[*].Url`
- `data:image/...;base64,...`：
  1. 网关写入本地 `BRIDGE_DIR`
  2. 通过 `/bridge/files/{filename}` 暴露静态文件
  3. 用 `PUBLIC_BASE_URL + /bridge/files/...` 生成后端可访问 URL

> 注意：`PUBLIC_BASE_URL` 必须是后端模型服务机器也能访问到的地址。若模型服务不在本机，不能写 `127.0.0.1`，应改成实际域名或网关出口地址。

## 会话策略

OpenAI 原生 `chat/completions` 本身不强制会话 ID，但你的后端必须先建会话。因此这里提供两种策略：

1. **无状态默认模式**：每次请求都 `create_conversation()`，把完整 `messages` 压平成一段 `Query`
2. **有状态复用模式**：传 `X-Session-ID` 或 `metadata.session_key`，网关将复用本地保存的 `AppConversationID`

返回头中会带：

- `X-Trace-ID`
- `X-App-Conversation-ID`

## Trace 日志

每个请求单独一套目录：

```text
logs/YYYYMMDD/<trace_id>/
├── request_raw.json
├── request_parsed.json
├── backend_forward_request.json
├── response_final.json
├── backend_raw_sse.txt
├── emitted_openai_sse.txt
└── events.jsonl
```

### 你要求的日志字段，这套实现里对应如下

- 接收到的原始请求消息：`request_raw.json`
- 解析后的请求消息：`request_parsed.json`
- 转发后的请求消息：`backend_forward_request.json`
- 响应消息：`response_final.json` 或 `emitted_openai_sse.txt`
- 消息状态：`events.jsonl` 中的 `status`
- 消息内容：`events.jsonl` 的 `payload`
- 每一段 SSE 解析输出：`backend_raw_sse.txt` + `events.jsonl`

## 测试

```bash
cd openai_compat_fastapi
pytest -q
```

当前已经覆盖：

1. 基础 SSE 解析
2. 普通文本非流式
3. 带 tool call / tool message 历史的非流式
4. 带图片 data URL 的流式
5. 基于 `X-Session-ID` 的会话复用

## 手工验证示例

### 1. 普通文本

```bash
curl http://127.0.0.1:8000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "mock-model",
    "messages": [
      {"role": "system", "content": "你是助手"},
      {"role": "user", "content": "你好"}
    ]
  }'
```

### 2. 带 tool 历史

```bash
curl http://127.0.0.1:8000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "mock-model",
    "messages": [
      {"role": "user", "content": "请查询北京天气"},
      {
        "role": "assistant",
        "tool_calls": [
          {
            "id": "call_123",
            "type": "function",
            "function": {"name": "get_weather", "arguments": "{\"city\":\"北京\"}"}
          }
        ]
      },
      {"role": "tool", "tool_call_id": "call_123", "content": "{\"temp\":26,\"condition\":\"晴\"}"},
      {"role": "user", "content": "继续总结"}
    ]
  }'
```

### 3. 带图片 + 流式

```bash
curl http://127.0.0.1:8000/v1/chat/completions \
  -N \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "mock-model",
    "stream": true,
    "messages": [
      {
        "role": "user",
        "content": [
          {"type": "text", "text": "帮我描述这张图"},
          {"type": "image_url", "image_url": {"url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9sQ5n/8AAAAASUVORK5CYII="}}
        ]
      }
    ]
  }'
```

## 一个重要限制

这套网关已经兼容了 **OpenAI Chat Completions 的输入格式**，包括 `tool` 历史消息与图片输入；
但**输出侧的原生 `tool_calls` 结构**，你的后端当前并没有提供对应的结构化事件，只返回文本 SSE。因此当前实现默认把后端输出映射成普通 assistant 文本。

如果你后续希望“真正输出 OpenAI 原生 tool_calls”，需要二选一：

1. 让底层服务返回结构化 tool call 事件
2. 或在网关层额外约束模型输出 JSON，再在网关里二次解析成 `tool_calls`

在现有后端能力下，我建议先把“历史 tool message 兼容 + trace 可观测 + 多模态桥接”先做稳，这也是这个示例的重点。
