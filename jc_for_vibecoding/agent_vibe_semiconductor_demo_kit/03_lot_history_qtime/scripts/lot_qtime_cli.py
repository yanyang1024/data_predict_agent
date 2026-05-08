#!/usr/bin/env python3
import argparse
import csv
import json
from datetime import datetime
from pathlib import Path

REQUIRED = ['lot_id','product','route_seq','step_id','equipment_id','chamber_id','recipe_id','move_in','move_out']


def parse_dt(s):
    return datetime.fromisoformat(s)


def hours(delta):
    return round(delta.total_seconds() / 3600.0, 3)


def main():
    ap = argparse.ArgumentParser(description='Synthetic lot history UT/QTime analysis CLI')
    ap.add_argument('--lot-id', required=True)
    ap.add_argument('--input', required=True)
    ap.add_argument('--thresholds', required=True)
    ap.add_argument('--output-dir', required=True)
    args = ap.parse_args()

    inp = Path(args.input)
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    cfg = json.loads(Path(args.thresholds).read_text(encoding='utf-8'))

    with inp.open(encoding='utf-8') as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED if c not in reader.fieldnames]
        if missing:
            raise SystemExit(f'Missing required fields: {missing}')
        rows = [r for r in reader if r['lot_id'] == args.lot_id]

    rows.sort(key=lambda r: int(r['route_seq']))
    warnings = []
    if not rows:
        warnings.append('No rows for requested lot')

    summary = []
    for i, r in enumerate(rows):
        move_in = parse_dt(r['move_in'])
        move_out = parse_dt(r['move_out'])
        ut = hours(move_out - move_in)
        next_step = rows[i+1]['step_id'] if i+1 < len(rows) else ''
        if i+1 < len(rows):
            next_in = parse_dt(rows[i+1]['move_in'])
            qtime = hours(next_in - move_out)
            pair = f"{r['step_id']}->{next_step}"
            threshold = cfg['step_pair_threshold_hours'].get(pair, cfg['default_qtime_hours'])
            flag = qtime > threshold
        else:
            qtime = ''
            pair = ''
            threshold = ''
            flag = False
        summary.append({
            'lot_id': r['lot_id'],
            'route_seq': r['route_seq'],
            'step_id': r['step_id'],
            'equipment_id': r['equipment_id'],
            'chamber_id': r['chamber_id'],
            'recipe_id': r['recipe_id'],
            'move_in': r['move_in'],
            'move_out': r['move_out'],
            'ut_hours': ut,
            'next_step': next_step,
            'step_pair': pair,
            'qtime_hours': qtime,
            'qtime_threshold_hours': threshold,
            'qtime_flag': flag,
        })

    summary_path = out / 'qtime_summary.csv'
    fieldnames = ['lot_id','route_seq','step_id','equipment_id','chamber_id','recipe_id','move_in','move_out','ut_hours','next_step','step_pair','qtime_hours','qtime_threshold_hours','qtime_flag']
    with summary_path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(summary)

    if rows:
        time_range = {'min_move_in': min(r['move_in'] for r in rows), 'max_move_out': max(r['move_out'] for r in rows)}
    else:
        time_range = {'min_move_in': None, 'max_move_out': None}
    manifest = {
        'lot_id': args.lot_id,
        'input': str(inp),
        'summary': str(summary_path),
        'row_count': len(rows),
        'time_range': time_range,
        'warnings': warnings,
        'stop_rule_note': 'This report is for engineering observation only; no lot disposition decision is made.'
    }
    (out / 'analysis_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(f'Wrote {summary_path}')
    print(f'Wrote {out / "analysis_manifest.json"}')

if __name__ == '__main__':
    main()
