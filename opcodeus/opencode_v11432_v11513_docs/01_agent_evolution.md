# 01. 从 Agent 技术演进到 OpenCode 工程实践

> 目标读者：有日常编码、调试、Code Review、测试经验的软件研发人员。  
> 教程目标：不是把 OpenCode 当成“AI 聊天窗口”介绍，而是把它作为一个可观测、可配置、可治理的 coding agent runtime 来讲清楚。

## 1. 一句话定位

一个成熟的 coding agent 不是“更会写代码的模型”，而是：

> **模型 + 代码仓库上下文 + 工具动作空间 + 权限系统 + 会话状态 + 快照/回滚 + 团队规则 的工作系统。**

OpenCode 可以作为这条演进链在本地开发场景中的一个工程化样本：

```text
ReAct 的思考-行动-观察闭环
  -> Function Calling / Tool Calling 的结构化动作
  -> SWE-agent 的软件工程专用 ACI
  -> OpenCode 的本地 coding agent runtime
```

## 2. ReAct：Agent 的最小闭环

ReAct 的价值不是“让模型说出更多推理”，而是建立一个循环：

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

## 3. Tool Calling：把“我想做”变成“可执行动作”

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

对应到 OpenCode，就是 `read`、`grep`、`glob`、`bash`、`edit`、`write`、`apply_patch`、`skill`、`todowrite`、`webfetch`、`websearch`、`question` 等工具。模型不再只是“建议你运行测试”，而是可以请求运行具体命令、读取具体文件、修改具体代码。

> 修订说明：原文中的 `list`、`task`、`repo_clone`、`repo_overview` 不建议写成 v1.14.32/v1.15.13 的稳定公开内置工具。官方 Tools 文档列出的稳定工具以上述工具为主；子代理能力应通过 agent/subagent 机制描述，而不是强依赖名为 `task` 的工具。

## 4. SWE-agent：软件工程需要专门的 ACI

通用工具对 coding agent 不够。软件开发任务天然需要：

- 文件阅读和搜索
- 精确编辑和补丁应用
- 终端命令
- 测试输出
- LSP 语义信息
- 代码库规则
- 会话轨迹和回滚

这就是 SWE-agent 的 Agent-Computer Interface 思想：给 agent 一张适合软件工程的“工作台”，而不是让它只靠聊天窗口猜。

## 5. OpenCode：把 coding agent 做成本地运行时

OpenCode 可以这样理解：

```text
OpenCode = 本地 TUI / CLI / Server / Desktop / IDE 集成
         + 多 provider LLM 调用
         + Agent / Subagent 配置
         + Tool Registry
         + Permission Gate
         + Session Processor
         + Snapshot / Undo
         + AGENTS.md / Skills / Commands / MCP / Plugins
```

它的关键价值不是“生成一段代码”，而是把研发过程中的“查、改、跑、验、审、回滚”串成一个可配置的运行时。

## 6. OpenCode 学习路线建议

面向软件研发人员，不建议一开始讲“怎么让模型写代码”。更合理的路线是：

1. 先理解 agent loop：模型如何观察、行动、接收反馈。
2. 再理解工具：读、搜、改、跑、查文档分别对应哪些 tool。
3. 再理解权限：哪些动作自动运行，哪些动作必须问，哪些动作必须禁止。
4. 再理解上下文：规则文件、命令模板、skill、子代理、长会话压缩如何进入上下文。
5. 最后理解治理：Git checkpoint、日志、快照、cache、provider、私有模型、性能排查。

一个适合教程中的比喻：

> ReAct 像“会自己排障的实习生”；OpenCode 像“带 IDE、终端、工单、权限审批、代码快照的本地开发工位”。
