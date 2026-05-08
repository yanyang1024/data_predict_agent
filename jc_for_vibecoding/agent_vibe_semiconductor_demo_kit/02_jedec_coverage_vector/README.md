# Scenario 2: JEDEC-like Coverage, Sequence, and Vector Demo

Business context:

Verification engineers want to feed a memory-like standard excerpt and an
environment library to an agent, then generate:

- Coverage points.
- Sequence IR.
- SystemVerilog sequence skeleton.
- FineSim-style vector.
- Verilog vector/testbench skeleton.

This scenario uses a synthetic JEDEC-like excerpt. It is not an actual JEDEC
standard and should not be used for real compliance work.

Run:

```bash
python3 scripts/generate_verification_artifacts.py
python3 scripts/validate_vector.py
```

Suggested Plan-mode prompt:

```text
Do not modify files. Read docs/synthetic_jedec_memory_excerpt.md,
env_lib/memory_env.json, and templates/coverage_template.sv.
Return a coverage plan, sequence ideas, vector format assumptions, and
all clauses that require designer confirmation.
```

Suggested Act-mode prompt:

```text
Use scripts/generate_verification_artifacts.py to generate coverage points,
sequence IR, SystemVerilog skeleton, FineSim-style vector, Verilog vector,
and a generation report. Then run scripts/validate_vector.py.
```
