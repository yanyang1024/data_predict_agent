# Demo 2 - Rich document pattern extraction and adaptation pipeline

## Teaching focus

This demo teaches how to design extraction rules for PDF/HTML/rich-text documents and how to chain skills/modules:

```text
rich document -> extracted verification patterns -> environment adaptation plan -> generated code -> syntax validation -> human logic review
```

The demo intentionally separates tool validation from human validation.

## Run

```bash
python3 scripts/run_pipeline.py --input docs/verification_guide.html
```

Optional PDF extraction path:

```bash
python3 scripts/run_pipeline.py --input docs/verification_guide.pdf
```

## What to teach

- Rich documents should be converted into structured intermediate records before code generation.
- The extraction schema must say what to capture and what not to infer.
- A skill can chain multiple deterministic modules.
- The agent can execute scripts, but humans should review extraction quality, adaptation assumptions, and final logic.
- Syntax validation is useful but not sufficient for verification signoff.
