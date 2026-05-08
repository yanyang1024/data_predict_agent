#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def adapt(pattern, env):
    sig = env['signals']
    limits = env['limits']
    pid = pattern['pattern_id']
    if pid == 'RESET_STABILITY':
        steps = [
            {'op': 'drive', 'signal': sig['reset'], 'value': 0, 'duration': '5ns'},
            {'op': 'drive', 'signal': sig['reset'], 'value': 1},
            {'op': 'expect', 'signal': sig['ready'], 'relation': '==', 'value': 1, 'within_cycles': 20},
        ]
    elif pid == 'BURST_WRITE_ACK':
        steps = [
            {'op': 'loop', 'count': 4, 'body': [
                {'op': 'write_bus', 'addr_signal': sig['addr'], 'data_signal': sig['data'], 'address': 'addr+i', 'data': 'data+i'},
                {'op': 'expect', 'signal': sig['ack'], 'relation': '==', 'value': 1},
            ]}
        ]
    elif pid == 'CLOCK_JITTER_TOLERANCE':
        steps = [
            {'op': 'set_jitter', 'clock_signal': sig['clock'], 'jitter_ns': limits['max_jitter_ns']},
            {'op': 'wait_cycles', 'cycles': 100},
            {'op': 'expect', 'signal': sig['ready'], 'relation': 'stable', 'value': True},
        ]
    else:
        steps = [{'op': 'human_review_required', 'reason': f'No adaptation rule for {pid}'}]
    return {'name': pid, 'objective': pattern['objective'], 'steps': steps, 'expected_result': pattern['expected_result'], 'human_review': pattern['human_review']}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--patterns', default='output/extracted_patterns.json')
    parser.add_argument('--env', default='env_package/env_config.json')
    parser.add_argument('--output-dir', default='output')
    args = parser.parse_args()

    patterns = json.loads((ROOT / args.patterns).read_text(encoding='utf-8'))['patterns']
    env = json.loads((ROOT / args.env).read_text(encoding='utf-8'))
    sequences = [adapt(pattern, env) for pattern in patterns]
    ir = {
        'schema_version': 'sequence-ir-v1',
        'generated_at': datetime.utcnow().isoformat() + 'Z',
        'environment': env['env_name'],
        'target_language': env['target_language'],
        'sequences': sequences,
        'tool_validation_scope': ['schema', 'supported_ops', 'python_syntax_after_generation'],
        'human_validation_scope': env['human_review_required_for'],
        'logic_validated': False
    }
    output = ROOT / args.output_dir
    output.mkdir(exist_ok=True)
    (output / 'sequence_ir.json').write_text(json.dumps(ir, indent=2), encoding='utf-8')

    lines = ['# Adaptation plan', '', '## Human checkpoints', '', '1. Review extracted patterns before adaptation.', '2. Review this plan before code generation.', '3. Review generated flow logic even if syntax validation passes.', '', '## Sequence plan', '']
    for seq in sequences:
        lines.append(f"### {seq['name']}")
        lines.append(f"- Objective: {seq['objective']}")
        lines.append(f"- Expected: {seq['expected_result']}")
        lines.append(f"- Human review: {seq['human_review']}")
        lines.append(f"- Step count: {len(seq['steps'])}")
        lines.append('')
    (output / 'adaptation_plan.md').write_text('\n'.join(lines), encoding='utf-8')
    print('Generated output/sequence_ir.json and output/adaptation_plan.md')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
