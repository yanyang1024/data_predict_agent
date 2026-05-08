#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--config-key', required=True)
    parser.add_argument('--new-value', required=True)
    parser.add_argument('--reason', required=True)
    parser.add_argument('--output-dir', default='output')
    args = parser.parse_args()

    contract = json.loads((ROOT / 'configs/approved_query_contract.json').read_text(encoding='utf-8'))
    if args.config_key not in contract['allowed_config_change_keys']:
        raise SystemExit(f'config key not allowed for request flow: {args.config_key}')

    output_dir = ROOT / args.output_dir
    output_dir.mkdir(exist_ok=True)
    request = {
        'status': 'pending_human_review',
        'created_at': datetime.utcnow().isoformat() + 'Z',
        'config_key': args.config_key,
        'new_value': args.new_value,
        'reason': args.reason,
        'protected_config_modified': False,
        'human_approval_required': True
    }
    (output_dir / 'config_change_request.json').write_text(json.dumps(request, indent=2), encoding='utf-8')
    with (output_dir / 'audit_log.jsonl').open('a', encoding='utf-8') as f:
        f.write(json.dumps({'event': 'config_change_request_created', 'config_key': args.config_key}, sort_keys=True) + '\n')
    print(json.dumps(request, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
