#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    output = ROOT / 'output'
    code_path = output / 'beta_event_monitor.py'
    errors = []
    if not code_path.exists():
        errors.append('missing generated implementation')
    else:
        try:
            py_compile.compile(str(code_path), doraise=True)
        except Exception as exc:
            errors.append(f'py_compile failed: {exc}')

    result_path = output / 'sample_beta_report.json'
    if not errors:
        spec = importlib.util.spec_from_file_location('beta_event_monitor', code_path)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)
        report = module.BetaEventMonitorJob(threshold=2).run(ROOT / 'inputs/sample_events.csv', result_path)
        if report['total_retained'] != 3:
            errors.append(f'expected 3 retained events, got {report["total_retained"]}')
        if report['by_component'].get('api') != 1:
            errors.append('expected one retained api event')

    traceability_path = output / 'requirements_traceability.json'
    if not traceability_path.exists():
        errors.append('missing requirements_traceability.json')
    else:
        traceability = json.loads(traceability_path.read_text(encoding='utf-8'))
        if not traceability.get('human_review_required'):
            errors.append('traceability must require human review')

    result = {'ok': not errors, 'errors': errors, 'validated': ['syntax', 'sample_behavior', 'traceability_manifest'], 'logic_validated_for_real_platform': False}
    (output / 'validation_manifest.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))
    return 0 if not errors else 1


if __name__ == '__main__':
    raise SystemExit(main())
