# Order Pricing Spec v1.0

This is a synthetic teaching spec. It describes a small pricing engine that must be portable across platforms.

## Normative Rules

```yaml
rules:
  currency: USD
  rounding: bankers_2_decimal
  base_total: sum(line.quantity * line.unit_price)
  discounts:
    - id: BULK10
      when: base_total >= 1000
      percent: 10
    - id: MEMBER5
      when: customer_tier in [gold, platinum]
      percent: 5
  tax:
    default_percent: 8
    exempt_regions: [OR, MT, NH]
  shipping:
    free_when_total_after_discount_gte: 500
    default_fee: 25
```

## Expected Processing Order

1. Compute `base_total`.
2. Apply all eligible discounts additively.
3. Compute `total_after_discount`.
4. Add tax unless region is exempt.
5. Add shipping unless `total_after_discount >= 500`.
6. Round monetary fields to 2 decimals.

## Ambiguity Log

- The spec does not define negative quantity behavior. Treat negative quantity as invalid input and stop.
- The spec does not define unknown customer tier. Treat it as no membership discount.

## Reference Output Contract

Every platform implementation must return JSON with:

```json
{
  "base_total": 0.0,
  "discount_percent": 0.0,
  "discount_amount": 0.0,
  "tax_amount": 0.0,
  "shipping_fee": 0.0,
  "final_total": 0.0,
  "applied_rules": []
}
```
