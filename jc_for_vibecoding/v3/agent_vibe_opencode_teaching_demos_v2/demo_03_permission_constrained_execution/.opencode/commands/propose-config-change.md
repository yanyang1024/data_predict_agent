---
description: Create a proposal for a protected config change without editing the protected config
agent: build
---

Use the `permission-constrained-analysis` skill.

Request:

$ARGUMENTS

Do not edit `protected_data/production_config.yaml`. Use `scripts/propose_config_change.py` to create a proposal in `output/`.
