#!/usr/bin/env python3
from __future__ import annotations
import subprocess

subprocess.run([
    'python3',
    'scripts/port_gradio_to_flask.py',
    '--source',
    'references/source/gradio_csv_analyzer.py',
    '--request',
    'docs/user_migration_request.md',
    '--style-spec',
    'docs/frontend_style_spec.md',
    '--output-dir',
    'generated/flask_app',
    '--report',
    'output/migration_report.md',
], check=True)
subprocess.run([
    'python3',
    'scripts/validate_flask_port.py',
    '--project-dir',
    'generated/flask_app',
    '--cases',
    'tests/analysis_cases.json',
], check=True)
subprocess.run(['python3', '../scripts/demo_viewer.py', '--demo', '01_doc_spec_portability', '--port', '8761', '--restart'], check=True)
print('Demo 01 done: generated/flask_app/')
