#!/usr/bin/env python3
import subprocess
subprocess.check_call(["python3", "scripts/extract_spec_rules.py", "--spec", "docs/order_pricing_spec.md", "--output", "output/normalized_rules.json", "--report", "output/spec_extraction_report.md"])
subprocess.check_call(["python3", "scripts/generate_implementations.py", "--rules", "output/normalized_rules.json", "--output-dir", "output"])
subprocess.check_call(["python3", "scripts/validate_portability.py", "--cases", "golden_cases/order_pricing_cases.json", "--python-impl", "output/platform_python/pricer.py", "--node-impl", "output/platform_node/pricer.mjs", "--report", "output/portability_report.md"])
