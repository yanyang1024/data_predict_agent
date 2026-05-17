# 运维故障处理手册

本文面向部署和维护 Flash-Agents 的运维人员。目标是在用户反馈异常时，能快速定位是前端、后端、数据库、认证、OpenCode、systemd、bubblewrap、网络代理还是文件系统问题。

## 快速定位流程

1. 确认入口是否可访问。

```bash
curl -fsS http://127.0.0.1:8000/health
```

2. 确认 MariaDB。

```bash
docker compose ps mariadb
docker compose logs --tail=100 mariadb
```

3. 确认后端日志。

```bash
journalctl -u flash-agents-backend.service -n 200 --no-pager
```

4. 确认前端/CDN/Nginx 是否正确代理 `/api`。

```bash
curl -i http://<域名或IP>/health
curl -i http://<域名或IP>/api/auth/sso-url
```

5. 确认 OpenCode 用户实例。

```bash
systemctl --user status 'opencode@<user_id>.service'
journalctl --user -u 'opencode@<user_id>.service' -n 200 --no-pager
```

6. 确认端口。

```bash
ss -lntp | grep ':<port>'
curl -i http://127.0.0.1:<port>/api/sessions
```

## 常用配置位置

| 配置 | 路径 |
| --- | --- |
| 后端环境变量 | `backend/.env` |
| 白名单 | `backend/whitelist.json` |
| 工作区 | `WORKSPACE_ROOT`，默认 `./workspaces` |
| 技能目录 | `SKILL_ROOT`，默认 `./skills_store` |
| Agent 配置 | `backend/agents/*.md` |
| OpenCode systemd 模板 | `systemd/opencode@.service` |
| OpenCode 用户 env | `~/.config/flash-agents/opencode/<user_id>.env` |
| Nginx 配置 | `cdn_server/nginx.conf` |

## 启动类问题

### 后端启动失败：`JWT_SECRET must be changed in production`

现象：

- `ENV=production` 时后端直接退出。

原因：

- `JWT_SECRET` 仍是默认值。

处理：

```env
ENV=production
JWT_SECRET=<至少32字节的强随机字符串>
```

然后重启后端：

```bash
sudo systemctl restart flash-agents-backend.service
```

### 后端启动失败：无法连接数据库

现象：

- 后端日志出现 `pymysql.err.OperationalError`、`Connection refused`、`Access denied`。

排查：

```bash
docker compose ps mariadb
docker compose logs --tail=100 mariadb
grep DATABASE_URL backend/.env
```

处理：

- MariaDB 未运行：`docker compose up -d mariadb`。
- 密码不一致：同步 `docker-compose.yml` 和 `backend/.env`。
- 数据库未初始化：执行 `scripts/init_db.sql` 或重建开发数据库。
- 连接数耗尽：检查 `DB_POOL_SIZE`、`DB_MAX_OVERFLOW` 和 MariaDB `max_connections`。

### 后端启动慢或卡在建表

原因：

- 数据库不可达。
- 表结构变更和已有旧表不兼容。
- 生产库没有迁移流程，`create_all()` 不会自动改旧列。

处理：

- 先备份数据库。
- 对比 `backend/models.py` 和实际表结构。
- 手动执行迁移 SQL 或引入 Alembic。

## 登录和认证问题

### 开发登录返回 403：`User is not in whitelist`

排查：

```bash
cat backend/whitelist.json
grep AUTH_ALLOW_UNLISTED backend/.env
```

处理：

- 将用户邮箱加入 `whitelist.json`。
- 或开发环境设置 `AUTH_ALLOW_UNLISTED=true`。
- 检查域是否在 `ALLOWED_DOMAINS` 中。

### 登录返回 403：`Domain is not allowed`

原因：

- 用户 claims 或白名单里的 `domain` 不在 `ALLOWED_DOMAINS`。

处理：

```env
ALLOWED_DOMAINS=RD,MEC,IT
DEFAULT_DOMAIN=IT
```

修改后重启后端。

### SSO 回调失败：`Invalid SSO state`

原因：

- 浏览器 sessionStorage 中的 state 和 IdP 回调 state 不一致。
- 回调跨域或打开了新的浏览器上下文。
- `JWT_SECRET` 变化导致后端无法解码 state。

处理：

- 从登录页重新发起 SSO。
- 确认 `SSO_REDIRECT_URI` 与 IdP 配置完全一致。
- 确认多实例后端使用同一个 `JWT_SECRET`。

### SSO 成功但用户域/管理员权限不对

原因：

- IdP claims 和 `whitelist.json` 冲突。
- 白名单优先覆盖 claims。

处理：

- 检查 `backend/whitelist.json` 中该用户的 `domain`、`roles`、`is_admin`。
- 检查 IdP userinfo 返回字段是否包含 `email`、`domain`、`roles`。

