from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.simple_profile.core import ProfileConfig, run_profile


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a simple local data profile and generate summary artifacts.")
    parser.add_argument("--input", required=True, help="Input CSV path")
    parser.add_argument("--value-column", required=True, help="Numeric column to analyze")
    parser.add_argument("--group-column", default=None, help="Optional group column, such as equipment_id")
    parser.add_argument("--time-column", default=None, help="Optional time column for trend plots")
    parser.add_argument("--output-dir", default="artifacts/simple-profile", help="Artifact output directory")
    parser.add_argument("--z-threshold", default=3.0, type=float, help="Outlier threshold in absolute z-score")
    args = parser.parse_args()

    manifest = run_profile(
        ProfileConfig(
            input_path=Path(args.input),
            value_column=args.value_column,
            group_column=args.group_column,
            time_column=args.time_column,
            output_dir=Path(args.output_dir),
            z_threshold=args.z_threshold,
        )
    )
    print(json.dumps(manifest, ensure_ascii=False))


if __name__ == "__main__":
    main()
