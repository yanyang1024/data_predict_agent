from __future__ import annotations

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
