# Demo 01：Doc Spec 开发规范与 Web App 跨框架迁移 Agent

## 教学定位

这个 demo 用“Gradio CSV 分析 Web App 迁移到 Flask 项目”的简化场景，讲解基于历史代码、用户迁移要求、功能文档和前端风格规范的开发：

```text
原始 Gradio Web App + 用户迁移要求
  -> Agent 加载功能 spec、Gradio->Flask 迁移规范、前端风格 spec
  -> Agent 调用受控脚本生成 Flask 项目候选实现
  -> Agent 运行标准路径、边界 CSV 行为验证和静态风格验证
  -> Agent 输出迁移报告、Flask 项目代码和人工 review 点
```

它对应真实业务中的“同一应用场景在不同 Web 框架中可移植实现”：例如现在已有一个 Gradio Web App 用于用户上传 CSV table 后做数据分析和绘图，需要按相同功能和相同前端界面风格迁移到 Flask。

## Context 构成

| Context | 文件 | 作用 |
|---|---|---|
| 用户迁移要求 | `docs/user_migration_request.md` | 说明目标框架 Flask、功能一致和前端风格一致 |
| 功能文档 | `docs/csv_analysis_app_spec.md` | 描述 CSV 上传、分析、绘图的语言/框架无关功能 |
| 迁移规范 | `docs/gradio_to_flask_migration_spec.md` | 说明 Gradio 组件到 Flask route/template/static 的映射 |
| 前端风格规范 | `docs/frontend_style_spec.md` | 固定迁移后的界面风格和视觉 token |
| 历史源代码 | `references/source/gradio_csv_analyzer.py` | 待迁移的 Gradio 实现，只读 |
| 目标样例 | `references/examples/flask_reference_style.py` | Flask route factory 风格参考 |
| 测试项 | `tests/analysis_cases.json`、`tests/*.csv` | 标准路径、无数值列、缺失值和空数据错误路径验收 |
| 脚本 | `scripts/port_gradio_to_flask.py` | 生成 Flask 项目和迁移报告 |
| 验证 | `scripts/validate_flask_port.py` | 执行样例行为和静态风格验证 |

## 从 0 到 1 构建步骤

```text
Step 0：收集原始 Gradio Web App 和用户迁移要求
Step 1：整理功能 spec、迁移规范和前端风格 spec
Step 2：写目标 Flask 风格参考和样例 CSV 验收数据
Step 3：先定义分析结果和风格检查验收标准
Step 4：写迁移脚本，生成 Flask 项目和 report
Step 5：写 Skill，规定 Agent 必须先读 spec，再生成，再验证
Step 6：写 Command，变成 /port-spec 一句话入口
Step 7：写 Tool，把脚本封装为结构化动作
Step 8：写权限配置，禁止直接改源材料，只允许写 generated/output
```

## 运行

```bash
python3 run_demo.py
```

运行后会自动启动或重启本地 viewer 服务，输出类似：

```text
Viewer URL: http://127.0.0.1:8761/
Primary URL: http://127.0.0.1:8761/output/migration_report.md
```

## OpenCode 演示 Prompt

```text
/port-spec 请把 references/source/gradio_csv_analyzer.py 迁移为 Flask 项目，输出到 generated/flask_app/。要求保持 docs/csv_analysis_app_spec.md 中的 CSV 分析和绘图功能，并遵循 docs/frontend_style_spec.md 的前端风格。先输出迁移计划和风险点，再调用脚本生成，并运行标准路径和边界 CSV 验证。
```
