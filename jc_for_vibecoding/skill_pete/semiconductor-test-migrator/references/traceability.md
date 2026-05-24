# Traceability Requirements

## Required artifacts

A migration case should produce these artifacts:

```text
migration_runs/<case>/
  case_metadata.json
  before_manifest.csv
  before_manifest.json
  after_manifest.csv
  after_manifest.json
  diff_summary.md
  change_log.md
  review_checklist.md
  test_item_map.csv
  parameter_update_map.csv
  deletion_batches/
    batch_001.md
    batch_002.md
```

A git branch with commits may replace snapshots, but still keep the case metadata and review logs.

## Change log template

Each major change should include:

```markdown
## <change id>: <short title>

- category: deletion | tester-refactor | parameter-update | validation | review
- affected product:
- affected tester platform:
- affected test items:
- files changed:
- before reference: commit/file/line/hash
- after reference: commit/file/line/hash
- reason:
- evidence:
- risk:
- human review required: yes/no
- reviewer decision:
```

## Human review checkpoints

Mark checkpoints as blocking when they affect coverage, product limits, bins, hardware resources, or platform flow behavior.

Suggested checkpoints:
1. whitelist accepted;
2. deletion candidate list accepted;
3. batch deletion diff reviewed;
4. product parameter updates reviewed;
5. tester-language mapping reviewed;
6. compile/static checks passed;
7. final coverage and datalog naming reviewed.

## Before/after evidence

For every deletion or modification:
- preserve the previous state by git commit, file hash, or snapshot;
- preserve the new state by git commit or after manifest;
- record why the change is safe;
- record the exact test item or product parameter that motivated the change.

## Release readiness summary

Use this final section:

```markdown
# Release Readiness Summary

## Scope
- source product/tester:
- target product/tester:
- migration branch or commit range:

## Coverage
- whitelist items preserved:
- deleted obsolete items:
- items requiring waiver/review:

## Parameters
- parameter source:
- changed limits/bins/units:
- unresolved mismatches:

## Validation
- build commands run:
- static checks:
- simulation/offline checks:
- hardware/prober/handler checks:

## Human approvals
- reviewer:
- open risks:
- go/no-go:
```
