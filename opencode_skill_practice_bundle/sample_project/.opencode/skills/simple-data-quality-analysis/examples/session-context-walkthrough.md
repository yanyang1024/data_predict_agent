# Session Context Walkthrough

This example shows how the opencode session context changes when a user runs a command that triggers a skill.

## Before the user message

The model sees project rules from `AGENTS.md`, enabled tools, and the `skill` tool description. The skill tool description includes available skill names and descriptions, not the full `SKILL.md` bodies.

```xml
<available_skills>
  <skill>
    <name>simple-data-quality-analysis</name>
    <description>Profile a local CSV dataset...</description>
  </skill>
</available_skills>
```

## User runs a command

```text
/profile-data data/sample_measurements.csv measurement_value equipment_id measurement_time
```

The command expands into a prompt:

```text
Use the `simple-data-quality-analysis` skill.
Analyze this local dataset request: ...
Rules: use the approved data-profile custom tool...
```

## Agent loads the skill

The agent calls:

```json
{"name": "simple-data-quality-analysis"}
```

After the tool returns, the session context gains the full `SKILL.md` instructions. The agent now knows the workflow, tool policy, output policy, and stop rules.

## Agent runs the tool

The agent calls `data-profile`. The result should be compact JSON pointing to artifacts, not the full raw dataset.

## Agent reads only compact outputs

If more detail is needed, the agent reads `summary.json` or `group_summary.csv`. It should avoid loading the entire raw CSV into context.

## Final answer

The final response follows `references/report-template.md` and cites artifacts from the manifest.
