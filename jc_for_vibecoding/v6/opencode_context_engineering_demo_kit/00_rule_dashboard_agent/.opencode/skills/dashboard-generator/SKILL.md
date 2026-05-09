---
name: dashboard-generator
description: use when the user asks to create or update a teaching progress dashboard, gantt chart, status report, or html board from a short natural-language update; convert conversation context into structured progress json, render approved templates, and validate outputs.
compatibility: opencode
metadata:
  language: zh-CN
  demo: context-engineering-00
---

# Dashboard Generator Skill

## 目标

把用户的一句话进展说明转成稳定的教学看板，而不是每次临时写 HTML。

## Context 加载顺序

1. 读项目 `AGENTS.md`。
2. 读 `references/context/dashboard_schema.md`。
3. 如需模板说明，读 `templates/dashboard_template_notes.md`。
4. 调用脚本，不要手写完整 HTML。

## 工作流

1. 归一化输入：课程总时长、当前分钟、四个 demo 的状态、用户问题、下一步。
2. 如果字段缺失，使用 `data/sample_progress.json` 的结构作为默认模板，并在报告中说明。
3. 调用：

```bash
python3 scripts/generate_dashboard.py --input data/sample_progress.json --output-dir output
```

如用户给出明确的 JSON，可改用该 JSON。

4. 验证：

```bash
python3 scripts/validate_dashboard.py --output-dir output
```

5. 输出回答：说明输入来源、生成文件、验证结果、仍需人工确认的教学内容。

## Stop Rules

- 不要把用户的临时自然语言直接当作最终事实；不确定时标记为默认值或待确认。
- 不要覆盖模板或 schema。
- 不要声称 dashboard 内容代表真实教学进度，除非讲师确认。
