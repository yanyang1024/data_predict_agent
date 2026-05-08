# Demo 3 rules

- Do not read or edit `protected/` directly.
- Do not use ad hoc SQL or direct data access.
- Use only `scripts/guarded_query.py` for data output.
- Use only `scripts/request_config_change.py` for config changes.
- Every run must create a manifest and audit entry.
- If the requested asset, field, or date range is outside the contract, stop.
