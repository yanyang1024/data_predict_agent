#!/usr/bin/env python3
from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parents[1]
cpp = ROOT / 'output/B_program_candidate/main.cpp'
pat = ROOT / 'output/B_program_candidate/pattern_b_generated.pat'
unsupported = ROOT / 'output/unsupported_functions.csv'

errors = []
if not cpp.exists():
    errors.append('Missing converted main.cpp')
else:
    text = cpp.read_text(encoding='utf-8')
    if 'a_load_pattern' in text or 'a_run_pattern' in text:
        errors.append('Converted C++ still contains direct platform A calls')
    if 'TODO HUMAN REVIEW' not in text:
        errors.append('Expected a human review marker for unsupported binning')

if not pat.exists():
    errors.append('Missing converted pattern')
else:
    ptext = pat.read_text(encoding='utf-8')
    for token in ['PATTERN', 'TIMESET', 'VECTOR', 'ENDPATTERN']:
        if token in ptext:
            errors.append(f'Converted pattern still contains A token {token}')

if not unsupported.exists():
    errors.append('Missing unsupported_functions.csv')
else:
    rows = list(csv.DictReader(unsupported.open(encoding='utf-8')))
    if not any(r['source_function'] == 'a_enable_binning' for r in rows):
        errors.append('Expected a_enable_binning in unsupported list')

if errors:
    for e in errors:
        print('ERROR:', e)
    raise SystemExit(1)
print('Validation passed for tester platform porting demo.')
