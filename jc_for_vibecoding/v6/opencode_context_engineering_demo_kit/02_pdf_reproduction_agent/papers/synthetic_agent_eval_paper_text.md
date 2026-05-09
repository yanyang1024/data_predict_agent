# Mini Paper: Adaptive Windowed Anomaly Detector for Signal Streams

## Objective

Reproduce a small signal anomaly detector for educational agent workflows. The detector scans a single numeric signal and flags points whose normalized score exceeds a threshold.

## Environment Requirements

Use the local environment package `env_pkg/chip_eval_env.py`. It provides:

- `load_signal_csv(path)` returning a list of float values.
- `mean(values)` and `std(values)`.
- `write_json(path, payload)`.

Do not import external data science packages.

## Algorithm

For each point at index i, use the previous `window` points as baseline. If fewer than `window` previous points exist, skip the point. Compute:

```text
score = abs(x_i - mean(previous_window)) / max(std(previous_window), 1e-6)
```

Flag an anomaly when `score >= threshold`.

Default parameters:

- `window = 4`
- `threshold = 2.5`

## Experiment Logic

Run the detector on `data/sample_signal.csv`. The expected anomaly index for the included demo data is 8.

## Native Code Instruction

Generate a Python package with:

- `src/adaptive_window.py`
- `tests/test_adaptive_window.py`
- `README.md`

The generated code should use only Python standard library and `env_pkg/chip_eval_env.py` copied into the project.

## Limitations

This paper excerpt is synthetic and only suitable for teaching PDF extraction and reproduction workflows. It does not prove real scientific correctness.
