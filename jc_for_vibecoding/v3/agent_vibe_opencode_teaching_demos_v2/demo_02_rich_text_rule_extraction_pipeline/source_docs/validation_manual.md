# Synthetic Validation Manual

This manual is synthetic and intended only for teaching rich-text rule extraction.

## Native Instruction Pattern Table

| Rule ID | Intent | Native Pattern | Expected Evidence | Review |
|---|---|---|---|---|
| RESET_STABILITY | Verify reset release stability | SET RESET_N=0; WAIT 10ns; SET RESET_N=1; WAIT 20ns; CHECK READY==1 | READY becomes 1 after reset release | Human must confirm reset polarity |
| VOLTAGE_SWEEP | Validate operation across voltage range | FOR VDD IN [0.9, 1.0, 1.1]: SET VDD; RUN BASIC_OP; CHECK PASS==1 | PASS remains 1 | Human must confirm allowed voltage range |
| JITTER_TOLERANCE | Validate clock jitter tolerance | SET CLK_JITTER=50ps; RUN BASIC_OP; CHECK ERROR_COUNT==0 | ERROR_COUNT remains zero | Human must confirm jitter model |

## Environment Adaptation Rules

- Native signal `RESET_N` maps to environment signal `rst_n`.
- Native signal `READY` maps to environment signal `ready`.
- Native signal `VDD` maps to environment parameter `supply_vdd`.
- Native signal `CLK_JITTER` maps to environment parameter `clock_jitter_ps`.
- Native macro `BASIC_OP` maps to environment function `basic_transaction()`.

## Human Review Gate

The pipeline can extract and adapt the patterns, but it cannot prove that the verification intent is complete. The reviewer must confirm polarity, legal voltage range, jitter model, and whether the expected evidence is sufficient.
