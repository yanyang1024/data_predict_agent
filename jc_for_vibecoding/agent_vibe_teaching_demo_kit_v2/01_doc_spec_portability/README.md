# Demo 1 - Doc/spec portability

## Teaching focus

This demo teaches doc/spec-driven development standards:

```text
platform-neutral spec + historical platform docs + examples -> mapping -> portable implementation -> traceability report
```

The domain is deliberately generic. It simulates moving the same feature from Platform Alpha to Platform Beta.

## Run

```bash
python3 scripts/build_portable_impl.py
python3 scripts/validate_portable_impl.py
```

## What to teach

- Start from a platform-neutral functional contract.
- Use historical docs and examples to learn platform-specific style.
- Do not generate code without a mapping table.
- Generate traceability from requirement IDs to implementation functions.
- Treat unsupported or uncertain mappings as first-class outputs, not failures to hide.
