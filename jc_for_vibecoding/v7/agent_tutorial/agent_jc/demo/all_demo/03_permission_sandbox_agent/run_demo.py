#!/usr/bin/env python3
from __future__ import annotations

import subprocess


subprocess.run(
    [
        'python3',
        'scripts/propose_config_patch.py',
        '--flag',
        'beta_dashboard',
        '--value',
        'true',
        '--reason',
        '培训演示需要',
    ],
    check=True,
)
subprocess.run(['python3', 'scripts/apply_patch_to_sandbox.py'], check=True)
subprocess.run(['python3', 'scripts/validate_config_patch.py'], check=True)
subprocess.run(['python3', 'scripts/query_lot_history_service.py', '--lot', 'LOT-A12'], check=True)
subprocess.run(['python3', 'scripts/validate_data_service.py'], check=True)
subprocess.run(['python3', '../scripts/demo_viewer.py', '--demo', '03_permission_sandbox_agent', '--port', '8763', '--restart'], check=True)
print('Demo 03 done: output/proposal_001.json and output/lot_history_summary.json')
