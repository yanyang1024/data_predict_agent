---
description: 按迁移规范和样例验证完成 Web App 跨框架候选实现
agent: plan
---

Use the `spec-porting` skill.

用户请求：

$ARGUMENTS

要求：
1. 先阅读 `docs/user_migration_request.md`、`docs/csv_analysis_app_spec.md`、`docs/gradio_to_flask_migration_spec.md`、`docs/frontend_style_spec.md`、`references/source/gradio_csv_analyzer.py`、`tests/analysis_cases.json`。
2. 先给迁移计划、动作空间、Gradio->Flask 映射和人工确认点。
3. 调用 `scripts/port_gradio_to_flask.py` 生成候选 Flask 项目，不要直接修改源文件。
4. 调用 `scripts/validate_flask_port.py` 跑标准路径、边界 CSV 行为验证和静态风格验证。
5. 调用 `../scripts/demo_viewer.py --demo 01_doc_spec_portability --port 8761 --restart` 暴露迁移报告、Flask 项目代码、迁移可视化图和验证 manifest。
6. 最终回答区分：已自动验证的行为、未覆盖风险、人工 review 项和浏览器 URL。
