# 2. OpenCode 源码模块视角

> **适用版本**：OpenCode CLI v1.14.32 / v1.15.13
>
> 本章从源码模块的视角拆解 OpenCode 的架构，帮助你理解「一次用户输入是如何被处理成代码变更的」，以及各个模块在其中扮演的角色。理解这些模块的职责边界，是后续自定义 Agent、扩展工具链、调试异常行为的基础。

---

## 2.1 从 Agent 抽象到模块映射

在深入源码之前，我们先建立一个统一的认知框架。学术界和工业界对 "Agent" 的抽象通常包含六个核心要素：**Goal（目标）、State（状态）、Actions（动作空间）、Observations（观察）、Policy（策略）、Runtime（运行时）**。OpenCode 的源码目录结构正是围绕这六个要素组织的。

| Agent 抽象 | 研发语义 | OpenCode 对应能力 / 模块 |
|---|---|---|
| **Goal** 目标 | 这次要修什么、验收标准是什么 | 用户 prompt、自定义 command、AGENTS.md 规则 |
| **State** 状态 | 当前会话、消息、todo、打开过的上下文、快照 | `session/`、`message-v2.ts`、`todo.ts`、`summary.ts`、`snapshot/` |
| **Actions** 动作空间 | 能读、搜、改、跑、查文档、派生子任务 | `tool/registry.ts` 和内置工具集 |
| **Observations** 观察 | 命令输出、测试失败、文件内容、LSP 结果 | tool output、truncation、Message parts |
| **Policy** 策略 | 用哪个 agent、哪个模型、是否能改代码 | `agent/`、Build / Plan / Explore / Scout、自定义 agent |
| **Runtime** 运行时 | 调度、权限、回滚、压缩、扩展、服务化 | `session/processor.ts`、`permission/`、`snapshot/`、MCP、plugins、server |

**一个适合放在教程里的比喻**：

- 如果你熟悉的 ReAct 框架像一个"会自己排障的实习生"——给它一个问题，它自己思考、行动、观察、再思考；
- 那么 OpenCode 就像一个"**带 IDE、终端、工单系统、权限审批、代码快照的本地开发工位**"——它不只负责"想"和"做"，还负责管理整个开发环境的运行态。

这个比喻的差距，正是 OpenCode 源码中 `session/`、`permission/`、`snapshot/` 等模块存在的意义。

---

## 2.2 session/：Agent Loop 的主控层

`session/` 是 OpenCode 最核心的目录，相当于整个 Agent 的"大脑皮层"——它负责**调度**、**记忆**和**生命周期管理**。

### 2.2.1 核心文件职责

| 文件 | 职责 |
|---|---|
| `processor.ts` | Agent Loop 的主控引擎，编排"输入 → LLM → Tool → 输出"的完整循环 |
| `prompt.ts` | 构造发给 LLM 的 system prompt，整合 agent 规则、上下文、工具描述 |
| `system.ts` | System prompt 的底层组装逻辑，处理 prompt 的分段和优先级 |
| `message-v2.ts` | 消息模型的定义与序列化，支持多模态消息（文本、图片、文件引用） |
| `compaction.ts` | 上下文压缩策略，当会话过长时自动裁剪历史消息 |
| `summary.ts` | 会话摘要生成，在 compaction 后保留关键上下文信息 |
| `revert.ts` | 代码回滚逻辑，支持单次变更的回退 |
| `todo.ts` | 待办事项管理，跟踪多步骤任务的状态 |
| `status.ts` | 会话状态机（idle/running/paused/error 等） |
| `run-state.ts` | 单次运行的状态追踪，与 `status.ts` 配合实现细粒度状态管理 |

### 2.2.2 简化的执行流程

理解 `session/` 的关键是抓住这条**主执行流**：

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  用户输入    │────▶│ 创建 session      │────▶│ 构造 system      │
│  (prompt)   │     │ message (v2)     │     │  prompt          │
└─────────────┘     └──────────────────┘     └─────────────────┘
                                                        │
                        ┌────────────────────────────────┘
                        ▼
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  最终答复    │◀────│ LLM 继续 / 结束   │◀────│ Tool 执行 +      │
│  (给用户)    │     │                 │     │ Observation     │
└─────────────┘     └──────────────────┘     └─────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────┐
│ snapshot / summary / todo / status / run-state 更新              │
└─────────────────────────────────────────────────────────────────┘
```

更细粒度的循环如下：

```
用户输入
  │
  ▼
