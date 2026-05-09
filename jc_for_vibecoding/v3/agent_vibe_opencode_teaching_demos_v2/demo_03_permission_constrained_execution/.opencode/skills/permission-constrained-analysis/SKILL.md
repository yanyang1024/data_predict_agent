---
name: permission-constrained-analysis
description: use when demonstrating or implementing safe agent execution where sensitive data, protected configuration, production resources, or high-risk actions must be blocked and the agent must operate only through approved scripts, parameter whitelists, manifests, and proposal files.
---

# Permission-Constrained Analysis

## Purpose

Constrain the agent's execution space. The agent should not directly inspect protected data or edit protected configuration. It should call approved scripts with validated parameters and produce manifest-backed outputs.

## Allowed workflows

### Safe query

```bash
python3 scripts/approved_query.py \
  --dataset training_metrics \
  --window-days 14 \
  --fields date,step,value,owner \
  --output output/query_result.csv \
  --manifest output/query_manifest.json

python3 scripts/render_safe_report.py \
  --input output/query_result.csv \
  --manifest output/query_manifest.json \
  --output output/safe_report.md
```

### Config change proposal

```bash
python3 scripts/propose_config_change.py \
  --parameter row_limit \
  --value 200 \
  --reason "teaching demo wants a larger sample" \
  --output output/config_change_proposal.json
```

## Forbidden actions

- Do not read `protected_data/customer_sensitive_metrics.csv`.
- Do not edit `protected_data/production_config.yaml`.
- Do not bypass `scripts/approved_query.py`.
- Do not increase query window or fields beyond `configs/policy.json`.
- Do not present a proposal as an applied change.

## Validation

Run:

```bash
python3 tests/test_permission_boundary.py
```

## Required explanation

Every response should explain:

- which approved script was used;
- which fields and window were allowed;
- where the manifest is;
- whether protected files were touched;
- what still requires owner approval.
