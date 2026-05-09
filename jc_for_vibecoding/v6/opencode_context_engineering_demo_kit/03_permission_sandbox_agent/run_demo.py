#!/usr/bin/env python3
from __future__ import annotations
import subprocess

subprocess.run(['python3', 'scripts/propose_config_patch.py', '--flag', 'beta_dashboard', '--value', 'true', '--reason', 'training demo', '--output', 'output/proposal_001.json'], check=True)
subprocess.run(['python3', 'scripts/apply_patch_to_sandbox.py', '--proposal', 'output/proposal_001.json', '--sandbox', 'workspace/sandbox_config.json', '--output', 'output/sandbox_config_after.json', '--audit', 'output/audit_log.jsonl'], check=True)
subprocess.run(['python3', 'scripts/validate_config_patch.py', '--proposal', 'output/proposal_001.json', '--sandbox-output', 'output/sandbox_config_after.json', '--audit', 'output/audit_log.jsonl'], check=True)
print('Demo 03 done: output/sandbox_config_after.json')
