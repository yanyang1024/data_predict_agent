# Project Instructions

This repository is a training project for opencode skill and tool practice.

## Rules

- Use local sample data only.
- Do not connect to production databases or internal APIs.
- Prefer the `data-profile` custom tool over ad-hoc shell commands.
- Keep outputs in `artifacts/`.
- Treat outlier detection as screening, not root-cause proof.

## Validation

Run the sample CLI with:

```bash
python3 simple_profile_cli.py --input data/sample_measurements.csv --value-column measurement_value --group-column equipment_id --time-column measurement_time --output-dir artifacts/simple-profile
```
