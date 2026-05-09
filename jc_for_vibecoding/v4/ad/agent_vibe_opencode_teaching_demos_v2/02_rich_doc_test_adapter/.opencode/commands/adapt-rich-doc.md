---
description: 从富文本说明中抽取验证模式并适配到目标环境测试代码
agent: plan
---

请使用 `rich-doc-test-adapter` skill。

用户需求：

$ARGUMENTS

先 Plan：读取富文本、抽取规则和环境包契约，列出抽取字段、映射规则、人工确认点。

确认后执行：

```bash
python3 scripts/extract_rich_doc_patterns.py --doc docs/rich_test_spec_export.html --rules references/extraction_rules.md --output output/extracted_patterns.json
python3 scripts/adapt_patterns_to_env.py --patterns output/extracted_patterns.json --env env_package/target_env_contract.json --output output/generated_tests.py --review output/review_packet.md
python3 scripts/validate_generated_tests.py --tests output/generated_tests.py --patterns output/extracted_patterns.json
```
