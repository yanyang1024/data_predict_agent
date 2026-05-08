# Adaptation plan

## Human checkpoints

1. Review extracted patterns before adaptation.
2. Review this plan before code generation.
3. Review generated flow logic even if syntax validation passes.

## Sequence plan

### RESET_STABILITY
- Objective: Verify that reset deassertion leads to ready within the allowed window.
- Expected: ready == 1 within 20 cycles after reset release
- Human review: Confirm reset deassertion timing with the design owner.
- Step count: 3

### BURST_WRITE_ACK
- Objective: Verify that four consecutive writes receive acknowledgements.
- Expected: ack == 1 for every write operation
- Human review: Confirm whether address wraparound is legal.
- Step count: 1

### CLOCK_JITTER_TOLERANCE
- Objective: Verify that the block remains stable when clock jitter is applied within environment limits.
- Expected: ready remains stable during jitter run
- Human review: Confirm jitter distribution and measurement method.
- Step count: 3
