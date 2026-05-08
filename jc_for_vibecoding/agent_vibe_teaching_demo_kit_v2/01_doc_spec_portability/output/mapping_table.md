# Platform mapping table

| Source concept | Target concept | Status | Note |
|---|---|---|---|
| `AlphaTable.read_csv` | `BetaDataset.from_csv` | automatic | Equivalent CSV load concept. |
| `AlphaReport.write_json` | `BetaReport.write_json` | automatic | Equivalent JSON report writer. |
| `implicit schema assumptions` | `BetaRuntime.validate_schema` | required_improvement | Beta requires explicit schema validation. |
| `AlphaLogger.info` | `not used in minimal demo` | manual_review | Logging policy is team-specific. |
