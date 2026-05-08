# Agent and Vibe Coding Semiconductor Demo Kit

This demo kit contains three synthetic, low-risk practice scenarios for teaching
agentic coding in semiconductor engineering contexts.

Scenarios:

1. `01_tester_platform_porting` - ATE tester program migration from platform A to platform B.
2. `02_jedec_coverage_vector` - JEDEC-like requirement excerpt to coverage, sequence IR, FineSim-style vector, and Verilog vector.
3. `03_lot_history_qtime` - Mock lot history data to UT/QTime analysis and engineering report.

All examples use synthetic materials. They are designed for classroom explanation,
not for production or real tester execution.

Recommended teaching flow:

1. Open the scenario README.
2. Ask the agent to work in Plan mode first and inspect docs/code only.
3. Ask for mapping, risks, and a smallest safe implementation step.
4. Switch to Act mode only for the deterministic scripts in `scripts/`.
5. Review generated artifacts and compare with `expected/` outputs.
6. Discuss stop rules and what must remain human-owned.

Run all examples:

```bash
python3 run_all_demos.py
```
