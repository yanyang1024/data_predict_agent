#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--proposal', required=True)
    ap.add_argument('--sandbox-output', required=True)
    ap.add_argument('--audit', required=True)
    args = ap.parse_args()
    proposal = json.loads(Path(args.proposal).read_text(encoding='utf-8'))
    sandbox = json.loads(Path(args.sandbox_output).read_text(encoding='utf-8'))
    if proposal.get('target') != 'sandbox':
        raise SystemExit('proposal target must be sandbox')
    if sandbox.get('environment') != 'sandbox':
        raise SystemExit('sandbox output environment must remain sandbox')
    if sandbox.get('flags', {}).get(proposal['flag']) != proposal['value']:
        raise SystemExit('sandbox flag value does not match proposal')
    audit_path = Path(args.audit)
    if not audit_path.exists() or not audit_path.read_text(encoding='utf-8').strip():
        raise SystemExit('audit log missing')
    baseline = json.loads(Path('policy/protected_hashes.json').read_text(encoding='utf-8'))
    protected_ok = True
    current = {}
    for rel, expected in baseline.items():
        digest = sha256(Path(rel))
        current[rel] = digest
        if digest != expected:
            protected_ok = False
    if not protected_ok:
        raise SystemExit('protected file hash changed')
    manifest = {
        'validated_at': datetime.now(timezone.utc).isoformat(),
        'proposal': args.proposal,
        'sandbox_output': args.sandbox_output,
        'audit': args.audit,
        'protected_integrity': protected_ok,
        'protected_hashes': current,
        'review_required': proposal.get('review_required', False),
        'limits': ['validated sandbox patch only', 'production rollout requires human approval']
    }
    out = Path('output')
    out.mkdir(exist_ok=True)
    (out / 'validation_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Config patch validation passed. Protected files unchanged.')

if __name__ == '__main__':
    main()
