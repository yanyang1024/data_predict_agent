# Demo 02 - 富文本规则提取与 Skill 串联

## 教学目标

展示如何从 PDF 或其他富文本格式中提取规则，并将规则用于后续流程。

```text
PDF / Markdown Manual
  -> manual-rule-extractor skill
  -> extracted_rules.json
  -> environment-sequence-adapter skill
  -> adapted_sequence.py + sequence_ir.json
  -> syntax-validation-gate skill
  -> validation_manifest.json
  -> human review
```

重点强调：

- Agent 不只是“读和建议”，也可以运行脚本生成中间产物；
- 但中间方案需要人确认；
- 代码或规范语言可以做语法验证；
- 逻辑正确性仍然需要人协同验证。

## 运行

```bash
python3 scripts/run_pipeline.py
```

或分步运行：

```bash
python3 scripts/extract_rules_from_manual.py --input source_docs/validation_manual.pdf --output output/extracted_rules.json --review output/human_review_points.md
python3 scripts/adapt_rules_to_env.py --rules output/extracted_rules.json --env env_package/signal_map.json --output output/adapted_sequence.py --ir output/sequence_ir.json
python3 scripts/validate_syntax.py --sequence output/adapted_sequence.py --ir output/sequence_ir.json --manifest output/validation_manifest.json
```
