下面的建议基于你给出的架构描述，以及我查到的 OpenCode 当前文档/公开 issue。没有看你的真实代码和日志，所以我会把建议写成“判断框架 + 可落地改造方向”，避免把不确定点说死。

## 一句话判断

你的应用现在最大的问题不是“OpenCode 不够完美”，而是**把 OpenCode 当成了稳定、多租户、可观测、可恢复的后端引擎来直接编排**。更稳的方向是：在 OpenCode 外面做一层**Engine Gateway / 会话状态机 / 事件归一化层**，把 OpenCode 视为“有状态、会丢事件、会重复事件、会卡住、语义不完全闭环的外部执行器”。

也就是说，核心方法论应该是：

> **不要让前端和业务逻辑直接适配 OpenCode 的细节；让后端维护平台自己的会话真相，把 OpenCode 事件只当作输入信号。**

---

## 先校准一个重要事实：你的部分判断可能是“版本差异”

最新 OpenCode Server 文档显示，它确实提供 headless HTTP server，并暴露 OpenAPI 3.1 规范，适合被程序化调用；文档也列出了 `/global/event`、`/event` SSE、`/session/status`、`/session/:id/abort`、`/session/:id/permissions/:permissionID`、`/session/:id/message`、`/session/:id/prompt_async` 等接口。尤其是 `/session/status` 文档写的是“Get session status for all sessions”，这和你提到“无批量状态 API”不完全一致，建议先确认你们部署的 OpenCode 版本、API 路径和文档版本是否一致。([OpenCode][1])

还有一个关键点：`POST /session/:id/message` 和 `prompt_async` 的请求体里支持 `messageID?`，虽然 `prompt_async` 返回 204 不返回内容，但你可以由平台自己生成 `messageID`，把它作为关联 ID 传入，而不是完全依赖 OpenCode 返回 request_id。([OpenCode][1])

---

# 一、建议先把问题分成 5 类，不要混在一起修

我建议你建立一个问题分类表，每个故障都必须归到下面某一类：

| 类别                         | 典型症状                                              | 归因方式            | 解决方向                                       |
| -------------------------- | ------------------------------------------------- | --------------- | ------------------------------------------ |
| **A. OpenCode API/事件语义缺口** | 全局 SSE、abort 不清理 pending question、事件重复/缺失、无法增量恢复  | OpenCode 原生行为   | 适配层状态机、事件去重、持久化 pending、必要时 upstream patch |
| **B. 你的后端编排问题**            | fire-and-forget race、SSE 未建好就发 prompt、恢复全量拉取、状态错乱 | 平台控制面不足         | Engine Gateway、turn 状态机、event sourcing     |
| **C. 前端请求风暴**              | 多组件轮询同一 status、刷新/多 tab 放大请求、异常实例反复 3s timeout    | 应用层重复请求         | 单一状态源、SSE invalidation、缓存、退避               |
| **D. 实例生命周期问题**            | systemd 实例太多、端口/pid/FD/内存压力、异常实例拖慢请求              | 运行时资源模型         | lease、circuit breaker、冷启动/热池、分片            |
| **E. Agent/Skill 体验问题**    | 工具重试、自己停住、skill 嵌套混乱、图片无法内联                       | agent 设计与产品承接问题 | 子 agent 编排、工具幂等、artifact registry、完成判定     |

这一步很重要，因为 **A 类不能靠前端轮询修，C 类也不能怪 OpenCode**。你现在的问题看起来是 A+B+C 混在一起了。

---

# 二、平台架构上，建议引入一个明确的 Engine Gateway

你现在的后端已经在做 OpenCodeClient，但我建议把它升级成一个更正式的 **Engine Gateway**，职责不是“转发 REST API”，而是“屏蔽 OpenCode 不稳定语义”。

## 1. 平台自己维护 turn_id / request_id / messageID

每次用户发送消息时，由平台生成：

```text
platform_turn_id
platform_request_id
opencode_session_id
opencode_message_id
conversation_id
user_id
tenant_id
instance_generation
```

