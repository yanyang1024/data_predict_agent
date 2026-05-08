# Project rules for the teaching demo kit

These rules are intentionally conservative because the kit is for teaching agentic workflows.

## Global workflow

- Start complex tasks in Plan mode. First read the relevant README, AGENTS.md, rules, configs, inputs, and scripts.
- Do not modify source inputs, specs, protected data, or reference examples unless the user explicitly asks.
- Prefer running the provided scripts over writing one-off code.
- Every execution must produce an output manifest or validation report.
- Clearly separate tool-verified claims from human-validated claims.

## Safe edit areas

- Allowed by default: `output/**`, temporary scratch files, and markdown notes created for teaching.
- Ask first: `scripts/**`, `rules/**`, `configs/**`, `.opencode/**`, `.clinerules/**`.
- Do not edit: `protected/**`, real credentials, real production data, or files that look like secrets.

## Teaching language

When explaining a result, use this pattern:

1. What the agent read.
2. What rule or script it used.
3. What artifact it generated.
4. What was validated by tools.
5. What still requires human review.
