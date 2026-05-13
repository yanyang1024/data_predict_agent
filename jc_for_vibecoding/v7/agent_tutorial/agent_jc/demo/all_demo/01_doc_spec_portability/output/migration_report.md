# Migration Report

Generated at: 2026-05-13T20:56:11.801816+00:00

## 输入

- Source: `references/source/python_order_rules.py`
- Output: `generated/pricing.mjs`
- Functional spec: `docs/order_discount_spec.md`
- Porting spec: `docs/porting_spec_py_to_js.md`

## 已迁移规则

- `calculate_order_total` -> `calculateOrderTotal`
- `round_money` -> `round2`
- `ValueError` -> `Error`
- `Decimal` -> `Number + round2`

## 自动验证

运行 `scripts/validate_port.py` 后查看结果。

## 人工 review 点

- Demo 中使用 Number，不代表生产金额计算可接受。
- Golden cases 覆盖了 3 条正常路径和 2 条错误路径，但未覆盖所有金额边界。
- Coupon 顺序是否符合真实业务规则，需要 owner 确认。
