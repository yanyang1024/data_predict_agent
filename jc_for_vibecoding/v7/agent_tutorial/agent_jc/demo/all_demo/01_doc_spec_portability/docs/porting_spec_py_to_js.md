# Python -> JavaScript/TypeScript 风格迁移规范

## 迁移目标

把 Python 规则模块迁移为 ES module，便于后续 TypeScript 化。

## 规范

| Python | JS/TS 风格 |
|---|---|
| `snake_case` 函数 | `camelCase` 函数 |
| `Decimal` | demo 中使用 `Number` + `round2`，生产系统需评估 decimal 库 |
| `dataclass` | JSDoc typedef 或 TypeScript interface |
| `ValueError` | `throw new Error(...)` |
| `None` | `null` 或 `undefined` |
| `dict` 输入 | plain object 输入 |

## 必须保持一致

- 输入字段语义保持不变。
- 会员折扣和 coupon 顺序保持不变。
- golden cases 必须全部通过。
- 不要改变 `Order` 的业务含义。

## 人工确认点

- 金额计算在真实生产中是否需要 decimal library。
- coupon 顺序是否有法务或商业定义。
- 未覆盖的 tier / coupon 应该报错还是忽略。
