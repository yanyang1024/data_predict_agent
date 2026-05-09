#!/usr/bin/env python3
from __future__ import annotations
import os
import shlex
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent

COMMANDS = [
    ("demo_00_rule_based_doc_generation", "python3 scripts/generate_training_artifacts.py --request sample_request.txt --progress data/course_progress.json --template configs/course_template.yaml --output-dir output"),
    ("demo_01_doc_spec_portability", "python3 scripts/extract_spec_rules.py --spec docs/order_pricing_spec.md --output output/normalized_rules.json --report output/spec_extraction_report.md"),
    ("demo_01_doc_spec_portability", "python3 scripts/generate_implementations.py --rules output/normalized_rules.json --output-dir output"),
    ("demo_01_doc_spec_portability", "python3 scripts/validate_portability.py --cases golden_cases/order_pricing_cases.json --python-impl output/platform_python/pricer.py --node-impl output/platform_node/pricer.mjs --report output/portability_report.md"),
    ("demo_02_rich_text_rule_extraction_pipeline", "python3 scripts/run_pipeline.py"),
]


def run(cwd_name: str, command: str):
    cwd = ROOT / cwd_name
    print(f"\n$ cd {cwd_name} && {command}", flush=True)
    completed = subprocess.run(command, cwd=cwd, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=90)
    print(completed.stdout, end="", flush=True)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def main():
    for cwd_name, command in COMMANDS:
        run(cwd_name, command)
    print("\nAll demos generated and validated.")

if __name__ == "__main__":
    main()
