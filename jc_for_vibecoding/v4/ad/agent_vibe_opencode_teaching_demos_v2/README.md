# OpenCode Agent 应用从 0 到 1：四个教学型 Demo

这套项目用于 1 小时左右的 Agent / Vibe Coding 实战教学。它不追求贴近某个真实部门系统，而是用四个足够简单、可运行、可讲解的项目，说明如何在 OpenCode 中把业务场景沉淀成稳定上下文：

```text
用户一句话 / 文件输入
  → OpenCode 对话
  → AGENTS.md 项目规则
  → Command 固定入口
  → Skill 任务流程
  → references/templates 业务知识
  → tool/api/script 受控执行动作
  → validator/report 人机协同验收
```

## 四个 Demo

| Demo | 教学主题 | 重点沉淀的上下文 | 一句话说明 |
|---|---|---|---|
| 00 | 基于规则的文档生成 | 模板、课程状态、PPT/Excel/Gantt 生成脚本、Skill 编排 | 用户一句话更新课程进度，生成 PPT、Excel 看板和 Gantt HTML |
| 01 | Doc Spec 开发规范与可移植实现 | 历史文档、历史样例、平台契约、可移植性检查表 | 从统一规范生成跨平台实现，并用测试保护语义一致性 |
| 02 | 富文本 / PDF 信息抽取到测试适配 | 抽取规则、环境包契约、模块串联 Skill、语法验证脚本 | 从富文本说明中抽取验证模式和原生指令，适配到目标环境代码 |
| 03 | 权限约束与受控数据操作 | 权限规则、安全 API、参数白名单、审计日志、Stop Rules | 避免 Agent 直接碰重要数据和配置，用封装脚本收窄执行空间 |

## 建议 1 小时讲解节奏

```text
00-08 min  Demo00：从一句话到 PPT/Excel/Gantt，讲清 OpenCode 辅助项目工作流
08-23 min  Demo01：从 Doc Spec 到多平台实现，讲清历史文档和样例如何变成上下文
23-40 min  Demo02：从富文本抽取到测试适配，讲清 Skill 串联、执行动作和人工确认点
40-55 min  Demo03：权限边界与受控执行，讲清 API/脚本/参数白名单/审计日志
55-60 min  Takeaway：Prompt → Context → Skill → Tool/API → Validator → Human Review
```

## 一键运行

```bash
python3 run_all_demos.py
```

每个子目录也可以单独运行，详见对应 `README.md`。

## OpenCode 使用方式

每个 demo 都包含：

```text
AGENTS.md                       项目长期规则
opencode.json                   权限和指令配置
.opencode/commands/*.md         常用任务入口
.opencode/tools/*.ts            Agent 可调用工具封装示例
.opencode/skills/<name>/        可复用任务 Skill，含 references/scripts/templates
scripts/*.py                    实际可运行脚本
inputs/docs/examples/configs    对话之外沉淀的业务上下文
output/                         示例输出
```

课堂建议先让学员看 `AGENTS.md` 和 `SKILL.md`，再看 scripts。这样能避免“把脚本扔给 AI”的误区：Agent 应用稳定性的核心，不是单次 prompt，而是上下文、边界、执行和验证的组合。
