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
  "cwd": "/workspace/<conversation_id>",
  "hostCwd": "/opt/flash-agents/workspaces/user-1/<conversation_id>",
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

`question` 建议包含：

```json
{
  "id": "question-id",
  "text": "是否覆盖已有文件？",
  "options": ["覆盖", "取消"]
}
```

## 中止

平台按顺序调用：

1. 本地 abort flag。
2. `POST /api/sessions/{id}/abort`。
3. `POST /api/sessions/{id}/questions/reject`。
4. sleep 200ms。
5. `POST /api/sessions/{id}/close`。
6. 清理本地 abort 状态。

## 回答问题

```http
POST /api/sessions/{session_id}/questions/{question_id}/answer
Content-Type: application/json
```

请求：

```json
{ "answer": "覆盖" }
```

该接口用于前端问题卡片的选项回答。若执行引擎暂不支持交互问题，可以不发送 `question` 事件。
