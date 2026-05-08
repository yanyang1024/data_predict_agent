---
name: lot-history-analysis
description: Use for semiconductor lot history analysis when the user asks to calculate unit time, queue time, step-level wait time, bottleneck steps, or engineering summaries from approved query api exports or mock lot movement data; never connect directly to production databases or give lot disposition decisions.
---

# Lot History Analysis

## Workflow

1. Normalize input parameters: lot_id, product, step filter, and time window.
2. Use mock data or approved Query API export only.
3. Run `scripts/lot_qtime_cli.py` to calculate UT and QTime.
4. Inspect `analysis_manifest.json` for row count, time range, and warnings.
5. Run `scripts/render_report.py` to generate a Markdown report.
6. State observations, limitations, and next checks.

## Stop Rules

Stop and ask for human review when:

- The user asks to query production databases directly.
- The user asks for lot hold/release, ship, or disposition decisions.
- Query range exceeds approved limits.
- Required fields are missing from the data.
- The sample size is insufficient for the requested conclusion.
