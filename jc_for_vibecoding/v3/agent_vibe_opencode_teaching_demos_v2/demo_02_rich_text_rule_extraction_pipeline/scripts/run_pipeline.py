#!/usr/bin/env python3
import subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
subprocess.check_call(["python3", "scripts/create_manual_pdf.py"], cwd=ROOT)
subprocess.check_call(["python3", "scripts/extract_rules_from_manual.py", "--input", "source_docs/validation_manual.pdf", "--output", "output/extracted_rules.json", "--review", "output/human_review_points.md"], cwd=ROOT)
subprocess.check_call(["python3", "scripts/adapt_rules_to_env.py", "--rules", "output/extracted_rules.json", "--env", "env_package/signal_map.json", "--output", "output/adapted_sequence.py", "--ir", "output/sequence_ir.json"], cwd=ROOT)
subprocess.check_call(["python3", "scripts/validate_syntax.py", "--sequence", "output/adapted_sequence.py", "--ir", "output/sequence_ir.json", "--manifest", "output/validation_manifest.json"], cwd=ROOT)
