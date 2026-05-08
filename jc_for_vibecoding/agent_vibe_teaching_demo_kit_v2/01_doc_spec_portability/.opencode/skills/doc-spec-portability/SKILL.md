---
name: doc-spec-portability
description: Use for doc/spec-driven development when the user wants to implement the same functional requirement across different platforms using historical documents, platform guides, examples, mapping rules, and traceability reports.
---

# Doc/spec portability

## Workflow

1. Read the platform-neutral spec and identify requirement IDs.
2. Read source and target platform docs.
3. Read historical examples only as behavior/style references.
4. Create a mapping table before generating implementation.
5. Generate target-platform code only into `output/`.
6. Run validation.
7. Report requirement traceability, mapping status, unsupported areas, and human review points.

## Quality bar

- Every generated behavior must map to a requirement ID.
- Platform-specific calls must stay in adapter classes or functions.
- Unsupported or uncertain mappings must be visible in the report.
- Validation proves sample behavior only; it does not prove production readiness.

## Stop rules

Stop if the spec lacks input/output definitions, if a mapping is missing for a platform SDK call, or if the user asks to claim production portability without human review.