然后把 `opencode_message_id` 放进 OpenCode 的 `messageID` 字段里。这样即使 `prompt_async` 没有返回 request_id，你也能靠平台侧 ID 做关联。OpenCode 文档里 `message` 与 `prompt_async` 请求体都包含 `messageID?`，这是你应优先利用的接口能力。([OpenCode][1])

建议表结构大概是：

```sql
agent_turn (
  id,
  tenant_id,
  user_id,
  conversation_id,
  platform_request_id,
  opencode_session_id,
  opencode_message_id,
  instance_id,
  instance_generation,
  status, -- CREATED / SENT / STREAMING / WAITING_PERMISSION / ABORTING / DONE / FAILED / ORPHANED
  created_at,
  updated_at,
  final_at,
  error_code,
  error_detail
)
```

不要再让一次用户请求只存在于内存映射里。

---

## 2. 把 SSE 变成平台事件日志，而不是直接转发流

OpenCode 的 `/global/event` 和 `/event` 都是 SSE 流，文档也明确列出“global events”和“bus events”。([OpenCode][1])
你的后端不应该只是按 sessionID 过滤后转发给前端，而应该做三件事：

第一，**标准化事件**：

```text
opencode_raw_event -> platform_event
```

第二，**去重和排序**：

```text
dedupe_key = instance_generation + opencode_session_id + event_type + message_id + part_id + event_hash
```

第三，**持久化关键事件**：

```sql
agent_event (
  id,
  tenant_id,
  conversation_id,
  turn_id,
  opencode_session_id,
  event_type,
  event_seq,
  raw_event_json,
  normalized_json,
  created_at
)
```

为什么要这么做？因为 OpenCode 公开 issue 里已经出现过事件重复触发的问题报告，比如 plugin event 多次 fired，同一类 `session.updated`、`message.updated`、`message.part.updated` 重复出现。即使这是特定版本 bug，也说明你的平台不能假设事件流严格 exactly-once。([GitHub][2])

---

## 3. 前端只订阅平台事件，不直接理解 OpenCode 事件

建议前端看到的是你的平台事件：

```text
turn.started
message.delta
tool.started
tool.completed
permission.requested
turn.waiting_user
turn.aborting
turn.aborted
turn.completed
turn.failed
artifact.created
conversation.updated
instance.degraded
```

不要让前端处理 OpenCode 的原始 `message.part.updated`、`session.updated`、`session.idle` 这类事件。这样以后 OpenCode API 改了，或者你换执行引擎，前端不用重写。

---

# 三、会话与消息发送：不要继续依赖 fire-and-forget + sleep

你现在的流程是：

```text
prompt_async + 0.5s 延迟确保 SSE 先建立
```

这个设计本质上是 race condition。更稳的做法是：

```text
1. 创建 platform_turn
2. 确保 instance lease 有效
3. 确保 OpenCode session 已绑定
4. 确保该 instance 的 SSE reader 已经处于 connected 状态
5. 写入 turn 状态 = READY_TO_SEND
6. 调 prompt_async，并传入平台生成的 messageID
7. 状态改为 SENT
8. SSE reader 负责驱动后续状态
9. watchdog 负责超时补偿
```

如果 SSE reader 没连上，不要靠 sleep，而是返回：

```text
turn.status = QUEUED_ENGINE_CONNECTING
```

然后由后台任务发送。这里不是“异步承诺给用户以后完成”，而是当前请求内完成状态落库，前端可以立刻显示“正在连接执行引擎”。

---

## 建议引入 turn 状态机

一个比较实用的状态机如下：

```text
CREATED
  -> BINDING_SESSION
  -> WAITING_ENGINE
  -> READY_TO_SEND
  -> SENT
  -> STREAMING
  -> WAITING_PERMISSION
  -> RESUMED
  -> COMPLETING
  -> COMPLETED

异常分支：
  -> ABORT_REQUESTED
  -> ABORT_SENT
  -> PERMISSIONS_REJECTED
  -> DRAINING
  -> ABORTED

恢复分支：
  -> ENGINE_RESTARTED
  -> RECONCILING
  -> ORPHANED
  -> RECOVERED / FAILED
```

