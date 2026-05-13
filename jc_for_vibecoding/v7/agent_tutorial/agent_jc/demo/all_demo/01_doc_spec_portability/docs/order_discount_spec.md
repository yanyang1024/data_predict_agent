# Order Discount Functional Spec

## 输入

`Order` 包含：

- `items`: 商品数组，每个商品有 `sku`, `qty`, `unit_price`, `category`
- `customer_tier`: `standard | silver | gold`
- `coupon`: 可选，当前 demo 支持 `WELCOME10` 和 `BULK5`
- `tax_rate`: 税率，例如 `0.0825`

## 规则

1. 小计 = 所有商品 `qty * unit_price` 之和。
2. 会员折扣：standard = 0%，silver = 5%，gold = 10%。
3. 优惠券：
   - `WELCOME10`：在会员折扣后再减 10%。
   - `BULK5`：当总件数 >= 10 时再减 5%，否则不生效。
4. 税费 = 折后金额 * tax_rate。
5. 总价 = 折后金额 + 税费。
6. 金额统一保留两位小数，使用四舍五入。

## 非目标

- 不处理多币种。
- 不处理库存。
- 不处理异步支付。
