---
description: Extract rules from a rich-text manual, adapt them to the environment package, and validate syntax
agent: build
---

Use the `rich-text-extraction-pipeline` skill.

Request:

$ARGUMENTS

Workflow:
1. Plan first: read `README.md`, inspect `source_docs/validation_manual.md`, `env_package/signal_map.json`.
2. Explain the intermediate artifacts and human review gates.
3. Run `python3 scripts/run_pipeline.py`.
4. Inspect `output/validation_manifest.json` and `output/human_review_points.md`.
5. State clearly: syntax validation passed or failed; logic correctness still requires human review.
