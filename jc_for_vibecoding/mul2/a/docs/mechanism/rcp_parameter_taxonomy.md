# RCP Parameter Taxonomy

## Parameter Groups

| Group | Parameters | Typical Impact |
|-------|------------|----------------|
| Gas | gas_type, gas_flow_ratio, total_flow | Etch rate, selectivity, uniformity |
| Power | source_power, bias_power, power_pulsing | Ion energy, plasma density, CD/profile |
| Pressure | chamber_pressure | Mean free path, ion directionality, loading |
| Temperature | electrode_temp, wall_temp, chuck_temp | Polymer deposition, byproduct volatility |
| Timing | etch_time, over_etch_time, step_sequence | Profile control, CD bias |
| Pulsing | bias_pulse_freq, bias_pulse_duty, source_pulse | Aspect ratio, charge damage |

## Parameter Naming Convention

Parameters are passed as key-value pairs using standardized names:
- Use snake_case: `bias_power`, `source_power`, `gas_flow`
- Unit suffixes in description only, not in key names
- Boolean/categorical parameters use string values

## RCP Structure Example

```yaml
recipes:
  - name: "MCH_std_v3"
    layer_type: MCH
    parameters:
      pressure: 50
      source_power: 800
      bias_power: 120
      gas_flow: 100
      temperature: 60
      etch_time: 45
```
