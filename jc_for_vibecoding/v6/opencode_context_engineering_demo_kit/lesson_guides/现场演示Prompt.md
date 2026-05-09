# 现场演示 Prompt

## Demo 00

```text
/dashboard 当前培训总时长 60 分钟。Demo 0 已完成，Demo 1 进行中，Demo 2 和 Demo 3 未开始。用户刚问：如何把一个临时 prompt 沉淀成稳定 Agent 应用？请生成讲师 dashboard。
```

## Demo 01

```text
/port-spec 请把 references/source/python_order_rules.py 按 docs/porting_spec_py_to_js.md 的规范迁移到 generated/pricing.mjs。先输出迁移计划和风险点，再调用脚本生成，并运行 golden tests。
```

## Demo 02

```text
/reproduce-paper 请从 papers/synthetic_agent_eval_paper.pdf 提取实验逻辑，结合 env_pkg/ 中的本地环境库，生成一个最小可运行复现项目。不要声称复现了论文全部结论，只验证语法和示例测试。
```

## Demo 03

```text
/safe-change 请把 sandbox 中的 beta_dashboard flag 打开，原因是培训演示需要。不要读取 customer_data.csv，不要修改 protected/prod_config.json，只能通过受控脚本生成 proposal 并应用到 sandbox。
```