## 前端访问问题

### 页面打开是空白

排查：

```bash
cd frontend
npm run build
```

处理：

- 本地缺依赖：先 `npm install`。
- CDN/Nginx 没有使用 SPA fallback：确认 `try_files $uri $uri/ /index.html;`。
- 浏览器控制台查看 JS 加载失败、API 404 或跨域错误。

### `/api` 请求 404

原因：

- Nginx 没有代理 `/api/`。
- `VITE_API_BASE` 配错。

处理：

- 使用 `cdn_server/nginx.conf` 中的 `/api/` 配置。
- 本地开发用 Vite 代理或设置 `VITE_API_BASE=/api`。

### 403 显示“没有权限访问当前资源”

原因：

- JWT 过期。
- 用户被禁用。
- 访问了其他域或其他用户资源。

处理：

- 退出后重新登录。
- 检查白名单 `disabled`。
- 检查后端资源是否属于当前用户和域。

## SSE 和聊天问题

### 发送消息后一直转圈

排查：

```bash
curl -fsS http://127.0.0.1:8000/health
journalctl -u flash-agents-backend.service -n 200 --no-pager
```

检查浏览器 Network：

- `POST /api/conversations/messages/stream` 是否返回 200。
- Response 是否持续有 SSE 数据。
- 代理是否缓冲。

处理：

- Nginx 必须关闭代理缓冲：`proxy_buffering off;`，并设置较长 `proxy_read_timeout`。
- 后端不可达则先恢复后端。
- OpenCode 不可达时开发环境可开启 `OPENCODE_MOCK_ON_FAILURE=true` 验证平台链路。

### 45 秒无事件，前端提示流式响应卡住

原因：

- OpenCode 没有继续输出 SSE。
- 反向代理缓冲或断开。
- OpenCode 执行任务阻塞。

处理：

- 查 OpenCode 实例日志。
- 查 Nginx/CDN 是否启用 buffering。
- 临时中止会话。
- 生产建议在 OpenCode 端输出心跳或阶段事件。

### 用户点击中止无效

排查：

```bash
journalctl --user -u 'opencode@<user_id>.service' -n 200 --no-pager
```

平台中止会依次调用：

1. 本地 abort flag。
2. `/sessions/{id}/abort`。
3. `/sessions/{id}/questions/reject`。
4. `/sessions/{id}/close`。

处理：

- 确认 OpenCode 兼容这些接口。
- 不兼容时至少实现 abort 或 close。
- 必要时停止该用户实例：`systemctl --user stop opencode@<user_id>.service`。

### 刷新页面后提示 OpenCode 内存状态丢失

原因：

- 会话有 `opencode_session_id`，但对应用户实例已停止或 todo 查询失败。

处理：

- 用户可继续发送新消息，让平台重新恢复主链路。
- 若同一会话不能恢复，建议新建会话。
- 运维检查空闲回收配置和 OpenCode 实例稳定性。

## OpenCode 实例问题

### 实例没有启动

排查：

```bash
grep SYSTEMD_ENABLED backend/.env
systemctl --user status 'opencode@<user_id>.service'
journalctl --user -u 'opencode@<user_id>.service' -n 200 --no-pager
```

处理：

- `SYSTEMD_ENABLED=false` 时后端处于 mock 管理模式，不会真正启动 systemd 服务。
- 执行 `scripts/install_systemd_template.sh`。
- 确认后端运行用户已启用 linger：

```bash
loginctl enable-linger <backend运行用户>
```

### `systemctl --user` 报 bus 不可用

原因：

- 后端服务用户没有 user manager。
- 没有启用 linger。
- systemd 用户环境不完整。

处理：

```bash
loginctl enable-linger <backend运行用户>
sudo -iu <backend运行用户>
systemctl --user daemon-reload
systemctl --user status
```

### 端口被占用

端口策略：

```text
OPENCODE_BASE_PORT + employee_no
```

排查：

```bash
ss -lntp | grep ':<port>'
```

处理：

- 检查是否有重复员工序号。
- 修改用户 `employee_no` 或 `OPENCODE_BASE_PORT`。
- 停止占用端口的旧实例。

### OpenCode session 创建失败

排查：

```bash
curl -i http://127.0.0.1:<port>/api/sessions
journalctl --user -u 'opencode@<user_id>.service' -n 200 --no-pager
```

重点确认：

- OpenCode 是否监听 `127.0.0.1:<port>`。
- OpenCode API 前缀是否为 `/api`。
- OpenCode 是否接受 `cwd=/workspace/<conversation_id>`。
- bwrap 是否已把用户工作区绑定到 `/workspace`。

处理：

- 调整 `OPENCODE_API_PREFIX`。
- 修复 OpenCode 启动命令。
- 修复 bwrap wrapper。
- 生产环境建议设置 `OPENCODE_MOCK_ON_FAILURE=false`，避免真实失败被 mock 掩盖。

