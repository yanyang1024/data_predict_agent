#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--proposal', required=True)
    ap.add_argument('--sandbox', required=True)
    ap.add_argument('--output', required=True)
    ap.add_argument('--audit', required=True)
    args = ap.parse_args()
    proposal = json.loads(Path(args.proposal).read_text(encoding='utf-8'))
    if proposal.get('target') != 'sandbox':
        raise SystemExit('only sandbox target is allowed')
    sandbox_path = Path(args.sandbox)
    if sandbox_path.parts and sandbox_path.parts[0] == 'protected':
        raise SystemExit('protected sandbox path is not allowed')
    config = json.loads(sandbox_path.read_text(encoding='utf-8'))
    if config.get('environment') != 'sandbox':
        raise SystemExit('input config must be sandbox')
    flag = proposal['flag']
    config.setdefault('flags', {})[flag] = proposal['value']
    config['last_patch'] = {'flag': flag, 'value': proposal['value'], 'reason': proposal['reason'], 'applied_at': datetime.now(timezone.utc).isoformat()}
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding='utf-8')
    audit = Path(args.audit)
    audit.parent.mkdir(parents=True, exist_ok=True)
    audit_entry = {'event': 'sandbox_patch_applied', 'proposal': args.proposal, 'output': args.output, 'flag': flag, 'protected_written': False, 'ts': datetime.now(timezone.utc).isoformat()}
    with audit.open('a', encoding='utf-8') as f:
        f.write(json.dumps(audit_entry, ensure_ascii=False) + '\n')
    print(f'Sandbox output written: {out}')

if __name__ == '__main__':
    main()
