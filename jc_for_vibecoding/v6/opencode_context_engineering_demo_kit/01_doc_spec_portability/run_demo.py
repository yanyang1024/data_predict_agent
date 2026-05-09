#!/usr/bin/env python3
from __future__ import annotations
import subprocess

subprocess.run(['python3', 'scripts/port_py_to_js.py', '--source', 'references/source/python_order_rules.py', '--output', 'generated/pricing.mjs', '--report', 'output/migration_report.md'], check=True)
subprocess.run(['python3', 'scripts/validate_port.py', '--module', 'generated/pricing.mjs', '--cases', 'tests/golden_cases.json'], check=True)
print('Demo 01 done: generated/pricing.mjs')
