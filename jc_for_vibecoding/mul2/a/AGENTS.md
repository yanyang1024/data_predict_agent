# AGENTS.md

## Project Identity

Semiconductor Etch multi-agent framework built on OpenCode 1.15.10+. Primary design document: `dsad.txt` (1600 lines). OpenCode tutorial reference: `ref/opencode-custom-tools-subagents-tutorial.md`.

## Architecture

7 subagents + 1 orchestrator (Supervisor + Expert Pool + Producer-Reviewer hybrid):

| Agent | Role | Maturity |
|-------|------|----------|
| `etch-orchestrator` | Task decomposition, dispatching, user interaction | Framework |
| `etch-mechanism` | Qualitative physics/chemistry reasoning | Placeholder (no real simulator) |
| `etch-literature` | Literature retrieval + method transfer | API exists but closed |
| `etch-data-optimization` | Historical data modeling + multi-objective opt | API exists but closed |
| `etch-doe` | DOE design, matrix generation, ANOVA, HTML report | Can build locally first |
| `etch-constraint` | RCP/CD/historical-space/mechanism constraint check | New, rule-based |
| `etch-integration` | Conflict resolution, evidence grading (A–E) | New, LLM-driven |
| `etch-report` | Final Markdown/HTML report generation | New, template-based |

## Implementation Structure

```
.opencode/
  agent/        # Subagent definitions (Markdown + YAML frontmatter)
  tools/        # Tool definitions (TypeScript, @opencode-ai/plugin)
  skill/
    etch-multi-agent/  # SKILL.md + workflow + schemas + examples
docs/
  mechanism/
  constraints/
  schemas/
```

## Critical Rules

- **Never fabricate API/simulator results.** If an API is unavailable, return a structured fallback/placeholder; do not invent metrics, paper titles, links, or simulation values.
- **Constraint FAIL cannot be overridden** by any other agent.
- **Evidence levels:** A (data+constraint+mechanism aligned), B (data+warnings), C (mechanism/literature only), D (DOE exploration only), E (insufficient).
- **DOE recommendations** are experimental plans, not validated conclusions.

## API Status

| API | Host | Status |
|-----|------|--------|
| Literature | `10.18.220.244:32300` | Closed |
| Data (primary) | `10.20.52.249:5314` | Closed |
| Data (secondary) | `10.20.52.249:5315` | Closed |

## Implementation Phases

1. **Phase 0** — Agent/tool/skill stubs + docs skeleton (no live APIs needed)
2. **Phase 1** — DOE local tools (matrix generation, CSV, run randomization, HTML report)
3. **Phase 2** — Constraint Agent (parameter/CD boundary checks, PASS/WARNING/FAIL/UNKNOWN)
4. **Phase 3** — Literature API adapter (create_conversation → chat_query_v2_sse → get_message_info)
5. **Phase 4** — Data API adapter (data_quality → model_compare → optimize → predict_override → export_files)
6. **Phase 5** — Mechanism simulator adapter (when simulator owner provides interface)

## Tool vs Subagent Convention

- **Tool** — deterministic, atomic: API calls, matrix generation, constraint checking, mock placeholder
- **Subagent** — multi-step reasoning, expert judgment: mechanism explanation, literature migration, optimization interpretation, DOE planning, result integration, report generation
- **Skill** — workflow orchestration binding subagents + tools together

## Default Orchestration Flow

1. User input → Orchestrator parses task type
2. Parallel: Mechanism / Literature / Data agents
3. Sequential: Constraint checks Data agent output
4. If gap: DOE generates validation experiment
5. Integration does conflict arbitration → Report generates final document
