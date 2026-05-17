# Flash-Agents

Flash-Agents 是一个企业级多 Agent 平台参考实现，包含前端对话入口、FastAPI 后端、多租户会话编排、文件系统技能、每用户 OpenCode 实例管理和 systemd/bubblewrap 隔离脚本。

- 前端：React + TypeScript + Vite + Tailwind 的多 Agent 对话入口。
- 后端：FastAPI + MariaDB，负责 SSO/JWT、域名多租户、会话编排、文件/技能/API 管理。
- AI 执行：外部 OpenCode 引擎，每个用户独占一个 `systemd --user` 托管实例。
- 隔离：`bubblewrap` 沙箱工作区隔离，`systemd` cgroup v2 限制 32G RAM / 2 CPU。
- 通信：SSE 流式返回，支持心跳、卡住检测、首条消息延迟绑定 OpenCode session。
- 内置 9 个专业 Agent：代码、PPT、流程图、数据、文档、测试、运维、会议、安全。
- 企业特性：白名单热加载、确定性端口、6 步中止、孤儿问题检测、空闲回收、文件系统技能、消息历史。

## 目录

```text
Flash-Agents/
  backend/      FastAPI 后端
  frontend/     React 前端
  cdn_server/   Nginx/CDN 入口配置
  docs/         架构、部署、API、安全文档
  logs/         运行日志目录
  scripts/      初始化、开发、systemd、bwrap 脚本
  systemd/      systemd user service 模板
```

## 文档

- [文档索引](docs/index.md)
- [开发者指南](docs/developer-guide.md)：模块说明、现阶段完成情况、二次开发入口。
- [运维故障处理手册](docs/ops-runbook.md)：登录、数据库、SSE、OpenCode、systemd、bwrap、文件和技能问题排查。
- [用户使用教程](docs/user-guide.md)：登录、聊天、Agent、工作区文件、技能和管理后台使用。
- [架构说明](docs/architecture.md)
- [API 概览](docs/api.md)
- [OpenCode 执行引擎契约](docs/opencode-contract.md)
- [安全设计](docs/security.md)
- [部署指南](docs/deployment.md)

## 本地开发启动

1. 启动 MariaDB：

```bash
docker compose up -d mariadb
```

2. 后端（在项目根目录执行）：

```bash
python -m venv backend/.venv
. backend/.venv/bin/activate
pip install -r backend/requirements.txt
cp backend/.env.example backend/.env
PYTHONPATH=. uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

3. 前端：

```bash
cd frontend
npm install
npm run dev
```

4. 浏览器访问 `http://localhost:5173`，开发登录可使用：

```text
admin@example.com / IT / employee_no=1
rd@example.com    / RD / employee_no=101
```

## 生产切换点

- 设置 `ENV=production`、强随机 `JWT_SECRET`、`SSO_ENABLED=true`。
- 设置 `SYSTEMD_ENABLED=true` 并执行 `scripts/install_systemd_template.sh`。
- 安装 `bubblewrap`、OpenCode CLI，并确保 `opencode` 支持 `serve --host 127.0.0.1 --port <port>`。
- 将前端 `dist/` 交给 `cdn_server/nginx.conf` 服务，并代理 `/api` 到 FastAPI。

## OpenCode API 契约

后端默认转发到：

- `POST /api/sessions`
- `POST /api/sessions/{session_id}/messages`，返回 SSE。
- `GET /api/sessions/{session_id}/todos`
- `POST /api/sessions/{session_id}/abort`
- `POST /api/sessions/{session_id}/questions/reject`
- `POST /api/sessions/{session_id}/questions/{question_id}/answer`
- `POST /api/sessions/{session_id}/close`

如果 OpenCode 暂不可用，`OPENCODE_MOCK_ON_FAILURE=true` 时会返回 mock 流，方便先验证平台主链路。

## 当前完成情况

主链路已完成：认证、域隔离、会话、消息历史、SSE、工作区文件、技能管理、内置 Agent、OpenCode 实例启动/停止、空闲回收和基础管理后台。

生产化仍建议补齐：数据库迁移体系、多后端实例下的 OpenCode 状态恢复、监控告警、完整自动化测试、企业 IdP claims 适配和更细粒度的权限策略。
