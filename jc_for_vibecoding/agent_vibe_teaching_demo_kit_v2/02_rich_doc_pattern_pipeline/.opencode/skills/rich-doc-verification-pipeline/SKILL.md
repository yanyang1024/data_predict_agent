---
name: rich-doc-verification-pipeline
description: Use for extracting verification or test implementation patterns from PDF, HTML, markdown, or other rich-text specifications and adapting them to an environment package through staged extraction, adaptation, code generation, syntax validation, and human logic review.
---

# Rich document verification pipeline

## Staged workflow

1. Inspect the source document and `rules/extraction_rules.json`.
2. Extract structured patterns with `scripts/01_extract_patterns.py`.
3. Pause for human review of extracted records.
4. Adapt patterns to the environment package with `scripts/02_adapt_patterns.py`.
5. Pause for human review of the adaptation plan.
6. Generate target code with `scripts/03_generate_code.py`.
7. Validate syntax and schema with `scripts/04_validate_syntax.py`.
8. State clearly that syntax validation does not prove logical correctness.

## Validation language

Use precise language:

- OK: "The generated Python file passed syntax validation."
- OK: "The sequence IR uses only supported environment operations."
- Not OK: "The verification logic is correct."
- Not OK: "Coverage is complete."

## Stop rules

Stop if extraction rules are missing, if the document has conflicting instructions, if an environment operation is unsupported, or if the user asks to bypass human review.
