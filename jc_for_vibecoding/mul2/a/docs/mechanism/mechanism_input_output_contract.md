# Mechanism Agent Input/Output Contract

## Input Contract

```json
{
  "layer_type": "LCH or MCH",
  "rcp": {
    "parameter_name": "value"
  },
  "target_metrics": [
    "Row1 stripe",
    "Row7 stripe",
    "Bias CD",
    "Bottom CD",
    "Max CD",
    "distortion rate"
  ],
  "known_constraints": {},
  "question": "What should be improved?"
}
```

## Output Contract

```json
{
  "success": true,
  "mode": "real_simulator or placeholder",
  "parameter_effects": [
    {
      "parameter": "bias_power",
      "expected_effect": "May affect ion energy and CD/profile",
      "confidence": "LOW/MEDIUM/HIGH",
      "evidence": "mechanism assumption / simulator / user data"
    }
  ],
  "process_window_hypotheses": [],
  "root_cause_hypotheses": [],
  "constraints_for_optimization": [],
  "limitations": []
}
```

## Confidence Levels
- **HIGH**: supported by known mechanism and user-provided data
- **MEDIUM**: mechanism-plausible but not experimentally verified
- **LOW**: hypothesis only

## Mode Values
- `placeholder`: no real simulator connected (current)
- `real_simulator`: actual Etch simulator integrated (future)
