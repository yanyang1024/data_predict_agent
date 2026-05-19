# Semiconductor Operation and Data Logic

## Core entities and join keys

Use this table to reason about data structure even when actual schemas are unknown.

| Domain | Typical entities | Common join/time keys | RCA use |
|---|---|---|---|
| MES / route | product, route, operation, step, lot, wafer, carrier | lot_id, wafer_id, operation_id, step_id, start/end time | establish exposure path and process sequence |
| equipment | tool, chamber, module, station, recipe, run | tool_id, chamber_id, recipe_id, run_id, process start/end | isolate tool/chamber/recipe effects |
| sensor/FDC | sensor tag, recipe phase, alarm, trace, statistic | run_id, chamber_id, timestamp, phase/step | detect abnormal equipment behavior |
| APC / recipe | setpoint, control move, recipe version, model version | recipe_id, version, timestamp, product/layer | identify control logic or setpoint changes |
| qtime / dispatch | queue start/end, hold/release, priority, lot state | lot_id, operation pair, timestamp | test dwell-time and scheduling hypotheses |
| inline/metrology | CD, thickness, overlay, defect count, site map | wafer_id, lot_id, measurement time, tool_id | link process exposure to quality metrics |
| inspection/yield/test | wafer map, bin, e-test, final yield, defect class | wafer_id, die/bin, test time, layer/product | define failure signature and impact |
| maintenance | PM, clean, part change, calibration, qualification | tool/chamber, event time, engineer, reason | overlay events and post-maintenance transients |
| materials | chemical batch, target, gas, reticle, FOUP, supplier lot | batch_id, carrier_id, reticle_id, exposure time | test material/common-cause mechanisms |
| facilities/environment | temp, humidity, vacuum, gas, power, scrubber | area/tool, timestamp | detect site-wide or utility-driven excursions |

## Operation logic checklist

Before proposing root causes, reconstruct:

1. **Process boundary**: where the symptom is generated vs where it is measured.
2. **Route sequence**: upstream operations capable of causing the symptom.
3. **Tool/chamber path**: whether bad units share a tool, chamber, station, or recipe phase.
4. **Recipe versioning**: setpoint, APC model, endpoint, limit, or FDC threshold changes.
5. **Lot genealogy**: merge, split, hold, rework, retest, scrap, pilot lots, engineering lots.
6. **Queue time**: qtime window start/end, time since previous operation, time to metrology.
7. **Maintenance state**: PM, wet clean, part change, target age, seasoning, qualification, recovery lots.
8. **Dispatch logic**: priority, hot lots, batch composition, chamber assignment rules.
9. **Containment and interventions**: holds or recipe/tool changes made after detection.

## Data logic checklist

Verify these before trusting a signal:

- **Granularity**: lot-level, wafer-level, die-level, run-level, chamber-level, or sensor-sample-level.
- **Timestamp semantics**: process start, process end, event log time, database insert time, metrology time.
- **Join correctness**: one-to-one vs one-to-many joins; avoid duplicating wafers by sensor samples.
- **Lead/lag**: upstream exposure must precede downstream metric; metrology delay can obscure timing.
- **Sampling**: not all wafers/lots are measured; bad lots may be oversampled after alarms.
- **Censoring**: held/scrapped/reworked lots may disappear from later yield data.
- **Aggregation**: lot averages can hide wafer/slot/chamber patterns; die maps can hide lot-level effects.
- **Data leakage**: downstream alarms, retest decisions, or disposition labels may encode the outcome.
- **Metrology validity**: gauge repeatability, tool matching, calibration, sampling site, recipe.
- **Baseline selection**: compare to stable period and same product/layer where possible.

## Common semiconductor RCA mechanisms

| Category | Candidate mechanisms | Observable signatures |
|---|---|---|
| tool/chamber | chamber drift, matching issue, leak, RF/power instability, pressure/MFC deviation, temperature control | bad units concentrated by chamber/tool, residuals vs setpoint, post-PM shift, run-order gradient |
| recipe/APC/FDC | recipe version change, endpoint logic, APC overcorrection, FDC threshold disabled/mis-tuned | change coincides with version/control move, good/bad separated by model version or limit history |
| qtime/dispatch | excessive wait, queue before sensitive operation, hot-lot priority causing unusual path | threshold-like relationship, affected lots have longer dwell, interaction with humidity/process layer |
| material/consumable | chemical batch, target age, gas purity, reticle contamination, FOUP issue | cross-tool commonality, start/stop by material batch, spatial or lot-family pattern |
| metrology/inspection | measurement drift, recipe mismatch, sampling bias, retest effect | shift only on one metrology tool/recipe, inconsistent repeats, no downstream yield confirmation |
| upstream process | prior layer CD/thickness/overlay/film property propagates downstream | lagged signal from upstream operation, downstream symptom not explained by local tool |
| wafer/slot/spatial | edge exclusion, center-edge gradient, slot effect, handling scratch, clamp/contact issue | wafer map pattern, slot-position pattern, repeated spatial orientation |
| facilities/environment | chilled water, exhaust, gas cabinet, cleanroom humidity, power instability | multi-tool common-mode event, time-aligned facility alarm, area-level pattern |
| procedure/people | wrong recipe selection, skip/hold/release error, undocumented change | event log/operator/change-ticket evidence, isolated manual intervention |

## Data-type-specific analysis prompts

### FDC / sensor traces

Ask:

- Are traces aligned to recipe phase rather than wall-clock only?
- Which features changed: mean, max, slope, integral, stability, overshoot, endpoint time, residual vs setpoint?
- Is the abnormal sensor upstream of the quality effect or only an alarm after the process failed?
- Do bad wafers separate from matched good wafers on the same product/layer/tool/time window?
- Does the signal localize to one chamber/module or all chambers?

### QTime

Ask:

- What exact operation pair defines the qtime window?
- Does risk increase continuously or after a threshold?
- Are qtime violations confounded by product, priority, hold reason, or dispatch path?
- Does qtime explain all bad units or only a subset?
- Is there an interaction with humidity, material exposure, or queue before a sensitive process?

### Inline/metrology

Ask:

- Does the metrology tool/recipe/site map show a measurement artifact?
- Is the metric shift replicated on another metrology tool or downstream yield/e-test?
- Are sampled wafers representative of the full lot?
- Does the metric align with a specific upstream process mechanism?

### Wafer map / defect pattern

Use spatial signatures:

- **center-edge/ring**: process uniformity, temperature, gas flow, spin coat, etch/deposition profile.
- **scratch/linear**: handling, robot, FOUP, track, CMP, brush/contact.
- **cluster/localized**: particles, chamber contamination, reticle defect, chuck/contact.
- **field/reticle repeating**: mask/reticle, lithography field, scanner alignment.
- **slot/order effect**: batch position, queue order, chamber seasoning, cassette/FOUP issue.

### Yield / e-test

Ask:

- Is the fail mode parametric or catastrophic?
- Does bin-map pattern match inline/defect spatial pattern?
- Which operation is physically capable of causing the electrical signature?
- Does the issue correlate with product design sensitivity or process split?
