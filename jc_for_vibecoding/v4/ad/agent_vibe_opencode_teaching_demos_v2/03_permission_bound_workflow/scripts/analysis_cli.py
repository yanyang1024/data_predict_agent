#!/usr/bin/env python3
import argparse, csv, json, statistics
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    ap.add_argument('--output', required=True)
    ap.add_argument('--report', required=True)
    args = ap.parse_args()
    rows = list(csv.DictReader(Path(args.input).open(encoding='utf-8')))
    values = [float(r['value']) for r in rows]
    summary = {
        'row_count': len(rows),
        'metric': rows[0]['metric'] if rows else None,
        'team': rows[0]['team'] if rows else None,
        'min': min(values) if values else None,
        'max': max(values) if values else None,
        'mean': round(statistics.mean(values), 4) if values else None,
        'validated_by_script': ['csv parsed', 'numeric aggregation'],
        'requires_human_review': ['business interpretation', 'production action', 'threshold appropriateness']
    }
    out = Path(args.output); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    report = f"""# Permission Bound Analysis Report\n\n- metric: {summary['metric']}\n- team: {summary['team']}\n- rows: {summary['row_count']}\n- min: {summary['min']}\n- max: {summary['max']}\n- mean: {summary['mean']}\n\n## 自动验证范围\n\n- CSV 读取成功。\n- 数值聚合成功。\n\n## 人工确认范围\n\n- 趋势是否代表真实异常。\n- 是否需要生产动作。\n- 阈值和口径是否合适。\n"""
    Path(args.report).write_text(report, encoding='utf-8')
    print('analysis summary ->', out)

if __name__ == '__main__':
    main()
