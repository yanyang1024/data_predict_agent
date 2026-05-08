# Platform A Tester Manual Excerpt - Synthetic

This excerpt is fictional and used for classroom training.

## Digital Test APIs

| Function | Arguments | Meaning | Notes |
|---|---|---|---|
| `a_load_pattern(path)` | pattern file path | Load a Platform A pattern file into the active pattern memory. | Pattern syntax uses `PATTERN`, `TIMESET`, and `VECTOR`. |
| `a_set_voltage(rail, volts)` | rail name, voltage | Configure a named power rail. | Allowed range in this demo: 0.9 V to 1.4 V. |
| `a_set_timing(clock, period_ns)` | clock name, period | Configure a named timing set. | Period is in ns. |
| `a_force_pin(pin, value)` | pin name, 0/1/Z | Force a static pin state. | Used for reset and mode pins. |
| `a_wait_us(value)` | microseconds | Wait a number of microseconds. | Platform A wait unit is us. |
| `a_run_pattern(label)` | pattern label | Execute a loaded pattern block and return `AResult`. | Result fields: pass_count, fail_count. |
| `a_log_value(name, value)` | datalog key, numeric value | Emit a scalar value to datalog. | |
| `a_enable_binning(mode)` | string | Configure binning mode. | No direct B mapping in this demo. |

## Pattern Syntax

Platform A pattern files use:

```text
PATTERN <name>
TIMESET <name>
VECTOR <index>: <pin assignments>
ENDPATTERN
```
