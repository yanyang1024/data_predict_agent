#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import py_compile
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def walk_ops(step):
    if step.get('op') == 'loop':
        yield 'loop'
        for inner in step.get('body', []):
            yield from walk_ops(inner)
    else:
        yield step.get('op')


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--ir', default='output/sequence_ir.json')
    parser.add_argument('--code', default='output/generated_validation_flow.py')
    parser.add_argument('--env', default='env_package/env_config.json')
    parser.add_argument('--output-dir', default='output')
    args = parser.parse_args()

    errors = []
    code_path = ROOT / args.code
    try:
        py_compile.compile(str(code_path), doraise=True)
    except Exception as exc:
        errors.append(f'python syntax failed: {exc}')

    ir = json.loads((ROOT / args.ir).read_text(encoding='utf-8'))
    env = json.loads((ROOT / args.env).read_text(encoding='utf-8'))
    supported = set(env['supported_ops'])
    for seq in ir['sequences']:
        for step in seq['steps']:
            for op in walk_ops(step):
                if op not in supported:
                    errors.append(f'unsupported op in {seq["name"]}: {op}')

    dry_run_log = None
    if not errors:
        completed = subprocess.run([sys.executable, str(code_path)], cwd=ROOT, text=True, capture_output=True, check=True)
        dry_run_log = json.loads(completed.stdout)
        (ROOT / args.output_dir / 'dry_run_log.json').write_text(json.dumps(dry_run_log, indent=2), encoding='utf-8')

    result = {
        'ok': not errors,
        'errors': errors,
        'validated_by_tool': ['python_syntax', 'supported_operation_names', 'dry_run_runtime_no_exception'],
        'not_validated_by_tool': ['spec_logic_correctness', 'coverage_completeness', 'timing_semantics'],
        'logic_validated': False,
        'human_review_required': True,
        'dry_run_event_count': len(dry_run_log or [])
    }
    (ROOT / args.output_dir / 'syntax_manifest.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))
    return 0 if not errors else 1


if __name__ == '__main__':
    raise SystemExit(main())
