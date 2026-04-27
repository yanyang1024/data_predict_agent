# Example Request

```text
/profile-data data/sample_measurements.csv measurement_value equipment_id measurement_time
```

Expected behavior:

1. The command expands to a prompt that asks the agent to use `simple-data-quality-analysis`.
2. The agent loads the skill through the `skill` tool.
3. The agent calls `data-profile` with the CSV path and column names.
4. The agent reads compact output artifacts if needed.
5. The agent returns the report template.
