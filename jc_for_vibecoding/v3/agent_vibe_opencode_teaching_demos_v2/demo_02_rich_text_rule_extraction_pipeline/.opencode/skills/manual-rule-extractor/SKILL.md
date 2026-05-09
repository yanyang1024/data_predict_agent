---
name: manual-rule-extractor
description: use for extracting structured validation rules, test patterns, native instructions, tables, expected evidence, and human review items from manuals, PDFs, markdown, or other rich-text technical documents.
---

# Manual Rule Extractor

## Workflow

1. Identify document source and type.
2. Extract text conservatively.
3. Extract only explicit rule IDs and native patterns.
4. Write `output/extracted_rules.json`.
5. Write `output/human_review_points.md`.

## Approved command

```bash
python3 scripts/extract_rules_from_manual.py \
  --input source_docs/validation_manual.pdf \
  --output output/extracted_rules.json \
  --review output/human_review_points.md
```

## Quality rules

- Preserve rule IDs exactly.
- Do not invent missing native instructions.
- Put uncertain extraction in human review points.