创建 Session Message（text / image / file_ref 等多种 part 类型）
  │
  ▼
构造 System Prompt（agent 规则 + 工具描述 + 上下文摘要 + AGENTS.md 指令）
  │
  ▼
调用 LLM（流式接收 response）
  │
  ▼
解析 Tool Call（LLM 请求调用某个工具）
  │
  ▼
Permission 判断（allow / ask / deny）——见 2.4 节
  │
  ▼
Tool 执行（读文件、执行 shell、编辑代码等）——见 2.3 节
  │
  ▼
生成 Observation（工具输出，可能被 truncation 截断）
  │
  ▼
LLM 继续（基于 Observation 进行下一步推理）
  │
  ├── 还有 tool call？→ 继续循环
  │
  └── 没有 tool call？→ 生成最终答复
          │
          ▼
    更新 snapshot（代码变更点）
    更新 summary（会话摘要）
    更新 todo（任务进度）
    更新 status / run-state（会话状态）
```

### 2.2.3 v1.15.13 的重要改进

在 v1.15.13 中，`session/` 模块有两项值得关注的变化：

1. **Header Timeout 机制**：针对长时间运行的 LLM 请求增加了 header timeout 处理，防止因网络延迟导致的请求挂起，提升了会话稳定性。

2. **后台 Agent 推送（Background Agent Push）**：支持 Agent 在后台运行时的状态推送，用户可以在 Agent 执行耗时任务时保持交互，不必等待全部完成才能看到进度。

3. **OPENCODE_CONFIG_CONTENT 优先级修复**：环境变量 `OPENCODE_CONFIG_CONTENT` 的配置优先级被正确提升，确保通过环境注入的配置能够覆盖本地配置文件，这在 CI/CD 场景中尤为重要。

---

## 2.3 tool/：Agent 的"手"和"眼"

如果说 `session/` 是大脑，那么 `tool/` 就是 Agent 的**感知器官**和**执行器官**。所有与外部世界的交互——读文件、执行命令、搜索代码——都通过 tool 完成。

### 2.3.1 工具分类体系

OpenCode 的内置工具按功能可分为五类：

| 类别 | 工具示例 | 作用 |
|---|---|---|
| **观察类**（感知） | `read`、`grep`、`glob`、`lsp`、`webfetch`、`websearch` | 让 Agent "看到"代码库、文档、网络资源 |
| **修改类**（执行） | `edit`、`write`、`apply_patch` | 让 Agent "改动"代码文件 |
| **执行类**（运行） | `shell` / `bash` | 让 Agent "运行"命令，获取实时反馈 |
| **编排类**（调度） | `task`、`skill`、`todo`、`question` | 让 Agent "规划"和"分解"任务 |
| **研究类**（探索） | `repo_clone`、`repo_overview` | 让 Agent "研究"外部代码库 |

### 2.3.2 观察类工具详解

**`read`**：读取文件内容。支持行范围指定（如 `read:0-50`），避免一次性加载大文件。返回的内容可能经过 truncation，防止超出 LLM 上下文窗口。

**`grep`**：在代码库中搜索文本模式。类似于 `ripgrep`，支持正则表达式，是 Agent 定位代码的主要手段。

**`glob`**：文件路径匹配。用于批量发现文件（如 "找到所有 `*.test.ts` 文件"）。

**`lsp`**：语言服务器协议调用。让 Agent 获得精确的代码语义信息——跳转到定义、查找引用、类型推断等。这是 OpenCode 超越简单文本编辑的关键能力。

**`webfetch`** / **`websearch`**：网络信息获取。用于查阅文档、搜索 API 用法、获取外部资源。

### 2.3.3 修改类工具详解

**`edit`**：原地编辑文件。通常配合 `read` 使用——先读、再改、再验证。

**`write`**：写入新文件或覆盖整个文件。适用于创建新组件、新配置文件等场景。

**`apply_patch`**：应用 patch 格式的变更。支持更复杂的批量修改，类似于 `git apply`。

> **最佳实践**：修改类工具通常与 `read` 工具配合使用，形成 "读 → 理解 → 改 → 验证" 的闭环。在自定义 Agent 规则中，你可以通过 AGENTS.md 强化这一模式。

### 2.3.4 编排类工具详解

**`task`**：创建子任务。当一个任务过于复杂时，Agent 可以将其分解为多个子任务，每个子任务可以指派给不同的子 Agent（如 Scout、Explore）。

**`skill`**：调用预定义的技能模板。Skill 是可复用的操作序列，类似于"宏"或"剧本"。

**`todo`**：管理待办事项列表。与 `session/todo.ts` 配合，实现任务进度的可视化追踪。

**`question`**：向用户提问。当信息不足或需要确认时，Agent 可以通过此工具与用户交互。

### 2.3.5 tool/registry.ts：工具的"调度中心"

`tool/registry.ts` 是整个工具系统的核心枢纽，负责：

1. **初始化内置工具**：在启动时加载所有内置工具（read、edit、shell 等）。
2. **加载自定义工具**：从用户配置目录加载自定义工具定义。
3. **加载 Plugin 工具**：通过 MCP（Model Context Protocol）或 plugin 机制加载外部工具。
4. **过滤工具**：根据当前 Agent 的权限配置，决定哪些工具可用。
5. **注入上下文**：将工具描述、参数 schema 注入到 system prompt 中，让 LLM 知道"自己能做什么"。

```typescript
// 伪代码示意 tool/registry.ts 的核心逻辑
class ToolRegistry {
  private tools: Map<string, Tool> = new Map();

