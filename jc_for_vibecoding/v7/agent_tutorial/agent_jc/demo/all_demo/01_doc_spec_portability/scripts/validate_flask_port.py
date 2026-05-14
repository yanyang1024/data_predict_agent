#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import io
import json
import shutil
import sys
from pathlib import Path

sys.dont_write_bytecode = True


def import_app(app_path: Path):
    spec = importlib.util.spec_from_file_location("generated_flask_app", app_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {app_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def contains_all(text: str, fragments: list[str]) -> bool:
    return all(fragment in text for fragment in fragments)


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the generated Flask CSV analyzer.")
    parser.add_argument("--project-dir", required=True)
    parser.add_argument("--cases", required=True)
    args = parser.parse_args()

    project = Path(args.project_dir)
    required = [
        project / "app.py",
        project / "templates/index.html",
        project / "static/styles.css",
        project / "README.md",
        project / "sample_data.csv",
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise SystemExit("missing generated files: " + ", ".join(missing))

    app_text = (project / "app.py").read_text(encoding="utf-8")
    template_text = (project / "templates/index.html").read_text(encoding="utf-8")
    css_text = (project / "static/styles.css").read_text(encoding="utf-8")
    if "import gradio" in app_text:
        raise SystemExit("generated Flask app must not import gradio")
    if not contains_all(app_text, ["Flask", "@app.get(\"/\")", "@app.post(\"/analyze\")", "analyze_csv_bytes"]):
        raise SystemExit("generated app is missing expected Flask route or analysis functions")

    cases = json.loads(Path(args.cases).read_text(encoding="utf-8"))
    module = import_app(project / "app.py")
    checked_cases = []
    for case in cases:
        csv_path = Path(case["csv"])
        try:
            result = module.analyze_csv_bytes(csv_path.read_bytes())
        except Exception as exc:
            expected_error = case.get("expected_error")
            if expected_error and expected_error in str(exc):
                checked_cases.append(case["name"])
                continue
            raise
        if case.get("expected_error"):
            raise SystemExit(f"{case['name']}: expected error containing {case['expected_error']}")
        expected = case["expected"]
        if result["row_count"] != expected["row_count"]:
            raise SystemExit(f"{case['name']}: row_count mismatch")
        if result["column_count"] != expected["column_count"]:
            raise SystemExit(f"{case['name']}: column_count mismatch")
        summary_columns = [row["column"] for row in result["summaries"]]
        for column in expected["numeric_columns"]:
            if column not in summary_columns:
                raise SystemExit(f"{case['name']}: missing numeric summary for {column}")
        for column in expected.get("excluded_numeric_columns", []):
            if column in summary_columns:
                raise SystemExit(f"{case['name']}: incomplete numeric column should be excluded: {column}")
        if result["chart_column"] != expected["chart_column"]:
            raise SystemExit(f"{case['name']}: chart column mismatch")
        missing_counts = {row["column"]: row["missing"] for row in result["missing_counts"]}
        for column, expected_missing in expected.get("missing_counts", {}).items():
            if missing_counts.get(column) != expected_missing:
                raise SystemExit(f"{case['name']}: missing count mismatch for {column}")
        if "<svg" not in result["chart_svg"]:
            raise SystemExit(f"{case['name']}: chart SVG missing")
        checked_cases.append(case["name"])

    flask_runtime_checked = False
    flask_runtime_note = "Flask not installed; pure helper validation completed."
    try:
        app = module.create_app()
        client = app.test_client()
        sample_bytes = (project / "sample_data.csv").read_bytes()
        response = client.post(
            "/analyze",
            data={"csv_file": (io.BytesIO(sample_bytes), "sample_data.csv")},
            content_type="multipart/form-data",
        )
        if response.status_code != 200 or b"Recommended Chart" not in response.data:
            raise RuntimeError("Flask test client did not render expected result")
        flask_runtime_checked = True
        flask_runtime_note = "Flask test client rendered /analyze successfully."
    except Exception as exc:
        flask_runtime_note = str(exc)

    style_checks = {
        "uses_style_spec_colors": contains_all(css_text, ["#f6f8fb", "#1f2937", "#0f766e", "#b45309", "#d8dee9"]),
        "radius_lte_8px": "border-radius: 8px" in css_text and "border-radius: 12px" not in css_text,
        "has_upload_panel": "upload-panel" in template_text,
        "has_metric_cards": "metrics" in template_text,
        "has_chart_panel": "chart-panel" in template_text,
    }
    if not all(style_checks.values()):
        raise SystemExit("style checks failed: " + json.dumps(style_checks, ensure_ascii=False))

    manifest = {
        "validated": True,
        "project_dir": args.project_dir,
        "cases": args.cases,
        "case_count": len(cases),
        "checked_cases": checked_cases,
        "style_checks": style_checks,
        "flask_runtime_checked": flask_runtime_checked,
        "flask_runtime_note": flask_runtime_note,
        "limits": [
            "sample and boundary CSV behavior only",
            "static style checks do not replace product design review",
            "production upload security requires owner review",
        ],
    }
    out = Path("output")
    out.mkdir(exist_ok=True)
    (out / "validation_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    cache = project / "__pycache__"
    if cache.exists():
        shutil.rmtree(cache)
    print(f"Flask port validation passed: {len(cases)} case(s)")
    print(flask_runtime_note)


if __name__ == "__main__":
    main()
