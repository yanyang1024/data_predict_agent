# Scenario 1: Tester Platform Porting Demo

Business context:

A product was originally developed on tester platform A. Later, manufacturing
capacity and new platform adoption require the test program to be migrated to
platform B. The source materials include:

- Platform A test program in C++ and a simple pattern language.
- Platform A manual excerpt.
- Platform B manual excerpt.
- A known-good B reference program for style calibration.

Teaching goal:

Show that an agent should not blindly translate code. It should first build an
A-to-B mapping, identify unsupported functions, migrate one small block, and
produce a conversion report and validation checklist.

Run:

```bash
python3 scripts/convert_tester_program.py
python3 scripts/validate_conversion.py
```

Suggested Plan-mode prompt:

```text
Do not modify files. Read docs/A_tester_manual_excerpt.md,
docs/B_tester_manual_excerpt.md, src/A_program/main.cpp, and
examples/B_reference_program/main.cpp.

Return:
1. A-to-B API mapping.
2. Pattern language differences.
3. Automatically portable functions.
4. Functions that need human review.
5. The smallest first migration step.
```

Suggested Act-mode prompt:

```text
Use the existing script to migrate only the basic_function_check block.
Generate output/B_program_candidate/main.cpp, output/pattern_b_generated.pat,
output/conversion_report.md, and output/unsupported_functions.csv.
Then run scripts/validate_conversion.py.
```
