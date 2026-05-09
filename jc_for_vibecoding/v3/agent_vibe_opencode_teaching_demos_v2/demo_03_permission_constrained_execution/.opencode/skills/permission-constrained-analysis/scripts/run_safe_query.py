#!/usr/bin/env python3
import subprocess
subprocess.check_call(["python3", "scripts/approved_query.py", "--dataset", "training_metrics", "--window-days", "14", "--fields", "date,step,value,owner", "--output", "output/query_result.csv", "--manifest", "output/query_manifest.json"])
subprocess.check_call(["python3", "scripts/render_safe_report.py", "--input", "output/query_result.csv", "--manifest", "output/query_manifest.json", "--output", "output/safe_report.md"])
