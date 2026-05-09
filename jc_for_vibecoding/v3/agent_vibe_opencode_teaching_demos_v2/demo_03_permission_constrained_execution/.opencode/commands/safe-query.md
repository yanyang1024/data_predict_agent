---
description: Run an approved safe query and report without reading protected data directly
agent: build
---

Use the `permission-constrained-analysis` skill.

Request:

$ARGUMENTS

Rules:
1. Do not read `protected_data/`.
2. Use only `scripts/approved_query.py` for data access.
3. Use only allowed dataset, fields, and window.
4. Render the report with `scripts/render_safe_report.py`.
5. Summarize the manifest and safety boundary.
