#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {'true', '1', 'yes', 'y', 'on'}:
        return True
    if normalized in {'false', '0', 'no', 'n', 'off'}:
        return False
    raise argparse.ArgumentTypeError(f'Invalid boolean value: {value}')


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def append_audit(path: Path, event: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8') as fh:
        fh.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + '\n')


def main() -> None:
    parser = argparse.ArgumentParser(description='Create an auditable sandbox config proposal.')
    parser.add_argument('--flag', required=True)
    parser.add_argument('--value', required=True, type=parse_bool)
    parser.add_argument('--reason', required=True)
    parser.add_argument('--policy', default='policy/allowed_flags.json')
    parser.add_argument('--sandbox', default='workspace/sandbox_config.json')
    parser.add_argument('--proposal', default='output/proposal_001.json')
    parser.add_argument('--audit-log', default='output/audit_log.jsonl')
    args = parser.parse_args()

    policy_path = ROOT / args.policy
    sandbox_path = ROOT / args.sandbox
    proposal_path = ROOT / args.proposal
    audit_path = ROOT / args.audit_log
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.write_text('', encoding='utf-8')

    policy = load_json(policy_path)
    sandbox = load_json(sandbox_path)
    flag_policy = policy.get('flags', {}).get(args.flag)
    if not flag_policy:
        raise SystemExit(f'Flag {args.flag!r} is not declared in policy allowlist.')
    if not flag_policy.get('auto_apply'):
        raise SystemExit(f'Flag {args.flag!r} requires human approval and cannot be auto-applied.')
    if flag_policy.get('type') != 'boolean':
        raise SystemExit(f'Flag {args.flag!r} is not a boolean flag.')
    if sandbox.get('environment') != policy.get('allowed_environment'):
        raise SystemExit('Only sandbox environment can be changed by this demo.')
    if len(args.reason.strip()) < int(policy.get('required_reason_min_length', 1)):
        raise SystemExit('Reason is too short for audit.')
    if args.flag not in sandbox.get('flags', {}):
        raise SystemExit(f'Flag {args.flag!r} does not exist in sandbox config.')

    before = sandbox['flags'][args.flag]
    proposal = {
        'proposal_id': 'proposal_001',
        'requested_change': {
            'flag': args.flag,
            'value': args.value,
            'reason': args.reason.strip(),
        },
        'scope': {
            'environment': sandbox['environment'],
            'target': 'workspace/sandbox_config.json',
            'write_output': 'output/sandbox_config_after.json',
        },
        'action_space': {
            'allowed_scripts': [
                'scripts/propose_config_patch.py',
                'scripts/apply_patch_to_sandbox.py',
                'scripts/validate_config_patch.py',
            ],
            'denied_paths': policy['denied_paths'],
        },
        'operations': [
            {
                'op': 'set_flag',
                'path': ['flags', args.flag],
                'before': before,
                'after': args.value,
            }
        ],
        'evidence': {
            'policy': args.policy,
            'schema': 'schemas/config_patch_schema.json',
            'sandbox_before': args.sandbox,
        },
        'human_review': [
            '确认业务原因是否充分。',
            '确认该变更只应用到 sandbox，而不是 production。',
            '确认自动验证只覆盖结构、安全边界和样例行为。',
        ],
    }

    proposal_path.parent.mkdir(parents=True, exist_ok=True)
    proposal_path.write_text(json.dumps(proposal, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    append_audit(
        audit_path,
        {
            'event': 'proposal_created',
            'proposal_id': proposal['proposal_id'],
            'flag': args.flag,
            'value': args.value,
            'timestamp': datetime.now(timezone.utc).isoformat(),
        },
    )
    print(f'Wrote {args.proposal}')


if __name__ == '__main__':
    main()
