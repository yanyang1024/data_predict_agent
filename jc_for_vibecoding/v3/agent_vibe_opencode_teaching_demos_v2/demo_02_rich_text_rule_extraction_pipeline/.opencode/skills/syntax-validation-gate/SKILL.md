---
name: syntax-validation-gate
description: use to validate generated code or sequence files for syntax, schema, importability, dry-run behavior, and manifest generation while explicitly separating syntax correctness from human-reviewed logic correctness.
---

# Syntax Validation Gate

## Workflow

1. Parse generated code with `ast.parse`.
2. Compile with `py_compile`.
3. Run a dry-run in the tiny environment.
4. Write `output/validation_manifest.json`.
5. Report that logic correctness is not proven by syntax checks.

## Approved command

```bash
python3 scripts/validate_syntax.py \
  --sequence output/adapted_sequence.py \
  --ir output/sequence_ir.json \
  --manifest output/validation_manifest.json
```

## Required wording

Always distinguish:

- syntax valid;
- dry-run passed;
- logic correctness not verified;
- human review required.
