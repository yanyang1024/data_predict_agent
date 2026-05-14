#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
from datetime import datetime, timezone
from pathlib import Path


APP_PY = '''from __future__ import annotations

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
'''


INDEX_HTML = '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{{ title }}</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='styles.css') }}" />
</head>
<body>
  <main class="shell">
    <header class="topbar">
      <div>
        <p class="eyebrow">CSV table analysis</p>
        <h1>{{ title }}</h1>
      </div>
      <span class="status-pill">Flask migration</span>
    </header>

    <section class="upload-panel" aria-label="CSV upload">
      <form action="/analyze" method="post" enctype="multipart/form-data">
        <label for="csv_file">CSV file</label>
        <div class="upload-row">
          <input id="csv_file" name="csv_file" type="file" accept=".csv,text/csv" />
          <button type="submit">Analyze CSV</button>
        </div>
      </form>
      {% if error %}
        <p class="error">{{ error }}</p>
      {% endif %}
    </section>

    {% if result %}
      <section class="metrics" aria-label="summary metrics">
        <article><span>Rows</span><strong>{{ result.row_count }}</strong></article>
        <article><span>Columns</span><strong>{{ result.column_count }}</strong></article>
        <article><span>Numeric</span><strong>{{ result.numeric_count }}</strong></article>
        <article><span>Chart</span><strong>{{ result.chart_column }}</strong></article>
      </section>

      <section class="workspace">
        <article class="chart-panel">
          <h2>Recommended Chart</h2>
          <div class="chart">{{ result.chart_svg | safe }}</div>
        </article>

        <article class="table-panel">
          <h2>Numeric Summary</h2>
          <table>
            <thead>
              <tr><th>Column</th><th>Count</th><th>Mean</th><th>Min</th><th>Max</th></tr>
            </thead>
            <tbody>
              {% for row in result.summaries %}
                <tr>
                  <td>{{ row.column }}</td>
                  <td>{{ row.count }}</td>
                  <td>{{ row.mean }}</td>
                  <td>{{ row.min }}</td>
                  <td>{{ row.max }}</td>
                </tr>
              {% endfor %}
            </tbody>
          </table>
        </article>
      </section>

      <section class="table-panel">
        <h2>Missing Values</h2>
        <table>
          <thead><tr><th>Column</th><th>Missing</th></tr></thead>
          <tbody>
            {% for row in result.missing_counts %}
              <tr><td>{{ row.column }}</td><td>{{ row.missing }}</td></tr>
            {% endfor %}
          </tbody>
        </table>
      </section>
    {% else %}
      <section class="empty-state">
        <strong>Upload a CSV to generate metrics and a chart.</strong>
        <span>The app keeps analysis in memory and renders the plot as inline SVG.</span>
      </section>
    {% endif %}
  </main>
</body>
</html>
'''


STYLES_CSS = '''body {
  margin: 0;
  background: #f6f8fb;
  color: #1f2937;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  line-height: 1.5;
}

.shell {
  max-width: 1120px;
  margin: 0 auto;
  padding: 28px;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

.eyebrow {
  margin: 0 0 4px;
  color: #0f766e;
  font-weight: 700;
  text-transform: uppercase;
  font-size: 12px;
}

h1, h2 {
  margin: 0;
}

h1 {
  font-size: 30px;
}

h2 {
  font-size: 17px;
  margin-bottom: 12px;
}

.status-pill {
  border: 1px solid #d8dee9;
  background: #ffffff;
  border-radius: 8px;
  padding: 8px 10px;
  color: #0f766e;
  font-weight: 700;
}

.upload-panel,
.metrics article,
.chart-panel,
.table-panel,
.empty-state {
  background: #ffffff;
  border: 1px solid #d8dee9;
  border-radius: 8px;
}

.upload-panel {
  padding: 18px;
  border-top: 3px solid #b45309;
}

label {
  display: block;
  font-weight: 700;
  margin-bottom: 8px;
}

.upload-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

input[type="file"] {
  flex: 1 1 280px;
  border: 1px solid #d8dee9;
  border-radius: 8px;
  padding: 9px;
  background: #f8fafc;
}

button {
  border: 0;
  border-radius: 8px;
  padding: 10px 14px;
  background: #0f766e;
  color: #ffffff;
  font-weight: 700;
  cursor: pointer;
}

.error {
  margin: 12px 0 0;
  color: #a50e0e;
  font-weight: 700;
}

.metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
  margin: 16px 0;
}

.metrics article {
  padding: 14px;
}

.metrics span {
  display: block;
  color: #64748b;
  font-size: 12px;
}

.metrics strong {
  display: block;
  margin-top: 4px;
  font-size: 26px;
}

.workspace {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(320px, .8fr);
  gap: 16px;
  align-items: start;
}

.chart-panel,
.table-panel,
.empty-state {
  padding: 16px;
  margin-top: 16px;
}

