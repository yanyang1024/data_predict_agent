from __future__ import annotations

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