你的后端所有逻辑都围绕这个状态机写，而不是围绕“当前 SSE 连接还在不在”。

---

# 四、Pending question / permission 必须平台持久化

你提到 OpenCode 的 abort 不自动处理 pending questions，pending 状态只在内存里。这类问题必须由平台接管。

OpenCode 文档里有 `POST /session/:id/permissions/:permissionID`，用于响应 permission request。([OpenCode][3])
你应当在收到 permission/question 类事件时落库：

```sql
pending_permission (
  id,
  tenant_id,
  user_id,
  conversation_id,
  turn_id,
  opencode_session_id,
  permission_id,
  question_payload_json,
  status, -- PENDING / APPROVED / REJECTED / AUTO_REJECTED / EXPIRED
  created_at,
  resolved_at
)
```

中断时不要只做“手动 reject 内存 pending questions”，而是：

```text
1. turn.status = ABORT_REQUESTED
2. 调 OpenCode abort
3. 查询 DB 中该 turn/session 所有 PENDING permission
4. 调 permissions API 逐个 reject
5. 本地状态改 AUTO_REJECTED
6. SSE drain 一个短窗口
7. 如果仍未 idle，标记 ABORTED_WITH_ENGINE_UNCERTAIN
8. 下次恢复时 reconcile
```

这样即使 OpenCode 重启，平台也知道“这个 permission 原本存在过，并且平台已尝试拒绝”。

---

# 五、恢复策略：不要每次刷新都全量拉历史

OpenCode 文档当前只显示 `GET /session/:id/message` 支持 `limit?`，没有看到按事件序列增量拉取的接口。([OpenCode][1])
所以你平台侧需要自己建增量层：

```text
OpenCode 全量消息 -> 平台事件日志 / 消息快照 -> 前端增量拉取
```

推荐接口：

```http
GET /api/conversations/:id/events?after_event_id=xxx
GET /api/conversations/:id/snapshot
GET /api/conversations/:id/turns/:turn_id
```

恢复流程改成：

```text
页面刷新
  -> 拉平台 snapshot
  -> 拉 after_event_id 之后的平台事件
  -> 接入平台 SSE
```

只有当平台发现事件日志不完整、OpenCode 实例重启、或者 session generation 变化时，才去 OpenCode 全量拉取并 reconcile。

---

# 六、前端问题：你自己的判断基本是对的，但要系统化改

你提到的几个自身设计问题，我认为优先级很高：

```text
1. 三个组件各自轮询同一 instance/status
2. ConversationList 10s 轮询过高
3. health check timeout=3s 过长
4. unhealthy 不走缓存 fast path
5. httpx.AsyncClient 未复用连接
```

这些都属于“应用级请求放大器”。

## 1. 前端建立单一状态源

不要让 3 个组件各自请求：

```text
ConversationList -> /instance/status
ChatHeader       -> /instance/status
InputBox         -> /instance/status
```

改成：

```text
useInstanceStatus(instanceId)
```

由 React Query / SWR / Zustand 统一缓存。所有组件读同一个状态。

建议策略：

```text
active conversation:
  主要靠 SSE 更新
  status 接口只作为兜底

inactive conversation list:
  30s - 60s 轮询
  页面不可见时停止
  SSE 收到 conversation.updated 时 invalidate

unhealthy instance:
  不高频探测
  使用 30s 左右负缓存 + jitter
```

## 2. SSE 连接数也要控制

浏览器 EventSource 在非 HTTP/2 场景下有连接数限制，MDN 提到同一浏览器 + 域名下限制很低，常见是 6 个连接，这在多 tab、多会话场景会非常痛。([MDN Web Docs][4])

所以建议：

```text
每个浏览器 tab 尽量 1 条平台 SSE
多会话事件在这条 SSE 上 multiplex
多 tab 用 BroadcastChannel 共享状态
```

不要每个组件、每个会话、每个状态面板都开独立 SSE。

---

# 七、后端 health/status：做缓存、singleflight、circuit breaker

