# Portable Protocol Verification Guide v0.3

This synthetic guide contains rich-text sections that describe verification patterns and native instructions. It is not a real standard.

---PATTERN---
PATTERN_ID: RESET_STABILITY
OBJECTIVE: Verify that reset deassertion leads to ready within the allowed window.
NATIVE: DRIVE RESET LOW 5ns; DRIVE RESET HIGH; EXPECT READY WITHIN 20 CYCLES
EXPECTED: ready == 1 within 20 cycles after reset release
HUMAN_REVIEW: Confirm reset deassertion timing with the design owner.
---END---

---PATTERN---
PATTERN_ID: BURST_WRITE_ACK
OBJECTIVE: Verify that four consecutive writes receive acknowledgements.
NATIVE: LOOP 4 WRITE ADDR++ DATA++; EXPECT ACK EACH WRITE
EXPECTED: ack == 1 for every write operation
HUMAN_REVIEW: Confirm whether address wraparound is legal.
---END---

---PATTERN---
PATTERN_ID: CLOCK_JITTER_TOLERANCE
OBJECTIVE: Verify that the block remains stable when clock jitter is applied within environment limits.
NATIVE: SET CLOCK_JITTER MAX_ALLOWED; RUN 100 CYCLES; EXPECT READY STABLE
EXPECTED: ready remains stable during jitter run
HUMAN_REVIEW: Confirm jitter distribution and measurement method.
---END---

## Do not infer

- Do not infer voltage levels.
- Do not infer coverage completeness.
- Do not infer signoff readiness.
