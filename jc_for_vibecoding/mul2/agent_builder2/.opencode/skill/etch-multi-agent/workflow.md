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

## Dispatch Rules

| Condition | Action |
|-----------|--------|
| User asks for parameter optimization | Mechanism + Data → Constraint → Integration → Report |
| User asks for DOE design | DOE → Report |
| User asks for root-cause analysis | Mechanism + Literature → Integration → Report |
| User asks for literature search | Literature only → Report |
| User asks for integrated solution | All 7 agents → Integration → Report |
| API unavailable for an agent | Agent runs in fallback/placeholder mode; mark clearly in output |
| Constraint Agent returns FAIL | Integration must respect FAIL; cannot override |

## Placeholder Rules
- Mechanism Agent: qualitative hints only, no fabricated numbers
- Literature Agent: query strategy + placeholder schema, no fabricated paper titles
- Data Agent: processing plan + expected schema, no fabricated R-squared
- DOE: can run locally with coded factors
- Constraint: UNKNOWN is valid when boundary data is missing
