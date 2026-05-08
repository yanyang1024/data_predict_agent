#!/usr/bin/env python3
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
cmds = [
    ['python3', 'scripts/convert_tester_program.py'],
    ['python3', 'scripts/generate_verification_artifacts.py'],
    ['python3', 'scripts/lot_qtime_cli.py', '--lot-id', 'LOT1001', '--input', 'mock_data/lot_history_sample.csv', '--thresholds', 'configs/qtime_thresholds.json', '--output-dir', 'output'],
    ['python3', 'scripts/render_report.py', '--summary', 'output/qtime_summary.csv', '--manifest', 'output/analysis_manifest.json', '--output', 'output/lot_history_report.md'],
]
folders = [
    ROOT / '01_tester_platform_porting',
    ROOT / '02_jedec_coverage_vector',
    ROOT / '03_lot_history_qtime',
    ROOT / '03_lot_history_qtime',
]
for folder, cmd in zip(folders, cmds):
    print(f'==> {folder.name}: {" ".join(cmd)}')
    subprocess.run(cmd, cwd=folder, check=True)
print('All demos completed.')
