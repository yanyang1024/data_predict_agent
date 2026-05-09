# Demo00 项目规则

1. 本 demo 不连接任何外部系统。
2. 不要让 Agent 直接“自由设计”PPT 结构；必须先读取 `templates/slide_outline.json` 和 `references/report_template.md`。
3. 用户的一句话需求应先被归一化到 `inputs/course_status.json`，再由脚本生成文件。
4. 生成后必须运行 `scripts/validate_outputs.py`。
5. PPT/Excel/HTML 的内容正确性需要讲师人工确认；脚本只验证文件存在和关键字段。
