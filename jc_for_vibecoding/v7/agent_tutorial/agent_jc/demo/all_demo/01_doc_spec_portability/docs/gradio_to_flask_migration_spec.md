# Gradio -> Flask Web App 迁移规范

## 迁移目标

把 `references/source/gradio_csv_analyzer.py` 中的 Gradio CSV 分析应用迁移为 Flask 项目：

```text
原始 Gradio Blocks 应用
  -> Flask route + Jinja template + static CSS
  -> 保持 CSV 分析和绘图功能一致
  -> 保持 `docs/frontend_style_spec.md` 中定义的前端界面风格
```

## 框架映射

| Gradio 实现 | Flask 实现 |
|---|---|
| `gr.Blocks` 页面结构 | `templates/index.html` |
| `gr.File` 上传控件 | `request.files["csv_file"]` |
| `gr.Markdown` 总览 | summary cards |
| `gr.Dataframe` 数值摘要 | HTML table |
| `gr.Plot` / HTML 图表 | inline SVG chart |
| `css=` 自定义样式 | `static/styles.css` |
| `demo.launch()` | `app.run()` |

## 必须保持一致

- CSV 输入语义保持一致。
- 行数、列数、数值列识别和数值摘要口径保持一致。
- 推荐绘图列优先选择第一个完整数值列。
- 页面视觉风格遵循 `docs/frontend_style_spec.md`。
- 生成代码必须放在 `generated/flask_app/`。

## 人工确认点

- 生产环境是否允许浏览器直接上传 CSV。
- 文件大小限制、MIME 校验、病毒扫描和审计策略。
- SVG 图是否满足业务方真实绘图需求。
- Flask 部署方式和依赖安装方式。

