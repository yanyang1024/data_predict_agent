
const RULES = {"currency": "USD", "rounding": "bankers_2_decimal", "base_total": "sum(line.quantity * line.unit_price)", "discounts": [{"id": "BULK10", "when": "base_total >= 1000", "percent": 10}, {"id": "MEMBER5", "when": "customer_tier in [gold, platinum]", "percent": 5}], "tax": {"default_percent": 8, "exempt_regions": ["OR", "MT", "NH"]}, "shipping": {"free_when_total_after_discount_gte": 500, "default_fee": 25}};

function money(x) {
  return Number((Math.round((x + Number.EPSILON) * 100) / 100).toFixed(2));
}

export function calculate(order) {
  for (const line of order.lines || []) {
    if ((line.quantity || 0) < 0) throw new Error("negative quantity is not allowed by normalized rules");
  }
  const baseTotal = (order.lines || []).reduce((acc, line) => acc + line.quantity * line.unit_price, 0);
  let discountPercent = 0;
  const applied = [];
  if (baseTotal >= 1000) { discountPercent += 10; applied.push("BULK10"); }
  if (["gold", "platinum"].includes(order.customer_tier)) { discountPercent += 5; applied.push("MEMBER5"); }
  const discountAmount = baseTotal * discountPercent / 100;
  const totalAfterDiscount = baseTotal - discountAmount;
  const taxAmount = ["OR", "MT", "NH"].includes(order.region) ? 0 : totalAfterDiscount * 0.08;
  const shippingFee = totalAfterDiscount >= 500 ? 0 : 25;
  const finalTotal = totalAfterDiscount + taxAmount + shippingFee;
  return {
    base_total: money(baseTotal),
    discount_percent: money(discountPercent),
    discount_amount: money(discountAmount),
    tax_amount: money(taxAmount),
    shipping_fee: money(shippingFee),
    final_total: money(finalTotal),
    applied_rules: applied,
  };
}

if (process.argv[1] && process.argv[1].endsWith("pricer.mjs")) {
  let input = "";
  process.stdin.on("data", chunk => input += chunk);
  process.stdin.on("end", () => {
    const order = JSON.parse(input || "{}");
    console.log(JSON.stringify(calculate(order)));
  });
}
