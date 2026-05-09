# Demo00：基于规则的文档生成

## 教学目标

这是整个实践的入口 demo。它展示一个非常通用的 Agent 应用：用户只说一句话，Agent 根据沉淀好的模板和规则，把课程进度生成成 PPT、Excel 看板和 Gantt HTML。

它用来讲解：

```text
一句话需求
  → Agent 解析为结构化 course_status.json
  → Skill 规定生成流程
  → references/templates 提供模板和口径
  → scripts 生成 PPT/Excel/HTML
  → validator 检查输出
  → 人确认内容是否符合真实课程进度
```

## 为什么适合作为第 0 个 demo

1. 场景通用，所有学员都容易理解。
2. 输出物直观：PPT、Excel、Gantt dashboard。
3. 可以清楚解释“LLM 负责理解和归纳，脚本负责稳定生成”。
4. 可以自然引出 OpenCode 的 AGENTS.md、Command、Skill、Tool 和权限。

## 运行

```bash
cd 00_rule_based_document_generation
python3 scripts/build_course_assets.py --status inputs/course_status.json --request inputs/one_sentence_request.txt --output output
python3 scripts/validate_outputs.py --output output
```

生成文件：

```text
output/course_update.pptx
output/course_dashboard.xlsx
output/gantt_dashboard.html
output/agent_summary.md
output/context_manifest.json
```

## OpenCode 对话演示

Plan 阶段：

```text
请使用 teaching-document-generator skill。
我想更新培训进度：1 小时课程，四个 demo，当前第 0 个 demo 已完成，第 1 个 demo 正在讲 doc spec，第 2 个 demo 准备讲富文本抽取，第 3 个 demo 讲权限边界。用户问题主要集中在 Skill 目录、Tool 和权限配置。请先不要生成文件，先提取结构化进度和输出计划。
```

Build 阶段：

```text
确认按刚才计划执行。请更新 inputs/course_status.json，然后运行脚本生成 PPT、Excel 和 Gantt HTML。完成后运行 validate_outputs.py，并说明哪些内容需要人工确认。
```

## 教学讲解重点

- `inputs/course_status.json` 是结构化业务状态。
- `references/report_template.md` 是输出模板。
- `templates/slide_outline.json` 是 PPT 结构。
- `scripts/build_course_assets.py` 是可执行动作。
- `.opencode/skills/teaching-document-generator/SKILL.md` 是 Agent 作业指导书。
- 人需要确认“进度是否真实、问题是否完整、时间安排是否合理”，脚本只能保证文件生成和格式基本有效。
