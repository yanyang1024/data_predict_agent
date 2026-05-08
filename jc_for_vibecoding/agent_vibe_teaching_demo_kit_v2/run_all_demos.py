#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_PYTHON = '/usr/bin/python3' if Path('/usr/bin/python3').exists() else sys.executable
PYTHON = os.environ.get('PYTHON', DEFAULT_PYTHON)

COMMANDS = [
    ('00_rule_based_report_generation', [PYTHON, 'scripts/generate_project_report.py']),
    ('00_rule_based_report_generation', [PYTHON, 'scripts/validate_project_report.py']),
    ('01_doc_spec_portability', [PYTHON, 'scripts/build_portable_impl.py']),
    ('01_doc_spec_portability', [PYTHON, 'scripts/validate_portable_impl.py']),
    ('02_rich_doc_pattern_pipeline', [PYTHON, 'scripts/run_pipeline.py', '--input', 'docs/verification_guide.html']),
    ('03_permission_guarded_execution', [PYTHON, 'scripts/guarded_query.py', '--asset', 'PILOT_A', '--start-date', '2026-04-01', '--end-date', '2026-04-07', '--fields', 'timestamp,asset,metric,value', '--output-dir', 'output']),
    ('03_permission_guarded_execution', [PYTHON, 'scripts/request_config_change.py', '--config-key', 'threshold.warning', '--new-value', '0.78', '--reason', 'training demo change request only', '--output-dir', 'output']),
    ('03_permission_guarded_execution', [PYTHON, 'scripts/validate_guardrails.py']),
]


def run_demo(workdir: str, cmd: list[str]) -> None:
    print(f'\n=== {workdir}: {" ".join(cmd)} ===')
    subprocess.run(cmd, cwd=ROOT / workdir, check=True)


def main() -> int:
    for workdir, cmd in COMMANDS:
        run_demo(workdir, cmd)
    print('\nAll demos completed successfully.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
