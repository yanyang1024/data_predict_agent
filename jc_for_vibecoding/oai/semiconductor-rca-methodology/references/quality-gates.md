# RCA Quality Gates and Failure Modes

## Quality gates before accepting a root cause

A proposed root cause should pass most of these checks:

1. **Temporal order**: cause exposure precedes the metric shift.
2. **Scope coverage**: explains most affected units without also explaining many unaffected units.
3. **Specificity**: localizes to a plausible product/layer/tool/chamber/recipe/qtime/material group.
4. **Mechanism**: has a credible physical/process/equipment/data mechanism.
5. **Contrast**: demonstrated against matched good controls.
6. **Confounding**: product, time, tool, chamber, route, qtime, metrology, and maintenance effects considered.
7. **Measurement validity**: metrology/inspection/test artifact checked.
8. **Replicability**: observed across enough units or repeated after a known change when possible.
9. **Disconfirmation attempted**: at least one strong contrary test was considered.
10. **Actionability**: corrective action targets occurrence cause and escape point.
11. **Monitoring**: recurrence detection metric and control limits/trigger are defined.
12. **Documentation**: assumptions and evidence strength are explicit.

## Common RCA failure modes

| Failure mode | Description | Mitigation |
|---|---|---|
| correlation-as-cause | factor is enriched in bad lots but not proven causal | require temporal order, mechanism, controls |
| single-chain 5 why | one linear chain hides multiple contributors | use hypothesis tree/fishbone and evidence matrix |
| downstream alarm trap | alarm happens after outcome and is treated as cause | classify alarms by event time and process phase |
| mixed grain | lot averages, wafer traces, die maps, and chamber runs are joined incorrectly | state grain and aggregation rules before analysis |
| data leakage | disposition/retest/downstream labels used as predictors | exclude post-outcome variables from cause search |
| survivor bias | scrapped/held/reworked lots absent from downstream yield | include dispositioned material in population definition |
| Simpson's paradox | overall trend reverses within product/layer/chamber strata | stratify by key confounders |
| over-prioritizing easy data | convenient FDC signal displaces harder upstream/material cause | score hypotheses by mechanism and coverage, not just availability |
| metrology artifact | measurement tool/recipe shift mistaken for process shift | repeat/alternate metrology and gauge checks |
| maintenance confounding | post-PM changes coincide with product mix or chamber seasoning | compare sister chambers and run order after PM |
| qtime proxy | qtime correlates with priority/hold/rework rather than causing outcome | control hold reason, product, dispatch, and route |
| no escape-point analysis | occurrence cause fixed but detection system remains weak | include FDC/control plan/inspection/FMEA update |

## RCA output self-review rubric

Before finalizing an answer, check:

- Did I clearly define the problem metric and affected population?
- Did I reconstruct both operation logic and data logic?
- Did I avoid declaring a root cause prematurely?
- Did every top hypothesis include mechanism, expected signature, and disconfirming evidence?
- Did I include a practical next-step verification plan?
- Did I mention confidence/evidence strength?
- Did I include containment and prevention if the user asks for action?

## Confidence wording

- **Low confidence**: “plausible hypothesis; current input is insufficient to prioritize strongly.”
- **Medium confidence**: “supported by temporal and stratified evidence but still needs mechanism or replication check.”
- **High confidence**: “supported by temporal order, matched controls, mechanism, and intervention/replication evidence.”

Avoid using **confirmed root cause** unless evidence is high confidence.
