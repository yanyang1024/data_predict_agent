# 开发者指南

本文面向需要理解、修改和扩展 Flash-Agents 的开发者。它说明项目模块边界、现阶段完成情况，以及常见二次开发入口。

## 项目定位

Flash-Agents 是一个 AI agent 企业平台应用。前端提供多 Agent 对话入口，后端负责认证、多租户、会话编排、文件/技能/API 管理，核心 AI 执行交给外部 OpenCode 引擎。每个用户对应一个 OpenCode 实例，由 systemd user service 托管，并通过 bubblewrap 工作区沙箱限制文件访问。

## 目录结构

```text
Flash-Agents/
  backend/              FastAPI 后端
    api/                HTTP API 路由
    services/           OpenCode、实例、工作区、Agent 配置服务
    agents/             内置 9 个 Agent 的 Markdown 配置
    config.py           环境配置
    database.py         SQLAlchemy 连接池和建表入口
    models.py           ORM 模型
    schemas.py          Pydantic DTO
    auth.py             JWT、白名单、当前用户、审计工具
  frontend/             React + TypeScript + Vite 前端
    src/contexts/       Auth、Agent、Toast 等 Provider
    src/hooks/          会话 Hook
    src/services/       API/SSE 客户端和事件 reducer
    src/components/     聊天、文件、Markdown、工具卡片等组件
    src/pages/          登录、回调、聊天、技能、管理页面
  docs/                 项目文档
  scripts/              本地开发、健康检查、systemd、bwrap、技能打包脚本
  systemd/              后端和 OpenCode systemd 模板
  cdn_server/           Nginx 反向代理配置
```

## 后端模块

### `backend/main.py`

FastAPI 应用入口。启动时执行四步：

1. 校验环境变量和运行目录。
2. 调用 `Base.metadata.create_all()` 创建 ORM 表。
3. 在启用 systemd 时同步 `systemd/opencode@.service`。
4. 启动空闲实例回收循环。

### `backend/config.py`

集中管理环境变量。重要配置包括：

- `DATABASE_URL`：MariaDB 连接串。
- `JWT_SECRET`、`JWT_EXPIRE_MINUTES`：JWT 签发配置。
- `SSO_ENABLED` 和 SSO URL：OAuth 2.0 code flow 配置。
- `WORKSPACE_ROOT`、`SKILL_ROOT`、`AGENT_ROOT`：文件系统根目录。
- `SYSTEMD_ENABLED`、`OPENCODE_BASE_PORT`、`IDLE_TIMEOUT_SECONDS`：实例生命周期配置。

### `backend/models.py`

当前包含 6 张表：

- `users`：用户、域、员工序号、角色、管理员标记。
- `conversations`：会话元数据、软删除、OpenCode session 绑定。
- `conversation_messages`：用户和助手消息历史。
- `user_skills`：技能索引，技能文件仍存文件系统。
- `instance_logs`：实例启动/停止/失败日志。
- `audit_logs`：审计日志。

当前没有 Alembic 迁移体系。开发环境可依赖 `create_all()` 建表；生产环境变更字段或索引时应补正式迁移脚本。

### `backend/auth.py` 和 `backend/api/auth.py`

职责：

- JWT 签发和解析。
- `whitelist.json` 热加载。
- SSO callback 处理。
- 开发登录。
- 当前用户依赖 `get_current_user()`。
- 管理员依赖 `require_admin()`。
- 审计日志写入。

白名单在每次认证时从磁盘读取，适合小规模热更新。大规模组织建议改为数据库或企业 IAM 同步。

### `backend/api/conversations.py`

会话核心模块：

- 创建、读取、更新、软删除会话。
- 首条消息时创建会话和工作区，实现延迟 OpenCode session 绑定。
- `POST /conversations/messages/stream` 返回 SSE。
- 保存用户消息和助手最终消息。
- 提供历史消息读取。
- 支持中止任务、孤儿状态检测、问题回答转发。

SSE 事件由 `services/opencode.py` 转发或 mock。前端主要消费：

- `conversation.bound`
- `assistant.delta`
- `reasoning`
- `todo.update`
- `tool.start`
- `tool.end`
- `question`
- `done`
- `error`
- `aborted`

### `backend/services/opencode.py`

OpenCode 客户端。职责：

- 确保每个用户实例存在。
- 首次发送消息时调用 OpenCode 创建 session。
- 把平台消息转发到 OpenCode SSE 接口。
- 解析 OpenCode SSE 行并转为平台事件。
- 执行中止流程。
- 查询 todo 恢复状态。
- 转发 question answer。

注意：传给 OpenCode 的 `cwd` 是沙箱内路径 `/workspace/<conversation_id>`，`hostCwd` 仅用于调试或外部引擎需要映射时参考。

