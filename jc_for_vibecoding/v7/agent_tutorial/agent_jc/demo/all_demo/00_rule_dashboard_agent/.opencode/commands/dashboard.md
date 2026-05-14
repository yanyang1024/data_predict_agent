---
description: 根据一句话教学进展生成讲师 HTML dashboard 和状态报告
agent: plan
---

Use the `dashboard-generator` skill.

用户请求：

$ARGUMENTS

要求：
1. 先把用户的一句话提取为结构化 progress 字段；不确定的字段使用 `data/sample_progress.json` 的默认结构。
2. 不要修改 `templates/` 和 `references/`。
3. 调用 `scripts/generate_dashboard.py` 生成 `output/dashboard.html` 和 `output/status_report.md`。
4. 调用 `scripts/validate_dashboard.py` 验证。
5. 调用 `../scripts/demo_viewer.py --demo 00_rule_dashboard_agent --port 8760 --restart` 启动或重启 viewer。
6. 最终回答要说明生成依据、默认字段、验证结果、Viewer URL 和 Primary URL。
