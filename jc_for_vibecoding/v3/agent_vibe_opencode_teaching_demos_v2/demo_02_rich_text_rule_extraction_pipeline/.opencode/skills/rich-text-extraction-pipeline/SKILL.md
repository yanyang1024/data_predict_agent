---
name: rich-text-extraction-pipeline
description: use when the user wants to extract validation, testing, procedure, or native instruction patterns from PDF, markdown, Word-like rich text, manuals, or specification documents and then chain extraction, environment adaptation, syntax validation, and human review using modular opencode skills.
---

# Rich Text Extraction Pipeline

## Skill chaining plan

This is an orchestration skill. It should coordinate these sub-skills:

1. `manual-rule-extractor`
2. `environment-sequence-adapter`
3. `syntax-validation-gate`

## Workflow

1. Inspect input document type. Prefer text extraction for text-based PDFs; do not OCR unless necessary.
2. Extract rules into `output/extracted_rules.json`.
3. Stop for review if rule IDs, expected evidence, or native instructions are missing.
4. Adapt extracted rules to the environment package into:
   - `output/sequence_ir.json`
   - `output/adapted_sequence.py`
5. Run syntax validation and dry run:
   - `output/validation_manifest.json`
6. Summarize:
   - what the Agent extracted;
   - what it executed;
   - what was syntactically validated;
   - what still requires human logic review.

## Approved command

```bash
python3 scripts/run_pipeline.py
```

## Stop rules

Stop and ask for human review if:

- the document is scanned and extraction quality is uncertain;
- a native instruction cannot be mapped to the environment package;
- an expected evidence condition is ambiguous;
- syntax passes but verification intent is unclear;
- the user asks to treat generated sequence as signed-off.