  async initialize() {
    // 1. 注册内置工具
    this.registerBuiltInTools();
    // 2. 加载自定义工具
    await this.loadCustomTools();
    // 3. 加载 plugin 工具（MCP 等）
    await this.loadPluginTools();
  }

  getAvailableTools(agentConfig: AgentConfig): Tool[] {
    // 4. 根据 agent 权限过滤工具
    return Array.from(this.tools.values())
      .filter(t => this.isToolAllowed(t, agentConfig));
  }

  injectToolDescriptions(tools: Tool[]): string {
    // 5. 生成 tool 描述文本，注入 system prompt
    return tools.map(t => formatToolSchema(t)).join('\n');
  }
}
```

### 2.3.6 v1.14.32 的工具相关修复

v1.14.32 在工具层面有几项重要修复：

- **图像处理修复**：改进了 `message-v2.ts` 中图像消息的编码和处理逻辑，确保多模态输入（截图、图片等）能正确传递给 LLM。
- **Agent 目录访问修复**：修复了特定场景下 Agent 通过 `glob` 和 `read` 访问工作区目录时的权限边界问题，确保沙箱隔离性。

---

## 2.4 permission/：把自治变成可控

权限系统是 OpenCode 与纯自治 Agent 的核心区别之一。它回答了一个关键问题：**Agent 能做什么、不能做什么，由谁决定？**

### 2.4.1 三级权限模型

OpenCode 采用简单的三级权限模型：

| 级别 | 行为 | 适用场景 |
|---|---|---|
| `allow` | 直接运行，无需确认 | 低风险的只读操作（read、grep）、已授权的操作 |
| `ask` | 先询问用户，等待确认 | 中等风险操作（edit、shell 执行非破坏性命令） |
| `deny` | 阻止执行 | 高风险操作（删除文件、执行危险命令）、被明确禁止的操作 |

### 2.4.2 权限配置的粒度

权限配置支持多个维度，形成一个**从粗到细**的控制体系：

```
全局默认权限（global）
  │
  ├── Agent 级别权限（per-agent）← v1.15.13 新增独立权限设置
  │       └── 可以为 Build、Plan、Explore 等不同 Agent 设置不同权限
  │
  ├── 工具级别权限（per-tool）
  │       └── 如：shell 默认 ask，read 默认 allow
  │
  └── 路径级别权限（per-path）
          └── 如：`.env` 文件 deny 写入，`src/` 目录允许编辑
