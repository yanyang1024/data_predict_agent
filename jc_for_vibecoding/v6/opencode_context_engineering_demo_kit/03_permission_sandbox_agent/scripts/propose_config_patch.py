#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def parse_bool(value: str) -> bool:
    if value.lower() in {'true', '1', 'yes', 'on'}:
        return True
    if value.lower() in {'false', '0', 'no', 'off'}:
        return False
    raise argparse.ArgumentTypeError('value must be boolean')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--flag', required=True)
    ap.add_argument('--value', required=True, type=parse_bool)
    ap.add_argument('--reason', required=True)
    ap.add_argument('--output', required=True)
    args = ap.parse_args()
    policy = json.loads(Path('policy/allowed_flags.json').read_text(encoding='utf-8'))
    if args.flag in policy.get('denied_flags', []):
        raise SystemExit(f'flag denied: {args.flag}')
    if args.flag not in policy.get('allowed_flags', {}):
        raise SystemExit(f'flag not in allowed list: {args.flag}')
    if not args.reason.strip():
        raise SystemExit('reason required')
    proposal = {
        'target': policy['allowed_target'],
        'flag': args.flag,
        'value': args.value,
        'reason': args.reason,
        'review_required': args.flag in policy.get('review_required', []),
        'created_at': datetime.now(timezone.utc).isoformat(),
        'guardrails': ['sandbox_only', 'do_not_edit_protected', 'audit_required']
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proposal, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Proposal written: {out}')

if __name__ == '__main__':
    main()
