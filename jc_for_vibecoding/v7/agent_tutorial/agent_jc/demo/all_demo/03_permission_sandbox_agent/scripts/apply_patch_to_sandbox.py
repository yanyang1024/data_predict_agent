#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def append_audit(path: Path, event: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8') as fh:
        fh.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + '\n')


def main() -> None:
    parser = argparse.ArgumentParser(description='Apply an approved proposal to sandbox output only.')
    parser.add_argument('--proposal', default='output/proposal_001.json')
    parser.add_argument('--sandbox', default='workspace/sandbox_config.json')
    parser.add_argument('--output', default='output/sandbox_config_after.json')
    parser.add_argument('--audit-log', default='output/audit_log.jsonl')
    args = parser.parse_args()

    proposal = load_json(ROOT / args.proposal)
    sandbox = load_json(ROOT / args.sandbox)
    if proposal.get('scope', {}).get('environment') != 'sandbox':
        raise SystemExit('Proposal target is not sandbox.')
    if proposal.get('scope', {}).get('target') != args.sandbox:
        raise SystemExit('Proposal target does not match sandbox input.')

    after = copy.deepcopy(sandbox)
    for operation in proposal.get('operations', []):
        if operation.get('op') != 'set_flag':
            raise SystemExit(f'Unsupported operation: {operation.get("op")}')
        path = operation.get('path', [])
        if len(path) != 2 or path[0] != 'flags':
            raise SystemExit(f'Unsupported path: {path}')
        flag = path[1]
        if flag not in after.get('flags', {}):
            raise SystemExit(f'Flag {flag!r} does not exist in sandbox config.')
        if after['flags'][flag] != operation.get('before'):
            raise SystemExit(f'Before value mismatch for {flag!r}.')
        after['flags'][flag] = operation.get('after')

    output_path = ROOT / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(after, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    append_audit(
        ROOT / args.audit_log,
        {
            'event': 'sandbox_output_written',
            'proposal_id': proposal['proposal_id'],
            'output': args.output,
            'timestamp': datetime.now(timezone.utc).isoformat(),
        },
    )
    print(f'Wrote {args.output}')


if __name__ == '__main__':
    main()