### `backend/services/instance_manager.py`

每用户 OpenCode 实例管理器。职责：

- 按 `OPENCODE_BASE_PORT + employee_no` 计算端口。
- 写入 systemd 环境文件。
- 启动/停止 `opencode@<user_id>.service`。
- 维护进程内运行状态。
- 空闲超时回收。

当前实例状态主要保存在后端进程内存中。多 worker、后端重启后，需要通过 systemd 状态重新恢复的能力仍属于生产化增强项。

### `backend/services/workspace.py`

工作区文件管理：

- 每个会话一个目录：`WORKSPACE_ROOT/user-<user_id>/<conversation_id>`。
- 路径穿越防护：NUL、绝对路径、`..`、`resolve()`、`relative_to()`。
- 文本读取支持 `utf-8 -> gbk -> latin-1` 回退。
- 上传、写入、删除、列表。

### `backend/api/skills.py`

技能管理：

- ZIP 上传。
- 解压前拒绝绝对路径、`..` 和 symlink。
- 技能文件存储在 `SKILL_ROOT/domains/<domain>/users/<user_id>/...`。
- 系统技能可放在 `SKILL_ROOT/domains/<domain>/system/shared/...`。
- 列表接口会同步磁盘目录到数据库索引。

### `backend/services/agent_manager.py`

从 `backend/agents/*.md` 加载 Agent 配置，支持 frontmatter 字段：

```yaml
---
id: code
name: 代码工程师
description: 代码生成、重构、调试和仓库分析
category: engineering
domains: RD,IT
skills: code-review,repo-edit
icon: code
---
```

正文部分作为 system prompt 传给 OpenCode，不返回前端。

## 前端模块

### `frontend/src/App.tsx`

路由入口：

- `/login`：登录页。
- `/auth/callback`：SSO 回调页。
- `/`：聊天页。
- `/skills`：技能页。
- `/admin`：管理页。

### `contexts/AuthContext.tsx`

管理认证状态：

- 从 localStorage 读取 JWT。
- 调用 `/auth/me` 恢复用户。
- 开发登录。
- SSO callback 换取平台 JWT。
- 登出。

### `contexts/AgentContext.tsx`

登录后加载当前用户域可见 Agent。

### `hooks/useConversation.ts`

聊天主 Hook：

- 加载会话列表。
- 发送消息并处理 SSE。
- 选择会话时加载历史消息。
- 检查 OpenCode orphan 状态。
- 中止任务。
- 新建本地空白会话。
- 45 秒无事件时提示卡住。

### `services/api.ts`

统一 HTTP 和 SSE 客户端：

- `apiFetch()` 自动附加 Bearer token。
- `streamSse()` 使用 fetch-stream 发送 POST 请求，支持读取 SSE。
- `createEventSource()` 保留给 GET 型 SSE 或未来断线重连能力。

### `services/sseEventHandler.ts`

纯 reducer，把 SSE event 转为 UI 状态。二次开发新增事件时，应优先在这里扩展。

### 聊天组件

- `ChatUI.tsx`：三栏布局、Agent 选择、消息输入、会话列表。
- `MarkdownMessage.tsx`：Markdown、GFM、KaTeX、Mermaid 渲染。
- `TodoDock.tsx`：todo 状态。
- `ToolCard.tsx`：工具调用。
- `QuestionCard.tsx`：问题确认和选项回答。
- `WorkspaceFilePanel.tsx`：工作区文件列表和预览入口。
- `FilePreview.tsx`：PDF 首页预览，PPT/PPTX 原文件打开。

## 现阶段完成情况

| 能力 | 状态 | 说明 |
| --- | --- | --- |
| 多 Agent 列表 | 已完成 | 9 个 Markdown Agent，按域过滤。 |
| 开发登录 | 已完成 | `/auth/dev-login`，生产 SSO 开启时隐藏。 |
| SSO code flow | 基础完成 | 后端 callback、前端回调页、state 校验已具备；仍需对接企业 IdP 的实际 claims。 |
| 多租户域隔离 | 基础完成 | 用户、Agent、Skill、Conversation、Workspace 按域和用户过滤。 |
| 会话延迟绑定 | 已完成 | 首条消息才创建 OpenCode session。 |
| 消息历史 | 基础完成 | 用户和助手最终消息落库；细粒度 token 级历史不单独保存。 |
| SSE 流式响应 | 已完成 | fetch-stream POST SSE，15 秒心跳由后端提供。 |
| OpenCode mock | 已完成 | OpenCode 不可达时可返回 mock 流，生产建议关闭。 |
| systemd 用户实例 | 基础完成 | 单后端进程内状态管理；多 worker/重启恢复需增强。 |
| bubblewrap 沙箱 | 基础完成 | 工作区绑定到 `/workspace`，网络共享用于本地端口通信。 |
| 工作区文件 | 已完成 | 列表、读取、写入、上传、删除、raw 下载。 |
| 技能管理 | 基础完成 | ZIP 上传、磁盘同步、用户/系统技能索引。 |
| 管理后台 | 基础完成 | 统计、用户列表、审计日志、CSV 导出。 |
| 数据库迁移 | 未完成 | 当前使用 `create_all()`，生产应补 Alembic。 |
| 自动化测试 | 未完成 | 建议补 API、SSE reducer、路径安全、ZIP 安全测试。 |
| 监控告警 | 未完成 | 建议接入日志、指标、OpenCode 实例健康检查。 |

