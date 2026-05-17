# 安全设计

## 路径穿越防护

`WorkspaceManager.safe_path()` 实施四层防护：

1. 拒绝 NUL、绝对路径、Windows drive 前缀。
2. `normpath` 标准化。
3. `resolve()` 解析真实路径。
4. `relative_to()` 确认仍在用户会话工作区内。

所有异常返回 404，避免枚举目录结构。

## ZIP 技能包防护

上传技能只接受 `.zip`，解压前检查：

- 不允许绝对路径。
- 不允许 `..` 路径段。
- 不允许 symlink。
- 必须包含 `SKILL.md` 或 manifest entrypoint。

## SSE Token

平台认证依赖同时支持：

- `Authorization: Bearer <jwt>`
- `?token=<jwt>`

当前聊天主链路使用 fetch-stream POST SSE，首选 `Authorization` header，不主动把 JWT 放入 query string。保留 query token 是为了兼容 `EventSource`、文件 raw 预览和 CSV 下载等浏览器无法设置自定义 header 的场景。

运维侧应避免在反向代理访问日志中记录完整 query string，或至少对 `token` 参数做脱敏。

## bubblewrap + systemd cgroup

每用户一个 `opencode@<user_id>.service`：

- `MemoryMax=32G`
- `CPUQuota=200%`
- `TasksMax=512`
- `NoNewPrivileges=yes`
- `ProtectSystem=strict`
- 工作区只绑定到 `/workspace`

## 白名单热加载

`backend/whitelist.json` 在每次认证依赖中读取，修改后无需重启即可生效。