你现在 `timeout=3s` 的问题很典型：健康实例 50ms 内返回，异常实例却让每次请求卡 3s，最后把异常放大成雪崩。

建议拆成两类接口：

## 1. 用户请求路径上的 status：永远读缓存

```http
GET /api/instance/:id/status
```

返回：

```json
{
  "status": "healthy|starting|busy|unhealthy|unknown",
  "cached": true,
  "stale": false,
  "checked_at": "...",
  "next_probe_after": "..."
}
```

不要在用户请求路径里同步等 OpenCode health 3 秒。

## 2. 后台探测路径：短 timeout + 退避

状态缓存建议：

```text
healthy    TTL 5-10s
busy       TTL 1-3s
starting   TTL 1-2s，指数退避
unhealthy  TTL 30-60s，带 jitter
unknown    允许快速探测一次
```

并且加 singleflight：

```text
同一个 instance 同一时刻最多一个 health probe
其他请求直接复用该 probe 的 future 或读取旧缓存
```

## 3. httpx.AsyncClient 必须复用

HTTPX 官方文档明确提醒：为了获得连接池收益，不要在 hot loop 里反复实例化多个 `AsyncClient`，应该使用单个 scoped/global client，或者显式关闭。([Httpx][5])

FastAPI 里建议用 lifespan 创建：

```python
@app.on_event("startup")
async def startup():
    app.state.http = httpx.AsyncClient(
        timeout=httpx.Timeout(connect=0.2, read=1.0, write=1.0, pool=0.2),
        limits=httpx.Limits(
            max_connections=500,
            max_keepalive_connections=100,
            keepalive_expiry=30,
        ),
    )

@app.on_event("shutdown")
async def shutdown():
    await app.state.http.aclose()
```

具体数值要压测后调，但方向是：**复用连接池 + 局部短 timeout + 异常负缓存**。

---

# 八、实例生命周期：每用户独占实例可以保留，但要改成 lease 模型

“每用户一个 systemd 托管 OpenCode 实例”隔离性很好，但 1000 用户规模下，你要区分：

```text
注册用户数 1000
同时在线用户数 N
同时执行任务用户数 M
```

不要让“每位用户独占实例”变成“1000 个长期常驻实例”。

建议引入：

```sql
engine_instance_lease (
  id,
  tenant_id,
  user_id,
  node_id,
  port,
  systemd_unit,
  pid,
  generation,
  status,
  last_heartbeat_at,
  last_used_at,
  expires_at
)
```

核心规则：

```text
1. 只有活跃用户持有 lease
2. idle 超时释放
3. 每次重启 generation +1
4. 事件必须带 instance_generation 校验
5. 旧 generation 的 SSE 事件全部丢弃
6. 端口由 allocator 管理，不手写随机端口
```

这样可以解决很多幽灵事件、旧连接误写状态、实例重启后事件串线的问题。

---

# 九、OpenCode 原生体验问题的解决方向

## 问题 1：工具调用报错后重试

这不是单纯 bug，Agent 系统里工具失败后重试很常见。你要做的是让工具**可重试、可判定、可幂等**。

建议：

```text
1. 工具返回结构化错误，不要只返回文本
2. 区分 retryable / non_retryable
3. 对写操作加 idempotency_key
4. 对危险操作加 dry_run / confirm
5. 工具参数先 schema validate
6. 工具超时必须短于 turn 超时
7. 所有工具调用写入 tool_call 表
```

例如工具返回：

```json
{
  "ok": false,
  "error_code": "INVALID_ARGUMENT",
  "retryable": false,
  "message": "缺少 project_id，不能继续执行"
}
```

这样模型更不容易盲目重试。

---

## 问题 2：会话执行一部分后自己停止，需要用户说“继续”

这个要分三种情况排查：

```text
A. 模型自己判断完成
B. agent steps 上限触发
C. compaction / 上下文 / 工具异常导致提前 idle
```

OpenCode agents 文档里有 `steps` 配置；当达到上限时，agent 会被要求总结已经完成的工作和剩余任务。([OpenCode][6])
所以你可以给不同 agent 设置不同 steps，不要让复杂任务用默认不可控行为。

