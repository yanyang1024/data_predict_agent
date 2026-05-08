---
name: rule-based-project-report
description: Use for rule-based project status, weekly update, or management report generation when the user provides structured progress data, report rules, and a template and wants a markdown or PPT-style report with validation and human review checkpoints.
---

# Rule-based project report

## Workflow

1. Inspect `inputs/progress_update.json`, `rules/report_rules.json`, and `templates/project_status_template.md`.
2. Restate the source data, required sections, forbidden phrases, and validation plan.
3. Do not invent project status, metrics, dates, owners, blockers, or decisions.
4. Run `python3 scripts/generate_project_report.py` only after the user accepts the plan or explicitly asks to execute.
5. Run `python3 scripts/validate_project_report.py`.
6. Summarize:
   - artifacts generated,
   - what validation checked,
   - what still requires human review.

## Stop rules

Stop and ask for human input if:

- required status fields are missing,
- the template asks for content not present in the input,
- the user asks to invent progress or hide a blocker,
- the report would be used for external or executive communication without review.
