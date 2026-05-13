#!/usr/bin/env python3
from __future__ import annotations
import subprocess

subprocess.run(['python3', 'scripts/generate_dashboard.py', '--input', 'data/sample_progress.json', '--output-dir', 'output'], check=True)
subprocess.run(['python3', 'scripts/validate_dashboard.py', '--output-dir', 'output'], check=True)
print('Demo 00 done: output/dashboard.html')
