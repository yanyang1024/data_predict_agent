# Conversion Report

- AUTO `a_load_pattern` -> `b.loadPattern("pattern_b_generated.pat")` using B manual: b.loadPattern(path).
- NEEDS REVIEW `a_set_voltage` -> `b.power.setRail("VDD", 1.20)`. Product owner must confirm voltage and limit semantics.
- AUTO `a_set_timing` -> `b.timing.setPeriod("CLK", 5.0)` using B manual: b.timing.setPeriod(clock, period_ns).
- AUTO `a_force_pin` -> `b.pin.force("RESET_N", 0)` using B manual: b.pin.force(pin, value).
- TRANSFORM `a_wait_us` -> `b.wait.ns(10 * 1000)` using B manual: b.wait.ns(value).
- AUTO `a_force_pin` -> `b.pin.force("RESET_N", 1)` using B manual: b.pin.force(pin, value).
- TRANSFORM `a_run_pattern` -> `BRunResult result = b.executePattern("BASIC_READ")` using B manual: b.executePattern(label).
- TRANSFORM `a_log_value` -> `b.datalog.scalar("basic_read_pass", result.passed)` using B manual: b.datalog.scalar(name, value).
- UNSUPPORTED `a_enable_binning`: Binning must be configured in platform B flow setup, not direct API..

## Human Validation Checklist

- Confirm voltage limits and power rail naming.
- Confirm timing set equivalence.
- Confirm binning configuration in platform B flow setup.
- Compile candidate code against platform B SDK.
- Run generated pattern in offline parser before tester execution.