平台侧建议做一个 **completion contract**：

要求 agent 最终输出结构化结束标记，例如：

```text
<final_status>
status: completed | blocked | needs_user | partial
remaining_tasks:
...
</final_status>
```

当收到 `session.idle` 后，平台检查：

```text
1. 是否有 final_status
2. 是否还有未完成 todo
3. 是否最后一句明显是“下一步我将...”
4. 是否有 pending permission
5. 是否最后一个 tool_call 失败
```

如果判断为“非用户阻塞的 partial”，平台可以自动补一轮：

```text
请继续完成上一步中未完成的任务。不要重新开始，基于已有上下文继续。
```

但必须限制次数，比如：

```text
auto_continue_max = 1 或 2
```

否则会制造无限循环。

---

## 问题 3：触发一个 skill 同时又调用另一个 skill，耗时长、逻辑乱

你的直觉是对的：**复杂多 skill 任务不应该靠 skill 嵌套自然涌现，应该由 orchestrator + subagents 编排。**

OpenCode 文档里 agents 分 primary agents 和 subagents；subagents 可以由 primary agent 自动调用，也可以通过 `@` 手动调用；内置 subagents 包括 General、Explore、Scout。文档还写到 General 可用于复杂问题和多步任务，Explore 是只读快速探索，Scout 用于外部文档和依赖研究。([OpenCode][6])

建议你的企业平台里定义：

```text
primary agent:
  enterprise-orchestrator

subagents:
  domain-policy-reader
  data-analyst
  code-inspector
  document-writer
  chart-renderer
  qa-reviewer
```

然后让 skill 变成“某个 agent 的局部能力包”，而不是“工作流编排器”。

OpenCode 还支持通过 `permission.task` 控制某个 agent 可以调用哪些 subagent，也支持 hidden subagent。这个非常适合企业场景：用户看不到内部 helper agent，但 orchestrator 可以调用。([OpenCode][6])

推荐模式：

```text
用户请求
  -> orchestrator 拆任务
  -> read-only subagents 并行探索
  -> orchestrator 汇总
  -> build/write agent 串行执行
  -> reviewer agent 复核
  -> 输出 final_status
```

不要让：

```text
skill A -> skill B -> skill C -> 工具 X -> 工具 Y
```

这种链条失控。

---

## 问题 4：图片渲染无法直接在对话里展示

这个应该由你的平台解决，不要指望 OpenCode 原生聊天 UI 直接满足企业 Web 产品体验。

OpenCode custom tools 支持在 `.opencode/tools/` 下定义工具，并且工具可以调用任意语言脚本；工具执行上下文里有 `sessionID`、`messageID`、`directory`、`worktree` 等信息。([OpenCode][7])

你可以做一个平台级 artifact 规范：

```json
{
  "type": "artifact.created",
  "artifacts": [
    {
      "kind": "image",
      "path": "/workspace/output/chart.png",
      "mime": "image/png",
      "title": "销售趋势图",
      "display": "inline"
    }
  ]
}
```

然后后端：

```text
1. 监听 workspace 产物
2. 校验路径必须在用户 workspace 内
3. 生成 artifact 记录
4. 生成带权限校验的 signed URL
5. 通过平台 SSE 发 artifact.created
6. 前端以内联图片/card 渲染
```

前端渲染成：

```markdown
![销售趋势图](/api/artifacts/{artifact_id}/content?token=...)
```

这样用户就能在聊天里看到图，而不是去路径里找。

---

# 十、Skill 商店要注意：skill 不是安全边界

OpenCode skill 文档显示，skill 是通过 `SKILL.md` 定义的可复用行为，OpenCode 会发现 repo 或 home 目录里的 skill，agent 通过原生 `skill` tool 按需加载。skill frontmatter 只识别 `name`、`description`、`license`、`compatibility`、`metadata` 等字段。([OpenCode][8])

企业平台里不要把 skill 当“可信插件”。建议：

