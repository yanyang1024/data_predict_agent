#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

ADAPTIVE_WINDOW = '''from __future__ import annotations

from pathlib import Path
from chip_eval_env import load_signal_csv, mean, std, write_json


def detect_anomalies(values: list[float], window: int = 4, threshold: float = 2.5) -> list[dict]:
    anomalies: list[dict] = []
    for i, value in enumerate(values):
        if i < window:
            continue
        baseline = values[i - window:i]
        score = abs(value - mean(baseline)) / max(std(baseline), 1e-6)
        if score >= threshold:
            anomalies.append({'index': i, 'value': value, 'score': round(score, 4)})
    return anomalies


def run(input_csv: str | Path, output_json: str | Path, window: int = 4, threshold: float = 2.5) -> dict:
    values = load_signal_csv(input_csv)
    anomalies = detect_anomalies(values, window=window, threshold=threshold)
    payload = {'window': window, 'threshold': threshold, 'count': len(anomalies), 'anomalies': anomalies}
    write_json(output_json, payload)
    return payload


if __name__ == '__main__':
    run('data/sample_signal.csv', 'output/anomalies.json')
'''

TEST_CODE = '''from __future__ import annotations

import json
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT))

from adaptive_window import detect_anomalies, run


class AdaptiveWindowTests(unittest.TestCase):
    def test_detects_expected_demo_anomaly(self):
        values = [10, 11, 10, 12, 11, 10, 12, 11, 30, 12, 11]
        anomalies = detect_anomalies(values, window=4, threshold=2.5)
        self.assertEqual([a['index'] for a in anomalies], [8])

    def test_run_writes_json(self):
        out = ROOT / 'output' / 'anomalies_test.json'
        payload = run(ROOT / 'data' / 'sample_signal.csv', out)
        self.assertTrue(out.exists())
        saved = json.loads(out.read_text(encoding='utf-8'))
        self.assertEqual(saved['count'], payload['count'])


if __name__ == '__main__':
    unittest.main()
'''

README = '''# Generated Reproduction Project

This project was generated from `output/evidence.json` for a teaching demo.

## What it implements

An adaptive window anomaly detector:

```text
score = abs(x_i - mean(previous_window)) / max(std(previous_window), 1e-6)
```

Default parameters:

- window = 4
- threshold = 2.5

## Run tests

```bash
python3 -m unittest discover -s tests
```

## Limitation

Passing tests only proves the generated demo project is syntactically valid and matches the included sample data. It does not prove scientific correctness or full paper reproduction.
'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--evidence', required=True)
    ap.add_argument('--env', required=True)
    ap.add_argument('--output-dir', required=True)
    args = ap.parse_args()
    evidence = json.loads(Path(args.evidence).read_text(encoding='utf-8'))
    if not evidence.get('algorithm_steps'):
        raise SystemExit('missing algorithm evidence')
    out = Path(args.output_dir)
    (out / 'src').mkdir(parents=True, exist_ok=True)
    (out / 'tests').mkdir(parents=True, exist_ok=True)
    (out / 'data').mkdir(parents=True, exist_ok=True)
    (out / 'output').mkdir(parents=True, exist_ok=True)
    (out / 'src' / 'adaptive_window.py').write_text(ADAPTIVE_WINDOW, encoding='utf-8')
    (out / 'tests' / 'test_adaptive_window.py').write_text(TEST_CODE, encoding='utf-8')
    (out / 'README.md').write_text(README, encoding='utf-8')
    shutil.copy2(args.env, out / 'chip_eval_env.py')
    shutil.copy2('data/sample_signal.csv', out / 'data' / 'sample_signal.csv')
    design = {
        'objective': evidence.get('objective'),
        'default_parameters': evidence.get('default_parameters'),
        'generated_files': ['src/adaptive_window.py', 'tests/test_adaptive_window.py', 'chip_eval_env.py', 'data/sample_signal.csv'],
        'human_review_items': evidence.get('human_review_items', [])
    }
    (Path('output') / 'design_brief.md').write_text('# Design Brief\n\n' + json.dumps(design, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Built reproduction project in {out}')

if __name__ == '__main__':
    main()
