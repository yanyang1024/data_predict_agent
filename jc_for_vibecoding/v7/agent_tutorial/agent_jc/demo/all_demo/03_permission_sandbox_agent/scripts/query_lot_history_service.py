#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def append_audit(path: Path, event: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8') as fh:
        fh.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + '\n')


def load_rows(path: Path, lot_id: str) -> list[dict]:
    with path.open(newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        rows = [row for row in reader if row.get('lot_id') == lot_id]
    rows.sort(key=lambda row: int(row['start_min']))
    return rows


def build_chart(rows: list[dict], output: Path, max_qtime_min: int) -> None:
    width = 720
    row_h = 34
    height = 72 + len(rows) * row_h
    max_duration = max(max(int(row['end_min']) - int(row['start_min']), 1) for row in rows)
    bars = []
    previous_end: int | None = None
    for index, row in enumerate(rows):
        start = int(row['start_min'])
        end = int(row['end_min'])
        queue = 0 if previous_end is None else max(0, start - previous_end)
        duration = max(1, end - start)
        y = 48 + index * row_h
        bar_w = max(24, int(duration / max_duration * 360))
        queue_w = min(160, int(queue / max(max_qtime_min, 1) * 160))
        queue_color = '#c5221f' if queue > max_qtime_min else '#fbbc04'
        bars.append(
            f'<text x="20" y="{y + 18}" font-size="12">{row["step"]}</text>'
            f'<rect x="150" y="{y}" width="{bar_w}" height="18" fill="#1a73e8" rx="3" />'
            f'<rect x="530" y="{y}" width="{queue_w}" height="18" fill="{queue_color}" rx="3" />'
            f'<text x="{156 + bar_w}" y="{y + 14}" font-size="11">{duration}m</text>'
            f'<text x="{536 + queue_w}" y="{y + 14}" font-size="11">{queue}m</text>'
        )
        previous_end = end
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" role="img" '
        f'aria-label="Lot history process and queue time chart">'
        '<rect width="100%" height="100%" fill="#fff" />'
        '<text x="20" y="26" font-size="16" font-weight="700">Lot history summary</text>'
        '<text x="150" y="42" font-size="12">Process duration</text>'
        '<text x="530" y="42" font-size="12">Queue time</text>'
        f'{"".join(bars)}'
        '</svg>'
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(svg, encoding='utf-8')


def summarize_lot(rows: list[dict], max_qtime_min: int, chart_path: str) -> dict:
    if not rows:
        raise SystemExit('No lot history rows found.')
    total_process = 0
    total_queue = 0
    max_queue = 0
    qtime_risk_steps = []
    previous_end: int | None = None
    for row in rows:
        start = int(row['start_min'])
        end = int(row['end_min'])
        total_process += end - start
        queue = 0 if previous_end is None else max(0, start - previous_end)
        total_queue += queue
        max_queue = max(max_queue, queue)
        if queue > max_qtime_min:
            qtime_risk_steps.append({'step': row['step'], 'queue_min': queue, 'limit_min': max_qtime_min})
        previous_end = end
    first_start = int(rows[0]['start_min'])
    last_end = int(rows[-1]['end_min'])
    elapsed = max(1, last_end - first_start)
    yield_status = 'fail' if any(row['result'] != 'pass' for row in rows) else 'pass'
    return {
        'lot_id': rows[0]['lot_id'],
        'product': rows[0]['product'],
        'step_count': len(rows),
        'total_process_min': total_process,
        'total_queue_min': total_queue,
        'max_queue_min': max_queue,
        'yield_status': yield_status,
        'utilization': round(total_process / elapsed, 4),
        'qtime_risk_steps': qtime_risk_steps,
        'chart': chart_path,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description='Query lot history through a controlled service wrapper.')
    parser.add_argument('--lot', required=True)
    parser.add_argument('--policy', default='policy/data_access_policy.json')
    parser.add_argument('--output', default='output/lot_history_summary.json')
    parser.add_argument('--chart', default='output/lot_qtime_chart.svg')
    parser.add_argument('--audit-log', default='output/audit_log.jsonl')
    args = parser.parse_args()

    policy = load_json(ROOT / args.policy)
    if args.lot not in policy.get('allowed_lots', []):
        raise SystemExit(f'Lot {args.lot!r} is not allowed by data access policy.')
    source = ROOT / policy['source']
    rows = load_rows(source, args.lot)
    max_qtime_min = int(policy.get('max_qtime_min', 60))
    build_chart(rows, ROOT / args.chart, max_qtime_min)
    summary = summarize_lot(rows, max_qtime_min, args.chart)
    denied = set(policy.get('denied_output_fields', []))
    leaked = denied.intersection(summary.keys())
    if leaked:
        raise SystemExit(f'Denied fields leaked into output: {sorted(leaked)}')

    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    append_audit(
        ROOT / args.audit_log,
        {
            'event': 'lot_history_summary_generated',
            'lot_id': args.lot,
            'output': args.output,
            'chart': args.chart,
            'timestamp': datetime.now(timezone.utc).isoformat(),
        },
    )
    print(f'Wrote {args.output} and {args.chart}')


if __name__ == '__main__':
    main()