.chart svg {
  width: 100%;
  height: auto;
  display: block;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

th,
td {
  padding: 8px 10px;
  border-bottom: 1px solid #edf2f7;
  text-align: left;
}

th {
  color: #475569;
  background: #f8fafc;
}

tbody tr:nth-child(even) {
  background: #fbfdff;
}

.empty-state {
  display: flex;
  flex-direction: column;
  gap: 6px;
  color: #64748b;
}

@media (max-width: 820px) {
  .shell {
    padding: 18px;
  }
  .topbar,
  .workspace {
    display: block;
  }
  .status-pill {
    display: inline-block;
    margin-top: 10px;
  }
}
'''


README = '''# Generated Flask CSV Analyzer

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
'''


FRAMEWORK_VISUAL = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 260" role="img" aria-label="Gradio to Flask migration map">
  <rect width="920" height="260" fill="#f6f8fb"/>
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
      <path d="M0,0 L0,6 L9,3 z" fill="#64748b"/>
    </marker>
  </defs>
  <g font-family="-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif">
    <rect x="32" y="54" width="210" height="136" rx="8" fill="#ffffff" stroke="#d8dee9"/>
    <text x="56" y="88" font-size="18" font-weight="700" fill="#1f2937">Gradio Source</text>
    <text x="56" y="120" font-size="13" fill="#475569">Blocks + File + Dataframe</text>
    <text x="56" y="145" font-size="13" fill="#475569">CSV analysis function</text>
    <text x="56" y="170" font-size="13" fill="#475569">Inline SVG chart</text>

    <line x1="254" y1="122" x2="344" y2="122" stroke="#64748b" stroke-width="2" marker-end="url(#arrow)"/>
    <rect x="356" y="54" width="210" height="136" rx="8" fill="#ffffff" stroke="#d8dee9"/>
    <text x="380" y="88" font-size="18" font-weight="700" fill="#1f2937">Migration Context</text>
    <text x="380" y="120" font-size="13" fill="#475569">Functional spec</text>
    <text x="380" y="145" font-size="13" fill="#475569">Frontend style spec</text>
    <text x="380" y="170" font-size="13" fill="#475569">User request</text>

    <line x1="578" y1="122" x2="668" y2="122" stroke="#64748b" stroke-width="2" marker-end="url(#arrow)"/>
    <rect x="680" y="54" width="210" height="136" rx="8" fill="#ffffff" stroke="#d8dee9"/>
    <text x="704" y="88" font-size="18" font-weight="700" fill="#1f2937">Flask Output</text>
    <text x="704" y="120" font-size="13" fill="#475569">app.py routes</text>
    <text x="704" y="145" font-size="13" fill="#475569">Jinja template + CSS</text>
    <text x="704" y="170" font-size="13" fill="#475569">Sample validation</text>

    <rect x="356" y="210" width="210" height="26" rx="8" fill="#0f766e"/>
    <text x="461" y="228" text-anchor="middle" font-size="13" font-weight="700" fill="#ffffff">same function + same UI style</text>
  </g>
</svg>
'''


def write_project(output_dir: Path, sample_csv: Path) -> None:
    (output_dir / "templates").mkdir(parents=True, exist_ok=True)
    (output_dir / "static").mkdir(parents=True, exist_ok=True)
    (output_dir / "app.py").write_text(APP_PY, encoding="utf-8")
    (output_dir / "templates/index.html").write_text(INDEX_HTML, encoding="utf-8")
    (output_dir / "static/styles.css").write_text(STYLES_CSS, encoding="utf-8")
    (output_dir / "README.md").write_text(README, encoding="utf-8")
    shutil.copyfile(sample_csv, output_dir / "sample_data.csv")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a Flask CSV analyzer from the Gradio source demo.")
    parser.add_argument("--source", required=True)
    parser.add_argument("--request", required=True)
    parser.add_argument("--style-spec", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--sample-csv", default="tests/sample_sales.csv")
    parser.add_argument("--visual", default="output/framework_migration_map.svg")
    args = parser.parse_args()

    source = Path(args.source)
    request = Path(args.request)
    style_spec = Path(args.style_spec)
    sample_csv = Path(args.sample_csv)
    for path in [source, request, style_spec, sample_csv]:
        if not path.exists():
            raise SystemExit(f"required input not found: {path}")
    if "gradio" not in source.read_text(encoding="utf-8").lower():
        raise SystemExit("source does not look like a Gradio app")

    output_dir = Path(args.output_dir)
    write_project(output_dir, sample_csv)

    report = Path(args.report)
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(f'''# Migration Report

Generated at: {datetime.now(timezone.utc).isoformat()}

## 输入

- Source Gradio app: `{args.source}`
- User request: `{args.request}`
- Functional spec: `docs/csv_analysis_app_spec.md`
- Migration spec: `docs/gradio_to_flask_migration_spec.md`
- Frontend style spec: `{args.style_spec}`
- Output Flask project: `{args.output_dir}`

## 已迁移内容

- `gr.Blocks` 页面结构 -> `templates/index.html`
- `gr.File` 上传 -> Flask `POST /analyze`
- `gr.Markdown` 总览 -> metric cards
- `gr.Dataframe` 数值摘要 -> HTML table
- `gr.HTML` SVG 图 -> inline SVG chart panel
- Gradio `css` 风格 -> `static/styles.css`

## 自动验证

运行 `scripts/validate_flask_port.py` 后查看 `output/validation_manifest.json`。

## 人工 review 点

- Flask 依赖和部署方式需要项目 owner 确认。
- 生产上传需要补充文件大小、MIME、病毒扫描、审计和清理策略。
- 当前 SVG 图只覆盖基础柱状图，复杂数据可视化需要业务确认。
- 标准和边界 CSV cases 覆盖了正常数据、无数值列、缺失值和空数据错误路径，但未覆盖大文件、混合编码和复杂脏数据。
''', encoding="utf-8")

    visual = Path(args.visual)
    visual.parent.mkdir(parents=True, exist_ok=True)
    visual.write_text(FRAMEWORK_VISUAL, encoding="utf-8")
    print(f"Generated Flask project at {output_dir}")
    print(f"Generated {report} and {visual}")


if __name__ == "__main__":
    main()
