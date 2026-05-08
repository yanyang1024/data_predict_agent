---
name: jedec-coverage-vector
description: Use for IC design or verification tasks where the user provides a JEDEC-like specification excerpt and environment library and asks to generate coverage points, verification sequences, FineSim-style vectors, Verilog vectors, or generation reports with explicit ambiguity and human-review lists.
---

# JEDEC Coverage and Vector Generation

## Workflow

1. Read the specification excerpt and environment library.
2. Extract feature requirements, timing rules, voltage corners, reset behavior, and illegal conditions.
3. Generate coverage points before generating sequences.
4. Generate a neutral sequence IR before emitting simulator-specific vector formats.
5. Generate FineSim-style and Verilog-style outputs from the same IR.
6. Validate signal names, vector columns, and expected sequence count.
7. Report ambiguities and human-review items.

## Stop Rules

Stop and ask for review when:

- A clause is ambiguous or conflicts with the environment library.
- A signal name is missing from the environment library.
- The user asks for final signoff or standard compliance certification.
- Timing, voltage, or illegal-command semantics are underspecified.