```

### 2.4.3 v1.15.13 的权限系统改进

v1.15.13 对权限系统进行了重要增强：

1. **Agent 级别的独立权限设置**：现在可以为每个 Agent 单独配置权限规则。例如，你可以让 `Build` Agent 拥有代码编辑权限，而 `Scout` Agent 只有只读权限，从而实现"最小权限原则"。

2. **权限规则顺序修复**：修复了多条权限规则冲突时的优先级判定逻辑。现在权限评估严格按照配置文件中规则的**声明顺序**进行，第一条匹配的规则生效，这使得权限配置的行为更加可预测。

示例配置（`~/.config/opencode/config.json`）：

```json
{
  "permissions": {
    "default": "ask",
    "agents": {
      "Build": {
        "shell": "ask",
        "edit": "allow",
        "write": "allow"
      },
      "Scout": {
        "shell": "deny",
        "edit": "deny",
        "read": "allow",
        "grep": "allow"
      }
    },
    "paths": {
      ".env*": { "write": "deny", "read": "ask" },
      "node_modules/**": { "write": "deny", "edit": "deny" }
    }
  }
}
```

### 2.4.4 权限判断的执行时机

权限判断发生在 `session/processor.ts` 的 tool call 阶段：

```
LLM 请求调用 tool
  │
  ▼
解析 tool call 参数
  │
  ▼
查询 PermissionRegistry（按 agent → tool → path 逐级匹配）
  │
  ├── allow ──▶ 直接执行 tool
  │
  ├── ask ────▶ 向用户展示确认提示 ──▶ 用户确认 ──▶ 执行
  │                                    └─▶ 用户拒绝 ──▶ 返回错误
  │
  └── deny ───▶ 直接返回权限拒绝错误
```

---

## 2.5 agent/：不同角色的策略封装

`agent/` 模块实现了 OpenCode 的 **Policy 层**——决定"用哪个 Agent、怎么做事"。每个 Agent 本质上是一个**角色模板**，包含特定的 system prompt、可用工具集、模型配置和行为策略。

### 2.5.1 Agent 分类体系

| 类别 | Agent | 职责 | 典型使用场景 |
|---|---|---|---|
| **主 Agent** | `Build` | 构建代码，执行具体的开发任务 | 写功能、修 bug、重构代码 |
| **主 Agent** | `Plan` | 制定计划，分解复杂任务 | 大型功能开发前的任务拆分 |
| **子 Agent** | `General` | 通用问答和简单操作 | 解释代码、回答技术问题 |
| **子 Agent** | `Explore` | 探索代码库结构 | 熟悉新项目、查找相关代码 |
| **子 Agent** | `Scout` | 快速侦察和定位 | 找到某个函数的定义、查找引用 |
| **系统 Agent** | `Compaction` | 上下文压缩 | 自动触发，用户无感知 |
| **系统 Agent** | `Title` | 生成会话标题 | 自动命名新会话 |
| **系统 Agent** | `Summary` | 生成会话摘要 | 会话结束时总结做了什么 |

### 2.5.2 主 Agent：Build 与 Plan

**Build Agent** 是 OpenCode 的"主力工程师"：
- 拥有完整的工具访问权限（读、写、执行）
- 默认使用能力最强的模型
- 遵循 "读 → 理解 → 改 → 验证" 的工作流
- 可以创建子任务，委派给 Scout 或 Explore

**Plan Agent** 是"架构师"：
- 专注于任务分解和方案设计
- 在执行前先生成详细的实施计划
- 通常作为复杂任务的入口 Agent

### 2.5.3 子 Agent：General、Explore、Scout

子 Agent 的设计体现了**"分而治之"**的策略——将不同类型的工作分配给专门的角色，避免主 Agent 在不适合的任务上浪费上下文窗口。

**Scout Agent** 是最轻量的子 Agent，专注于"快速找到东西"：
- 只读工具（read、grep、glob、lsp）
- 不修改代码
- 快速返回搜索结果
- 被 Build Agent 频繁调用来定位代码

**Explore Agent** 用于"理解代码库结构"：
- 比 Scout 更全面的探索能力
- 可以生成代码库的高层次概览
- 适用于接手新项目时的初始化探索

**General Agent** 处理非编码任务：
- 解释代码逻辑
- 回答技术问题
- 执行简单的文件操作

### 2.5.4 系统隐藏 Agent

系统 Agent 对用户透明，由 `session/` 自动触发：

| Agent | 触发时机 | 作用 |
|---|---|---|
| `Compaction` | 上下文长度接近上限 | 压缩历史消息，保留关键信息 |
| `Title` | 新会话创建时 | 自动生成描述性标题 |
| `Summary` | 会话结束或手动触发 | 生成会话内容摘要 |

### 2.5.5 自定义 Agent

OpenCode 支持通过 **AGENTS.md** 文件自定义 Agent 行为。你可以在项目根目录或全局配置目录创建此文件，定义：

- 自定义角色描述和行为规则
- 项目特定的编码规范
- 特定文件/目录的操作指南
- 工具使用的偏好设置

```markdown
<!-- AGENTS.md 示例 -->
# 项目 Agent 规则

