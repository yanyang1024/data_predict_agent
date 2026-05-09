---
description: Generate a rule-based teaching status deck, Excel dashboard, Gantt image, and brief
agent: build
---

Use the `rule-based-doc-generator` skill.

User request:

$ARGUMENTS

Workflow:
1. First read `README.md`, `configs/course_template.yaml`, and `data/course_progress.json`.
2. Explain what will be generated and which fields need human review.
3. Run `python3 scripts/generate_training_artifacts.py --request sample_request.txt --progress data/course_progress.json --template configs/course_template.yaml --output-dir output`.
4. Inspect `output/generation_manifest.json` and summarize generated files.
5. Do not claim the generated PPT/Excel is final without human review.
