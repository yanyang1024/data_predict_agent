from __future__ import annotations

import csv
import io
import statistics

import gradio as gr


APP_TITLE = "CSV Insight Workbench"


def _number_or_none(value: str):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def analyze_csv(file_obj):
    """Original Gradio implementation used as source material for migration."""
    if file_obj is None:
        return "Please upload a CSV file.", [], "<p>No chart yet.</p>"

    raw = file_obj.read()
    if isinstance(raw, str):
        text = raw
    else:
        text = raw.decode("utf-8-sig")

    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)
    if not reader.fieldnames or not rows:
        return "CSV must include a header row and at least one data row.", [], "<p>No chart yet.</p>"

    summaries = []
    chart_column = None
    chart_values = []
    for column in reader.fieldnames:
        values = []
        for row in rows:
            number = _number_or_none((row.get(column) or "").strip())
            if number is None:
                values = []
                break
            values.append(number)
        if values:
            if chart_column is None:
                chart_column = column
                chart_values = values
            summaries.append(
                [
                    column,
                    len(values),
                    round(statistics.mean(values), 2),
                    round(min(values), 2),
                    round(max(values), 2),
                ]
            )

    overview = (
        f"Rows: {len(rows)} | Columns: {len(reader.fieldnames)} | "
        f"Numeric columns: {len(summaries)} | Chart: {chart_column or 'none'}"
    )
    chart_html = render_bar_svg(chart_column, chart_values)
    return overview, summaries, chart_html


def render_bar_svg(column, values):
    if not column or not values:
        return "<svg viewBox='0 0 640 220'><text x='24' y='40'>No numeric column detected.</text></svg>"
    max_value = max(values) or 1
    bars = []
    for index, value in enumerate(values[:12]):
        height = int((value / max_value) * 150)
        x = 36 + index * 44
        y = 182 - height
        bars.append(f"<rect x='{x}' y='{y}' width='28' height='{height}' rx='4'></rect>")
    return (
        "<svg viewBox='0 0 640 220' role='img'>"
        f"<title>{column} bar chart</title>"
        "<g fill='#0f766e'>" + "".join(bars) + "</g>"
        f"<text x='24' y='28'>{column}</text>"
        "</svg>"
    )


with gr.Blocks(css="""
.gradio-container { max-width: 1120px; margin: auto; background: #f6f8fb; }
.metric-card { border-radius: 8px; border: 1px solid #d8dee9; }
""") as demo:
    gr.Markdown(f"# {APP_TITLE}\nUpload a CSV table to inspect numeric columns and charts.")
    csv_file = gr.File(label="CSV file", file_types=[".csv"])
    analyze = gr.Button("Analyze CSV", variant="primary")
    overview = gr.Markdown()
    summary = gr.Dataframe(headers=["column", "count", "mean", "min", "max"])
    chart = gr.HTML()
    analyze.click(analyze_csv, inputs=[csv_file], outputs=[overview, summary, chart])


if __name__ == "__main__":
    demo.launch()

