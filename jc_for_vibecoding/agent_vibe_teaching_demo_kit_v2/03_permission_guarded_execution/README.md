# Demo 3 - Permission-guarded execution

## Teaching focus

This demo teaches permission constraints and safe wrappers:

```text
user request -> approved wrapper script -> parameter contract -> output manifest + audit log
```

The agent must not directly edit important data or protected config. It can only use wrapper scripts that enforce an allowlist, row/date limits, and change-request workflow.

## Run

```bash
python3 scripts/guarded_query.py \
  --asset PILOT_A \
  --start-date 2026-04-01 \
  --end-date 2026-04-07 \
  --fields timestamp,asset,metric,value \
  --output-dir output

python3 scripts/request_config_change.py \
  --config-key threshold.warning \
  --new-value 0.78 \
  --reason "training demo change request only" \
  --output-dir output

python3 scripts/validate_guardrails.py
```

## What to teach

- `opencode.json` prevents or asks for risky tool actions.
- Script-level parameter validation is still required.
- Config changes should become reviewable requests, not direct edits.
- Audit logs and manifests are part of the output contract.
