# 从 Agent 技术演进到 OpenCode 工程实践：面向软件研发人员的 Coding Agent 教程

> **目标读者**：有日常编码、调试、Code Review、测试经验的软件研发人员。
>
> **教程目标**：不是把 OpenCode 当成"AI 聊天窗口"介绍，而是把它作为一个**可观测、可配置、可治理的 coding agent runtime** 来讲清楚：它如何继承 ReAct / SWE-agent 的思想，如何通过 session、agent、tool、permission、snapshot 等模块落地，以及研发团队应该如何安全使用。

## 一句话定位

一个成熟的 coding agent 不是"更会写代码的模型"，而是：

> **模型 + 代码仓库上下文 + 工具动作空间 + 权限系统 + 会话状态 + 快照/回滚 + 团队规则** 的工作系统。

OpenCode 可以作为这条演进链在本地开发场景中的一个工程化样本：

```
ReAct 的思考-行动-观察闭环
  -> Function Calling / Tool Calling 的结构化动作
  -> SWE-agent 的软件工程专用 ACI
  -> OpenCode 的本地 coding agent runtime
```

## 版本适用性说明

本教程基于 **OpenCode v1.14.32** 和 **v1.15.13** 版本编写，覆盖核心架构与常用功能。若你使用的是更新版本，大部分概念和配置仍然适用，但部分 UI 界面和默认设置可能有所变化，建议以官方最新文档为准。

## 文档导读

| 章节 | 内容概要 |
|------|---------|
| **01 - ReAct 与 Tool Calling 基础** | 理解 ReAct 循环、Tool Calling 机制，以及 OpenCode 中 tool schema 的定义方式 |
| **02 - 配置你的第一个 Agent** | 从安装到运行，配置模型 provider、system prompt、可用工具集 |
| **03 - Session 与上下文管理** | Session 的生命周期、上下文窗口管理、多轮对话中的状态维护 |
| **04 - Permission 与安全防护** | 权限分级、命令执行控制、文件访问边界、团队安全策略 |
| **05 - Snapshot 与回滚机制** | 快照的创建与恢复、基于 Git 的变更追踪、安全网设计 |
| **06 - 团队治理与最佳实践** | 配置即代码、规则模板、Code Review 工作流、多成员协作 |

建议按顺序阅读前四章以建立完整认知，后两章可根据实际关注点选读。
