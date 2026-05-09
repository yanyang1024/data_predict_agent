
import json
from decimal import Decimal, ROUND_HALF_EVEN

RULES = {"currency": "USD", "rounding": "bankers_2_decimal", "base_total": "sum(line.quantity * line.unit_price)", "discounts": [{"id": "BULK10", "when": "base_total >= 1000", "percent": 10}, {"id": "MEMBER5", "when": "customer_tier in [gold, platinum]", "percent": 5}], "tax": {"default_percent": 8, "exempt_regions": ["OR", "MT", "NH"]}, "shipping": {"free_when_total_after_discount_gte": 500, "default_fee": 25}}


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
    return {
        "base_total": money(base_total),
        "discount_percent": money(discount_percent),
        "discount_amount": money(discount_amount),
        "tax_amount": money(tax_amount),
        "shipping_fee": money(shipping_fee),
        "final_total": money(final_total),
        "applied_rules": applied,
    }


if __name__ == "__main__":
    import sys
    order = json.loads(sys.stdin.read())
    print(json.dumps(calculate(order), ensure_ascii=False))
