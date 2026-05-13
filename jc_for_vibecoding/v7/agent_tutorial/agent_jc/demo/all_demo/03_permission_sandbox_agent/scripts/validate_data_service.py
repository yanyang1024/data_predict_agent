#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(8192), b''):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description='Validate controlled lot history service outputs.')
    parser.add_argument('--summary', default='output/lot_history_summary.json')
    parser.add_argument('--chart', default='output/lot_qtime_chart.svg')
    parser.add_argument('--audit-log', default='output/audit_log.jsonl')
    parser.add_argument('--policy', default='policy/data_access_policy.json')
    parser.add_argument('--schema', default='schemas/lot_query_schema.json')
    parser.add_argument('--protected-hashes', default='policy/protected_hashes.json')
    parser.add_argument('--manifest', default='output/data_service_manifest.json')
    args = parser.parse_args()

    errors: list[str] = []
    policy = load_json(ROOT / args.policy)
    schema = load_json(ROOT / args.schema)
    summary_path = ROOT / args.summary
    chart_path = ROOT / args.chart
    summary = load_json(summary_path) if summary_path.exists() else {}

    required = set(schema.get('required', []))
    missing = required - summary.keys()
    if missing:
        errors.append(f'summary missing keys: {sorted(missing)}')

    allowed_fields = set(policy.get('allowed_output_fields', []))
    denied_fields = set(policy.get('denied_output_fields', []))
    extra_fields = set(summary.keys()) - allowed_fields
    leaked_fields = set(summary.keys()).intersection(denied_fields)
    if extra_fields:
        errors.append(f'summary contains fields outside allowlist: {sorted(extra_fields)}')
    if leaked_fields:
        errors.append(f'summary contains denied fields: {sorted(leaked_fields)}')

    lot_id = summary.get('lot_id')
    if lot_id not in policy.get('allowed_lots', []):
        errors.append(f'lot {lot_id!r} is not allowed by policy')
    if not isinstance(summary.get('qtime_risk_steps', []), list):
        errors.append('qtime_risk_steps must be a list')
    if not chart_path.exists() or '<svg' not in chart_path.read_text(encoding='utf-8'):
        errors.append('chart svg is missing or invalid')

    audit_events = []
    audit_path = ROOT / args.audit_log
    if audit_path.exists():
        audit_events = [json.loads(line) for line in audit_path.read_text(encoding='utf-8').splitlines() if line.strip()]
    event_names = {event.get('event') for event in audit_events}
    if 'lot_history_summary_generated' not in event_names:
        errors.append('audit log missing lot_history_summary_generated event')

    protected_hashes = load_json(ROOT / args.protected_hashes)
    protected_results = {}
    for relative_path, expected_hash in protected_hashes.items():
        actual_hash = sha256_file(ROOT / relative_path)
        protected_results[relative_path] = {
            'expected_sha256': expected_hash,
            'actual_sha256': actual_hash,
            'unchanged': actual_hash == expected_hash,
        }
        if actual_hash != expected_hash:
            errors.append(f'protected file changed: {relative_path}')

    manifest = {
        'status': 'failed' if errors else 'passed',
        'summary': args.summary,
        'chart': args.chart,
        'audit_log': args.audit_log,
        'checks': {
            'schema_like': not missing,
            'field_allowlist': not extra_fields and not leaked_fields,
            'lot_allowlist': lot_id in policy.get('allowed_lots', []),
            'audit_events': sorted(event_names),
        },
        'protected_files': protected_results,
        'errors': errors,
        'human_review_required': [
            '自动验证只证明数据服务返回字段受控，不证明真实业务口径正确。',
            'QTime / UT 口径需要数据 owner 和工艺 owner 共同确认。',
            '真实落地时应把脚本替换为带鉴权、审计和限流的 HTTP Data Service。',
        ],
    }
    manifest_path = ROOT / args.manifest
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    if errors:
        print('Data service validation failed:')
        for error in errors:
            print('-', error)
        raise SystemExit(1)
    print('Data service validation passed.')


if __name__ == '__main__':
    main()
