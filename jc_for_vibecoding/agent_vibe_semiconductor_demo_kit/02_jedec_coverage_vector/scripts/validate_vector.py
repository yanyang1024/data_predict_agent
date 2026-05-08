#!/usr/bin/env python3
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output'
errors = []

seq_ir = OUT / 'sequence_ir.json'
vec = OUT / 'finesim_vector.vec'
vv = OUT / 'verilog_vector.v'

if not seq_ir.exists():
    errors.append('Missing sequence_ir.json')
else:
    obj = json.loads(seq_ir.read_text(encoding='utf-8'))
    if len(obj.get('sequences', [])) < 3:
        errors.append('Expected at least 3 sequences')
    if not obj.get('human_review'):
        errors.append('Expected human_review items')

if not vec.exists():
    errors.append('Missing finesim_vector.vec')
else:
    lines = [l for l in vec.read_text(encoding='utf-8').splitlines() if l and not l.startswith('#')]
    header = lines[0].split()
    required = ['cycle','RESET_N','CS_N','WE_N','RE_N','ADDR','WDATA','EXP_RDATA','VDD_MV']
    for r in required:
        if r not in header:
            errors.append(f'Missing vector column {r}')
    for line in lines[1:]:
        if len(line.split()) != len(header):
            errors.append('Vector row width mismatch')
            break

if not vv.exists():
    errors.append('Missing verilog_vector.v')

if errors:
    for e in errors:
        print('ERROR:', e)
    raise SystemExit(1)
print('Validation passed for JEDEC-like vector demo.')
