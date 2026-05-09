#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

def run(args):
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True)

# Allowed safe query
ok = run([sys.executable, "scripts/approved_query.py", "--dataset", "training_metrics", "--window-days", "14", "--fields", "date,step,value,owner", "--output", "output/test_query.csv", "--manifest", "output/test_manifest.json"])
assert ok.returncode == 0, ok.stderr

# Block unknown dataset
blocked_dataset = run([sys.executable, "scripts/approved_query.py", "--dataset", "prod_sensitive", "--window-days", "14", "--fields", "date,value", "--output", "output/bad.csv", "--manifest", "output/bad.json"])
assert blocked_dataset.returncode != 0
assert "dataset not allowed" in blocked_dataset.stderr or "dataset not allowed" in blocked_dataset.stdout

# Block too-large window
blocked_window = run([sys.executable, "scripts/approved_query.py", "--dataset", "training_metrics", "--window-days", "365", "--fields", "date,value", "--output", "output/bad.csv", "--manifest", "output/bad.json"])
assert blocked_window.returncode != 0
assert "exceeds max" in blocked_window.stderr or "exceeds max" in blocked_window.stdout

# Block disallowed fields
blocked_field = run([sys.executable, "scripts/approved_query.py", "--dataset", "training_metrics", "--window-days", "14", "--fields", "date,secret_metric", "--output", "output/bad.csv", "--manifest", "output/bad.json"])
assert blocked_field.returncode != 0
assert "fields not allowed" in blocked_field.stderr or "fields not allowed" in blocked_field.stdout

print("permission boundary tests passed")
