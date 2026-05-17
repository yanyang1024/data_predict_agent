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

## SSE 双 Token

浏览器 `EventSource` 无法设置自定义 header，因此平台同时支持：

- `Authorization: Bearer <jwt>`
- `?token=<jwt>`

Fetch-stream 首选 header，同时追加 query token 兼容反向代理和重连。

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
