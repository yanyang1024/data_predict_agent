# Etch Multi-Agent Skill

## Purpose
This skill coordinates multiple Etch subagents to support semiconductor Etch process analysis, RCP recommendation, mechanism reasoning, literature-based reference, historical data optimization, DOE planning, constraint checking, and final report generation.

## When to Use
Use this skill when the user asks for:
- Etch recipe optimization,
- RCP parameter recommendation,
- Etch abnormality root-cause analysis,
- DOE experiment planning,
- literature-based Etch methodology,
- historical data mining,
- multi-agent Etch workflow generation.

## Input Schema
See `input_schema.md` for the full structure. Key fields:
- `layer_type` (LCH/MCH), `current_rcp` (key-value object)
- `objectives` (minimize/maximize lists)
- `constraints` (CD bounds: Bias_CD, Bottom_CD, Max_CD)
- `historical_data_path`, `doe_budget.max_runs`
- `apis_enabled` (literature, data_optimization, simulator booleans)

## Dispatch Decision Tree

```
User Input
    │
    ▼
Parse task type (6 types: parameter_optimization / doe_design /
literature_search / mechanism_analysis / parameter_explanation /
integrated_solution)
    │
    ├── parameter_optimization ──────────────────┐
    │   ├── Parallel: Mechanism + Data            │
    │   ├── Sequential: Constraint (on Data out)  │
    │   ├── If gap: DOE                           │
    │   └── Integration → Report                  │
    │                                             │
    ├── doe_design ───────────────────────────────┤
    │   └── DOE → Report                          │
    │                                             │
    ├── literature_search ────────────────────────┤
    │   └── Literature → Report                   │
    │                                             │
    ├── mechanism_analysis ───────────────────────┤
    │   ├── Parallel: Mechanism + Literature      │
    │   └── Integration → Report                  │
    │                                             │
    ├── parameter_explanation ────────────────────┤
    │   └── Mechanism → Report                    │
    │                                             │
    └── integrated_solution ──────────────────────┤
        ├── Parallel: Mechanism + Literature + Data
        ├── Sequential: Constraint
        ├── If gap: DOE
        └── Integration → Report
```

## Agent Dependencies

| Agent | Depends On | Blocking? |
|-------|-----------|-----------|
| etch-mechanism | nothing | No |
| etch-literature | nothing | No |
| etch-data-optimization | nothing | No |
| etch-constraint | etch-data-optimization (optional) | Yes (only if Data ran) |
| etch-doe | gap detected by Integration | No |
| etch-integration | all preceding agents | Yes |
| etch-report | etch-integration | Yes |

## Error Handling

| Situation | Handling |
|-----------|----------|
| Literature API unavailable | Output query strategy only; do NOT fabricate paper titles/links |
| Data API unavailable | Output data processing plan + expected schema; do NOT fabricate R² |
| Simulator unavailable | Use placeholder mock; qualitative hints only, no numerical prediction |
| Constraint boundary undefined | Return UNKNOWN with message "参数边界未定义，不能自动判定" |
| Subagent task times out (>2min) | Mark agent as unavailable, log error, continue |
| All APIs unavailable | Orchestrator runs in "plan-only" mode; produces workflow plan with no fabricated results |

## Evidence Level Reference

| Level | Meaning | When to Assign |
|-------|---------|----------------|
| **A** | data + constraint + mechanism aligned | Data agent has model, Constraint passes, Mechanism agrees |
| **B** | data-supported with warnings | Data agent has model, but Constraint/Mechanism has WARNING |
| **C** | mechanism/literature only | No data model; supported by mechanism reasoning or literature analogy |
| **D** | DOE exploration only | Insufficient evidence; DOE plan proposed for validation |
| **E** | insufficient evidence | Cannot recommend; need more data, constraints, or user input |

## Important Rules
- Do not fabricate unavailable API results.
- Do not fabricate simulator results.
- Always separate:
   - verified result,
   - model prediction,
   - mechanism hypothesis,
   - literature analogy,
   - DOE exploration.
- **Constraint FAIL cannot be overridden** by any other agent.
- **DOE recommendations must be treated as experimental plans**, not validated conclusions.
- UNKNOWN is a valid constraint status when boundary data is missing.
