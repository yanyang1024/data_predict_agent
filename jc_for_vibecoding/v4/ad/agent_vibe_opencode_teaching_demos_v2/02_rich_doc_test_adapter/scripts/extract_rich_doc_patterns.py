#!/usr/bin/env python3
import argparse, json, re, html
from pathlib import Path


def strip_tags(s: str) -> str:
    return html.unescape(re.sub(r'<[^>]+>', '', s)).strip()


def extract_rows(doc: str):
    table_match = re.search(r'<table[^>]*data-role=["\']verification-pattern["\'][^>]*>(.*?)</table>', doc, flags=re.S|re.I)
    if not table_match:
        raise SystemExit('missing verification-pattern table')
    table = table_match.group(1)
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table, flags=re.S|re.I)
    parsed = []
    for row in rows:
        cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, flags=re.S|re.I)
        parsed.append([strip_tags(c) for c in cells])
    header, data = parsed[0], parsed[1:]
    required = ['pattern_id', 'intent', 'native_directive', 'expected', 'review_note']
    if header != required:
        raise SystemExit(f'unexpected header {header}, expected {required}')
    return [dict(zip(header, row)) for row in data]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--doc', required=True)
    ap.add_argument('--rules', required=True)
    ap.add_argument('--output', required=True)
    args = ap.parse_args()
    doc = Path(args.doc).read_text(encoding='utf-8')
    _rules = Path(args.rules).read_text(encoding='utf-8')
    patterns = extract_rows(doc)
    payload = {
        'source_doc': args.doc,
        'extraction_rules': args.rules,
        'patterns': patterns,
        'human_review_required': [p['review_note'] for p in patterns if p.get('review_note')]
    }
    out = Path(args.output); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    print('extracted patterns:', len(patterns), '->', out)

if __name__ == '__main__':
    main()
