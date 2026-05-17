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
2. `Base.metadata.create_all()` 创建 ORM 表。
3. 同步 `systemd/opencode@.service` 到 `~/.config/systemd/user`。
4. 启动空闲实例回收循环。

## ORM 表

- `users`：SSO/JWT 映射用户、域、员工序号、角色。
- `conversations`：会话元数据，软删除，首条消息后才绑定 OpenCode session。
- `conversation_messages`：用户消息和助手最终消息历史。
- `user_skills`：技能索引，技能实体仍存文件系统。
- `instance_logs`：实例启动/停止/失败日志。
- `audit_logs`：管理、会话、文件、技能操作审计。

当前项目没有 Alembic 迁移体系，生产环境修改模型后需要补迁移 SQL。

## 多租户隔离

租户域使用 `RD/MEC/IT`。认证时从 `whitelist.json` 或 SSO claims 得到域，后续 Agent、Skill、Conversation、Workspace 均按域和用户过滤。

## 端口策略

用户实例端口为：

```text
OPENCODE_BASE_PORT + employee_no
```

当缺少员工序号时使用 email 的 CRC32 稳定散列，确保端口可预测并可持久化。

## OpenCode 工作区映射

宿主机工作区：

```text
WORKSPACE_ROOT/user-<user_id>/<conversation_id>
```

bubblewrap 会把 `WORKSPACE_ROOT/user-<user_id>` 绑定到沙箱内 `/workspace`，因此传给 OpenCode 的 `cwd` 是：

```text
/workspace/<conversation_id>
```

后端响应中不应依赖宿主机路径作为前端展示信息；文件访问统一通过 `/api/files/...` 进行鉴权和路径防护。
