# 部署指南

## 依赖

- Python 3.12+
- Node.js 22+
- MariaDB 10.6+ / 11.x
- systemd user service
- bubblewrap
- OpenCode CLI 或兼容执行引擎
- Nginx 或企业 CDN

## 后端

```bash
cd /opt/flash-agents
python -m venv backend/.venv
. backend/.venv/bin/activate
pip install -r backend/requirements.txt
cp backend/.env.example backend/.env
vim backend/.env
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

生产建议：

```env
ENV=production
DEBUG=false
JWT_SECRET=<强随机密钥>
SSO_ENABLED=true
SYSTEMD_ENABLED=true
AUTH_ALLOW_UNLISTED=false
```

## systemd 用户实例

```bash
sudo apt-get install -y bubblewrap
./scripts/install_systemd_template.sh
loginctl enable-linger <backend运行用户>
```

后端会在每次 `ensure_instance()` 前写入：

```text
~/.config/flash-agents/opencode/<user_id>.env
```

里面包含 `OPENCODE_PORT`、`OPENCODE_WORKSPACE_ROOT`、`OPENCODE_BINARY` 等变量。

## 前端

```bash
cd frontend
npm install
npm run build
```

将 `frontend/dist` 发布到 Nginx/CDN，并参考 `cdn_server/nginx.conf` 代理 `/api`。SSE 必须关闭代理缓冲。

## MariaDB

```bash
docker compose up -d mariadb
```

或手动执行 `scripts/init_db.sql`。

## 升级注意

当前后端使用 SQLAlchemy `create_all()` 创建缺失表，但不会自动修改已有表结构。生产环境升级涉及 `backend/models.py` 变更时，需要先备份数据库，再执行迁移 SQL 或引入 Alembic。

## 故障处理

常见问题处理见 [运维故障处理手册](./ops-runbook.md)。
