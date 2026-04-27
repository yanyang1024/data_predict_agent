"""
Stage 0: an intentionally simple one-file script.
It reads a CSV, computes basic statistics for one value column, and writes a JSON summary.

This is the kind of script we will gradually turn into:
1) a reusable CLI,
2) an opencode custom tool,
3) an opencode command,
4) an opencode skill.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def analyze_csv(input_path: str, value_column: str, group_column: str | None = None) -> dict:
    df = pd.read_csv(input_path)
    df = df.dropna(subset=[value_column]).copy()
    df[value_column] = pd.to_numeric(df[value_column], errors="coerce")
    df = df.dropna(subset=[value_column])

    summary = {
        "row_count": int(len(df)),
        "value_column": value_column,
        "mean": float(df[value_column].mean()),
        "std": float(df[value_column].std(ddof=1)),
        "min": float(df[value_column].min()),
        "max": float(df[value_column].max()),
    }

    if group_column:
        grouped = (
            df.groupby(group_column)[value_column]
            .agg(["count", "mean", "std", "min", "max"])
            .reset_index()
        )
        summary["group_summary"] = grouped.to_dict(orient="records")

    return summary


if __name__ == "__main__":
    result = analyze_csv("data/sample_measurements.csv", "measurement_value", "equipment_id")
    out = Path("artifacts/original_summary.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {out}")
