# opencode Skill Practice Sample Project

This sample project shows how to turn a small Python data analysis function into:

1. a reusable CLI,
2. an opencode custom tool,
3. an opencode command,
4. an opencode skill.

## Run locally

```bash
python3 -m pip install -r requirements.txt
python3 simple_profile_cli.py \
  --input data/sample_measurements.csv \
  --value-column measurement_value \
  --group-column equipment_id \
  --time-column measurement_time \
  --output-dir artifacts/simple-profile
```

Outputs:

- `artifacts/simple-profile/summary.json`
- `artifacts/simple-profile/group_summary.csv`
- `artifacts/simple-profile/trend.html`
- `artifacts/simple-profile/manifest.json`

## Use in opencode

```text
/profile-data data/sample_measurements.csv measurement_value equipment_id measurement_time
```
