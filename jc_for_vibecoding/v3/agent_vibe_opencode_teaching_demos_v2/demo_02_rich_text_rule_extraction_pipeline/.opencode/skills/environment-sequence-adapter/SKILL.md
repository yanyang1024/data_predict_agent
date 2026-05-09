---
name: environment-sequence-adapter
description: use when extracted validation rules or native instruction patterns must be adapted to a local environment package, signal map, simulator wrapper, test harness, or framework-specific sequence API.
---

# Environment Sequence Adapter

## Workflow

1. Read `output/extracted_rules.json`.
2. Read `env_package/signal_map.json`.
3. Map native names to environment names.
4. Generate `output/sequence_ir.json`.
5. Generate `output/adapted_sequence.py`.

## Approved command

```bash
python3 scripts/adapt_rules_to_env.py \
  --rules output/extracted_rules.json \
  --env env_package/signal_map.json \
  --output output/adapted_sequence.py \
  --ir output/sequence_ir.json
```

## Stop rules

- Stop if a native signal, macro, or expected evidence cannot be mapped.
- Stop if generated code would require modifying the environment package.
