#!/usr/bin/env python3
import argparse, json, re
from pathlib import Path


def parse_table(md: str):
    lines = [ln.strip() for ln in md.splitlines() if ln.strip().startswith('|')]
    target = []
    in_rules = False
    for i, ln in enumerate(md.splitlines()):
        if ln.strip() == '## 规则表':
            in_rules = True
            continue
        if in_rules and ln.startswith('## '):
            break
        if in_rules and ln.strip().startswith('|'):
            target.append(ln.strip())
    rows = []
    for ln in target:
        if re.match(r'^\|\s*-', ln):
            continue
        cells = [c.strip() for c in ln.strip('|').split('|')]
        rows.append(cells)
    header, data = rows[0], rows[1:]
    rules = []
    for row in data:
        item = dict(zip(header, row))
        item['sla_hours'] = int(item['sla_hours'])
        rules.append(item)
    return rules


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--spec', required=True)
    ap.add_argument('--output', required=True)
    args = ap.parse_args()
    md = Path(args.spec).read_text(encoding='utf-8')
    contract = {
        'name': 'ticket_priority_spec',
        'version': '1.0',
        'entrypoint': 'classify(ticket)',
        'rule_order_is_significant': True,
        'rules': parse_table(md),
        'human_review_required': [
            'severity 大小写归一化是否符合业务预期',
            '多规则命中时采用第一条是否正确',
            'age_hours 缺失时按 0 处理是否正确'
        ]
    }
    out = Path(args.output); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(contract, ensure_ascii=False, indent=2), encoding='utf-8')
    print('wrote', out)

if __name__ == '__main__':
    main()
