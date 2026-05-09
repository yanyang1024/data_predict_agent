---
name: spec-portability-builder
description: use when building code from historical documents, written specs, reference examples, or golden cases where one document must drive portable implementations across multiple platforms or languages; supports spec extraction, normalized intermediate rules, target generation, and cross-platform validation.
---

# Spec Portability Builder

## Core idea

Do not translate prose directly into each target platform. First extract a normalized intermediate representation, then generate target implementations and validate them with golden cases.

## Workflow

1. Read the spec and examples:
   - `docs/order_pricing_spec.md`
   - `examples/`
   - `golden_cases/order_pricing_cases.json`
2. Identify normative rules, examples, ambiguity log, and output contract.
3. Run spec extraction:

```bash
python3 scripts/extract_spec_rules.py \
  --spec docs/order_pricing_spec.md \
  --output output/normalized_rules.json \
  --report output/spec_extraction_report.md
```

4. Generate platform implementations:

```bash
python3 scripts/generate_implementations.py \
  --rules output/normalized_rules.json \
  --output-dir output
```

5. Validate cross-platform behavior:

```bash
python3 scripts/validate_portability.py \
  --cases golden_cases/order_pricing_cases.json \
  --python-impl output/platform_python/pricer.py \
  --node-impl output/platform_node/pricer.mjs \
  --report output/portability_report.md
```

6. Summarize:
   - generated files;
   - validation pass/fail;
   - spec ambiguity items;
   - what requires human owner review.

## Stop rules

Stop and ask for human confirmation if:

- the spec has conflicting normative rules;
- golden cases disagree with the spec;
- a target platform lacks a required primitive;
- the user asks to mark the implementation as production-ready without review;
- rounding, time, unit, currency, or precision behavior is unclear.

## References

- `references/spec_extraction_rules.md`
- `references/platform_adapter_contract.md`
- `references/review_checklist.md`
