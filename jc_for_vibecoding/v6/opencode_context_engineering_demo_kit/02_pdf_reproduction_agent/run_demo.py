#!/usr/bin/env python3
from __future__ import annotations
import subprocess

subprocess.run(['python3', 'scripts/extract_pdf_evidence.py', '--pdf', 'papers/synthetic_agent_eval_paper.pdf', '--fallback', 'papers/synthetic_agent_eval_paper_text.md', '--output-dir', 'output'], check=True)
subprocess.run(['python3', 'scripts/build_repro_project.py', '--evidence', 'output/evidence.json', '--env', 'env_pkg/chip_eval_env.py', '--output-dir', 'repro_project'], check=True)
subprocess.run(['python3', 'scripts/validate_repro_project.py', '--project-dir', 'repro_project'], check=True)
print('Demo 02 done: repro_project/')