## 编码规范
- 使用 TypeScript 严格模式
- 所有 API 调用必须通过 `src/api/client.ts` 封装
- 错误处理必须使用 `Result<T, E>` 模式

## 文件组织
- 新组件放在 `src/components/` 下
- 工具函数放在 `src/utils/` 下
- 测试文件与源码同目录，命名 `*.test.ts`

## 特殊规则
- 修改 `src/db/schema.ts` 后必须运行 `npm run db:generate`
- 不要直接修改 `.env` 文件
```

AGENTS.md 的内容会被 `session/prompt.ts` 读取并注入到 system prompt 中，成为 Agent 的"项目上下文记忆"。

---

## 2.6 snapshot/ 与 /undo：方便但不能替代 Git

`snapshot/` 模块提供**轻量级的代码变更追踪**，让你可以快速回滚 Agent 的修改。

### 2.6.1 Snapshot 的工作原理

当 Agent 执行修改类工具（edit、write、apply_patch）时，snapshot 系统会：

1. **变更前**：保存文件的原始内容到 snapshot 存储
2. **变更后**：记录变更的元数据（文件名、变更类型、时间戳）
3. **恢复时**：将文件内容还原到变更前的状态

```
Agent 调用 edit
  │
  ▼
┌─────────────────────┐
│ 保存原始文件到 snapshot │ ◀── 变更前快照
└─────────────────────┘
  │
  ▼
执行 edit
  │
  ▼
┌─────────────────────┐
│ 记录变更元数据        │ ◀── 变更后记录
└─────────────────────┘
```

### 2.6.2 /undo 命令

OpenCode CLI 提供 `/undo` 命令来触发回滚：

```bash
# 回滚最后一次 Agent 修改
/undo

# 查看可回滚的变更列表
/undo list
```

### 2.6.3 重要提醒：Snapshot ≠ Git

> ⚠️ **Snapshot 是方便工具，不是版本控制系统。**
>
> - Snapshot 只在当前会话内有效，**不会跨会话持久化**
> - Snapshot 不记录变更的**语义**（为什么改、与哪个需求关联）
> - Snapshot 不支持**分支、合并、diff** 等版本控制操作
>
> **最佳实践**：Agent 完成一批修改后，**总是用 Git 提交**。将 `/undo` 视为"刚才的修改有问题，先回退一下"的快捷方式，而非替代 `git revert` 或 `git checkout` 的机制。

---

## 2.7 扩展机制：MCP、Plugins 与 Server

除了上述核心模块，OpenCode 还提供多种扩展机制，让它从"本地 CLI 工具"向"开发平台"演进。

### 2.7.1 MCP（Model Context Protocol）

MCP 是 OpenCode 与外部工具集成的标准化协议。通过 MCP，你可以：

- 连接自定义数据源（内部文档库、API 文档）
- 接入私有工具（公司内部的代码搜索、部署系统）
- 与其他 AI 应用共享上下文

MCP 工具通过 `tool/registry.ts` 的 `loadPluginTools()` 方法加载，与内置工具一样参与权限控制。

### 2.7.2 Plugins

Plugin 机制允许开发者扩展 OpenCode 的功能：

- 自定义工具（通过 npm 包形式分发）
- 自定义 Agent 行为
- 自定义命令和快捷键

### 2.7.3 Server 模式

OpenCode 支持以 server 模式运行，提供 HTTP API：

```bash
# 启动 OpenCode Server
opencode server --port 8080
```

Server 模式下，其他应用可以通过 API 调用 OpenCode 的能力，实现：

- IDE 插件集成（VS Code、JetBrains 等）
- CI/CD 流水线自动化
- 团队协作工作流

v1.15.13 中，Server 模式增加了**后台 Agent 推送**支持，允许长时间运行的任务异步通知客户端进度。

---

## 2.8 模块协作全景图

让我们用一个完整的用户请求流程，串联所有模块的协作：

```
用户输入："给登录功能添加验证码"
  │
  ▼
