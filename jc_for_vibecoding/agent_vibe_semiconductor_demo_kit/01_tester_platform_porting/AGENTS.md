# Tester Porting Rules

- Use Plan mode before editing code.
- Do not modify files under `src/A_program/`.
- Candidate B outputs must go under `output/B_program_candidate/`.
- Every converted API call must be traceable to `configs/platform_mapping.json`.
- Unknown mappings must be written to `output/unsupported_functions.csv`.
- Do not call generated B code production-ready.
