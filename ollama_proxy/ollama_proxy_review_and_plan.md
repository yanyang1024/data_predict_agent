# Ollama 兼容代理二版方案

## 目标

把现有“先创建会话，再基于会话 ID 流式聊天”的内部模型服务，改造成兼容 Ollama 原生接口的 FastAPI 代理服务，重点覆盖：

- `/api/chat`
- `/api/generate`
- `/api/tags`
- `/api/show`
- `/api/version`
- `/api/ps`
- 图片桥接访问服务

## 现有方案主要问题

1. 每次请求都新建会话，会丢失服务端对话状态。
2. 仅取最后一条 user message，会丢失 system / assistant / 历史上下文。
3. 用 `strip("data:")` 解析 SSE 不安全，会错误裁剪字符。
4. `async def` + `requests.Response.iter_lines()` 会阻塞事件循环。
5. 只适配了 `/api/chat` 和 `/api/generate`，很多 Ollama 客户端还会探测 `/api/tags`、`/api/version`、`/api/show`、`/api/ps`。
6. 多模态桥接只停留在“可能要暴露 URL”，没有落地成独立可控的文件服务。
7. 没有会话映射、并发安全、TTL、可观测性、错误映射策略。

## 推荐架构

- **兼容层**：FastAPI
- **协议转换**：上游 SSE -> Ollama NDJSON
- **会话适配**：Conversation DAG 映射（前缀哈希）
- **回退策略**：无法接续到已有 stateful 会话时，转为“完整历史重建提示词”
- **多模态桥接**：Base64 -> 文件落盘 / 对象存储 -> 可访问 URL -> `QueryExtends.Files`
- **模型目录**：用本地注册表或配置中心对外暴露 Ollama 模型列表
- **状态存储**：开发环境可用内存；生产建议 Redis

## 会话策略

### 主路径：前缀命中

如果当前 `messages` 的最长前缀能映射到某个已存在的内部 `conversation_id`，且剩余消息正好是最后一条 user 消息，则直接复用内部会话，只把最后一条 user 内容发给内部模型服务。

### 回退路径：历史重建

如果用户编辑历史、从中间分叉、导入旧对话、或者代理无法找到可复用前缀，则：

1. 创建新的内部会话。
2. 把完整 `messages` 序列渲染成结构化 prompt。
3. 如果历史里存在图片，把所有图片重新桥接并附加到本次 `QueryExtends.Files`。

## 多模态桥接

### 快速方案

FastAPI 暴露：

- `GET /bridge/files/{token}/{filename}`

处理流程：

1. 接收 Ollama 请求中的 base64 图片。
2. 解析并校验大小 / 类型。
3. 落盘。
4. 生成随机 token URL。
5. 组装成内部接口需要的：

```json
{
  "QueryExtends": {
    "Files": [
      {
        "Name": "image_1.jpg",
        "Path": "bridge/2026/03/12/sha256.jpg",
        "Size": 12345,
        "Url": "https://proxy.example.com/bridge/files/<token>/sha256.jpg"
      }
    ]
  }
}
```

### 生产推荐

- 单实例：FastAPI + 本地磁盘即可
- 多实例 / K8s：Nginx + 共享卷，或 MinIO / S3 预签名 URL

## 协议映射

### 上游 SSE 事件 -> Ollama Chat

- `message` / `message_replace` -> `message.content`
- `agent_thought` / `think_message` -> `message.thinking`
- `message_end` -> `done: true`
- `message_failed` -> 代理错误响应

### 上游 SSE 事件 -> Ollama Generate

- `message` / `message_replace` -> `response`
- `agent_thought` / `think_message` -> `thinking`
- `message_end` -> `done: true`
- `message_failed` -> 代理错误响应

## 兼容边界

### 建议支持

- chat/generate
- stream / non-stream
- think
- vision
- tags/show/version/ps

### 明确标成暂不支持或 best-effort

- tool calling
- logprobs
- 精确 token 统计
- 与真实 Ollama 完全一致的 `keep_alive` 语义
- 完整的 OpenAI 兼容层

## 生产化建议

1. 会话映射放 Redis，不要只放进程内内存。
2. 图片桥接改成共享存储或对象存储。
3. 路由保持同步 `def`，避免 `requests` 阻塞 async event loop。
4. 增加 request_id / conversation_id / task_id 贯通日志。
5. 针对上游异常做 502 映射，不要直接把内部栈暴露给客户端。
6. 对未知模型名直接 404。
7. 对不支持的字段采用“严格模式报错、兼容模式忽略并记日志”。

## 参考实现

配套参考代码文件：`ollama_proxy_v2.py`

默认使用 Mock 上游，替换 `PlaceholderRealUpstreamClient` 即可接入真实服务。
