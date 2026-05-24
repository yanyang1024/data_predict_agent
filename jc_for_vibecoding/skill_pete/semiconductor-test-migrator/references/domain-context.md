# Domain Context for Semiconductor PETE Test Code Migration

## Scope

This skill targets PETE product engineering and test engineering workflows for finished-test code migration. It assumes C/C++ source dominates, with tester-flow files such as `flow.c`, `efa`, vendor pattern files, parameter tables, and platform wrapper libraries.

## Required domain inputs

### Product context

Capture:
- product family, product code, silicon revision, package, site count, and target test insertion;
- required test-item whitelist;
- product parameter source of truth: spec table, CSV, YAML, Excel export, database dump, or legacy header file;
- units, limits, bins, datalog names, and test ordering constraints;
- product-specific exceptions, waived tests, and engineering approval owners.

### Tester or machine context

Capture:
- tester platform name and version;
- tester-language naming patterns for flow entries, pattern calls, setup, measurement, datalog, binning, and cleanup;
- machine resource model: pins, channels, power supplies, timing sets, relay/resource locks, multisite behavior;
- project wrappers around vendor APIs;
- generated files or vendor-owned files that must not be hand-edited.

### Code context

Capture:
- canonical entry files: for example `flow.c`, `efa`, pattern folders, top-level product folders, and common libraries;
- build commands and compile flags;
- `compile_commands.json`, ctags/cscope database, or IDE/LSP index if available;
- generated-code markers;
- project conventions in `AGENTS.md`, README, CI files, or coding standards.

## Test item extraction model

A test item is not just a line in a flow file. Model it as:

```yaml
test_item:
  id: ""
  aliases: []
  source_files: []
  entry_symbols: []
  support_symbols: []
  patterns: []
  parameters: []
  bins: []
  datalog_names: []
  status: keep | delete_candidate | parameter_update | needs_review
```

## Whitelist policy

The whitelist defines what must be preserved. A code element may be deleted only if it is both:

1. not on the whitelist; and
2. not needed by any whitelisted item.

A helper, variable, class, type, or macro is considered needed when it is reachable from a whitelisted test item, participates in shared setup/cleanup, affects limits or bins, or is part of tester framework behavior.

## Default file hints

Treat the following as likely high-value entry points when present:
- `flow.c`: flow ordering, test invocation, conditionals, binning, and product/test selection logic.
- `efa`: platform- or flow-related file that may encode tester-specific execution or pattern metadata.
- parameter headers/tables: product-specific limits and setup values.
- pattern directories: tester-language or vendor pattern calls.

Do not assume these are the only entry points. Inspect build files and project rules.
