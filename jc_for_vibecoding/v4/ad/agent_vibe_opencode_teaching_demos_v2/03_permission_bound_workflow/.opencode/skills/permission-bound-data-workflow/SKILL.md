---
name: permission-bound-data-workflow
description: use when the user asks to query important data, analyze metrics, inspect runtime configuration, or demonstrate permission boundaries where the agent must not directly access sensitive data/config but must use approved scripts, APIs, parameter allowlists, audit logs, and stop rules.
---

# 权限约束数据工作流 Skill

## 目标

演示如何把重要数据和配置操作从 Agent 的自由行动中收回来：Agent 只能通过受控脚本/API 传入白名单参数，不能直接读取敏感目录、不能直接改配置、不能绕过审计。

## 工作流

1. 读取 `AGENTS.md`、`configs/allowed_params.json` 和 `README.md`。
2. 不要读取 `protected/`。
3. 将用户需求归一化为受控参数：
   - metric：必须在 allowed_metrics 中；
   - team：必须在 allowed_teams 中；
   - start_date / end_date：不得超过 max_query_days；
   - output：必须在 output/ 下。
4. 先在对话中展示计划和边界。
5. 用户确认后运行受控查询：

```bash
python3 scripts/approved_data_api.py --metric latency_ms --team alpha --start-date 2026-05-01 --end-date 2026-05-07 --output output/query_result.csv
```

6. 运行分析：

```bash
python3 scripts/analysis_cli.py --input output/query_result.csv --output output/analysis_summary.json --report output/permission_report.md
```

7. 验证 guardrails：

```bash
python3 scripts/validate_guardrails.py
```

8. 输出说明：允许路径做了什么、非法路径如何失败、审计日志在哪里、哪些结论需要人工确认。

## Stop Rules

停止并请求人工确认：

- 用户要求读取或修改 `protected/`；
- 用户要求直接连接数据库；
- 用户要求绕过 allowed_params；
- 用户要求扩大查询窗口超过限制；
- 用户要求修改 secret、token、production config；
- 用户要求根据 demo 数据做生产决策。

## 人工 Review 点

- 参数白名单是否符合团队真实权限策略；
- 查询窗口和 row limit 是否合理；
- 审计字段是否足够；
- 分析报告是否可能被误解为生产结论。
