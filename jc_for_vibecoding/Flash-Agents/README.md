# Flash-Agents

Flash-Agents 是一个企业级多 Agent 平台参考实现，按你的描述复现了以下核心设计：

- 前端：React + TypeScript + Vite + Tailwind 的多 Agent 对话入口。
- 后端：FastAPI + MariaDB，负责 SSO/JWT、域名多租户、会话编排、文件/技能/API 管理。
- AI 执行：外部 OpenCode 引擎，每个用户独占一个 `systemd --user` 托管实例。
- 隔离：`bubblewrap` 沙箱工作区隔离，`systemd` cgroup v2 限制 32G RAM / 2 CPU。
- 通信：SSE 流式返回，支持心跳、前端重连策略、首条消息延迟绑定 OpenCode session。
- 内置 9 个专业 Agent：代码、PPT、流程图、数据、文档、测试、运维、会议、安全。
- 企业特性：白名单热加载、确定性端口、双 Token 传递、6 步中止、孤儿问题检测、空闲回收、文件系统技能。

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
- `POST /api/sessions/{session_id}/close`

如果 OpenCode 暂不可用，`OPENCODE_MOCK_ON_FAILURE=true` 时会返回 mock 流，方便先验证平台主链路。
