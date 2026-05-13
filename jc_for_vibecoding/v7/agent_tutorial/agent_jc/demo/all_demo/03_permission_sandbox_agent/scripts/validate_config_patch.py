#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_PROPOSAL_KEYS = {
    'proposal_id',
    'requested_change',
    'scope',
    'operations',
    'evidence',
    'human_review',
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(8192), b''):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description='Validate sandbox config proposal outputs.')
    parser.add_argument('--proposal', default='output/proposal_001.json')
    parser.add_argument('--sandbox-after', default='output/sandbox_config_after.json')
    parser.add_argument('--audit-log', default='output/audit_log.jsonl')
    parser.add_argument('--policy', default='policy/allowed_flags.json')
    parser.add_argument('--protected-hashes', default='policy/protected_hashes.json')
    parser.add_argument('--manifest', default='output/validation_manifest.json')
    args = parser.parse_args()

    errors: list[str] = []
    proposal_path = ROOT / args.proposal
    sandbox_after_path = ROOT / args.sandbox_after
    audit_path = ROOT / args.audit_log
    policy = load_json(ROOT / args.policy)
    proposal = load_json(proposal_path)
    sandbox_after = load_json(sandbox_after_path)

    missing = REQUIRED_PROPOSAL_KEYS - proposal.keys()
    if missing:
        errors.append(f'proposal missing keys: {sorted(missing)}')

    change = proposal.get('requested_change', {})
    flag = change.get('flag')
    flag_policy = policy.get('flags', {}).get(flag)
    if not flag_policy or not flag_policy.get('auto_apply'):
        errors.append(f'flag {flag!r} is not auto-apply allowed')
    if proposal.get('scope', {}).get('environment') != policy.get('allowed_environment'):
        errors.append('proposal is not scoped to sandbox')
    if proposal.get('scope', {}).get('target', '').startswith('protected/'):
        errors.append('proposal targets a protected path')

    operations = proposal.get('operations', [])
    if len(operations) != 1:
        errors.append('proposal must contain exactly one operation for this demo')
    else:
        operation = operations[0]
        if operation.get('op') != 'set_flag':
            errors.append('operation must be set_flag')
        if operation.get('path') != ['flags', flag]:
            errors.append('operation path does not match requested flag')
        if sandbox_after.get('environment') != 'sandbox':
            errors.append('sandbox output environment changed')
        if sandbox_after.get('flags', {}).get(flag) != change.get('value'):
            errors.append('sandbox output does not contain requested flag value')

    audit_events = []
    if audit_path.exists():
        audit_events = [json.loads(line) for line in audit_path.read_text(encoding='utf-8').splitlines() if line.strip()]
    event_names = {event.get('event') for event in audit_events}
    if not {'proposal_created', 'sandbox_output_written'} <= event_names:
        errors.append('audit log does not contain required events')

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
        'proposal': args.proposal,
        'sandbox_after': args.sandbox_after,
        'audit_log': args.audit_log,
        'protected_files': protected_results,
        'checks': {
            'proposal_schema_like': not missing,
            'policy_allowlist': bool(flag_policy and flag_policy.get('auto_apply')),
            'sandbox_only': proposal.get('scope', {}).get('environment') == 'sandbox',
            'audit_events': sorted(event_names),
        },
        'errors': errors,
        'human_review_required': [
            '自动验证未覆盖真实生产审批流程。',
            '自动验证未证明业务风险评估充分。',
            'protected 文件 hash 校验由受控脚本完成，Agent 不应直接读取敏感数据内容。',
        ],
    }
    manifest_path = ROOT / args.manifest
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    if errors:
        print('Config patch validation failed:')
        for error in errors:
            print('-', error)
        raise SystemExit(1)
    print('Config patch validation passed.')


if __name__ == '__main__':
    main()
