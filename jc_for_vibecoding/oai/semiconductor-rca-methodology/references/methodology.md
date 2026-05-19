# RCA Methodology Reference

## RCA levels

Distinguish these layers explicitly:

1. **Symptom**: what was observed, e.g., yield drop, inline CD shift, FDC alarm, defect count increase.
2. **Effect**: measurable consequence, e.g., bin loss, parametric fail, rework rate, tool down time.
3. **Proximal cause**: immediate associated condition, e.g., chamber B pressure residual high.
4. **Mechanism**: physical/process explanation, e.g., unstable plasma changes etch rate uniformity.
5. **Systemic cause**: why the condition was allowed, e.g., PM interval, FDC threshold, recipe control, dispatch rule.
6. **Escape point**: why detection/containment did not catch it earlier.

Do not stop at symptom or proximal cause when the user asks for root cause.

## Problem framing template

Use this before analysis:

- **Metric**: what changed? Include unit, target/spec, baseline, and current value if known.
- **Population**: affected product/layer/operation/lot/wafer/tool/chamber/recipe.
- **Time window**: first abnormal time, last known good, excursion period, recovery period.
- **Comparison group**: unaffected lots/wafers/tools/chambers/products.
- **Severity**: yield/quality/cost/throughput/customer impact.
- **Containment**: holds, tool stops, retest, scrap, recipe rollback, inspection escalation.
- **Decision needed**: identify root cause, prioritize investigation, propose data pulls, write 8D, or design experiment.

## Causal reasoning workflow

### 1. Establish temporal order

A cause must occur before the effect. For every hypothesis, specify:

- cause event/time
- affected unit exposure time
- expected lag to observed metric
- whether the measurement happened before or after the suspected cause

### 2. Build contrasts

RCA needs contrasts, not isolated bad cases. Recommended contrasts:

- bad vs good lots in the same product/layer/time window
- affected chamber vs sister chamber on same tool
- affected recipe version vs prior recipe version
- pre-PM vs post-PM
- qtime exceeded vs qtime not exceeded
- high residual sensor trace vs normal trace
- edge/center wafer regions with corresponding process hypotheses

### 3. Generate mechanisms

Each hypothesis should have this form:

`candidate cause -> process mechanism -> observable signature -> verification test -> expected disconfirming evidence`

Example:

`post-PM chamber seasoning instability -> etch rate drift in first N wafers -> CD shift strongest immediately after PM and decays by run count -> compare run order after PM -> hypothesis weak if no run-order gradient or sister chamber shows same shift without PM`

### 4. Control confounding

Common confounders in fab RCA:

- product and layer mix
- route alternatives and rework path
- chamber selection and dispatch policy
- lot priority and queue time
- metrology sampling and retest policy
- maintenance/qualification timing
- seasonal/facility conditions
- upstream operation changes
- engineer interventions during the excursion

### 5. Prioritize hypotheses

Score each hypothesis 1-5 on:

- temporal plausibility
- affected-population coverage
- observed effect size
- specificity to bad units
- physical/process plausibility
- ease of verification
- actionability
- recurrence/prevention value

High score means investigate first; it does not prove root cause.

## Method decision matrix

| Situation | Preferred methods | Watch-outs |
|---|---|---|
| vague issue | issue definition, SIPOC-style process boundary, minimum data request | do not overfit from anecdotes |
| time excursion | timeline, SPC, change-point, event overlay | avoid using spec limits as control limits |
| many categorical dimensions | stratification, Pareto, lift/enrichment, hypothesis matrix | adjust for product/time/chamber confounding |
| sensor/FDC traces | phase alignment, residuals vs setpoint, summary features, matched good/bad comparison | alarms may be downstream effects |
| wafer map/defect pattern | spatial signature mapping, defect taxonomy, layer/process matching | inspection sampling can bias pattern frequency |
| qtime suspicion | dwell-time distribution, threshold/segmented analysis, interaction terms | qtime may proxy dispatch/product priority |
| complex multi-step process | causal graph, process genealogy, upstream/downstream separation | avoid reverse causality from downstream holds |
| corrective action needed | 8D, FMEA update, control-plan review, CAPA | verify escape point, not only root cause |
| causal proof needed | DOE, A/B split, matched control, negative control, natural experiment | ensure intervention is safe and approved |

## Evidence strength ladder

Use this ladder to communicate confidence:

1. **Anecdotal**: one or a few observations; useful for ideation only.
2. **Correlational**: factor enriched among bad units; needs confounder control.
3. **Temporally plausible**: cause precedes effect with reasonable lag.
4. **Mechanistically plausible**: matches process physics or equipment behavior.
5. **Specific and contrastive**: explains bad units and excludes good units.
6. **Replicated**: seen across lots/tools/time or repeated after change.
7. **Intervention-validated**: controlled fix/removal changes the outcome.

Only levels 6-7 usually justify strong root-cause language.

## Recommended language

Use:

- “the strongest current hypothesis is...”
- “evidence supports / weakens this mechanism because...”
- “this is a likely contributor, not yet confirmed as root cause”
- “the next discriminating test is...”

Avoid:

- “the root cause is...” when evidence is incomplete
- “because two curves correlate” without temporal and confounder checks
- “5 why proves...” because 5 why is a prompt, not proof
