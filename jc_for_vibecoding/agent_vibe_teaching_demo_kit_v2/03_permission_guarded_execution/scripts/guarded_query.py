#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path):
    with path.open(encoding='utf-8') as f:
        return json.load(f)


def parse_date(value: str):
    return datetime.strptime(value, '%Y-%m-%d').date()


def audit(output_dir: Path, event: dict):
    output_dir.mkdir(exist_ok=True)
    with (output_dir / 'audit_log.jsonl').open('a', encoding='utf-8') as f:
        f.write(json.dumps(event, sort_keys=True) + '\n')


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--asset', required=True)
    parser.add_argument('--start-date', required=True)
    parser.add_argument('--end-date', required=True)
    parser.add_argument('--fields', required=True, help='Comma-separated allowed fields')
    parser.add_argument('--output-dir', default='output')
    args = parser.parse_args()

    contract = load_json(ROOT / 'configs/approved_query_contract.json')
    output_dir = ROOT / args.output_dir
    fields = [f.strip() for f in args.fields.split(',') if f.strip()]
    start = parse_date(args.start_date)
    end = parse_date(args.end_date)
    errors = []

    if args.asset not in contract['allowed_assets']:
        errors.append(f'asset not allowed: {args.asset}')
    disallowed_fields = sorted(set(fields) - set(contract['allowed_fields']))
    if disallowed_fields:
        errors.append(f'fields not allowed: {disallowed_fields}')
    if end < start:
        errors.append('end-date must be >= start-date')
    if (end - start).days > contract['max_window_days']:
        errors.append(f'date window exceeds {contract["max_window_days"]} days')

    if errors:
        audit(output_dir, {'event': 'guarded_query_rejected', 'asset': args.asset, 'errors': errors})
        raise SystemExit('; '.join(errors))

    rows = []
    with (ROOT / 'data/approved_sample_records.csv').open(encoding='utf-8', newline='') as f:
        for row in csv.DictReader(f):
            day = parse_date(row['timestamp'])
            if row['asset'] == args.asset and start <= day <= end:
                rows.append({field: row[field] for field in fields})

    if len(rows) > contract['max_rows']:
        rows = rows[:contract['max_rows']]

    output_dir.mkdir(exist_ok=True)
    result_path = output_dir / 'query_result.csv'
    with result_path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    manifest = {
        'status': 'ok',
        'asset': args.asset,
        'start_date': args.start_date,
        'end_date': args.end_date,
        'fields': fields,
        'row_count': len(rows),
        'contract': 'configs/approved_query_contract.json',
        'output': 'output/query_result.csv',
        'direct_database_access': False
    }
    (output_dir / 'query_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    audit(output_dir, {'event': 'guarded_query_ok', 'asset': args.asset, 'row_count': len(rows), 'fields': fields})
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
