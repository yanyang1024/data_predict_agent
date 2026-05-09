# Permission Policy Design Notes

Use multiple layers:

1. `opencode.json` to make risky operations ask/deny.
2. `AGENTS.md` to state project rules.
3. Approved CLI scripts to validate parameters.
4. Manifests to record what happened.
5. Proposal files instead of direct protected config edits.
