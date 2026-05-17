# OpenCode 执行引擎契约

后端不内嵌模型执行，只负责实例生命周期和 API 路由。外部 OpenCode 实例应提供以下 HTTP API。

## 创建 session

```http
POST /api/sessions
Content-Type: application/json
```

请求：

```json
{
  "title": "会话标题",
  "cwd": "/workspace/path",
  "agent": "code",
  "systemPrompt": "...",
  "domain": "RD",
  "userId": 101
}
```

响应：

```json
{ "id": "session-id" }
```

## 发送消息，返回 SSE

```http
POST /api/sessions/{session_id}/messages
```

事件建议：

- `reasoning`：`{"text":"..."}`
- `todo.update`：`{"items":[{"id":"1","text":"...","status":"running"}]}`
- `assistant.delta`：`{"text":"增量文本"}`
- `tool.start` / `tool.end`
- `question`
- `done`
- `error`

## 中止

平台按顺序调用：

1. 本地 abort flag。
2. `POST /api/sessions/{id}/abort`。
3. `POST /api/sessions/{id}/questions/reject`。
4. sleep 200ms。
5. `POST /api/sessions/{id}/close`。
6. 清理本地 abort 状态。
