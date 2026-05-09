# OpenCode Agent & Vibe Coding Teaching Demos v2

这是一套用于 1 小时教学演示的从 0 到 1 demo 仓库，重点不在具体业务实现，而在通过小样例讲清楚：

1. 如何用 OpenCode 协同完成一个可稳定运行的 agent 应用；
2. 如何把一次性的 prompt 变成可复用的 Skill / Command / Tool / Rules；
3. 如何把文档、spec、富文本规则和受控脚本串成可验证流程；
4. 如何通过权限和封装脚本约束 Agent 的执行空间。

## 60 分钟推荐讲法

| 时间 | Demo | 教学目标 | 讲师动作 |
|---:|---|---|---|
| 0-10 min | Demo 00: 基于规则的文档生成 | 用一句话生成 PPT、Excel、甘特图和 dashboard，介绍 OpenCode 从 0 到 1 工作流 | 展示 AGENTS.md、command、skill、script、输出物 |
| 10-25 min | Demo 01: Doc Spec 可移植开发 | 基于历史文档和样例，抽取规范并生成不同平台实现 | Plan: 读 spec；Act: 生成实现；Validate: 跑 golden cases |
| 25-45 min | Demo 02: 富文本规则提取与 Skill 串联 | 从 PDF/富文本提取验证规则，生成环境适配代码，并强调人工验证介入 | 展示 pipeline skill 调用 sub-skills 和 human review gates |
| 45-57 min | Demo 03: 权限约束执行 | 重要数据和配置不让 Agent 直接操作，只能调用 approved scripts | 展示 opencode.json、safe CLI、拒绝直连/直改 |
| 57-60 min | 总结 | Prompt -> Skill -> Tool -> Permission | 一页 takeaway |

## 一键运行

```bash
python3 run_all_demos.py
```

每个 demo 都有独立 README、OpenCode 配置、Command、Tool、Skill 目录和脚本。`run_all_demos.py` 会生成 Demo 00-02 的完整输出；Demo 03 是权限边界教学，建议按该 demo 的 README 单独运行安全查询、报告渲染、配置变更 proposal 和权限测试，便于现场逐步讲解。

## 推荐 OpenCode 演示入口

```text
# Demo 00
/teach-status 基于今天 1 小时 OpenCode + Agent 教学安排，生成当前进度看板、PPT大纲和 Excel 甘特图；当前已完成开场，Demo0 正在进行，用户问题：怎么保证 Agent 生成物稳定？

# Demo 01
/build-portable-spec 请基于 docs/order_pricing_spec.md 和 examples/ 生成 Python 与 Node 两个平台实现，并运行 golden cases。

# Demo 02
/extract-adapt-validate 请从 source_docs/validation_manual.pdf 提取验证规则，适配 env_package，并运行语法验证。

# Demo 03
/safe-query 请查询 training_metrics 最近 14 天的 step, value, owner 字段并生成安全报告；不要读取 protected_data。
```

## 教学提醒

- 这些样例故意保持简单，便于讲清楚流程。
- 重点不是“AI 一次性写完”，而是“Plan -> Act -> Validate -> Human Review -> Skill 化”。
- 所有生产相关数据、配置、manual 和业务名词均为模拟。
