# Context 分层速查表

| 层 | 放什么 | 在 OpenCode 中的位置 | 作用 |
|---|---|---|---|
| 对话层 | 用户当前需求、限制、反馈 | 当前聊天 | 说明这一次要做什么 |
| 规则层 | 项目结构、禁止操作、测试命令、编码规范 | `AGENTS.md` | 每次会话都应该遵守 |
| 流程层 | 某类任务怎么做、何时停止、如何报告 | `.opencode/skills/<name>/SKILL.md` | 把一次 prompt 变成一类 SOP |
| 入口层 | 高频任务的一句话命令 | `.opencode/commands/*.md` | 降低用户发起任务门槛 |
| 动作层 | 可执行能力、受控 API、脚本封装 | `.opencode/tools/*.ts`、`scripts/*.py` | 让 Agent 真正能做事 |
| 证据层 | 历史文档、样例、schema、模板、golden cases | `references/`、`docs/`、`tests/` | 让 Agent 有依据，不凭空生成 |
| 观察层 | 测试结果、lint、manifest、diff、报告 | `output/`、`manifest.json` | 让 Agent 能验证和纠偏 |
| 安全层 | 权限、白名单、sandbox、stop rules | `opencode.json`、Skill stop rules | 缩小动作空间，避免误操作 |

## 四个设计原则

1. 先设计动作空间，再谈自治。
2. 先让 Agent 学会取证、验证和纠偏，再要求它自动完成任务。
3. 不要把上下文当成越来越大的 Prompt，要把它当成可分层、可外部化、可交接的系统。
4. 生产里的 Agent 稳定性来自运行时、记忆、协议、工具、安全和工作流的组合。
