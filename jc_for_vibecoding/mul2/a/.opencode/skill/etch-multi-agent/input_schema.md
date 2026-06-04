# Etch Multi-Agent Input Schema

## Top-Level Structure

```json
{
  "layer_type": "LCH | MCH",
  "current_rcp": {
    "pressure": 50,
    "source_power": 800,
    "bias_power": 120,
    "gas_flow": 100,
    "temperature": 60
  },
  "objectives": {
    "minimize": ["Row1_stripe", "Row7_stripe"],
    "maximize": ["Row7_distortion_rate", "distortion_ratio"],
    "target": {}
  },
  "constraints": {
    "Bias_CD": { "min": null, "max": null },
    "Bottom_CD": { "min": null, "max": null },
    "Max_CD": { "min": null, "max": null }
  },
  "historical_data_path": null,
  "doe_budget": { "max_runs": null, "allow_randomize": true },
  "apis_enabled": {
    "literature": false,
    "data_optimization": false,
    "simulator": false
  }
}
```

## Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `layer_type` | string | yes | Etch layer type: LCH or MCH |
| `current_rcp` | object | yes | Current RCP parameter key-value pairs |
| `objectives` | object | yes | Optimization direction lists |
| `constraints` | object | no | CD constraints with min/max |
| `historical_data_path` | string | no | Path to historical data file |
| `doe_budget` | object | no | DOE max runs and randomization preference |
| `apis_enabled` | object | yes | Which external APIs are available |

## Task Type Detection

The orchestrator classifies tasks into one of:
- `parameter_explanation` — explain how parameters affect metrics
- `parameter_optimization` — recommend optimal parameter set
- `doe_design` — design experiment
- `literature_search` — find related methods
- `mechanism_analysis` — analyze process window and root cause
- `integrated_solution` — full multi-agent workflow
