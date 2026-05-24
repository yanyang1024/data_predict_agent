# Redundancy and Deletion Analysis

## Core deletion rule

Delete only code that is proven irrelevant to the target migration:

```text
safe_to_delete(symbol) =
  symbol not in whitelist
  and symbol not supporting any whitelist item
  and all known users of symbol are also safe_to_delete
  and symbol is not a platform/export/generated/callback/hook symbol
  and ambiguous references have been reviewed
```

## Why simple agent deletion misses symbols

Large C/C++ test repositories commonly produce missed matches because:
- functions are called through macros, tables, registration arrays, callback names, string-dispatched test IDs, or generated aliases;
- classes have constructors/destructors, virtual methods, static members, or inherited helper methods that do not appear in simple call chains;
- globals and structs are used via pointer fields, extern declarations, or header-only helpers;
- flow names in `flow.c` or `efa` differ from implementation symbols;
- product-specific code is selected through preprocessor flags rather than direct calls.

## Multi-pass analysis method

Use at least these passes before deletion:

1. **Text inventory**: grep/ripgrep for test IDs, aliases, function names, class names, datalog labels, and parameter names.
2. **Symbol inventory**: list functions, classes, methods, globals, typedefs, enums, macros, and exported symbols.
3. **Forward reachability**: from each whitelisted test item, collect all symbols it requires.
4. **Reverse reachability**: for each delete candidate, collect all callers/users.
5. **Preprocessor review**: inspect `#if`, `#ifdef`, macro-generated calls, include guards, and build flags.
6. **Registration/table review**: inspect arrays, maps, factory registrations, pattern tables, and string-to-function dispatch.
7. **Compile validation**: build after each small deletion batch.
8. **Residual search**: after deletion, search for orphaned declarations, unused aliases, stale comments, and stale parameter references.

## Conservative symbol classification

| class | delete rule |
| --- | --- |
| test function used only by deleted test item | deletable after reverse-call check |
| helper used only by deleted symbols | deletable in same batch |
| helper shared by keep and delete items | keep; optionally simplify only after review |
| global parameter for deleted test only | deletable or remove from table after parameter review |
| class used only by deleted test item | delete class and related factory/registration after constructor/destructor review |
| base class, virtual method, callback, exported API | never auto-delete; require review |
| macro-generated symbol | never auto-delete from name match alone |
| generated/vendor file | avoid editing unless generation source is updated |

## Batch deletion protocol

For each batch:

```markdown
### deletion batch <id>
- obsolete test item or feature:
- symbols removed:
- files changed:
- reverse-call evidence:
- shared-code risk:
- validation run:
- reviewer:
- outcome:
```

Keep batches small enough that a human can review the diff in one pass.

## Recommended tools when available

Prefer deterministic analysis tools over pure text reasoning:
- compiler database: `compile_commands.json`;
- LSP index: clangd or project IDE index;
- cross-reference tools: ctags, cscope, clang-query, tree-sitter, ripgrep;
- build/CI commands from `AGENTS.md`, README, or pipeline config.

If none are available, stay conservative and mark uncertain deletions as `needs_review`.
