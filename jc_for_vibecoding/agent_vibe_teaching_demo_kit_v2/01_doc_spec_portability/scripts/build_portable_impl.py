#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path):
    with path.open(encoding='utf-8') as f:
        return json.load(f)


def make_mapping_table(mapping):
    lines = ['# Platform mapping table', '', '| Source concept | Target concept | Status | Note |', '|---|---|---|---|']
    for row in mapping:
        lines.append(f"| `{row['source']}` | `{row['target']}` | {row['status']} | {row['note']} |")
    return '\n'.join(lines) + '\n'


def main() -> int:
    config = load_json(ROOT / 'configs/portability_rules.json')
    output = ROOT / 'output'
    output.mkdir(exist_ok=True)
    (output / 'mapping_table.md').write_text(make_mapping_table(config['mapping']), encoding='utf-8')

    code = r'''
#!/usr/bin/env python3
"""Generated Beta implementation for Widget event monitor.

Teaching note: this file uses local stand-ins for Beta SDK classes so the demo
runs anywhere. In a real migration, the adapter classes would wrap real SDK APIs.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


class BetaDataset:
    """Adapter for REQ-1 input loading."""

    @staticmethod
    def from_csv(path: str | Path) -> list[dict[str, str]]:
        with Path(path).open(encoding='utf-8', newline='') as f:
            return list(csv.DictReader(f))


class BetaRuntime:
    """Adapter for target-platform schema validation."""

    @staticmethod
    def validate_schema(records: list[dict[str, str]], required_fields: set[str]) -> None:
        for index, record in enumerate(records):
            missing = required_fields - set(record)
            if missing:
                raise ValueError(f'record {index} missing fields: {sorted(missing)}')


class BetaReport:
    """Adapter for REQ-5 output emission."""

    @staticmethod
    def write_json(path: str | Path, payload: dict) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(json.dumps(payload, indent=2, sort_keys=True), encoding='utf-8')


class BetaEventMonitorJob:
    def __init__(self, threshold: int):
        self.threshold = int(threshold)

    def run(self, input_csv: str | Path, output_json: str | Path) -> dict:
        records = BetaDataset.from_csv(input_csv)  # REQ-1
        BetaRuntime.validate_schema(records, {'timestamp', 'component', 'severity', 'message'})

        normalized = []
        for record in records:
            normalized.append({
                'component': record['component'].strip(),  # REQ-2
                'severity': int(record['severity']),       # REQ-2
                'message': record['message'],
                'timestamp': record['timestamp'],
            })

        retained = [row for row in normalized if row['severity'] >= self.threshold]  # REQ-3
        by_component = dict(Counter(row['component'] for row in retained))           # REQ-4
        report = {
            'threshold': self.threshold,
            'total_retained': len(retained),
            'by_component': by_component,
        }
        BetaReport.write_json(output_json, report)  # REQ-5
        return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--threshold', type=int, default=2)
    args = parser.parse_args()
    BetaEventMonitorJob(args.threshold).run(args.input, args.output)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
'''
    (output / 'beta_event_monitor.py').write_text(code.lstrip(), encoding='utf-8')

    traceability = {
        'generated_at': datetime.utcnow().isoformat() + 'Z',
        'requirements': config['required_traceability'],
        'implementation': 'output/beta_event_monitor.py',
        'mapping_table': 'output/mapping_table.md',
        'human_review_required': True,
        'human_review_rules': config['human_review_rules']
    }
    (output / 'requirements_traceability.json').write_text(json.dumps(traceability, indent=2), encoding='utf-8')

    report_lines = [
        '# Portability report',
        '',
        '## What was generated',
        '',
        '- `output/mapping_table.md`',
        '- `output/beta_event_monitor.py`',
        '- `output/requirements_traceability.json`',
        '',
        '## Human review points',
        '',
    ]
    report_lines.extend(f'- {item}' for item in config['human_review_rules'])
    report_lines.extend(['', '## Validation scope', '', 'The validator runs a small sample and checks syntax. It does not prove real platform compatibility.'])
    (output / 'portability_report.md').write_text('\n'.join(report_lines) + '\n', encoding='utf-8')
    print('Generated portable implementation in output/.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
