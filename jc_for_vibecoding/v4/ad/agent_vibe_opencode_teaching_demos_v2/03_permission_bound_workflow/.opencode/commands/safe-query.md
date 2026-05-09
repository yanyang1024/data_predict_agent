---
description: 使用受控 API 查询 mock 数据并生成分析报告
agent: plan
---

请使用 `permission-bound-data-workflow` skill。

用户需求：

$ARGUMENTS

先 Plan：说明会调用哪些脚本、允许的参数范围、审计日志位置、哪些内容不能直接操作。

确认后只允许运行以下脚本：

```bash
python3 scripts/approved_data_api.py --metric latency_ms --team alpha --start-date 2026-05-01 --end-date 2026-05-07 --output output/query_result.csv
python3 scripts/analysis_cli.py --input output/query_result.csv --output output/analysis_summary.json --report output/permission_report.md
python3 scripts/validate_guardrails.py
```

不要读取或修改 `protected/`。
