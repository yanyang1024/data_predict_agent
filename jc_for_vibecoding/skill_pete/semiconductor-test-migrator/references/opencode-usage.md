# OpenCode Usage Guide

## Skill placement

For OpenCode, place the skill directory in one of these forms depending on whether it is project-local or global:

```text
.opencode/skills/semiconductor-test-migrator/SKILL.md
~/.config/opencode/skills/semiconductor-test-migrator/SKILL.md
.claude/skills/semiconductor-test-migrator/SKILL.md
~/.claude/skills/semiconductor-test-migrator/SKILL.md
.agents/skills/semiconductor-test-migrator/SKILL.md
~/.agents/skills/semiconductor-test-migrator/SKILL.md
```

Keep `references/`, `scripts/`, and `assets/` beside `SKILL.md` in the same directory.

## Recommended OpenCode setup

1. Commit a project `AGENTS.md` with build commands, repo layout, generated-code boundaries, and tester-specific conventions.
2. Put this skill under `.opencode/skills/semiconductor-test-migrator/` for team-shared use.
3. Start in Plan mode for inventory, whitelist mapping, and deletion-batch planning.
4. Switch to Build mode only for small approved edits.
5. Commit each safe batch separately or record it in `migration_runs/<case>/change_log.md`.

## Permission example

Use `ask` for first adoption so the user explicitly approves skill loading:

```json
{
  "permission": {
    "skill": {
      "semiconductor-test-migrator": "ask"
    }
  }
}
```

After the team trusts the workflow, change to `allow` at project level if desired.

## Suggested AGENTS.md additions

Add project-specific facts that should apply to every OpenCode session:

```markdown
# Semiconductor Test Repository Rules

## Build and validation
- Build command:
- Unit/static check command:
- Offline tester simulation command:

## PETE migration conventions
- Do not delete any test item present in the product whitelist.
- Treat `flow.c`, `efa`, pattern files, parameter tables, and generated tester files as migration-critical.
- Generated/vendor files must not be hand-edited unless the generator source is updated.
- Preserve before/after evidence for each deletion or semantic change.

## Review gates
- Human review is required before deleting shared helpers, classes, callbacks, exported APIs, macros, or changing limits/bins/units.
```

## Prompt examples

### Plan-only inventory

```text
Use the semiconductor-test-migrator skill. In Plan mode, inspect this repo and create a migration contract for product <source> to <target> on tester <machine>. Focus on flow.c, efa, parameter tables, and the whitelist at <path>. Do not edit files yet.
```

### Deletion candidate analysis

```text
Use the semiconductor-test-migrator skill. Build a test-item map and deletion candidate list. For every function, variable, and class you propose deleting, include reverse-call evidence and mark uncertain cases as needs_review.
```

### Approved small batch

```text
Use the semiconductor-test-migrator skill. Apply only deletion batch 001 from migration_runs/<case>/deletion_batches/batch_001.md. Preserve before/after evidence, update the change log, and stop after validation.
```

### Parameter update

```text
Use the semiconductor-test-migrator skill. Update target-product parameters from <parameter-source>. Do not change limits, units, bins, or datalog names without logging old/new values and marking review-required items.
```

## Operating principle

OpenCode can be very effective at repository-wide editing, but this migration should remain gated: first plan, then small batch, then validate, then review.
