#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

DEMOS = [
    '00_rule_dashboard_agent',
    '01_doc_spec_portability',
    '02_pdf_reproduction_agent',
    '03_permission_sandbox_agent',
]

root = Path(__file__).resolve().parent
failures = []
for demo in DEMOS:
    print(f'\n=== Running {demo} ===', flush=True)
    demo_dir = root / demo
    if not demo_dir.exists():
        print(f'Missing demo directory: {demo_dir}', flush=True)
        failures.append(demo)
        continue
    proc = subprocess.run(['python3', 'run_demo.py'], cwd=demo_dir, text=True)
    if proc.returncode != 0:
        failures.append(demo)

print('\n=== Validating OpenCode context files ===', flush=True)
proc = subprocess.run(['python3', 'scripts/validate_opencode_context.py'], cwd=root, text=True)
if proc.returncode != 0:
    failures.append('context-validation')

if failures:
    print('FAILED:', ', '.join(failures))
    raise SystemExit(1)
print('\nAll demos completed successfully.')
