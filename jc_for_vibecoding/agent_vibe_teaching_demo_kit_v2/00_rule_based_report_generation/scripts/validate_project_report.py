#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path):
    with path.open(encoding='utf-8') as f:
        return json.load(f)


def main() -> int:
    rules = load_json(ROOT / 'rules/report_rules.json')
    report_path = ROOT / 'output/project_status_report.md'
    manifest_path = ROOT / 'output/report_manifest.json'
    errors = []

    if not report_path.exists():
        errors.append('missing output/project_status_report.md')
        report = ''
    else:
        report = report_path.read_text(encoding='utf-8')

    for section in rules['required_sections']:
        if f'## {section}' not in report:
            errors.append(f'missing required section: {section}')

    lower = report.lower()
    for phrase in rules['forbidden_phrases']:
        if phrase.lower() in lower:
            errors.append(f'forbidden phrase found: {phrase}')

    if not manifest_path.exists():
        errors.append('missing output/report_manifest.json')
    else:
        manifest = load_json(manifest_path)
        if not manifest.get('human_review_required'):
            errors.append('manifest must mark human_review_required=true')

    result = {'ok': not errors, 'errors': errors, 'checks': ['required_sections', 'forbidden_phrases', 'manifest_human_review']}
    (ROOT / 'output/validation_report.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))
    return 0 if not errors else 1


if __name__ == '__main__':
    raise SystemExit(main())