```text
1. skill 只是提示词/流程说明
2. custom tool 才是代码能力
3. skill 上架需要审核
4. skill 描述必须明确触发条件
5. 每个 domain/tenant 有 skill allowlist
6. 敏感 skill 默认 ask 或 deny
7. 高危工具只能通过 permission 控制
```

OpenCode 支持用 pattern-based permission 控制 skill，例如 allow、deny、ask，也支持 per-agent 覆盖。([OpenCode][8])

---

# 十一、你应该优先做的 10 个改造

按收益/风险排序，我建议这样排：

## P0：立刻做

**1. 复用 httpx.AsyncClient**

这是低风险高收益。

**2. 前端 status 请求合并**

三个组件统一读一个状态源，ConversationList 不再 10 秒固定轮询。

**3. health 加缓存和负缓存**

异常实例不要每次触发 3s timeout。

**4. 所有请求带平台 turn_id / messageID**

利用 OpenCode 请求体里的 `messageID?`，不要等待它返回 request_id。

**5. Pending permission 落库**

abort 前后都以 DB 里的 pending 状态为准。

---

## P1：一到两个迭代内做

**6. Engine Gateway 事件归一化**

Raw OpenCode event 不再直接进前端。

**7. turn 状态机**

所有 send、abort、recover 都围绕状态机。

**8. 平台 event log + snapshot**

页面刷新不再全量依赖 OpenCode message history。

**9. Instance lease + generation**

解决实例重启、旧 SSE、端口复用、孤儿事件问题。

**10. Artifact registry**

图片、报告、表格、文件都通过平台 artifact 渲染。

---

# 十二、建议的目标架构

可以收敛成下面这样：

```text
Browser
  |
  | 1 条平台 SSE / WebSocket-like SSE
  v
Frontend State Store
  |
  v
FastAPI API Layer
  |
  +-- Auth / SSO / Tenant Guard
  |
  +-- Conversation Service
  |
  +-- Turn State Machine
  |
  +-- Artifact Service
  |
  +-- Engine Gateway
        |
        +-- Instance Lease Manager
        +-- Health Cache / Circuit Breaker
        +-- OpenCode SSE Reader
        +-- OpenCode REST Client
        +-- Event Normalizer
        +-- Permission Reconciler
        +-- Abort Controller
        |
        v
     Per-user OpenCode systemd instance
        |
        +-- bubblewrap sandbox
        +-- cgroup limits
        +-- workspace
```

关键原则：

```text
OpenCode 是执行器，不是真相源。
MariaDB + 平台事件日志 + turn 状态机 才是真相源。
```

---

# 十三、上游 OpenCode 值得提 issue/PR 的方向

有些问题你可以在应用层规避，但长期最好推动 OpenCode API 改进：

```text
1. prompt_async 返回 accepted messageID / requestID
2. SSE event 增加 monotonic event_id / sequence
3. 支持 /session/:id/event?after=xxx
4. permission/pending question 持久化
5. abort 自动 reject pending permission/question
6. abort 返回最终取消状态，而不是只返回 boolean
7. /session/status 支持指定 sessionIDs 批量查询
8. /global/health 必须 fast path，不依赖重型初始化
9. message list 支持 after_message_id / after_part_id 增量
10. event schema 明确哪些事件 at-least-once，哪些可能重复
```

这类需求不是臆想。OpenCode 公开 issue 里已经有人问过通过 server API 如何判断 session 是否结束，说明 completion/status 语义对程序化集成确实容易踩坑。([GitHub][9])
也有人提到 OpenCode 使用内存事件通知系统会导致多个进程/客户端同步问题，这与你的“平台多客户端、多会话恢复”场景高度相关。([GitHub][10])

---

# 十四、排障方法论：每个问题都按这个模板处理

建议你们以后分析日志时统一用这个模板：

## 1. 先标注故障类型

```text
transport_error
sse_disconnect
duplicate_event
missing_event
engine_hang
permission_orphan
abort_incomplete
frontend_duplicate_polling
health_probe_amplification
tool_retry_loop
agent_partial_stop
artifact_missing
```

## 2. 每条日志必须有统一 trace 字段

至少包含：

