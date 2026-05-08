---
name: tester-platform-porting
description: Use for semiconductor tester program migration when the user provides platform A manuals, platform B manuals, source tester code, pattern files, and reference B programs; produce API mapping, candidate translated code, unsupported lists, and validation checklists without claiming production readiness.
---

# Tester Platform Porting

## Workflow

1. Inspect manuals and source/reference programs before editing.
2. Build or read the mapping file at `configs/platform_mapping.json`.
3. Separate mappings into auto, transform, unsupported, and needs-review.
4. Migrate a small block first. Do not rewrite the full program at once.
5. Generate candidate files under `output/` only.
6. Run validation scripts when available.
7. Produce a conversion report with assumptions, unsupported APIs, and next checks.

## Stop Rules

Stop and ask for human review when:

- A platform A function has no clear platform B equivalent.
- Timing, voltage, limit, or vector semantics differ.
- The user asks to execute on real tester hardware.
- The user asks to mark the result as production-ready.
- A generated pattern changes test intent rather than syntax.
