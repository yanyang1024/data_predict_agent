---
description: 根据一句话课程进度输入生成 PPT、Excel 看板和 Gantt HTML
agent: plan
---

请使用 `teaching-document-generator` skill。

用户需求：

$ARGUMENTS

执行要求：

1. 先读取 `AGENTS.md`、`references/report_template.md`、`templates/slide_outline.json`。
2. 先在对话中提取结构化 `course_status`，不要立即写文件。
3. 等用户确认后，更新 `inputs/course_status.json`。
4. 再切换到可执行阶段，运行：

```bash
python3 scripts/build_course_assets.py --status inputs/course_status.json --request inputs/one_sentence_request.txt --output output
python3 scripts/validate_outputs.py --output output
```

5. 最终说明哪些内容由脚本验证，哪些内容仍需讲师人工确认。