```text
trace_id
tenant_id
user_id_hash
conversation_id
platform_turn_id
platform_request_id
opencode_session_id
opencode_message_id
instance_id
instance_generation
systemd_unit
node_id
```

没有这些字段，你很难判断“这是 OpenCode 的错，还是你映射错了”。

## 3. 建一组固定压测/混沌场景

必须覆盖：

```text
1. SSE 建立前发送 prompt
2. 发送中刷新页面
3. 多 tab 同时打开同一会话
4. 工具调用中 abort
5. permission pending 时 abort
6. OpenCode 进程被 kill
7. OpenCode 端口复用
8. unhealthy instance 连续被访问
9. 大量 ConversationList 同时刷新
10. skill A 调 skill B 的长任务
11. 生成图片但聊天 UI 需要内联展示
12. OpenCode 返回重复事件
13. OpenCode 没有返回最终消息但 session idle
```

## 4. 指标化，不要只看单条日志

建议你至少监控：

```text
instance_start_latency_p50/p95/p99
health_check_latency_p50/p95/p99
health_check_timeout_count
status_cache_hit_ratio
frontend_status_requests_per_user_per_min
sse_reconnect_count
duplicate_event_count
orphan_permission_count
abort_success_latency
abort_uncertain_count
turn_auto_continue_count
tool_retry_count
full_history_reload_count
artifact_render_success_ratio
opencode_process_memory
opencode_process_cpu
active_instance_count
idle_recycle_count
```

这些指标能直接告诉你：到底是 OpenCode 不稳，还是你的适配层把小问题放大了。

---

# 十五、我对你当前问题的总体判断

你的架构方向并不差，尤其是：

```text
每用户实例隔离
bubblewrap + cgroup
延迟会话绑定
空闲回收
skill 商店
SSO / 多租户
SSE 流式体验
```

这些都是企业内部 Agent 平台需要的能力。

但现在缺的是三层“工程化保险丝”：

```text
1. 控制面保险丝：
   instance lease、health cache、circuit breaker、singleflight

2. 会话语义保险丝：
   turn 状态机、event log、pending permission 持久化、abort reconcile

3. 产品体验保险丝：
   artifact registry、auto-continue 限流、subagent 编排、前端单状态源
```

最推荐的路线是：

```text
第一阶段：止血
  修前端重复轮询、health timeout、httpx 连接复用、unhealthy fast path。

第二阶段：补状态
  turn_id/messageID、pending question 落库、event 去重、abort 状态机。

第三阶段：改架构
  Engine Gateway、instance lease、event sourcing、snapshot 恢复。

第四阶段：提体验
  subagent 编排复杂 skill、artifact 内联渲染、completion contract、auto-continue。
```

这样做之后，你就不会再被 OpenCode 的每一个 API 限制牵着走。你的平台会变成“可替换执行引擎的企业 Agent 平台”，OpenCode 只是其中一个 engine adapter。

[1]: https://opencode.ai/docs/server/ "Server | OpenCode"
[2]: https://github.com/sst/opencode/issues/3744 "plugin events are fired multiple times · Issue #3744 · anomalyco/opencode · GitHub"
[3]: https://opencode.ai/docs/zh-cn/server/ "服务器 | OpenCode"
[4]: https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events?utm_source=chatgpt.com "Using server-sent events - Web APIs | MDN - MDN Web Docs"
[5]: https://www.python-httpx.org/async/?utm_source=chatgpt.com "Async Support - HTTPX"
[6]: https://opencode.ai/docs/agents/ "Agents | OpenCode"
[7]: https://opencode.ai/docs/custom-tools/ "Custom Tools | OpenCode"
[8]: https://opencode.ai/docs/skills/ "Agent Skills | OpenCode"
[9]: https://github.com/sst/opencode/issues/3075 "[QUESTION] How can I know if the session has ended from the server API? · Issue #3075 · anomalyco/opencode · GitHub"
[10]: https://github.com/sst/opencode/issues/2783 "Idea: use Turso/ZeroMQ/WebSockets for shared event bus, synchronize multiple opencode TUIs and servers · Issue #2783 · anomalyco/opencode · GitHub"
