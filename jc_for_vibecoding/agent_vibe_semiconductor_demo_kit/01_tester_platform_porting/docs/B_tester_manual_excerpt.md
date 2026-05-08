# Platform B Tester Manual Excerpt - Synthetic

This excerpt is fictional and used for classroom training.

## Digital Test APIs

| Function | Arguments | Meaning | Notes |
|---|---|---|---|
| `b.loadPattern(path)` | pattern file path | Load a Platform B pattern file. | Pattern syntax uses `PROGRAM`, `TIMING_SET`, and `CYCLE`. |
| `b.power.setRail(rail, volts)` | rail name, voltage | Configure a power rail. | Voltage limits must be validated by product owner. |
| `b.timing.setPeriod(clock, period_ns)` | clock name, period | Configure timing period. | Period is in ns. |
| `b.pin.force(pin, value)` | pin name, 0/1/Z | Force a pin state. | Same semantic as A in this demo. |
| `b.wait.ns(value)` | nanoseconds | Wait a number of nanoseconds. | Platform B wait unit is ns. |
| `b.executePattern(label)` | pattern label | Execute loaded pattern block and return `BRunResult`. | Result fields: passed, failed. |
| `b.datalog.scalar(name, value)` | datalog key, numeric value | Emit a scalar value to datalog. | |

## Pattern Syntax

Platform B pattern files use:

```text
PROGRAM <name>
TIMING_SET <name>
CYCLE <index>: <pin assignments>
ENDPROGRAM
```
