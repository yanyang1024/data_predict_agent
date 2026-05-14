# Generated Flask CSV Analyzer

This project is generated from a Gradio CSV analysis app for Demo 01.

## Run

```bash
python3 -m pip install Flask
python3 app.py
```

Open `http://127.0.0.1:5000/` and upload `sample_data.csv`.

## What was preserved

- CSV upload workflow.
- Row, column and numeric-column summary.
- Numeric summary table.
- Inline SVG chart for the first numeric column.
- Frontend style tokens from `docs/frontend_style_spec.md`.

## Limitations

The demo validates sample and boundary CSV behavior plus static structure only. Production upload security, file size policy, deployment and richer plotting still need owner review.
