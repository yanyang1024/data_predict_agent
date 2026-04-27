from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.express as px


@dataclass(frozen=True)
class ProfileConfig:
    input_path: Path
    value_column: str
    group_column: str | None = None
    time_column: str | None = None
    output_dir: Path = Path("artifacts/simple-profile")
    z_threshold: float = 3.0


REQUIRED_OUTPUTS = [
    "summary.json",
    "group_summary.csv",
    "trend.html",
    "manifest.json",
]


def _validate_columns(df: pd.DataFrame, columns: list[str]) -> None:
    missing = [col for col in columns if col and col not in df.columns]
    if missing:
        raise ValueError(f"missing required columns: {missing}. Available columns: {list(df.columns)}")


def load_and_clean(config: ProfileConfig) -> pd.DataFrame:
    df = pd.read_csv(config.input_path)
    required = [config.value_column]
    if config.group_column:
        required.append(config.group_column)
    if config.time_column:
        required.append(config.time_column)
    _validate_columns(df, required)

    df = df.copy()
    df[config.value_column] = pd.to_numeric(df[config.value_column], errors="coerce")
    if config.time_column:
        df[config.time_column] = pd.to_datetime(df[config.time_column], errors="coerce")
    return df


def compute_profile(df: pd.DataFrame, config: ProfileConfig) -> tuple[dict[str, Any], pd.DataFrame]:
    value = config.value_column
    valid = df.dropna(subset=[value]).copy()

    mean = valid[value].mean()
    std = valid[value].std(ddof=1)
    if pd.isna(std) or std == 0:
        valid["z_score"] = 0.0
    else:
        valid["z_score"] = (valid[value] - mean) / std
    valid["is_outlier"] = valid["z_score"].abs() >= config.z_threshold

    summary: dict[str, Any] = {
        "input_path": str(config.input_path),
        "row_count": int(len(df)),
        "valid_value_count": int(len(valid)),
        "missing_value_count": int(df[value].isna().sum()),
        "value_column": value,
        "group_column": config.group_column,
        "time_column": config.time_column,
        "mean": float(mean) if pd.notna(mean) else None,
        "std": float(std) if pd.notna(std) else None,
        "min": float(valid[value].min()) if len(valid) else None,
        "max": float(valid[value].max()) if len(valid) else None,
        "z_threshold": config.z_threshold,
        "outlier_count": int(valid["is_outlier"].sum()),
    }

    if config.group_column:
        group_summary = (
            valid.groupby(config.group_column)[value]
            .agg(["count", "mean", "std", "min", "max"])
            .reset_index()
            .sort_values("mean", ascending=False)
        )
        summary["group_count"] = int(group_summary[config.group_column].nunique())
    else:
        group_summary = pd.DataFrame(
            [{"count": len(valid), "mean": mean, "std": std, "min": valid[value].min(), "max": valid[value].max()}]
        )

    return summary, group_summary


def render_trend(df: pd.DataFrame, config: ProfileConfig, output_html: Path) -> None:
    value = config.value_column
    plot_df = df.dropna(subset=[value]).copy()

    x_col = config.time_column if config.time_column else plot_df.index
    color_col = config.group_column if config.group_column else None

    if config.time_column:
        plot_df = plot_df.sort_values(config.time_column)
        fig = px.scatter(plot_df, x=config.time_column, y=value, color=color_col, title="Simple Data Profile Trend")
    else:
        plot_df["row_index"] = range(len(plot_df))
        fig = px.scatter(plot_df, x="row_index", y=value, color=color_col, title="Simple Data Profile Trend")

    fig.update_layout(template="plotly_white", xaxis_title=config.time_column or "row_index", yaxis_title=value)
    fig.write_html(output_html, include_plotlyjs="cdn", full_html=True)


def run_profile(config: ProfileConfig) -> dict[str, Any]:
    config.output_dir.mkdir(parents=True, exist_ok=True)
    df = load_and_clean(config)
    summary, group_summary = compute_profile(df, config)

    summary_path = config.output_dir / "summary.json"
    group_path = config.output_dir / "group_summary.csv"
    trend_path = config.output_dir / "trend.html"
    manifest_path = config.output_dir / "manifest.json"

    render_trend(df, config, trend_path)
    group_summary.to_csv(group_path, index=False)
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    manifest: dict[str, Any] = {
        "capability": "simple-data-quality-analysis",
        "version": "0.1.0",
        "input_path": str(config.input_path),
        "output_dir": str(config.output_dir),
        "outputs": {
            "summary": str(summary_path),
            "group_summary": str(group_path),
            "trend_html": str(trend_path),
        },
        "row_count": summary["row_count"],
        "valid_value_count": summary["valid_value_count"],
        "outlier_count": summary["outlier_count"],
        "warnings": [],
    }

    if summary["row_count"] == 0:
        manifest["warnings"].append("input dataset is empty")
    if summary["missing_value_count"] > 0:
        manifest["warnings"].append("value column contains missing or non-numeric values")
    if summary["outlier_count"] > 0:
        manifest["warnings"].append("potential outliers detected by z-score rule")

    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return manifest
