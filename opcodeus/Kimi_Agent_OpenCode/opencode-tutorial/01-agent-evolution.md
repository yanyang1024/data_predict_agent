# 1. 技术演进主线：从"会想"到"能安全地改代码"

---

## 1.1 ReAct：Agent 的最小闭环

ReAct 的价值不是"让模型说出更多推理"，而是建立了一个循环：

```text
观察任务 -> 形成假设 -> 调用动作 -> 接收观察 -> 修正计划 -> 再行动
```

放到研发场景里，就是：

```text
怀疑 bug 在鉴权中间件
-> grep 路由入口
-> read 认证逻辑
-> 跑一条失败测试
-> 发现根因在 token refresh
-> 最小修改
-> 再跑测试验证
```

所以，ReAct 阶段解决的是：**模型不再只做一次性回答，而是可以边查边改、边改边验证。**

### 为什么 ReAct 对 coding 不够

ReAct 定义了循环范式，但没解决：
- 动作如何稳定执行（自然语言不可靠）
- 动作空间如何定义（通用 vs 专用）
- 改错了如何回滚
- 团队如何治理权限

这就引出了 Tool Calling。

---

## 1.2 Tool Calling：把"我想做"变成"可执行动作"

自然语言的动作无法稳定执行。Coding agent 需要把动作做成结构化接口：

```json
{
  "tool": "grep",
  "input": {
    "pattern": "refreshToken",
    "path": "src"
  }
}
```

这一步对应到 OpenCode，就是 `read`、`grep`、`glob`、`bash`、`edit`、`write`、`apply_patch`、`task`、`skill`、`webfetch` 等工具。模型不再只是"建议你运行测试"，而是可以请求运行某个具体命令、读取某个文件、修改某段代码。

### Tool Calling 的本质变化

| 维度 | 之前 | 之后 |
|---|---|---|
| 交互方式 | 模型输出文本，人复制粘贴执行 | 模型输出结构化 tool call，runtime 自动执行 |
| 可靠性 | 人解释、人执行、易出错 | Schema 校验、参数类型安全 |
| 可观测性 | 黑盒对话 | 每个动作可记录、可审计、可拦截 |
| 可治理性 | 无法干预 | Permission Gate 可以 allow/ask/deny |

---

## 1.3 SWE-agent：软件工程需要专门的 ACI

通用工具对 coding agent 不够。软件开发任务天然需要：

- **文件阅读和搜索**：在大型代码库中快速定位
- **精确编辑和补丁应用**：最小化变更，避免重写整个文件
- **终端命令**：运行测试、构建、lint
- **测试输出**：验证修改是否正确
- **LSP 语义信息**：理解类型、引用、定义
- **代码库规则**：项目特定的约定和约束
- **会话轨迹和回滚**：改错了能恢复

这就是 SWE-agent 的 Agent-Computer Interface（ACI）思想：**给 agent 一张适合软件工程的"工作台"，而不是让它只靠聊天窗口猜。**

### ACI 的关键设计

```text
编辑器（view/edit）+ 终端（bash）+ 搜索（grep/find）+ 测试（test）
  = 软件工程专用的动作空间
```

OpenCode 继承了这一思想，并在其 `tool/` 目录中实现了类似的工具集。

---

## 1.4 OpenCode：把 coding agent 做成本地运行时

OpenCode 可以这样理解：

```text
OpenCode = 本地 TUI / CLI / Server
         + 多 provider LLM 调用
         + Agent 配置（Build / Plan / Explore / Scout）
         + Tool Registry（内置 + 自定义 + MCP + Plugin）
         + Permission Gate（allow / ask / deny）
         + Session Processor（ReAct loop 主控）
         + Snapshot / Undo（会话级回滚）
         + AGENTS.md / Skills / Commands / MCP / Plugins（扩展机制）
```

### 与前三个阶段的继承关系

| 前驱 | OpenCode 的继承 |
|---|---|
| ReAct 的循环 | `session/processor.ts` 中的 observation → LLM → tool call → observation 循环 |
| Tool Calling 的结构化 | `tool/registry.ts` 中每个工具的 JSON Schema 定义和参数校验 |
| SWE-agent 的 ACI | `tool/` 中的 `read`、`edit`、`bash`、`lsp` 等软件工程专用工具 |

### OpenCode 的工程化增量

除了继承上述能力，OpenCode 还新增了研发落地必需的模块：

| 模块 | 功能 | 源码入口 |
|---|---|---|
| Permission Gate | 把自治变成可控 | `permission/` |
| Session 管理 | 多轮对话状态、压缩、摘要 | `session/` |
| Snapshot / Undo | 会话级回滚（非 Git 替代） | `snapshot/` |
| 多 Agent 策略 | Build/Plan/Explore/Scout 不同角色 | `agent/` |
| 自定义扩展 | Skills、Commands、MCP、Plugins | `AGENTS.md`、`.opencode/` |
| 配置层级 | 全局/用户/项目三级配置 | `~/.config/opencode/`、`~/.opencode/`、`.opencode/` |

一个适合教程中的比喻：

> ReAct 像"会自己排障的实习生"；OpenCode 像"带 IDE、终端、工单、权限审批、代码快照的本地开发工位"。
