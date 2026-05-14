# Demo 01 Rules

## 允许修改

- `generated/`
- `output/`

## 禁止修改

- `docs/`
- `references/source/`
- `references/examples/`
- `tests/analysis_cases.json`
- `tests/*.csv`

## 验证命令

```bash
python3 scripts/port_gradio_to_flask.py --source references/source/gradio_csv_analyzer.py --request docs/user_migration_request.md --style-spec docs/frontend_style_spec.md --output-dir generated/flask_app --report output/migration_report.md
python3 scripts/validate_flask_port.py --project-dir generated/flask_app --cases tests/analysis_cases.json
python3 ../scripts/demo_viewer.py --demo 01_doc_spec_portability --port 8761 --restart
```

## Agent 要求

1. 先解释用户迁移要求、功能 spec、Gradio->Flask 映射和前端风格规范，不要直接改代码。
2. 迁移后必须跑标准路径、边界 CSV 行为验证和静态风格验证。
3. 验证后启动或重启 viewer 服务，暴露迁移报告、Flask 项目代码、迁移可视化图和验证 manifest。
4. 如果脚本只能证明样例 CSV 通过，必须说明还需要人工 review 上传安全、部署和复杂绘图需求。
