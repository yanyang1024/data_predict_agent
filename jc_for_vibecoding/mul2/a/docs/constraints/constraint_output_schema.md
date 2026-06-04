# Constraint Check Output Schema

```json
{
  "success": true,
  "overall": "PASS | WARNING | FAIL | UNKNOWN",
  "overall_message": "Human-readable summary",
  "details": {
    "parameter_checks": [
      {
        "label": "pressure",
        "status": "PASS | FAIL | UNKNOWN",
        "message": "pressure = 50 is within bounds"
      }
    ],
    "cd_checks": [
      {
        "label": "bias_cd",
        "status": "PASS | FAIL | UNKNOWN",
        "message": "bias_cd = 90 is within CD constraints"
      }
    ],
    "history_checks": [
      {
        "label": "bias_power",
        "status": "PASS | WARNING | UNKNOWN",
        "message": "bias_power = 140 is outside historical range [80, 120]"
      }
    ]
  }
}
```

## Status Definitions

| Status | Meaning | Default Action |
|--------|---------|---------------|
| PASS | No known violation | Proceed |
| WARNING | Possible risk or outside historical range | Flag for review |
| FAIL | Explicit violation | Block recommendation |
| UNKNOWN | Missing boundary or constraint data | Require owner input |