## bubblewrap 和沙箱问题

### bwrap 启动失败：命令不存在

处理：

```bash
sudo apt-get install -y bubblewrap
which bwrap
```

并确认：

```env
BWRAP_PATH=bwrap
```

### OpenCode 无法访问工作区文件

原因：

- OpenCode 在沙箱内只能看到 `/workspace`。
- 后端传给 OpenCode 的 cwd 应为 `/workspace/<conversation_id>`。
- wrapper 必须绑定用户工作区根目录到 `/workspace`。

排查：

```bash
cat ~/.config/flash-agents/opencode/<user_id>.env
```

处理：

- 确认 `OPENCODE_WORKSPACE_ROOT` 是 `WORKSPACE_ROOT/user-<user_id>`。
- 确认实际会话目录存在。

### OpenCode 需要访问外部网络

当前 bwrap 使用 `--share-net`，OpenCode 可访问网络并监听本地端口。企业环境若要更强隔离，需要在网络层增加 egress 白名单、代理或防火墙策略。

## 文件和技能问题

### 工作区文件列表为空

原因：

- 会话尚未发送首条消息，工作区未绑定。
- OpenCode 没有写入文件。
- 文件写入到了错误 cwd。

处理：

- 先发送一条消息创建会话。
- 检查会话目录：`workspaces/user-<user_id>/<conversation_id>`。
- 检查 OpenCode cwd 是否为 `/workspace/<conversation_id>`。

### 文件读取 404

原因：

- 路径不存在。
- 访问了目录。
- 路径包含 `..` 或绝对路径，被安全策略伪装成 404。

处理：

- 从文件列表点击打开，不手写路径。
- 检查文件是否在当前用户当前会话工作区内。

### 技能上传失败：`ZIP contains unsafe path`

原因：

- ZIP 内包含绝对路径、`..`、symlink。

处理：

- 重新打包，确保文件都在包根目录下。
- 使用 `scripts/create_skill_zip.sh`。

### 系统技能放入磁盘后不显示

处理：

确认目录：

```text
skills_store/domains/<DOMAIN>/system/shared/<skill-name>/SKILL.md
```

然后刷新技能页或调用：

```bash
curl -H "Authorization: Bearer <jwt>" http://127.0.0.1:8000/api/skills
```

## 管理后台问题

### 管理入口不可见

原因：

- 当前用户 `is_admin=false`。

处理：

- 在 `whitelist.json` 中设置：

```json
{
  "email": "admin@example.com",
  "domain": "IT",
  "is_admin": true,
  "roles": ["admin"]
}
```

重新登录。

### CSV 打开乱码

平台导出的 CSV 带 UTF-8 BOM。若仍乱码：

- 使用 Excel 的“从文本/CSV 导入”。
- 选择 UTF-8。
- 检查浏览器是否下载了完整文件。

## 数据库和升级问题

### 新代码启动后旧表缺列

原因：

- `create_all()` 不会修改已有表结构。

处理：

1. 备份数据库。
2. 对照 `backend/models.py` 编写 ALTER SQL。
3. 维护窗口执行迁移。
4. 重启后端。

建议尽快引入 Alembic，避免生产手工迁移。

### 连接池耗尽

现象：

- 后端日志出现 `QueuePool limit`。

处理：

- 检查请求是否阻塞在 SSE 或数据库事务。
- 调整：

```env
DB_POOL_SIZE=80
DB_MAX_OVERFLOW=40
```

- 同步提高 MariaDB `max_connections`。
- 增加后端实例前先规划数据库连接上限。

## 日常巡检

建议每日或每班次检查：

```bash
curl -fsS http://127.0.0.1:8000/health
docker compose ps mariadb
journalctl -u flash-agents-backend.service -p warning --since "24 hours ago" --no-pager
journalctl --user -p warning --since "24 hours ago" --no-pager
du -sh workspaces skills_store logs
```

建议监控指标：

- HTTP 5xx 数量。
- SSE 平均持续时间和异常断开次数。
- OpenCode 实例数。
- OpenCode 启动失败次数。
- MariaDB 连接数。
- 工作区磁盘占用。
- 空闲回收次数。

## 应急操作

停止单个用户 OpenCode：

```bash
systemctl --user stop 'opencode@<user_id>.service'
```

重载 OpenCode 模板：

```bash
./scripts/install_systemd_template.sh
systemctl --user daemon-reload
```

临时关闭真实 OpenCode，使用 mock 验证平台链路：

```env
SYSTEMD_ENABLED=false
OPENCODE_MOCK_ON_FAILURE=true
```

恢复生产真实执行：

```env
SYSTEMD_ENABLED=true
OPENCODE_MOCK_ON_FAILURE=false
```

修改后重启后端。
