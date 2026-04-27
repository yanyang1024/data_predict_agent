# Data Contract

## Input

The input is a local CSV file. Minimum required column:

- `measurement_value`: numeric column to analyze, or another numeric column explicitly provided by the user.

Recommended optional columns:

- `measurement_time`: timestamp used for trend plotting.
- `equipment_id`: group column for simple tool/equipment comparison.
- `measurement_item`: measurement item label.
- `lot_id`: lot label for human interpretation only.

## Outputs

The approved CLI writes:

- `summary.json`: compact machine-readable analysis summary.
- `group_summary.csv`: group-level count, mean, std, min, max.
- `trend.html`: interactive Plotly HTML scatter plot.
- `manifest.json`: artifact registry and warnings.

## Interpretation rules

- Missing and non-numeric values are excluded from numeric statistics.
- Outliers are flagged by absolute z-score threshold. This is a screening signal, not a confirmed root cause.
- Group differences should be described as observations unless domain evidence confirms causality.
