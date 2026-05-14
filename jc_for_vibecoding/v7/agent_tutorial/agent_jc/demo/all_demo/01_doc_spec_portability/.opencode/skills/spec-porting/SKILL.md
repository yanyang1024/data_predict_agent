---
name: spec-porting
description: use when the user asks to migrate or port a web app across frameworks based on a functional spec, historical source implementation, frontend style rules, migration requirements, and sample validation cases; plan first, generate only candidate code, run validation, and report review items.
compatibility: opencode
metadata:
  language: zh-CN
  demo: context-engineering-01
---

# Spec Porting Skill

## 目标

把“基于历史文档、用户迁移要求和样例的 Web App 跨框架迁移开发”变成稳定流程：先取证、再计划、再生成、再验证、最后交付 review 清单。

## 必读 context

1. `docs/user_migration_request.md`：用户提出的迁移目标和限制。
2. `docs/csv_analysis_app_spec.md`：框架无关功能要求。
3. `docs/gradio_to_flask_migration_spec.md`：Gradio 到 Flask 的组件映射和人工确认点。
4. `docs/frontend_style_spec.md`：迁移后必须保持的界面风格。
5. `references/source/gradio_csv_analyzer.py`：原始 Gradio 实现，只读。
6. `references/examples/flask_reference_style.py`：目标 Flask 风格参考，只读。
7. `tests/analysis_cases.json` 和 `tests/*.csv`：标准路径、无数值列、缺失值和错误路径验收，只读。

## 工作流

1. 输出迁移计划：列出 Gradio 组件、目标 Flask route/template/static 映射、功能保持点、前端风格保持点和风险。
2. 只生成候选实现到 `generated/`。
3. 调用：

```bash
python3 scripts/port_gradio_to_flask.py --source references/source/gradio_csv_analyzer.py --request docs/user_migration_request.md --style-spec docs/frontend_style_spec.md --output-dir generated/flask_app --report output/migration_report.md
```

4. 调用验证：

```bash
python3 scripts/validate_flask_port.py --project-dir generated/flask_app --cases tests/analysis_cases.json
```

5. 启动或重启 viewer：

```bash
python3 ../scripts/demo_viewer.py --demo 01_doc_spec_portability --port 8761 --restart
```

6. 回答中必须包含：
   - 迁移依据；
   - 自动验证结果；
   - 浏览器 URL；
   - 样例和边界 CSV 未覆盖项；
   - 是否需要人工确认上传安全、Flask 部署和复杂绘图需求。

## Stop Rules

- 不要修改 `docs/`、`references/`、`tests/analysis_cases.json` 或 `tests/*.csv`。
- 如果用户要求绕过前端风格规范或丢掉 CSV 分析功能，必须先停下来说明影响。
- 如果样例验证失败，必须停止并报告失败，不要继续扩写功能。
- 不要声称生成的 Flask 项目已满足生产上传安全和部署要求。
