# 现场演示 Prompt

## Demo 00

```text
/dashboard 当前培训总时长 60 分钟。Demo 0 已完成，Demo 1 进行中，Demo 2 和 Demo 3 未开始。用户刚问：如何把一个临时 prompt 沉淀成稳定 Agent 应用？请生成讲师 dashboard。
```

## Demo 01

```text
/port-spec 请把 references/source/gradio_csv_analyzer.py 迁移为 Flask 项目，输出到 generated/flask_app/。要求保持 docs/csv_analysis_app_spec.md 中的 CSV 分析和绘图功能，并遵循 docs/frontend_style_spec.md 的前端风格。先输出迁移计划和风险点，再调用脚本生成，并运行标准路径和边界 CSV 验证。
```

## Demo 02

```text
/reproduce-paper 请从 papers/synthetic_agent_eval_paper.pdf 提取实验逻辑，结合 env_pkg/ 中的本地环境库，生成一个最小可运行复现项目。不要声称复现了论文全部结论，只验证语法和示例测试。
```

## Demo 03

```text
/safe-change 请把 sandbox 中的 beta_dashboard flag 打开，原因是培训演示需要。不要读取 customer_data.csv，不要修改 protected/prod_config.json，只能通过受控脚本生成 proposal 并应用到 sandbox。
```

```text
/query-lot 请查询 LOT-A12 的 QTime / UT 汇总并生成图。不要读取 protected/lot_history_raw.csv，只能通过数据服务脚本返回聚合结果。
```
