# Iteration Guide

## Why v0 is abstract

This first version intentionally avoids hard-coded parser logic because no concrete code, whitelist format, tester-language examples, product parameter schema, or build system was provided. It gives a safe workflow and traceability contract that can be applied before automation is added.

## What to collect during first real runs

For each migration, save examples of:
- actual `flow.c`, `efa`, pattern, and parameter-table snippets;
- whitelist format and alias rules;
- test item naming patterns and normalized forms;
- examples where the agent missed functions, variables, or classes that should have been deleted;
- examples where a proposed deletion was unsafe;
- target tester-language idioms;
- build, lint, simulation, and hardware validation commands;
- human review comments.

## How to improve this skill

### 1. Add project-specific references

Create or update:
- `references/tester-patterns-<machine>.md` for platform idioms;
- `references/product-parameter-schema.md` for parameter source format;
- `references/whitelist-format.md` for required test item format;
- `references/repo-conventions.md` for build commands and generated-code boundaries.

Then link these files from `SKILL.md`.

### 2. Add deterministic scripts

Add scripts only after the input formats are stable. Candidate scripts:
- whitelist parser and normalizer;
- `flow.c` / `efa` test-item extractor;
- C/C++ symbol indexer using `compile_commands.json`, ctags, cscope, or tree-sitter;
- reverse-call graph generator;
- deletion candidate checker;
- parameter diff generator;
- migration evidence pack generator.

Each script should be runnable from CLI, produce machine-readable output, and be tested on a small fixture.

### 3. Add fixtures

Create `fixtures/` with small anonymized code samples:

```text
fixtures/
  simple_flow/
    flow.c
    efa
    src/
    whitelist.csv
    parameters.csv
    expected_test_item_map.csv
    expected_deletion_candidates.csv
```

Do not include confidential product data unless your internal policy allows it.

### 4. Measure skill quality

Track:
- false deletes: unsafe deletions proposed or applied;
- missed deletes: symbols that should have been removed but were missed;
- ambiguous cases correctly marked `needs_review`;
- parameter update accuracy;
- compile/simulation pass rate;
- review time per batch.

Use these metrics to decide whether to tighten rules or add scripts.

## Recommended v1 roadmap

1. Encode actual whitelist schema and aliases.
2. Add tester-platform pattern references for the top 1-2 machines.
3. Add a symbol/reachability helper based on tools already available in the repo.
4. Add fixtures from one successful migration.
5. Update `SKILL.md` to require the script where it is more reliable than reasoning.
