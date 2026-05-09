#!/usr/bin/env python3
import argparse, csv, json
from pathlib import Path
from datetime import date, datetime

ROOT = Path(__file__).resolve().parents[1]

def parse_date(s): return datetime.strptime(s, '%Y-%m-%d').date()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--metric', required=True)
    ap.add_argument('--team', required=True)
    ap.add_argument('--start-date', required=True)
    ap.add_argument('--end-date', required=True)
    ap.add_argument('--output', required=True)
    args = ap.parse_args()
    cfg = json.loads((ROOT / 'configs/allowed_params.json').read_text(encoding='utf-8'))
    if args.metric not in cfg['allowed_metrics']:
        raise SystemExit(f'metric not allowed: {args.metric}')
    if args.team not in cfg['allowed_teams']:
        raise SystemExit(f'team not allowed: {args.team}')
    start, end = parse_date(args.start_date), parse_date(args.end_date)
    if end < start:
        raise SystemExit('end-date must be >= start-date')
    if (end - start).days + 1 > int(cfg['max_query_days']):
        raise SystemExit('query window exceeds max_query_days')

    rows = []
    with (ROOT / 'data/mock_metrics.csv').open(encoding='utf-8') as f:
        for r in csv.DictReader(f):
            d = parse_date(r['date'])
            if start <= d <= end and r['team'] == args.team and r['metric'] == args.metric:
                rows.append(r)
    if len(rows) > int(cfg['row_limit']):
        raise SystemExit('row limit exceeded')

    out = Path(args.output); out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['date','team','metric','value'])
        writer.writeheader(); writer.writerows(rows)

    audit = ROOT / 'output/audit_log.jsonl'
    audit.parent.mkdir(exist_ok=True)
    event = {'action':'approved_data_api.query','metric':args.metric,'team':args.team,'start_date':args.start_date,'end_date':args.end_date,'rows':len(rows)}
    with audit.open('a', encoding='utf-8') as f:
        f.write(json.dumps(event, ensure_ascii=False) + '\n')
    print('approved query rows:', len(rows), '->', out)

if __name__ == '__main__':
    main()
