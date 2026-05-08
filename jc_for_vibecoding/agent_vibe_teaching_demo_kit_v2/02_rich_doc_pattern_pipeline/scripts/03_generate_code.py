#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def emit_step(step, indent='    '):
    op = step['op']
    if op == 'drive':
        return f"{indent}drive(log, {step['signal']!r}, {step['value']!r}, duration={step.get('duration')!r})"
    if op == 'expect':
        return f"{indent}expect(log, {step['signal']!r}, {step['relation']!r}, {step['value']!r}, within_cycles={step.get('within_cycles')!r})"
    if op == 'wait_cycles':
        return f"{indent}wait_cycles(log, {step['cycles']!r})"
    if op == 'set_jitter':
        return f"{indent}set_jitter(log, {step['clock_signal']!r}, {step['jitter_ns']!r})"
    if op == 'write_bus':
        return f"{indent}write_bus(log, {step['addr_signal']!r}, {step['data_signal']!r}, {step['address']!r}, {step['data']!r})"
    if op == 'loop':
        lines = [f"{indent}for i in range({step['count']}):"]
        for inner in step['body']:
            lines.append(emit_step(inner, indent + '    '))
        return '\n'.join(lines)
    return f"{indent}log.append({{'op': 'human_review_required', 'reason': {step.get('reason', op)!r}}})"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--ir', default='output/sequence_ir.json')
    parser.add_argument('--output', default='output/generated_validation_flow.py')
    args = parser.parse_args()

    ir = json.loads((ROOT / args.ir).read_text(encoding='utf-8'))
    lines = [
        '#!/usr/bin/env python3',
        'from __future__ import annotations',
        'import json',
        'import sys',
        'from pathlib import Path',
        "sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'env_package'))",
        'from test_runtime import begin_sequence, end_sequence, drive, expect, wait_cycles, write_bus, set_jitter',
        '',
        'def run_all():',
        '    log = []',
    ]
    for seq in ir['sequences']:
        lines.append(f"    begin_sequence(log, {seq['name']!r})")
        for step in seq['steps']:
            lines.append(emit_step(step, '    '))
        lines.append(f"    end_sequence(log, {seq['name']!r})")
    lines.extend([
        '    return log',
        '',
        "if __name__ == '__main__':",
        "    print(json.dumps(run_all(), indent=2))",
    ])
    output_path = ROOT / args.output
    output_path.parent.mkdir(exist_ok=True)
    output_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'Generated {args.output}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
