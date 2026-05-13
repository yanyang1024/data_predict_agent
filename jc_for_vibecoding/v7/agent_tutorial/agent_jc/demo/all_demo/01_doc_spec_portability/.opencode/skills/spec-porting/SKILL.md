---
name: spec-porting
description: use when the user asks to migrate or port code across languages or platforms based on a functional spec, historical source implementation, target-language examples, migration rules, and golden tests; plan first, generate only candidate code, run validation, and report review items.
compatibility: opencode
metadata:
  language: zh-CN
  demo: context-engineering-01
---

# Spec Porting Skill

## 目标

把“基于历史文档和样例的迁移开发”变成稳定流程：先取证、再计划、再生成、再验证、最后交付 review 清单。

## 必读 context

1. `docs/order_discount_spec.md`：语言无关功能要求。
2. `docs/porting_spec_py_to_js.md`：迁移规范和人工确认点。
3. `references/source/python_order_rules.py`：源实现，只读。
4. `references/examples/js_reference_style.mjs`：目标风格样例，只读。
5. `tests/golden_cases.json`：验收行为，只读。

## 工作流

1. 输出迁移计划：列出源 API、目标 API、字段映射、风险。
2. 只生成候选实现到 `generated/`。
3. 调用：

```bash
python3 scripts/port_py_to_js.py --source references/source/python_order_rules.py --output generated/pricing.mjs --report output/migration_report.md
```

4. 调用验证：

```bash
python3 scripts/validate_port.py --module generated/pricing.mjs --cases tests/golden_cases.json
```

5. 回答中必须包含：
   - 迁移依据；
   - 自动验证结果；
   - golden cases 未覆盖项；
   - 是否需要人工确认金额精度策略。

## Stop Rules

- 不要修改 `docs/`、`references/`、`tests/golden_cases.json`。
- 如果目标语言金额精度要求不明确，不能声称生产可用。
- 如果 golden tests 失败，必须停止并报告失败，不要继续扩写功能。
