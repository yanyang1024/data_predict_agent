#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_source(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {'.html', '.htm'}:
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(path.read_text(encoding='utf-8'), 'html.parser')
            return soup.get_text('\n')
        except Exception:
            text = path.read_text(encoding='utf-8')
            return re.sub(r'<[^>]+>', '\n', text)
    if suffix == '.pdf':
        try:
            from pypdf import PdfReader
        except Exception as exc:
            raise SystemExit(f'pypdf is required for PDF extraction: {exc}')
        reader = PdfReader(str(path))
        return '\n'.join(page.extract_text() or '' for page in reader.pages)
    return path.read_text(encoding='utf-8')


def parse_patterns(text: str, rules: dict) -> list[dict]:
    start = re.escape(rules['record_delimiters']['start'])
    end = re.escape(rules['record_delimiters']['end'])
    blocks = re.findall(start + r'(.*?)' + end, text, flags=re.S)
    records = []
    for block in blocks:
        data = {}
        for field in rules['fields']:
            match = re.search(rf'{field}:\s*(.*)', block)
            if match:
                data[field] = match.group(1).strip()
        if data:
            records.append({
                'pattern_id': data.get('PATTERN_ID'),
                'objective': data.get('OBJECTIVE'),
                'native_instruction': data.get('NATIVE'),
                'expected_result': data.get('EXPECTED'),
                'human_review': data.get('HUMAN_REVIEW'),
            })
    return records


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--rules', default='rules/extraction_rules.json')
    parser.add_argument('--output-dir', default='output')
    args = parser.parse_args()

    source_path = ROOT / args.input
    rules = json.loads((ROOT / args.rules).read_text(encoding='utf-8'))
    text = read_source(source_path)
    records = parse_patterns(text, rules)
    output = ROOT / args.output_dir
    output.mkdir(exist_ok=True)
    (output / 'extracted_patterns.json').write_text(json.dumps({'patterns': records}, indent=2), encoding='utf-8')
    manifest = {
        'generated_at': datetime.utcnow().isoformat() + 'Z',
        'source': args.input,
        'record_count': len(records),
        'fields_required': rules['fields'],
        'do_not_infer': rules['do_not_infer'],
        'human_review_required': True,
        'human_checkpoint': 'Review extracted pattern list against source document.'
    }
    (output / 'extraction_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(json.dumps(manifest, indent=2))
    return 0 if records else 1


if __name__ == '__main__':
    raise SystemExit(main())
