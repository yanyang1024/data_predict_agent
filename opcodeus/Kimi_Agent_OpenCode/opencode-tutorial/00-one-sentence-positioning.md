# 0. 一句话定位

一个成熟的 coding agent 不是"更会写代码的模型"，而是：

> **模型 + 代码仓库上下文 + 工具动作空间 + 权限系统 + 会话状态 + 快照/回滚 + 团队规则 的工作系统。**

OpenCode 可以作为这条演进链在本地开发场景中的一个工程化样本：

```text
ReAct 的思考-行动-观察闭环
  -> Function Calling / Tool Calling 的结构化动作
  -> SWE-agent 的软件工程专用 ACI
  -> OpenCode 的本地 coding agent runtime
```

## 把 OpenCode 放在 Agent 演进图谱中看

| 阶段 | 代表 | 解决的问题 | 形态 |
|---|---|---|---|
| ReAct | 论文范式 | 模型不再一次性回答，而是边查边改 | 思维链 + 动作循环 |
| Tool Calling | OpenAI Function Calling | 自然语言 → 结构化可执行动作 | JSON Schema 接口 |
| SWE-agent | Princeton NLP | 软件开发需要专门的工作台 | ACI（Agent-Computer Interface）|
| **OpenCode** | **anomalyco/opencode** | **把 coding agent 做成本地可运行时** | **TUI/CLI + 可配置 Runtime** |

所以，OpenCode 的核心价值不是"生成一段代码"，而是把研发过程中的**查、改、跑、验、审、回滚**串成一个可配置、可观测、可治理的运行时。
