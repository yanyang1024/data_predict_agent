# Anthropic Messages API 兼容转发服务（FastAPI）

这个示例项目把“先创建会话，再基于 `AppConversationID` 用 SSE 流式 chat”的上游模型服务，改造成一个 **兼容 Anthropic Messages API (`POST /v1/messages`)** 的 FastAPI 代理。

## 已实现能力

1. **Anthropic `POST /v1/messages` 兼容入口**
   - 支持 `stream=false` 返回完整 JSON。
   - 支持 `stream=true` 返回 Anthropic 风格 SSE：
     - `message_start`
     - `content_block_start`
     - `content_block_delta`
     - `content_block_stop`
     - `message_delta`
     - `message_stop`

2. **你当前上游接口的适配**
   - 适配 `create_conversation() -> str`
   - 适配 `chat_query_v2_sse(user_id, app_conversation_id, content)`
   - 如果你的真实函数还支持 `query_extends` 第 4 个参数，适配器会自动传入。
   - 如果你的真实函数只收 3 个参数，代理会自动把 `QueryExtends.Files` 的信息降级拼接进 `content`。

3. **tool message/tool history 支持**
   - Anthropic 的 `tool_use` / `tool_result` 会被序列化成文本标签拼接到上游 `Query`。
   - 示例格式：
     - `<assistant_tool_use ...>{...}</assistant_tool_use>`
     - `<user_tool_result ...>...</user_tool_result>`

4. **多模态图片桥接**
   - 支持 Anthropic `image.source.type=url`
   - 支持 Anthropic `image.source.type=base64`
   - 对于 `base64` 图片，代理会落盘到本地 `MEDIA_DIR`，并通过 `/proxy/media/{filename}` 暴露可访问链接。
   - 生成的 URL 会放进上游 `QueryExtends.Files[].Url`。

5. **完整 trace 日志**
   - 每次请求生成单独 trace 文件：`logs/traces/YYYYMMDD/trace_<trace_id>.jsonl`
   - 记录：
     - 原始请求
     - 规范化后的 Anthropic 请求
     - 转发到上游的请求
     - 上游响应状态
     - 每一条上游 SSE 原始行
     - 每一条解析后的上游事件
     - 每一条转发给客户端的 Anthropic SSE 事件
     - 最终完整响应
     - 异常和 traceback

## 目录结构

```text
anthropic_fastapi_proxy/
  app/
    main.py                 # FastAPI 入口
    config.py               # 配置
    models.py               # 请求/响应模型
    anthropic_mapper.py     # Anthropic -> 上游 Query/QueryExtends 映射
    upstream_adapter.py     # 适配 create_conversation/chat_query_v2_sse + SSE 解析
    sse_bridge.py           # 上游 SSE -> Anthropic SSE 重组
    media.py                # base64 图片落盘 + 文件 URL 暴露
    logging_utils.py        # 运行日志 / trace 日志
    store.py                # session 模式的会话映射
    mock_backend.py         # mock 上游，便于联调
  tests/
    test_message_mapping.py
    test_sse_bridge.py
    test_api.py
  requirements.txt
  README.md
```

## 你要接入真实函数时怎么改

### 方式一：直接新建 `user_backend.py`

在项目根目录新建 `user_backend.py`：

```python
def create_conversation() -> str:
    ...


def chat_query_v2_sse(user_id: str, app_conversation_id: str, content: str, query_extends=None):
    ...
```

然后启动前设置：

```bash
export USE_MOCK_BACKEND=false
```

### 方式二：把你的真实函数 import 进去

也可以直接把 `app/upstream_adapter.py` 中：

```python
module_name = "app.mock_backend" if settings.use_mock_backend else "user_backend"
```

替换成你自己的模块路径。

## 运行

### 1) 安装依赖

```bash
pip install -r requirements.txt
```

### 2) 启动

