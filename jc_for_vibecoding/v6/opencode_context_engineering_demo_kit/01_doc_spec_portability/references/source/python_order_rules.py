from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

@dataclass
class OrderItem:
    sku: str
    qty: int
    unit_price: Decimal
    category: str

@dataclass
class Order:
    items: list[OrderItem]
    customer_tier: str
    coupon: str | None
    tax_rate: Decimal


def round_money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_order_total(order: Order) -> dict:
    subtotal = sum((item.unit_price * item.qty for item in order.items), Decimal("0"))
    tier_discount = {"standard": Decimal("0"), "silver": Decimal("0.05"), "gold": Decimal("0.10")}
    if order.customer_tier not in tier_discount:
        raise ValueError(f"unsupported customer tier: {order.customer_tier}")
    discounted = subtotal * (Decimal("1") - tier_discount[order.customer_tier])
    total_qty = sum(item.qty for item in order.items)
    if order.coupon == "WELCOME10":
        discounted = discounted * Decimal("0.90")
    elif order.coupon == "BULK5" and total_qty >= 10:
        discounted = discounted * Decimal("0.95")
    elif order.coupon not in (None, "BULK5"):
        raise ValueError(f"unsupported coupon: {order.coupon}")
    tax = discounted * order.tax_rate
    total = discounted + tax
    return {
        "subtotal": round_money(subtotal),
        "discounted": round_money(discounted),
        "tax": round_money(tax),
        "total": round_money(total),
    }
