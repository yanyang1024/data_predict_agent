# Etch Multi-Agent Workflow

## Orchestration Flow

```
User Input
    │
    ▼
Etch Orchestrator — parse task type
    │
    ├── Parallel Dispatch ──────────────────┐
    │   ├── etch-mechanism                  │
    │   │   └── qualitative reasoning       │
    │   ├── etch-literature                 │
    │   │   └── similar-scenario search     │
    │   └── etch-data-optimization          │
    │       └── historical data modeling    │
    │                                       │
    ├── Sequential ─────────────────────────┤
    │   └── etch-constraint                 │
    │       └── check data agent output     │
    │                                       │
    ├── If gap detected ────────────────────┤
    │   └── etch-doe                        │
    │       └── generate validation plan    │
    │                                       │
    ├── Conflict arbitration ───────────────┤
    │   └── etch-integration                │
    │       └── evidence grading A–E        │
    │                                       │
    └── Final delivery ─────────────────────┘
        └── etch-report
            └── Markdown/HTML report
```

## Dispatch Rules — by Task Type

| # | Task Type | Dispatch Pipeline | DOE Trigger |
|---|-----------|-------------------|-------------|
| 1 | `parameter_optimization` | Mechanism + Data (parallel) → Constraint → Integration → Report | If Data shows low R² (<0.7) or Constraint has WARNING |
| 2 | `doe_design` | DOE → Report | Always (this IS a DOE task) |
| 3 | `literature_search` | Literature → Report | Never |
| 4 | `mechanism_analysis` | Mechanism + Literature (parallel) → Integration → Report | If mechanism uncertain |
| 5 | `parameter_explanation` | Mechanism → Report | Never |
| 6 | `integrated_solution` | All 7 agents → Integration → Report | If Integration finds gap |

## API Availability × Dispatch Matrix

| Literature API | Data API | Simulator | Available Agents | Fallback Mode |
|:---:|:---:|:---:|:---|:---|
| ✅ | ✅ | ✅ | All 7 | Full mode |
| ✅ | ✅ | ❌ | All 7 (mechanism=mock) | Mechanism uses placeholder |
| ✅ | ❌ | ✅ | All but data-optimization | Data agent: plan-only |
| ❌ | ✅ | ✅ | All but literature | Literature: query strategy only |
| ❌ | ❌ | ❌ | All 7 (literature+data placeholder, mechanism mock) | Plan-only mode; no fabricated results |
| ❌ | ❌ | ✅ | All but literature, data | As above + mechanism available |

## Placeholder Rules

| Agent | Normal Output | Fallback Output (API unavailable) |
|-------|--------------|-----------------------------------|
| Mechanism | Simulator results | Qualitative hints only; no numbers |
| Literature | Paper citations + links | Query strategy + "API unavailable" note |
| Data | R², model comparison, Top N candidates | Data processing plan + expected schema; no fabricated R² |
| DOE | Design matrix + CSV + HTML report | N/A — always available (local tool) |
| Constraint | PASS/WARNING/FAIL | UNKNOWN when boundary undefined |
| Integration | Evidence-graded ranking | Same (LLM-driven, always available) |
| Report | Markdown/HTML | Same (LLM-driven, always available) |

## Execution Order Rules

| # | Rule |
|---|------|
| 1 | Mechanism, Literature, Data have no dependencies → must run in parallel |
| 2 | Constraint requires Data output → must run AFTER Data |
| 3 | DOE runs only if Integration identifies a data/mechanism gap |
| 4 | Integration requires all preceding agent outputs |
| 5 | Report requires Integration output |
| 6 | If any agent fails/timeouts, the orchestrator continues with remaining agents |
| 7 | Constraint FAIL is terminal for the candidate (Integration cannot override) |
