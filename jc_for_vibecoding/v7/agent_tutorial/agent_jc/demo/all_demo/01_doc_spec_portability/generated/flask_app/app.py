from __future__ import annotations

import csv
import io
import statistics
from html import escape

try:
    from flask import Flask, render_template, request
except ImportError:  # Allows validation of pure analysis helpers without Flask installed.
    Flask = None
    render_template = None
    request = None


APP_TITLE = "CSV Insight Workbench"
MAX_UPLOAD_BYTES = 2 * 1024 * 1024


def coerce_number(value: str):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_csv_bytes(raw: bytes) -> tuple[list[str], list[dict[str, str]]]:
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        raise ValueError("CSV must include a header row.")
    rows = [
        {key: (value or "").strip() for key, value in row.items()}
        for row in reader
    ]
    if not rows:
        raise ValueError("CSV must include at least one data row.")
    return list(reader.fieldnames), rows


def detect_numeric_columns(fieldnames: list[str], rows: list[dict[str, str]]) -> dict[str, list[float]]:
    numeric: dict[str, list[float]] = {}
    for column in fieldnames:
        values: list[float] = []
        complete_numeric = True
        for row in rows:
            raw_value = row.get(column, "").strip()
            if raw_value == "":
                complete_numeric = False
                break
            number = coerce_number(raw_value)
            if number is None:
                complete_numeric = False
                break
            values.append(number)
        if complete_numeric and values:
            numeric[column] = values
    return numeric


def summarize_numeric(numeric: dict[str, list[float]]) -> list[dict[str, float | int | str]]:
    summaries = []
    for column, values in numeric.items():
        summaries.append(
            {
                "column": column,
                "count": len(values),
                "mean": round(statistics.mean(values), 2),
                "min": round(min(values), 2),
                "max": round(max(values), 2),
            }
        )
    return summaries


def missing_counts(fieldnames: list[str], rows: list[dict[str, str]]) -> list[dict[str, int | str]]:
    return [
        {
            "column": column,
            "missing": sum(1 for row in rows if row.get(column, "").strip() == ""),
        }
        for column in fieldnames
    ]


def build_bar_svg(column: str | None, values: list[float]) -> str:
    if not column or not values:
        return (
            "<svg viewBox='0 0 680 260' role='img' aria-label='empty chart'>"
            "<rect width='680' height='260' fill='#f6f8fb'/>"
            "<text x='28' y='44' fill='#1f2937'>No numeric column detected.</text>"
            "</svg>"
        )

    width = 680
    height = 260
    left = 54
    bottom = 218
    plot_width = 560
    plot_height = 156
    max_value = max(values) or 1
    bar_gap = 10
    bar_width = max(14, int((plot_width - bar_gap * (len(values) - 1)) / max(len(values), 1)))
    bars = []
    for index, value in enumerate(values[:12]):
        bar_height = int((value / max_value) * plot_height)
        x = left + index * (bar_width + bar_gap)
        y = bottom - bar_height
        label = escape(str(index + 1))
        bars.append(
            f"<rect x='{x}' y='{y}' width='{bar_width}' height='{bar_height}' rx='4' fill='#0f766e'/>"
            f"<text x='{x + bar_width / 2:.1f}' y='238' text-anchor='middle' fill='#64748b' font-size='11'>{label}</text>"
        )
    title = escape(column)
    return (
        f"<svg viewBox='0 0 {width} {height}' role='img' aria-label='{title} bar chart'>"
        "<rect width='680' height='260' fill='#ffffff'/>"
        f"<text x='28' y='34' fill='#1f2937' font-size='18' font-weight='700'>{title}</text>"
        "<line x1='54' y1='218' x2='624' y2='218' stroke='#d8dee9'/>"
        "<line x1='54' y1='62' x2='54' y2='218' stroke='#d8dee9'/>"
        + "".join(bars) +
        f"<text x='624' y='56' text-anchor='end' fill='#64748b' font-size='12'>max {round(max_value, 2)}</text>"
        "</svg>"
    )


def analyze_csv_bytes(raw: bytes) -> dict:
    fieldnames, rows = parse_csv_bytes(raw)
    numeric = detect_numeric_columns(fieldnames, rows)
    chart_column = next(iter(numeric.keys()), None)
    chart_values = numeric.get(chart_column, []) if chart_column else []
    return {
        "row_count": len(rows),
        "column_count": len(fieldnames),
        "numeric_count": len(numeric),
        "chart_column": chart_column or "none",
        "summaries": summarize_numeric(numeric),
        "missing_counts": missing_counts(fieldnames, rows),
        "chart_svg": build_bar_svg(chart_column, chart_values),
    }


def create_app():
    if Flask is None:
        raise RuntimeError("Flask is not installed. Run: python3 -m pip install Flask")

    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_BYTES

    @app.get("/")
    def index():
        return render_template("index.html", title=APP_TITLE, result=None, error=None)

    @app.post("/analyze")
    def analyze():
        upload = request.files.get("csv_file")
        if upload is None or upload.filename == "":
            return render_template("index.html", title=APP_TITLE, result=None, error="Please choose a CSV file.")
        try:
            result = analyze_csv_bytes(upload.read())
        except Exception as exc:
            return render_template("index.html", title=APP_TITLE, result=None, error=str(exc))
        return render_template("index.html", title=APP_TITLE, result=result, error=None)

    return app


app = create_app() if Flask is not None else None


if __name__ == "__main__":
    if app is None:
        raise SystemExit("Flask is not installed. Run: python3 -m pip install Flask")
    app.run(debug=True)
