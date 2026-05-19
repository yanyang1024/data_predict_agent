---
name: semiconductor-rca-methodology
description: use this skill to perform root cause analysis, causal hypothesis generation, evidence planning, and structured troubleshooting for semiconductor manufacturing and engineering data. trigger on requests involving rca, yield loss, defectivity, excursion, fdc, sensor traces, equipment logs, qtime, inline metrology, wafer maps, recipe/tool/chamber issues, lot/wafer operation logic, data logic, causal analysis, fishbone, 5 why, 8d, fmea, capa, or requests to turn fab observations into hypotheses, verification plans, and analysis templates. this is a methodology-first skill; it does not run code or assume a specific database.
---

# Semiconductor RCA Methodology

## Core stance

Use this skill as a methodology coach for semiconductor root cause analysis. Focus on framing, causal reasoning, hypothesis generation, evidence design, and RCA report structure. Do not run code, invent database schemas, or claim a root cause without sufficient evidence.

Always separate:

- **Known facts**: explicitly present in the user input.
- **Reasonable inferences**: derived from operation/data logic and marked as inference.
- **Candidate causes**: possible mechanisms, not conclusions.
- **Evidence gaps**: what must be checked before confirmation.
- **Recommended verification**: data comparisons, experiments, controls, or expert checks.

Treat fab problems as temporal, multi-level, and confounded: route sequence, equipment/chamber state, recipe/APC/FDC behavior, lot/wafer genealogy, queue time, inline sampling, metrology reliability, maintenance events, and product mix can all change the apparent signal.

## Default workflow

For RCA tasks, follow this sequence unless the user asks for a narrower deliverable:

1. **Frame the problem**: define the symptom, metric, baseline, affected population, time window, severity, and current containment.
2. **Reconstruct operation logic**: route/operation/step order, tool/chamber/recipe path, qtime windows, holds/rework/splits, maintenance and qualification events.
3. **Reconstruct data logic**: data sources, entity grain, join keys, timestamps, lag/lead relationships, sampling logic, missingness, aggregation, and leakage risks.
4. **Select analysis lenses**: choose from timeline analysis, stratification/Pareto, SPC/change point, fishbone, 5 why, hypothesis tree, FMEA/8D, causal graph, matched controls, DOE, or expert review.
5. **Generate candidate mechanisms**: connect each hypothesis to a physical/process mechanism and an observable data signature.
6. **Prioritize hypotheses**: rank by evidence support, temporal plausibility, effect size, coverage of affected units, testability, actionability, and recurrence risk.
7. **Design verification**: specify the comparison groups, controls, data fields, expected observations, and disconfirming evidence.
8. **Produce the output**: use a compact RCA report, hypothesis matrix, evidence plan, or agent prompt depending on the user request.

Ask clarifying questions only when the missing information blocks useful analysis. Otherwise make explicit assumptions and proceed with a best-effort methodology answer.

## Semiconductor-specific defaults

When the user mentions semiconductor engineering data, default to this entity model:

- **product/process grain**: product, technology, layer, route, operation, process step, recipe, reticle/mask where relevant.
- **manufacturing grain**: lot, wafer, slot, die/bin, carrier/FOUP, run, batch, dispatch group.
- **equipment grain**: tool, chamber/module, station, recipe step/phase, sensor tag, consumable set, PM/clean/qualification state.
- **time grain**: process start/end, recipe phase timestamps, qtime start/end, hold/release, metrology time, inspection time, maintenance time.

Default fishbone categories for semiconductor RCA:

1. product/process/design
2. tool/chamber/module
3. recipe/apc/fdc/control logic
4. time/qtime/dispatch/queue
5. material/reticle/carrier/chemical/consumables
6. measurement/metrology/inspection/yield test
7. people/procedure/change management
8. environment/facilities/utilities

## Method selection guide

Use these decision rules:

- **Unclear problem statement** → create an issue-definition template and minimum data request.
- **Excursion over time** → build event timeline, baseline vs excursion comparison, SPC/change-point plan, and maintenance/change overlay.
- **Affected vs unaffected lots/wafers** → use stratification by product, route, tool, chamber, recipe, operator/dispatch, qtime, metrology sample, and upstream path.
- **Sensor/FDC trace issue** → compare recipe-phase-aligned traces, setpoint residuals, summary features, alarm order, and good/bad matched wafers.
- **Inline/yield/metrology shift** → check metrology repeatability, sampling plan, time lag from process to measurement, wafer-map spatial signature, and upstream operation sequence.
- **QTime/queue suspicion** → compare dwell-time distributions, threshold behavior, interaction with product/layer/tool, and before/after qtime window crossing.
- **Multiple plausible causes** → create a causal graph or hypothesis tree and design controls before ranking.
- **Need corrective action** → use 8D/FMEA/CAPA framing: containment, root cause, escape point, permanent corrective action, prevention, and monitoring.

## Output rules

For most RCA answers, include:

1. **One-line problem framing**
2. **Operation logic**
3. **Data logic**
4. **Top causal hypotheses**
5. **Evidence matrix**
6. **Recommended next analysis / verification plan**
7. **Risks and assumptions**

Use tables when comparing hypotheses or evidence. Keep conclusions probabilistic unless the evidence is decisive. Use the user's language unless they request otherwise.

## Load references as needed

- For a full RCA workflow or method decision matrix, consult `references/methodology.md`.
- For semiconductor-specific data sources, joins, failure signatures, and operation/data logic, consult `references/semiconductor-data-logic.md`.
- For final report formats, hypothesis matrices, 8D-style outputs, and fishbone/DAG templates, consult `references/output-templates.md`.
- For reusable agent prompts and user intake prompts, consult `references/agent-prompts.md`.
- For review checklists and common RCA failure modes, consult `references/quality-gates.md`.
