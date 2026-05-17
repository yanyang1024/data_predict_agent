# API 概览

基础前缀：`/api`

## Auth

- `GET /auth/me`
- `GET /auth/sso-url`
- `POST /auth/callback`
- `POST /auth/dev-login`

## Agents

- `GET /agents`：返回当前用户域可见 Agent。

## Conversations

- `GET /conversations`
- `POST /conversations`
- `GET /conversations/{id}`
- `PATCH /conversations/{id}`
- `DELETE /conversations/{id}`
- `GET /conversations/{id}/orphan-check`
- `POST /conversations/{id}/abort`
- `POST /conversations/messages/stream`：SSE，支持 header Bearer 和 query token。

## Files

- `GET /files/{conversation_id}?path=.`
- `GET /files/{conversation_id}/read?path=...`
- `PUT /files/{conversation_id}/write`
- `POST /files/{conversation_id}/upload?path=...`
- `DELETE /files/{conversation_id}?path=...`

## Skills

- `GET /skills`
- `POST /skills/upload`
- `GET /skills/{skill_id}`
- `DELETE /skills/{skill_id}`

## Instance

- `GET /instance/me`
- `POST /instance/me/ensure`
- `POST /instance/me/stop`

## Admin

- `GET /admin/stats`
- `GET /admin/users`
- `GET /admin/audit`
- `GET /admin/audit.csv?tz=+08:00`
