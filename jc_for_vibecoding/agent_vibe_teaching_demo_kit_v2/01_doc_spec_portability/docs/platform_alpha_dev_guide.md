# Platform Alpha development guide excerpt

Alpha SDK concepts:

- `AlphaTable.read_csv(path)` returns a list of dictionaries.
- `AlphaReport.write_json(path, payload)` serializes a report object.
- `AlphaLogger.info(message)` logs informational messages.

Alpha style:

- Script-like jobs are common.
- Function names often start with `alpha_`.
- Error handling is minimal in old examples and should not be copied blindly.
