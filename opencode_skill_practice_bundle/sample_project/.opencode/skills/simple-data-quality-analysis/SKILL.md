---
name: simple-data-quality-analysis
description: Profile a local CSV dataset for training or non-production data analysis. Use when the user asks to summarize one numeric column, compare groups, detect simple outliers, generate a trend plot, or turn a small Python data-processing script into a reusable opencode tool, command, and skill workflow.
license: internal
compatibility: opencode
metadata:
  owner: data-analysis-enablement
  version: "0.1.0"
---

# Simple Data Quality Analysis

## Purpose

Use this skill to run a small, safe, repeatable local data analysis workflow. The workflow reads a local CSV, analyzes one numeric value column, optionally compares groups, generates a simple trend HTML plot, and returns a concise engineering-style report.

This is a training skill. It intentionally avoids production databases, private APIs, model training, and complex semiconductor domain logic.

## Default workflow

1. Restate the user's analysis goal.
2. Identify the required parameters:
   - input CSV path
   - value column
   - optional group column
   - optional time column
   - optional output directory
3. If parameters are missing, ask one short clarification question.
4. Use the `data-profile` custom tool to run the approved CLI.
5. Inspect the returned manifest and summary paths.
6. If necessary, read only `summary.json` and `group_summary.csv`; do not load the full raw dataset into context.
7. Return the standard report format from `references/report-template.md`.

## Tool policy

Use `data-profile` for execution. Do not run ad-hoc Python through `bash` unless the approved custom tool is unavailable and the user explicitly asks for manual debugging.

Do not use this skill for:
- production database access
- SQL query generation
- recipe/spec/control-limit decisions
- large confidential datasets
- automated file modification

## Output policy

Always mention:
- analyzed file path
- value column
- group column, if provided
- output artifacts
- row count
- missing value count
- outlier count
- top group differences, when group summary exists
- limitations and recommended next checks

## Stop rules

Stop and ask before:
- reading a dataset larger than the local training scope
- using production data
- changing input files
- changing the CLI algorithm
- treating z-score outliers as confirmed process anomalies

## References

Read these only when needed:
- `references/data-contract.md` for required columns and artifact contract.
- `references/report-template.md` for the final response template.
- `examples/session-context-walkthrough.md` to explain how opencode context changes after command and skill loading.
