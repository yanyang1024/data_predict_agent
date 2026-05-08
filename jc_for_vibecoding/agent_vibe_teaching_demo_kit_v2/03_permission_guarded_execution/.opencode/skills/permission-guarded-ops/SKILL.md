---
name: permission-guarded-ops
description: Use when a task involves important data, protected configuration, constrained queries, change requests, or other operations where the agent must operate through approved wrapper scripts, parameter allowlists, manifests, audit logs, and permission boundaries instead of direct file/database access.
---

# Permission-guarded operations

## Workflow

1. Read `README.md`, `AGENTS.md`, `configs/approved_query_contract.json`, and `opencode.json`.
2. Do not read or edit `protected/` directly.
3. Validate the user request against allowed assets, fields, date windows, and row limits.
4. For data access, run `scripts/guarded_query.py` only.
5. For config updates, run `scripts/request_config_change.py` only. Never edit the protected config directly.
6. Run `scripts/validate_guardrails.py`.
7. Summarize output manifest, audit trail, and guardrail validation.

## Stop rules

Stop if the user requests a direct database connection, protected config edit, unbounded query, disallowed asset, disallowed field, or date range beyond the contract.

## Reporting rule

Say "change request created" instead of "config updated" unless a human has approved and applied the change outside the agent workflow.
