from __future__ import annotations

import csv
import json
import math
from pathlib import Path


def load_signal_csv(path: str | Path) -> list[float]:
    with Path(path).open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return [float(row['value']) for row in reader]


def mean(values: list[float]) -> float:
    if not values:
        raise ValueError('mean requires at least one value')
    return sum(values) / len(values)


def std(values: list[float]) -> float:
    if not values:
        raise ValueError('std requires at least one value')
    m = mean(values)
    return math.sqrt(sum((v - m) ** 2 for v in values) / len(values))


def write_json(path: str | Path, payload: dict) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
