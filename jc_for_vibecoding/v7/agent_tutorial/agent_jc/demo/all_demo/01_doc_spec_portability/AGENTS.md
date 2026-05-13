# Demo 01 Rules

## 允许修改

- `generated/`
- `output/`

## 禁止修改

- `docs/`
- `references/source/`
- `references/examples/`
- `tests/golden_cases.json`

## 验证命令

```bash
python3 scripts/port_py_to_js.py --source references/source/python_order_rules.py --output generated/pricing.mjs --report output/migration_report.md
python3 scripts/validate_port.py --module generated/pricing.mjs --cases tests/golden_cases.json
```

## Agent 要求

1. 先解释迁移规范和 golden cases，不要直接改代码。
2. 迁移后必须跑验证。
3. 如果脚本只能证明 golden cases 通过，必须说明还需要人工 review 边界条件。
