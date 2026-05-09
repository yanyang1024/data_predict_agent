#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--module', required=True)
    ap.add_argument('--cases', required=True)
    args = ap.parse_args()
    if not Path(args.module).exists():
        raise SystemExit(f'module not found: {args.module}')
    cases = json.loads(Path(args.cases).read_text(encoding='utf-8'))
    if len(cases) < 3:
        raise SystemExit('need at least 3 golden cases')
    proc = subprocess.run(['node', 'tests/run_golden_cases.mjs', args.module, args.cases], text=True, capture_output=True)
    if proc.returncode != 0:
        print(proc.stdout)
        print(proc.stderr)
        raise SystemExit(proc.returncode)
    manifest = {
        'module': args.module,
        'cases': args.cases,
        'case_count': len(cases),
        'node_stdout': proc.stdout.strip(),
        'validated': True,
        'limits': ['golden cases validate sample behavior only', 'business logic requires human review']
    }
    out = Path('output')
    out.mkdir(exist_ok=True)
    (out / 'validation_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    print(proc.stdout.strip())
    print('Port validation passed.')

if __name__ == '__main__':
    main()
