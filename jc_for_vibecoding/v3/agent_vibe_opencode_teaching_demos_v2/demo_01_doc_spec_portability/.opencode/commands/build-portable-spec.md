---
description: Build portable implementations from a document spec and validate golden cases
agent: build
---

Use the `spec-portability-builder` skill.

Request:

$ARGUMENTS

Workflow:
1. In Plan mode, read `docs/order_pricing_spec.md`, `examples/`, and `golden_cases/order_pricing_cases.json`.
2. Extract normalized rules, do not directly rewrite implementations from prose.
3. Run the three approved scripts in order.
4. Summarize portability report and human review items.
