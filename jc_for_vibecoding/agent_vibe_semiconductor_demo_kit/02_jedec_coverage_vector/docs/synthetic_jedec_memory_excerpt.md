# Synthetic JEDEC-like Memory Excerpt

This excerpt is fictional and only for classroom training.

## Reset Requirement

The device shall sample `RESET_N=0` for at least two rising clock edges. After
`RESET_N` returns high, the controller shall wait at least `tINIT = 5 ns` before
issuing READ or WRITE commands.

## Read and Write Commands

A WRITE command is encoded as `CS_N=0, WE_N=0, RE_N=1`. A READ command is
encoded as `CS_N=0, WE_N=1, RE_N=0`.

The supported burst lengths are 4 and 8. A WRITE followed by READ to the same
address shall observe `tW2R >= 2 cycles`.

## Voltage and Clock Conditions

Nominal VDD is 1.20 V. Verification shall include low and high VDD corners at
1.08 V and 1.32 V. Clock jitter stress shall include +/-5 percent period
variation in at least one sequence.

## Illegal Command

`WE_N=0` and `RE_N=0` in the same cycle is illegal. The device shall not corrupt
previously stored data after an illegal command.

## Ambiguity for Training

The excerpt does not define read latency in cycles. For this demo, the generated
sequence IR marks read latency as `needs_designer_confirmation`.
