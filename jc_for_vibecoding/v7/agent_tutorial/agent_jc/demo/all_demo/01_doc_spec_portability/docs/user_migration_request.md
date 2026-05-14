# User Migration Request

请把原始 Gradio Web App 迁移成 Flask 实现。

原始应用用于用户上传 CSV table 后做数据分析和绘图。迁移后需要保持相同功能场景，并且遵循相同的前端界面风格规范。

输入包括：

- 原始项目实现代码：`references/source/gradio_csv_analyzer.py`
- 迁移要求：实现方式改为 Flask，前端风格保持一致
- 功能说明：`docs/csv_analysis_app_spec.md`
- 前端风格规范：`docs/frontend_style_spec.md`

输出应该是 Flask 项目实现代码，写入 `generated/flask_app/`。

