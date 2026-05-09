# Generated Reproduction Project

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
