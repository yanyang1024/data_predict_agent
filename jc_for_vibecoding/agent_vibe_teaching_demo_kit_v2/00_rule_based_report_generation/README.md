# Demo 0 - Rule-based project report generation

## Teaching focus

This demo is the entry point for the workshop. It shows a low-risk, general-purpose agent workflow:

```text
structured status input + report rules + template -> generated markdown/PPTX -> validation manifest -> human review
```

It is intentionally not domain-specific. It can represent project status reporting, weekly updates, or training progress summaries.

## Run

```bash
python3 scripts/generate_project_report.py
python3 scripts/validate_project_report.py
```

## What to teach

- How opencode starts from project rules (`AGENTS.md`), a command, and a skill.
- Why the agent should first inspect rules and inputs in Plan mode.
- Why generated business reports need validation and human review.
- How to iterate a stable agent app: draft skill -> run -> inspect failure -> tighten rules -> rerun.