```bash
export USE_MOCK_BACKEND=true
export PUBLIC_BASE_URL=http://127.0.0.1:8000
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

> `PUBLIC_BASE_URL` 必须是 **你的现有模型服务器可以访问到的地址**。如果上游访问不到这个代理的 `/proxy/media/*`，就无法让 `QueryExtends.Files[].Url` 生效。

## 可选配置

```bash
export CONVERSATION_MODE=stateless     # stateless | session
export MEDIA_PROXY_MODE=passthrough    # passthrough | download
export DEFAULT_USER_ID=anthropic-proxy-user
export LOG_DIR=./logs
export MEDIA_DIR=./media
export EXPOSE_THINKING_AS_TEXT=false
```

### `CONVERSATION_MODE`

- `stateless`：
  - 每次 `/v1/messages` 请求都创建一个新的上游 conversation。
  - 会把完整 `messages[]` 序列化后发给上游。
  - 最接近 Anthropic 的“无状态 Messages API”语义。
- `session`：
  - 用请求头 `x-proxy-conversation-id` 绑定一个代理级会话。
  - 代理内部把它映射到上游 `AppConversationID`。
  - 只转发新增消息，避免重复灌入历史。

## 手工测试

### 1) 非流式纯文本

```bash
curl http://127.0.0.1:8000/v1/messages \
  -H 'content-type: application/json' \
  -H 'anthropic-version: 2023-06-01' \
  -d '{
    "model": "claude-sonnet-4-6",
    "max_tokens": 128,
    "messages": [
      {"role": "user", "content": "你好"}
    ]
  }'
```

### 2) 流式 SSE

```bash
curl http://127.0.0.1:8000/v1/messages \
  -N \
  -H 'content-type: application/json' \
  -H 'anthropic-version: 2023-06-01' \
  -d '{
    "model": "claude-sonnet-4-6",
    "stream": true,
    "messages": [
      {"role": "user", "content": "讲个一句话故事"}
    ]
  }'
```

### 3) 带 tool history

```bash
curl http://127.0.0.1:8000/v1/messages \
  -H 'content-type: application/json' \
  -d '{
    "model": "claude-sonnet-4-6",
    "messages": [
      {"role": "user", "content": "帮我查天气"},
      {"role": "assistant", "content": [
        {"type": "tool_use", "id": "toolu_1", "name": "weather", "input": {"location": "北京"}}
      ]},
      {"role": "user", "content": [
        {"type": "tool_result", "tool_use_id": "toolu_1", "content": "晴 25 度"}
      ]}
    ]
  }'
```

### 4) 带 base64 图片

```bash
curl http://127.0.0.1:8000/v1/messages \
  -H 'content-type: application/json' \
  -d @sample_image_request.json
```

## 自动化测试

```bash
PYTHONPATH=. pytest -q
```

当前包含 3 组测试：

1. **SSE 解析/重组测试**
   - 测基础 `message_start -> message -> message_cost -> message_end` 是否能正确转成 Anthropic SSE。

2. **消息映射测试**
   - 纯文本消息
   - 带 `tool_use` / `tool_result` 消息
   - 带图片消息，验证 `QueryExtends.Files` 是否生成

3. **接口集成测试**
   - 非流式文本消息
   - 流式文本消息
   - 带 tool history 的消息
   - 带图片文件的消息
   - trace 日志落盘验证

## 日志说明

### 全局日志

- `logs/app.log`

### 单请求 trace 日志

- `logs/traces/YYYYMMDD/trace_<trace_id>.jsonl`

每一行都是一条 JSON 记录，便于按 `trace_id` 回放整次请求。

## 建议的上线方式

如果你的上游模型服务能直接访问这个代理机器：

1. 把这个代理部署成独立 FastAPI 服务。
2. `PUBLIC_BASE_URL` 指向这个代理的公网/内网可达地址。
3. 让上游通过 `QueryExtends.Files[].Url` 直接回拉图片。

如果你的上游模型服务 **不能** 访问这个代理：

1. 把 `media.py` 改成把图片上传到对象存储（如 OSS / S3 / MinIO）。
2. `QueryExtends.Files[].Url` 改成对象存储的签名 URL。

## 当前方案的边界

1. **Anthropic 真正的结构化 `tool_use` 响应**：
   - 你的上游当前只暴露 `tool_message`/文本 SSE 事件说明，无法稳定还原成 Anthropic 原生 `tool_use` 内容块。
   - 所以当前方案把 tool 相关历史 **降级为文本上下文** 传给上游。

2. **Anthropic Files API / `image.source.type=file`**：
   - 本示例未实现 `/v1/files`。
   - 如需完全补齐，可继续加一个文件上传 API，把 `file_id` 映射到本地或对象存储。

3. **严格无状态 vs 上游有状态**：
   - Anthropic Messages API 本身是无状态的。
   - 你的上游依赖 conversation。
   - 所以示例同时给了 `stateless` 和 `session` 两种模式。

## 建议你优先这样联调

1. 先跑 `USE_MOCK_BACKEND=true`
2. 先测纯文本非流式
3. 再测纯文本流式 SSE
4. 再测 tool history
5. 再测图片 base64/url
6. 最后把 `user_backend.py` 接成真实函数
7. 对照 `trace_*.jsonl` 看：
   - 收到的原请求
   - 转发后的 Query / QueryExtends
   - 上游每条 SSE
   - 转换后的每条 Anthropic SSE



## 图片统一处理

当前版本对所有接收到的图片统一执行以下流程：

1. 无论是 `image.source.type=base64` 还是 `image.source.type=url`，都先保存到本地 `MEDIA_DIR/MEDIA_SUBDIR/`。
2. 自动构造上游 `query_extends`：

```python
query_extends = {
    "Files": [
        {
            "Name": "upload_rawpic_xxx.png",
            "Path": "uploaded_images/upload_rawpic_xxx.png",
            "Size": 47525,
            "Url": "http://127.0.0.1:8000/proxy/media/uploaded_images/upload_rawpic_xxx.png",
        }
    ]
}
```

可通过环境变量调整：

- `PUBLIC_BASE_URL`：外部可访问的服务地址
- `MEDIA_DIR`：本地落盘根目录
- `MEDIA_SUBDIR`：图片相对目录，默认 `uploaded_images`
- `MEDIA_URL_PREFIX`：图片访问前缀，默认 `/proxy/media`
- `UPLOAD_FILENAME_PREFIX`：base64 图片默认前缀，默认 `upload_rawpic`
- `MEDIA_PROXY_MODE`：默认 `download`，统一走本地落盘
