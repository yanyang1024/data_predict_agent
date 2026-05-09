# Demo03：权限约束与受控数据 / 配置操作

## 教学目标

这个 demo 说明：当场景涉及重要数据、敏感配置或生产风险时，不应该让 Agent 直接读写数据库或配置文件，而应通过封装好的 API / CLI / 脚本来收窄执行空间。

核心教学点：

```text
危险方式：Agent 自己找数据库、拼 SQL、读配置、改配置
安全方式：Agent 调用 approved_data_api.py 和 safe_config_cli.py，只能传受限参数，并留下 audit log
```

## 运行

```bash
cd 03_permission_bound_workflow
python3 scripts/approved_data_api.py --metric latency_ms --team alpha --start-date 2026-05-01 --end-date 2026-05-07 --output output/query_result.csv
python3 scripts/analysis_cli.py --input output/query_result.csv --output output/analysis_summary.json --report output/permission_report.md
python3 scripts/safe_config_cli.py get --key max_query_days
python3 scripts/validate_guardrails.py
```

## OpenCode 对话演示

Plan 阶段：

```text
请使用 permission-bound-data-workflow skill。
我想查看 alpha 团队最近一周 latency_ms 的趋势，并确认 max_query_days 当前设置。先不要读取 protected/，也不要直接改配置。请说明你会调用哪些受控脚本、参数边界是什么、哪些动作需要人工确认。
```

Build 阶段：

```text
确认执行。请只使用 approved_data_api.py、analysis_cli.py 和 safe_config_cli.py，不要读取 protected/。运行合法查询和 guardrail 验证，并解释非法参数为什么会被拒绝。
```