## 本地开发

### 启动 MariaDB

```bash
docker compose up -d mariadb
```

### 启动后端

```bash
python -m venv backend/.venv
. backend/.venv/bin/activate
pip install -r backend/requirements.txt
cp backend/.env.example backend/.env
PYTHONPATH=. uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 启动前端

```bash
cd frontend
npm install
npm run dev
```

浏览器访问 `http://localhost:5173`。

## 二次开发指南

### 新增 Agent

1. 在 `backend/agents/` 新建 `<agent_id>.md`。
2. 添加 frontmatter：`id`、`name`、`description`、`category`、`domains`、`skills`、`icon`。
3. 正文写该 Agent 的 system prompt。
4. 刷新前端或调用 `/api/agents`，后端会按 mtime 自动重载。

示例：

```markdown
---
id: legal
name: 合规助手
description: 合同条款、合规检查、风险提示
category: office
domains: IT,RD
skills: doc-writer
icon: shield
---
你是企业合规 Agent。输出风险等级、依据、建议动作和需要人工确认的点。
```

### 新增技能

用户技能：

1. 准备一个 ZIP，根目录包含 `SKILL.md` 或 manifest 中声明的 entrypoint。
2. 可选 `skill.json`：

```json
{
  "name": "repo-edit",
  "version": "0.1.0",
  "entrypoint": "SKILL.md"
}
```

3. 在技能页上传 ZIP。

系统技能：

1. 将技能目录放到 `skills_store/domains/<DOMAIN>/system/shared/<skill-name>`。
2. 确保包含 `SKILL.md` 或 manifest entrypoint。
3. 调用 `/api/skills` 或打开技能页，后端会同步索引。

### 新增后端 API

1. 在 `backend/api/` 新增或修改 router。
2. 使用 `Depends(get_current_user)` 保护普通接口。
3. 管理接口使用 `Depends(require_admin)`。
4. 新增 DTO 放在 `backend/schemas.py`。
5. 需要审计的写操作调用 `audit()`。
6. 在 `backend/main.py` include router。
7. 更新 `docs/api.md`。

### 新增 SSE 事件

1. OpenCode 按 SSE 格式返回新事件。
2. 后端 `services/opencode.py` 默认会透传未知事件。
3. 如需落库，在 `api/conversations.py` 的 `_collect_assistant_event()` 增加聚合逻辑。
4. 前端在 `services/sseEventHandler.ts` 增加 reducer 分支。
5. 如需 UI 展示，新增或修改聊天组件。

### 新增前端页面

1. 在 `frontend/src/pages/` 新增页面。
2. 在 `App.tsx` 增加 lazy import 和 route。
3. 普通登录后页面放在 `Layout` 内。
4. 复用 `apiFetch()` 和 Context，不直接散落 fetch 调用。

### 修改数据库模型

当前没有迁移体系。开发阶段可改 `models.py` 并重建数据库；生产阶段应：

1. 编写迁移 SQL 或引入 Alembic。
2. 先备份。
3. 在灰度环境验证。
4. 再更新代码。

### 对接真实 OpenCode

真实 OpenCode 或兼容引擎必须满足 [OpenCode 执行引擎契约](./opencode-contract.md)。重点检查：

- 能通过 `opencode serve --host 127.0.0.1 --port <port>` 启动。
- 创建 session 接受 `cwd=/workspace/<conversation_id>`。
- message 接口返回标准 SSE。
- 支持 abort、question reject、close。
- question answer 如需交互确认，应支持 `/questions/{question_id}/answer`。

## 开发约定

- 后端接口返回 404 时不要泄露其他用户资源是否存在。
- 新增文件访问能力必须走 `WorkspaceManager.safe_path()`。
- 新增 ZIP/归档处理必须先检查路径和 symlink。
- 不要把 Agent system prompt、宿主机绝对路径、JWT 放进前端可见的普通响应。
- OpenCode 不可达时 mock 适合开发，生产建议设置 `OPENCODE_MOCK_ON_FAILURE=false`。
- 修改 SSE 协议时，同时更新后端、前端 reducer 和文档。
