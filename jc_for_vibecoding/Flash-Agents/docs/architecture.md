# 架构说明

## 总体链路

```mermaid
flowchart LR
  Browser[React/Vite 对话界面] -->|JWT + SSE| API[FastAPI]
  API --> DB[(MariaDB)]
  API --> FS[(Workspace / Skills)]
  API --> IM[InstanceManager]
  IM -->|systemctl --user| SVC[opencode@user.service]
  SVC --> BWRAP[bubblewrap sandbox]
  BWRAP --> OC[OpenCode Engine]
  OC -->|SSE events| API --> Browser
```

## 启动 4 步

1. 环境与目录校验。
2. `Base.metadata.create_all()` 创建 5 张 ORM 表。
3. 同步 `systemd/opencode@.service` 到 `~/.config/systemd/user`。
4. 启动空闲实例回收循环。

## 5 张 ORM 表

- `users`：SSO/JWT 映射用户、域、员工序号、角色。
- `conversations`：会话元数据，软删除，首条消息后才绑定 OpenCode session。
- `user_skills`：技能索引，技能实体仍存文件系统。
- `instance_logs`：实例启动/停止/失败日志。
- `audit_logs`：管理、会话、文件、技能操作审计。

## 多租户隔离

租户域使用 `RD/MEC/IT`。认证时从 `whitelist.json` 或 SSO claims 得到域，后续 Agent、Skill、Conversation、Workspace 均按域和用户过滤。

## 端口策略

用户实例端口为：

```text
OPENCODE_BASE_PORT + employee_no
```

当缺少员工序号时使用 email 的 CRC32 稳定散列，确保端口可预测并可持久化。
