# 从 Agent 技术演进到 OpenCode 工程实践：面向软件研发人员的 Coding Agent 教程

> 目标读者：有日常编码、调试、Code Review、测试经验的软件研发人员。
> 教程目标：不是把 OpenCode 当成"AI 聊天窗口"介绍，而是把它作为一个可观测、可配置、可治理的 coding agent runtime 来讲清楚：它如何继承 ReAct / SWE-agent 的思想，如何通过 session、agent、tool、permission、snapshot 等模块落地，以及研发团队应该如何安全使用。

---

## 文档结构

| 章节 | 文件 | 内容概要 |
|---|---|---|
| 第 0 章 | [00-one-sentence-positioning.md](00-one-sentence-positioning.md) | 一句话定位：成熟的 coding agent 是什么 |
| 第 1 章 | [01-agent-evolution.md](01-agent-evolution.md) | 技术演进主线：ReAct → Tool Calling → SWE-agent → OpenCode |
| 第 2 章 | [02-opencode-architecture.md](02-opencode-architecture.md) | OpenCode 的 Agent 抽象与源码模块视角 |
| 第 3 章 | [03-configuration-hierarchy.md](03-configuration-hierarchy.md) | **配置层级体系**：全局配置、用户配置、项目配置；模型选择与 API Key 管理 |
| 第 4 章 | [04-path-resolution-pitfalls.md](04-path-resolution-pitfalls.md) | **路径解析坑点**：Skill/Tool/Script 的引用路径、默认原点、agent 调用时的路径问题 |
| 第 5 章 | [05-sop-workflow.md](05-sop-workflow.md) | 面向研发人员的 OpenCode 使用 SOP、安全基线与 AGENTS.md 模板 |
| 第 6 章 | [06-common-pitfalls.md](06-common-pitfalls.md) | 常见坑与解决方案 |
| 第 7 章 | [07-prompts-and-conclusion.md](07-prompts-and-conclusion.md) | Prompt 模板与教程结语 |

---

## 阅读建议

- **快速上手**：阅读第 0 章定位 → 第 3 章了解配置 → 第 5 章按 SOP 开始使用。
- **深入理解**：按顺序阅读第 1-2 章理解技术背景与架构。
- **避坑排雷**：第 4 章（路径问题）和第 6 章（运行时坑点）是工程实践中最常踩的坑，建议所有使用者阅读。
- **团队落地**：重点关注第 3 章（团队级配置管理）和第 5 章（SOP 与模板）。

---

## 关键新增内容

相比原始文档，本次重组重点补充了以下内容：

1. **三级配置体系**：详细说明全局配置（`~/.config/opencode/`）、用户配置（`~/.opencode/`）和项目配置（`.opencode/`）的优先级、覆盖规则和实际使用场景。
2. **模型选择与 API Key 配置**：在不同配置层级中如何选择 LLM 模型、填写 API Key，以及多模型切换的实际操作。
3. **路径解析深度指南**：Skill 和 Tool 的脚本在 agent 对话中如何被引用、默认路径原点是哪里、`SKILL.md` 与 `reference` 文档中的路径描述如何与 agent 实际执行时的工作目录对应。
