# Historical Platform A reference sample.
# This sample is intentionally small and not used as the final source of truth.

def price(order):
    subtotal = sum(line["quantity"] * line["unit_price"] for line in order["lines"])
    discount = 0
    if subtotal >= 1000:
        discount += 10
    if order.get("customer_tier") in ["gold", "platinum"]:
        discount += 5
    after = subtotal * (1 - discount / 100)
    tax = 0 if order.get("region") in ["OR", "MT", "NH"] else after * 0.08
    ship = 0 if after >= 500 else 25
    return round(after + tax + ship, 2)
