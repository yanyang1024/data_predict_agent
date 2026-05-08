# Platform Beta development guide excerpt

Beta SDK concepts:

- `BetaDataset.from_csv(path)` loads records.
- `BetaReport.write_json(path, payload)` writes structured output.
- `BetaRuntime.validate_schema(records, required_fields)` validates input fields.
- `BetaJob` style keeps configuration in a class and exposes a `run()` method.

Beta style:

- Prefer explicit adapters.
- Validate input schema before processing.
- Emit a manifest for generated artifacts.
