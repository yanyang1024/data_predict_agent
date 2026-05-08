# Scenario 3: Lot History UT/QTime Demo

Business context:

Engineers frequently need ad hoc lot history retrieval and UT/QTime analysis.
A direct database connection or one-off SQL is risky and hard to reuse. This
classroom scenario uses a mock CSV file and CLI scripts to demonstrate the
recommended pattern:

Query API or approved export -> Analysis CLI -> Report CLI -> Skill.

Run:

```bash
python3 scripts/lot_qtime_cli.py --lot-id LOT1001 --input mock_data/lot_history_sample.csv --thresholds configs/qtime_thresholds.json --output-dir output
python3 scripts/render_report.py --summary output/qtime_summary.csv --manifest output/analysis_manifest.json --output output/lot_history_report.md
```

Suggested Plan-mode prompt:

```text
Do not connect to any database. Read mock_data/lot_history_sample.csv,
configs/qtime_thresholds.json, and scripts/lot_qtime_cli.py.
Explain the schema, UT/QTime definitions, validation checks, and report format.
```

Suggested Act-mode prompt:

```text
Run the approved local CLI for lot LOT1001. Generate qtime_summary.csv,
analysis_manifest.json, and lot_history_report.md. Do not make hold/release
recommendations.
```
