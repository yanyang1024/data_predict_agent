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

## Workflow
1. Parse user objective.
2. Identify required inputs:
   - layer type,
   - current RCP,
   - target metrics,
   - CD constraints,
   - historical data availability,
   - DOE budget,
   - API availability.
3. Call subagents:
   - etch-mechanism,
   - etch-literature,
   - etch-data-optimization,
   - etch-doe,
   - etch-constraint,
   - etch-integration,
   - etch-report.
4. Produce final report.

## Important Rules
- Do not fabricate unavailable API results.
- Do not fabricate simulator results.
- Always separate:
   - verified result,
   - model prediction,
   - mechanism hypothesis,
   - literature analogy,
   - DOE exploration.
- Constraint FAIL cannot be overridden by other agents.
- DOE recommendations must be treated as experimental plans, not validated conclusions.