┌─────────────────────────────────────────────────────────┐
│  session/processor.ts                                    │
│  - 创建 message-v2 消息                                  │
│  - 读取 AGENTS.md 项目规则                               │
│  - 调用 prompt.ts 构造 system prompt                     │
└─────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────┐
│  agent/Build（主 Agent）                                  │
│  - 接收任务，分析需求                                    │
│  - 决定先让 Scout 定位登录相关代码                        │
└─────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────┐
│  tool/registry.ts                                        │
│  - 为 Scout 加载只读工具集（read/grep/glob/lsp）         │
│  - 应用 Scout 的权限配置（v1.15.13 独立权限）            │
└─────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────┐
│  Scout 执行 grep "login" / read 相关文件                  │
│  - 返回 Observation（文件列表和关键代码片段）              │
└─────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────┐
│  Build 基于 Observation 制定计划                          │
│  - 创建 todo 列表（修改登录页、添加后端接口、更新测试）     │
│  - 开始执行 edit/write 工具                              │
└─────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────┐
│  permission/                                             │
│  - 检查 edit 权限：Build Agent 有 allow 权限 → 执行       │
│  - 检查 write 到 .env：路径权限 deny → 拒绝               │
└─────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────┐
│  snapshot/                                               │
│  - 每个 edit 前保存原始文件                              │
│  - 记录变更历史                                          │
└─────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────┐
│  任务完成                                                │
│  - session/summary.ts 生成会话摘要                       │
│  - todo.ts 标记所有任务完成                              │
│  - status.ts 更新为 idle                                 │
│  - 提示用户：记得 git commit！                           │
└─────────────────────────────────────────────────────────┘
```

---

## 2.9 本章小结

| 模块 | 一句话概括 | 关键文件 |
|---|---|---|
| `session/` | Agent Loop 的主控大脑 | `processor.ts`、`prompt.ts`、`message-v2.ts` |
| `tool/` | Agent 的手和眼 | `registry.ts`、内置工具集 |
| `permission/` | 自治的安全边界 | 三级权限模型、agent 级权限（v1.15.13） |
| `agent/` | 不同角色的策略封装 | Build、Plan、Explore、Scout、系统 Agent |
| `snapshot/` | 轻量级回滚机制 | snapshot 存储、`/undo` 命令 |

理解这些模块的分工，你就掌握了 OpenCode 的"骨架"。下一章我们将深入探讨如何自定义 Agent 行为，通过 AGENTS.md 和配置文件让 OpenCode 适应你的团队和项目规范。

---

## 版本变更日志

### v1.15.13
- **新增**：Header timeout 机制，提升长时间 LLM 请求的稳定性
- **新增**：后台 Agent 推送，支持异步任务状态通知
- **新增**：Agent 级别的独立权限设置
- **修复**：权限规则顺序评估逻辑
- **修复**：`OPENCODE_CONFIG_CONTENT` 环境变量优先级

### v1.14.32
- **修复**：Prompt 编辑相关问题
- **修复**：工作区目录访问边界
- **修复**：图像消息编码和处理
- **修复**：Agent 目录访问权限
