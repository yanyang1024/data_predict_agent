// Generated candidate module. Review before production use.
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
