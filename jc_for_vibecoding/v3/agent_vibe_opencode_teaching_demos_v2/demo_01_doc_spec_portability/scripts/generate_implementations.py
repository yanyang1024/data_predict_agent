#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path

PY_IMPL = r'''
import json
from decimal import Decimal, ROUND_HALF_EVEN

RULES = {rules_json}


def money(x):
    return float(Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN))


def calculate(order):
    for line in order.get("lines", []):
        if line.get("quantity", 0) < 0:
            raise ValueError("negative quantity is not allowed by normalized rules")
    base_total = sum(line["quantity"] * line["unit_price"] for line in order.get("lines", []))
    discount_percent = 0.0
    applied = []
    if base_total >= 1000:
        discount_percent += 10
        applied.append("BULK10")
    if order.get("customer_tier") in ["gold", "platinum"]:
        discount_percent += 5
        applied.append("MEMBER5")
    discount_amount = base_total * discount_percent / 100
    total_after_discount = base_total - discount_amount
    tax_amount = 0.0 if order.get("region") in ["OR", "MT", "NH"] else total_after_discount * 0.08
    shipping_fee = 0.0 if total_after_discount >= 500 else 25.0
    final_total = total_after_discount + tax_amount + shipping_fee
    return {{
        "base_total": money(base_total),
        "discount_percent": money(discount_percent),
        "discount_amount": money(discount_amount),
        "tax_amount": money(tax_amount),
        "shipping_fee": money(shipping_fee),
        "final_total": money(final_total),
        "applied_rules": applied,
    }}


if __name__ == "__main__":
    import sys
    order = json.loads(sys.stdin.read())
    print(json.dumps(calculate(order), ensure_ascii=False))
'''

NODE_IMPL = r'''
const RULES = {rules_json};

function money(x) {{
  return Number((Math.round((x + Number.EPSILON) * 100) / 100).toFixed(2));
}}

export function calculate(order) {{
  for (const line of order.lines || []) {{
    if ((line.quantity || 0) < 0) throw new Error("negative quantity is not allowed by normalized rules");
  }}
  const baseTotal = (order.lines || []).reduce((acc, line) => acc + line.quantity * line.unit_price, 0);
  let discountPercent = 0;
  const applied = [];
  if (baseTotal >= 1000) {{ discountPercent += 10; applied.push("BULK10"); }}
  if (["gold", "platinum"].includes(order.customer_tier)) {{ discountPercent += 5; applied.push("MEMBER5"); }}
  const discountAmount = baseTotal * discountPercent / 100;
  const totalAfterDiscount = baseTotal - discountAmount;
  const taxAmount = ["OR", "MT", "NH"].includes(order.region) ? 0 : totalAfterDiscount * 0.08;
  const shippingFee = totalAfterDiscount >= 500 ? 0 : 25;
  const finalTotal = totalAfterDiscount + taxAmount + shippingFee;
  return {{
    base_total: money(baseTotal),
    discount_percent: money(discountPercent),
    discount_amount: money(discountAmount),
    tax_amount: money(taxAmount),
    shipping_fee: money(shippingFee),
    final_total: money(finalTotal),
    applied_rules: applied,
  }};
}}

if (process.argv[1] && process.argv[1].endsWith("pricer.mjs")) {{
  let input = "";
  process.stdin.on("data", chunk => input += chunk);
  process.stdin.on("end", () => {{
    const order = JSON.parse(input || "{{}}");
    console.log(JSON.stringify(calculate(order)));
  }});
}}
'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rules", required=True)
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()
    rules = json.loads(Path(args.rules).read_text(encoding="utf-8"))
    rules_json = json.dumps(rules["rules"], ensure_ascii=False)
    out = Path(args.output_dir)
    py_dir = out / "platform_python"
    node_dir = out / "platform_node"
    py_dir.mkdir(parents=True, exist_ok=True)
    node_dir.mkdir(parents=True, exist_ok=True)
    (py_dir / "pricer.py").write_text(PY_IMPL.format(rules_json=rules_json), encoding="utf-8")
    (node_dir / "pricer.mjs").write_text(NODE_IMPL.format(rules_json=rules_json), encoding="utf-8")
    (out / "generation_manifest.json").write_text(json.dumps({
        "ok": True,
        "generated": [str(py_dir / "pricer.py"), str(node_dir / "pricer.mjs")],
        "human_review_required": rules.get("human_review_required", []),
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"ok": True, "output_dir": str(out)}, indent=2))

if __name__ == "__main__":
    main()
