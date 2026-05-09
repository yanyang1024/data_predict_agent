---
description: 从 Doc Spec 和历史样例生成目标平台实现并验证
agent: plan
---

请使用 `doc-spec-portability` skill。

用户需求：

$ARGUMENTS

先执行 Plan：读取 `docs/ticket_priority_spec.md`、`examples/platform_a_python/` 和 `contexts/platform_b_contract.md`，输出 contract 计划、可移植性风险和人工确认点。

用户确认后执行：

```bash
python3 scripts/extract_spec_contract.py --spec docs/ticket_priority_spec.md --output output/spec_contract.json
python3 scripts/port_to_platform_b.py --contract output/spec_contract.json --output output/platform_b
python3 scripts/validate_port.py --impl output/platform_b/rule_engine.js --cases tests/platform_b_cases.json
```
