# 2. OpenCode 的 Agent 抽象与源码模块视角

---

## 2.1 Agent 的六个槽位如何落到模块

| Agent 抽象 | 研发语义 | OpenCode 对应能力 / 模块 |
|---|---|---|
| **Goal 目标** | 这次要修什么、验收标准是什么 | 用户 prompt、自定义 command、`AGENTS.md` 规则 |
| **State 状态** | 当前会话、消息、todo、打开过的上下文、快照 | `session/`、`message-v2.ts`、`todo.ts`、`summary.ts`、`snapshot/` |
| **Actions 动作空间** | 能读、搜、改、跑、查文档、派生子任务 | `tool/registry.ts` 和内置工具 |
| **Observations 观察** | 命令输出、测试失败、文件内容、LSP 结果 | tool output、truncation、Message parts |
| **Policy 策略** | 用哪个 agent、哪个模型、是否能改代码 | `agent/`、Build / Plan / Explore / Scout、自定义 agent |
| **Runtime 运行时** | 调度、权限、回滚、压缩、扩展、服务化 | `session/processor.ts`、`permission/`、`snapshot/`、MCP、plugins、server |

---

## 2.2 OpenCode 源码模块视角

> 下方模块名以 `anomalyco/opencode` 当前 `dev` 分支结构为参考。版本迭代可能调整目录或文件名，教学时建议以你实际使用版本为准。

### `session/`：Agent loop 的主控层

`session/` 可以看作 OpenCode 的会话大脑，包含：

- **`processor.ts`**：处理 LLM 流式输出、tool call、tool result、权限拦截、doom loop 检测。
- **`prompt.ts` / `system.ts`**：构建提示词和系统上下文。
- **`message-v2.ts`**：消息与 part 结构。
- **`compaction.ts` / `summary.ts`**：长会话压缩与摘要。
- **`revert.ts`**：会话级 revert / undo。
- **`todo.ts`**：多步骤任务列表。
- **`status.ts` / `run-state.ts`**：会话状态。

#### 简化后的执行流

```text
用户输入
  -> 创建 session message
  -> 构造 system prompt / instructions / agent config
  -> 调用 LLM
  -> LLM 输出文本或 tool call
  -> SessionProcessor 记录 tool call 状态
  -> Permission 判断 allow / ask / deny
  -> Tool 执行并返回 observation
  -> LLM 基于 observation 继续
  -> 生成最终答复
  -> snapshot / summary / todo / status 更新
```

#### 源码细节

`SessionProcessor` 在 LLM stream 开始前会先捕获 snapshot，避免工具执行过早导致快照捕获太晚。它也内置了 `DOOM_LOOP_THRESHOLD = 3`，当同一工具带相同输入重复调用 3 次时会触发 `doom_loop` 权限询问。

---

### `tool/`：Agent 的"手"和"眼"

`tool/` 目录下可以看到典型 coding agent 工具：

- **观察类**：`read`、`grep`、`glob`、`lsp`、`webfetch`、`websearch`
- **修改类**：`edit`、`write`、`apply_patch`
- **执行类**：`shell` / `bash`
- **编排类**：`task`、`skill`、`todo`、`question`
- **研究类**：`repo_clone`、`repo_overview`

#### Tool Registry 的职责

`tool/registry.ts` 是工具注册中心，负责：

1. 初始化内置工具。
2. 加载 `.opencode/tools/` 或全局目录中的自定义工具。
3. 加载 plugin 提供的工具。
4. 根据 provider、model、feature flag 和 agent 权限过滤工具。
5. 给 `task` 工具注入可用子代理说明，给 `skill` 工具注入可用技能说明。

这说明 OpenCode 的工具系统不是简单的"把 shell 暴露给模型"，而是有**工具定义、参数 schema、输出截断、权限检查和上下文注入**的一套动作空间。

---

### `permission/`：把自治变成可控

OpenCode 的 permission 不只是"开或关工具"，而是决定某个动作是：

```text
allow -> 直接运行
ask   -> 先问用户
deny  -> 阻止
```

团队落地时，permission 是最重要的安全阀。尤其要控制：

- `bash`
- `edit`
- `write` / `apply_patch`（它们受 `edit` 权限覆盖）
- `external_directory`
- `doom_loop`
- `task`
- `webfetch` / `websearch`
- MCP 工具

---

### `agent/`：不同角色的策略封装

OpenCode 内置的 agent 可以分成三类：

- **主 agent**：`Build`、`Plan`
- **子 agent**：`General`、`Explore`、`Scout`
- **系统隐藏 agent**：`Compaction`、`Title`、`Summary`

研发团队可以把它映射成工作角色：

| Agent | 建议角色 | 是否允许改代码 |
|---|---|---|
| Plan | 需求澄清、方案设计、风险分析 | 否 |
| Explore | 只读代码探索、定位入口 | 否 |
| Scout | 查外部依赖、上游实现、文档 | 否 |
| Build | 最小实现、补测试、跑验证 | 是，但需权限控制 |
| Review（自定义） | 安全、正确性、测试覆盖审查 | 否 |

---

### `snapshot/` 与 `/undo`：方便但不能替代 Git

OpenCode 有 snapshot / revert / diff 能力，并提供 `/undo`、`/redo` 等命令。但它应该被视为**"会话级便利回滚"**，不是团队级版本控制。

正确姿势：

```text
Git checkpoint 是主保险
OpenCode /undo 是辅助保险
```

尤其在多轮修改、子代理、长命令、跨平台文件系统、Windows 保留文件名、snapshot lock 异常等场景下，必须用 Git 自己做明确 checkpoint。

---

## 2.3 模块间的数据流

```text
+-----------+     +------------+     +-----------+
|  User     |---->|  Session   |---->|   LLM     |
|  Input    |     | Processor  |     |  Provider |
+-----------+     +------------+     +-----------+
                        |
                        v
                 +------------+
                 |  Permission|
                 |   Gate     |
                 +------------+
                        |
                        v
                 +------------+     +-----------+
                 |   Tool     |---->|  Bash/    |
                 |  Registry  |     |  Edit/    |
                 +------------+     |  Read/... |
                        |          +-----------+
                        v
                 +------------+
                 | Snapshot/  |
                 |   Undo     |
                 +------------+
```

1. **Session Processor** 接收用户输入，构造上下文，调用 LLM。
2. LLM 返回文本或 tool call 请求。
3. **Permission Gate** 根据配置判断该 tool call 是否允许执行。
4. **Tool Registry** 找到对应工具，执行并返回 observation。
5. Observation 回到 Session Processor，继续循环或生成最终答复。
6. **Snapshot** 在关键节点捕获代码状态，支持 `/undo`。
