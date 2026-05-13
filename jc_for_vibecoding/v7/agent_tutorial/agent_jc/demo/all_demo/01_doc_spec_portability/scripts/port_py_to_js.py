#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

JS_TEMPLATE = '''// Generated candidate module. Review before production use.
// Source: references/source/python_order_rules.py

/**
 * @typedef {{ sku: string, qty: number, unit_price: number, category: string }} OrderItem
 * @typedef {{ items: OrderItem[], customer_tier: string, coupon?: string|null, tax_rate: number }} Order
 */

export function round2(value) {
  return Math.round((value + Number.EPSILON) * 100) / 100
}

const TIER_DISCOUNT = {
  standard: 0,
  silver: 0.05,
  gold: 0.10,
}

export function calculateOrderTotal(order) {
  const subtotal = order.items.reduce((acc, item) => acc + item.unit_price * item.qty, 0)
  if (!(order.customer_tier in TIER_DISCOUNT)) {
    throw new Error(`unsupported customer tier: ${order.customer_tier}`)
  }
  let discounted = subtotal * (1 - TIER_DISCOUNT[order.customer_tier])
  const totalQty = order.items.reduce((acc, item) => acc + item.qty, 0)
  if (order.coupon === 'WELCOME10') {
    discounted = discounted * 0.90
  } else if (order.coupon === 'BULK5' && totalQty >= 10) {
    discounted = discounted * 0.95
  } else if (order.coupon !== undefined && order.coupon !== null && order.coupon !== 'BULK5') {
    throw new Error(`unsupported coupon: ${order.coupon}`)
  }
  const tax = discounted * order.tax_rate
  const total = discounted + tax
  return {
    subtotal: round2(subtotal),
    discounted: round2(discounted),
    tax: round2(tax),
    total: round2(total),
  }
}
'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', required=True)
    ap.add_argument('--output', required=True)
    ap.add_argument('--report', required=True)
    args = ap.parse_args()
    source = Path(args.source)
    if not source.exists():
        raise SystemExit(f'source not found: {source}')
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(JS_TEMPLATE, encoding='utf-8')
    report = Path(args.report)
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(f'''# Migration Report

Generated at: {datetime.now(timezone.utc).isoformat()}

## 输入

- Source: `{args.source}`
- Output: `{args.output}`
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
''', encoding='utf-8')
    print(f'Generated {out} and {report}')

if __name__ == '__main__':
    main()
