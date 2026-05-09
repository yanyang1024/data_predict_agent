# Demo 01 - Doc Spec 可移植开发

## 教学目标

展示“基于历史文档和样例开发，不同平台同一文档的可移植性实现”。

这个 demo 不模拟真实 tester，也不强调业务复杂度，而是用一个简单的订单计价规范说明：

```text
Doc Spec + Golden Cases + Historical Samples
  -> Normalized Rules
  -> Platform Python implementation
  -> Platform Node implementation
  -> Cross-platform validation report
```

## 运行

```bash
python3 scripts/extract_spec_rules.py \
  --spec docs/order_pricing_spec.md \
  --output output/normalized_rules.json \
  --report output/spec_extraction_report.md

python3 scripts/generate_implementations.py \
  --rules output/normalized_rules.json \
  --output-dir output

python3 scripts/validate_portability.py \
  --cases golden_cases/order_pricing_cases.json \
  --python-impl output/platform_python/pricer.py \
  --node-impl output/platform_node/pricer.mjs \
  --report output/portability_report.md
```

## 讲师提示

重点讲三件事：

1. Agent 先读 spec 和样例，不要直接改代码；
2. 先抽中间规则 `normalized_rules.json`，再生成多平台实现；
3. golden cases 验证的是一致性，业务合理性仍需 spec owner review。
