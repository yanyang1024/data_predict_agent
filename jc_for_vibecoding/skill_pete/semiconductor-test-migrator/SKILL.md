---
name: semiconductor-test-migrator
description: migrate and refactor semiconductor pete product engineering and test engineering c/c++ finished-test code by product and by tester platform. use when extracting mandatory test items, pruning non-whitelisted redundant code, adapting tester-language patterns, regenerating product parameters, preserving before/after versions, producing trace logs, and flagging human review points for production test migration.
---

# Semiconductor Test Migrator

## Purpose

Guide safe migration of semiconductor PETE finished-test code written mainly in C/C++ across product variants and tester platforms. Treat the work as a controlled engineering change, not a generic refactor: preserve required test coverage, delete only provably redundant code, update product parameters, and leave auditable before/after evidence for human review.

## Required context model

Before changing code, build a compact migration contract with these context groups:

1. **software engineering context**: repository layout, build system, compile flags, macros, generated-code boundaries, C/C++ entry points, symbol ownership, call graph, reverse call graph, tests, formatter, and version-control policy.
2. **semiconductor test context**: product family, DUT/revision, mandatory test items, limit tables, units, bins, sites, pins, pattern names, handler/prober assumptions, calibration dependencies, datalog requirements, and product parameter source.
3. **tester-platform context**: machine type, tester-language idioms, API wrappers, flow-control files, pattern files, platform-specific setup/teardown, timing/resource constraints, and known naming conventions.
4. **governance context**: whitelist source, deletion policy, trace-log format, human approval checkpoints, rollback method, and evidence required before release.

Use `references/domain-context.md` for terminology and example schemas. Use `references/redundancy-analysis.md` when deciding whether symbols, variables, classes, or helper modules can be deleted.

## Workflow overview

Follow this sequence unless the user explicitly scopes a smaller task.

### 1. Establish a migration case

Create or request a case folder before edits. Prefer a clean git branch plus a case artifact folder such as `migration_runs/<product>_<tester>_<date>/`.

Capture at minimum:
- source product and target product, source tester and target tester;
- entry files such as `flow.c`, `efa`, pattern folders, parameter tables, and shared libraries;
- required test-item whitelist and any explicit deletion blacklist;
- parameter source of truth for the target product;
- initial file manifest or commit hash.

If code execution is available, use `scripts/create_migration_case.py` to create the case skeleton and before manifest.

### 2. Extract and lock mandatory test items

Identify the smallest set of test units that must remain. Treat the whitelist as a coverage contract, not just a string list.

Build a test-item map with columns similar to:

| field | meaning |
| --- | --- |
| test_item_id | stable test identifier used in flow, datalog, or spec |
| source_location | file/function/macro/pattern where it appears |
| owning_function | top-level function or class method implementing it |
| support_symbols | helpers, variables, structs, classes, and APIs needed by the item |
| product_parameters | limits, pins, bins, voltage/current/timing parameters |
| tester_pattern | target tester-language or pattern idiom |
| status | keep, delete_candidate, parameter_update, needs_review |

For `flow.c`, `efa`, or tester-flow files, collect both exact text matches and normalized variants: case changes, prefixes/suffixes, macro-wrapped names, table-driven declarations, and generated names.

### 3. Build symbol ownership and reachability

Do not delete by filename or simple grep alone. Construct a conservative reachability model:

- Forward graph: entry point or test item -> functions/methods -> helpers -> globals/types/classes/macros.
- Reverse graph: symbol -> all callers/users.
- Ownership classification: whitelist-owned, delete-item-owned, shared, platform-owned, generated, unknown.

Only mark a symbol as safe to remove when all of these are true:
1. it is not part of a whitelisted test item;
2. it is not required by support code for a whitelisted item;
3. every known caller/user is also in the deletion set;
4. it is not a platform hook, exported API, generated-code anchor, interrupt/callback entry, or tester framework convention;
5. ambiguous macro/template/dynamic references have been manually reviewed.

### 4. Delete redundant code in guarded batches

Use small batches. For each batch, record:
- reason for deletion;
- source test item or obsolete product feature;
- symbols removed;
- reverse-call evidence;
- files changed;
- reviewer checkpoint.

After each batch, run compile/lint/static checks available in the repo. If build commands are unknown, ask OpenCode or the user to inspect `AGENTS.md`, README, CI config, or build scripts before continuing.

### 5. Refactor to tester-language patterns

After redundancy pruning, adapt surviving code to target tester-platform idioms. Preserve test semantics first; then normalize style.

Create a mapping table:

| source pattern | target tester idiom | affected files | behavior preserved | review need |
| --- | --- | --- | --- | --- |
| legacy setup/measure/bin | target api or wrapper | file/function | limits, units, bins, sites | yes/no |

Do not inline or hard-code platform behavior when a tester wrapper or project convention exists. If the target machine language pattern is not documented, add a `needs_review` marker instead of guessing.

### 6. Regenerate or update product parameters

Separate code migration from product parameter migration. Prefer table/config updates over code edits.

For every parameter change, record:
- product/revision;
- parameter name and old/new value;
- unit and precision;
- source of truth;
- affected test item;
- bin/limit impact;
- whether engineering approval is required.

Never silently convert units or limits. Flag unit mismatches, missing limits, defaulted values, and changed bin behavior.

### 7. Produce traceable before/after evidence

Every deletion or semantic modification must be traceable. Produce or update:
- `change_log.md` with before/after summary and rationale;
- `review_checklist.md` with human gates;
- `before_manifest.csv/json` and `after_manifest.csv/json` or equivalent git commits;
- grouped diffs by test item, platform refactor, and parameter update;
- a release readiness summary.

Use `references/traceability.md` for the required log sections.

## Human review gates

Stop and explicitly ask for human review before proceeding when any of these occur:

- deleting a symbol used outside the target delete set;
- deleting a class, virtual method, callback, exported function, global object, or macro that may be referenced indirectly;
- changing limits, units, binning, datalog names, site behavior, pattern selection, or setup/teardown order;
- encountering generated code, tester vendor APIs, hardware calibration flows, handler/prober sequencing, or platform hooks;
- compile checks fail after a deletion batch;
- the whitelist, product parameter source, or tester mapping is incomplete.

## Output format for a migration plan

When asked to plan or execute a migration, respond with this structure:

1. **migration contract**: product, tester, scope, entry files, whitelist, parameter source, assumptions.
2. **context inventory**: code graph, test-item map, tester pattern map, product parameter map.
3. **proposed workflow**: phases, batch boundaries, validation commands, review gates.
4. **deletion candidates**: grouped by test item/symbol with keep/delete/needs-review status.
5. **parameter updates**: old/new values, source, affected test items, risk.
6. **trace artifacts**: files/commits/logs that will preserve before/after evidence.
7. **open questions**: only questions blocking safe execution.

## OpenCode usage

For OpenCode-specific placement, permissions, and prompts, consult `references/opencode-usage.md`. In OpenCode, prefer Plan mode for context discovery and deletion planning, then Build mode for small approved batches.

## Iteration

This v0 skill is intentionally methodology-heavy because concrete product code, tester language examples, and parameter schemas are not yet available. After the first 2-3 real migrations, update the reference files with actual patterns, false-positive/false-negative examples, and deterministic scripts. See `references/iteration-guide.md`.
