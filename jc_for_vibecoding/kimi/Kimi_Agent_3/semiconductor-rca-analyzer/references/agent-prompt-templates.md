# Semiconductor RCA Agent Prompt Templates

## Introduction

This document contains reusable prompt structures that guide an AI agent through specific types of root cause analysis (RCA) in semiconductor manufacturing environments. Each template provides a structured thinking framework — the agent should adapt the template to the specific data and problem at hand, substituting bracketed placeholders with actual values and expanding or contracting steps based on data availability.

These templates are methodology-level prompts. They define **how** to think through a problem class, not **what** the answer is. The agent should treat each step as an instruction to perform a specific analytical action, draw intermediate conclusions, and synthesize findings into a coherent causal narrative with confidence-rated recommendations.

**Usage convention:** Replace all `[placeholder]` tokens with actual values from the specific RCA task. Remove steps that are inapplicable due to data unavailability. Add domain-specific detail where the template indicates expansion points.

---

## Template 1: FDC Multivariate Alarm RCA

### Applicability
Use when an FDC (Fault Detection and Classification) system fires a multivariate alarm (T-squared or SPE statistic exceeds control limit) and the goal is to determine why the alarm fired and what corrective action is required.

### Prompt Template

```markdown
# FDC Multivariate Alarm Root Cause Analysis

## Context
An FDC multivariate alarm has fired for [equipment_id] processing [product_type] at [timestamp].
The alarm type is [alarm_type] with T^2/SPE value of [value] vs control limit of [limit].
Contributing sensors (from FDC contribution plot): [sensor_list_with_contributions]

## Analysis Steps

### 1. Alarm Characterization
- Identify alarm severity and type: T^2 overload (correlated variable shift) vs SPE violation (uncorrelated variable anomaly).
- Extract top contributing sensors from the FDC contribution plot, ranked by contribution percentage.
- Check alarm frequency: Is this a repeat alarm (same equipment, same sensors) or a new alarm pattern?
- Review historical alarm log for this equipment over the past [lookback_period]: Identify any recurring patterns, seasonal trends, or post-PM alarm clusters.
- Classify the alarm as: process-related, equipment-degradation-related, or transient/recoverable.

### 2. Sensor Deep Dive
For each top-contributing sensor (typically the top 3-5):
- Extract and plot the sensor trace for the alarm lot against a reference set of [N] previous normal lots processed on the same chamber.
- Identify the specific process step or recipe phase within the recipe where the deviation occurs (e.g., stabilization, deposition, purge, cool-down).
- Compare the sensor profile against the chamber baseline established from the most recent post-PM qualification run.
- Check for gradual sensor drift in the lots leading up to the alarm lot (early warning indicators).
- Calculate statistical distance metrics: z-score, Mahalanobis distance, or deviation from chamber mean for the alarm lot.
- Flag any sensor saturation, signal dropout, or noise increase that may indicate a sensor hardware issue rather than a true process shift.

### 3. Cross-Reference with Equipment Events
- Query PM history: Time elapsed since last PM, PM type (scheduled, unscheduled, chamber-specific), and PM items performed on the alarm chamber.
- Query equipment event log for the [X] hours preceding the alarm: Record all errors, warnings, state changes, mode transitions, and interlock events.
- Check for recipe changes: Any recent parameter adjustments, recipe version updates, or software/firmware updates applied to the tool?
- Check maintenance records: Part replacements, adjustments, calibrations, or repairs performed since the last normal-processing period.
- Cross-reference event timestamps with the onset of sensor deviation identified in Step 2.

### 4. Cross-Reference with Inline Metrology
- Retrieve inline measurement data for the alarm lot and the [N] lots processed immediately after the alarm.
- Examine key inline metrics relevant to the process step: CD (critical dimension), film thickness, uniformity, roughness, or other layer-specific parameters.
- Compare inline values against the SPC control chart: Identify any rule violations (Western Electric rules), trend shifts, or out-of-control conditions.
- Determine whether the FDC alarm preceded or coincided with inline metric shifts — establish temporal ordering.
- If inline data is still pending (awaiting measurement), flag the risk window and recommend hold/skip-lot disposition.

### 5. Causal Chain Construction
Synthesize findings into a narrative causal chain with the following structure:
```
[Root cause event] -> [Equipment parameter shift] -> [Sensor signature change] -> [FDC alarm]
                                        |
                                        v
                              [Inline metrology impact (if observed)]
```
For each link in the chain:
- State the evidence supporting the causal link.
- Quantify the magnitude of change at each stage.
- Identify any missing links where data is insufficient.
- Flag any confounding factors or alternative explanations.

### 6. Confidence Assessment
Assign an overall confidence level to the root cause determination:
- **CONFIRMED**: Clear evidence chain with multiple independent corroborating data points; temporal ordering is unambiguous; alternative explanations are ruled out.
- **LIKELY**: Strong primary evidence with a plausible physical mechanism; one or two corroborating data points; minor gaps in the evidence chain.
- **POSSIBLE**: Some evidence supports the hypothesis; competing explanations exist with comparable support; additional data would be needed to discriminate.
- **INCONCLUSIVE**: Insufficient data to determine root cause; alarm may be due to sensor noise, model misfit, or unmeasured variables.

### 7. Recommendations
Structure recommendations by time horizon and risk level:
- **Immediate (0-4 hours)**: Action to contain risk — e.g., hold subsequent lots, quarantine suspect material, increase inspection frequency, notify shift supervisor.
- **Short-term (same shift / 24 hours)**: Corrective action — e.g., chamber re-qualification, recipe parameter adjustment, sensor recalibration, targeted maintenance action.
- **Long-term (1-4 weeks)**: Preventive measure — e.g., FDC model retraining, monitoring threshold adjustment, PM procedure revision, hardware upgrade evaluation.
- **Monitoring**: Define specific metrics and review frequency to verify effectiveness of corrective actions.
```

---

## Template 2: Process Drift RCA

### Applicability
Use when a process parameter shows a sustained directional shift over time, detected via SPC trend rules, VM (Virtual Metrology) prediction drift, or inline metrology trend analysis. The goal is to identify the origin of the drift and arrest it before it causes yield loss or excursion.

### Prompt Template

```markdown
# Process Drift Root Cause Analysis

## Context
A process drift has been detected in [process_step] for [product_type].
Detection method: [SPC trend rule / VM prediction drift / Inline metrology shift / FDC trend]
Drift direction: [increasing / decreasing / bimodal shift] from [baseline_value] to [current_value] over [time_period]
Affected equipment: [tool_list or "all tools"]
Drift metric: [specific_parameter_name] with units [units]

## Analysis Steps

### 1. Drift Characterization
- Quantify drift magnitude: Calculate total delta, drift rate per day/week, and drift as percentage of spec width and control limit distance.
- Determine drift onset time: Use change-point detection (e.g., CUSUM, Bayesian change point) to estimate when the drift began.
- Identify affected tools: Is the drift present on all chambers or specific chambers? Compute per-chamber drift vectors.
- Check product specificity: Does the drift affect all products, specific layers, specific recipes, or specific lot types?
- Assess current risk position: How much spec margin remains? Estimate time to spec violation at current drift rate.

### 2. Temporal Analysis
- Plot the parameter trend over the full analysis period with key equipment and operational events overlaid as annotations.
- Correlate drift onset timestamp with:
  * PM events (before/after any PM on affected chambers)
  * Recipe or parameter changes (software updates, recipe version changes)
  * Material lot changes (chemical/gas/wafer lot transitions)
  * Seasonal patterns (humidity, facility maintenance schedules)
  * Major facility events (power events, CDA maintenance, cooling water work)
- Characterize drift profile: Is the drift rate constant, accelerating, decelerating, or step-change? Fit appropriate model (linear, exponential, step function).
- Compare drift timelines across affected tools: Are chambers synchronized (common cause) or staggered (independent causes)?
- Check for recovery episodes: Has the parameter ever returned toward baseline, and if so, what preceded the recovery?

### 3. Equipment Parameter Analysis
- Compare full recipe parameter sets between the normal (pre-drift) period and the drift period. Flag any parameter differences.
- Check for gradual shifts in equipment control loop outputs: MFC flow rates, heater power, pressure controller outputs, RF parameters.
- Analyze APC (Run-to-Run) controller behavior:
  * Is the controller detecting and compensating for the drift?
  * Is controller output trending toward saturation or a limit?
  * Has controller performance degraded (larger prediction residuals)?
- Review chamber matching data: Is the drift chamber-specific, or are all chambers moving together?
- Examine equipment log for recurring minor errors or warnings that may indicate degrading hardware performance.

### 4. Material and Supplier Analysis
- Map raw material lot usage to the drift timeline: chemicals, gases, wafers, reticles, consumables.
- Identify any material lot changes that coincide with the drift onset within a reasonable process lag window.
- Check supplier change history: New supplier, new material grade, or supply chain change in the relevant period.
- Analyze material quality data (COA — Certificate of Analysis) for the material lots in use during drift: Are any COA parameters at the edge of specification?
- If suspect material is identified, check if lots processed before the material change are within normal range (pre/post comparison).

### 5. Environmental and Facilities Analysis
- Retrieve cleanroom environmental data for the drift period: Temperature, relative humidity, differential pressure, particle counts.
- Check facility system data: CDA (compressed dry air) pressure/quality, vacuum levels, cooling water temperature/flow, exhaust flow rates.
- Check for facility maintenance events: HVAC work, chiller maintenance, power distribution work.
- Analyze neighboring tool activities: Shared utilities, simultaneous maintenance events, or process changes on adjacent tools.
- Check for seasonal effects: Correlate drift with historical seasonal patterns if multi-year data is available.

### 6. Root Cause Hypothesis Testing
Apply the Ishikawa 6M framework systematically. For each category:

| Category | Hypothesis | Expected Data Signature | Actual Data | Support Level |
|----------|-----------|------------------------|-------------|---------------|
| **Man** | Operator shift change, training gap, procedure deviation | Shift-dependent pattern, SOP deviation records | [fill in] | [Strong/Weak/None] |
| **Machine** | Hardware degradation, calibration drift, consumable wear | Chamber-specific drift, sensor drift pattern | [fill in] | [Strong/Weak/None] |
| **Material** | Material lot change, supplier change, COA edge case | Lot-correlated onset, pre/post material comparison | [fill in] | [Strong/Weak/None] |
| **Method** | Recipe change, parameter adjustment, software update | Timestamp correlation with change event | [fill in] | [Strong/Weak/None] |
| **Measurement** | Metrology tool drift, gauge R&R issue, sampling change | Drift absent on backup metrology tool, GR&R shift | [fill in] | [Strong/Weak/None] |
| **Milieu** | Environmental shift, facility event, seasonal effect | Correlated environmental parameter shift | [fill in] | [Strong/Weak/None] |

For each hypothesis:
- State the hypothesis clearly.
- Define the expected data signature if the hypothesis were true.
- Compare expected signature against actual data.
- Assign support level: Strong / Weak / None / Conflicting evidence.

### 7. Validation
- Perform difference-in-differences analysis: Compare affected tools against unaffected but otherwise similar tools (same platform, same process, same products).
- If a corrective action has already been implemented: Monitor post-action data for drift reversal. Calculate reversal magnitude and statistical significance.
- Perform predictive validation: Does the hypothesized root cause quantitatively explain the observed drift pattern? (e.g., if material lot change is the cause, lots before the change should be normal, lots after should show drift).
- Check for confounding: Could a second factor be contributing? Quantify the relative contribution of each factor if multiple causes are suspected.

### 8. Recommendations
- **Immediate containment**: Define hold criteria, quarantine rules, or inspection ramp-up for lots at risk.
- **Corrective action**: Specify the action to arrest the drift (e.g., recipe adjustment, material lot change, hardware replacement, environmental control correction).
- **Verification plan**: Define the monitoring period, success criteria, and decision rules for declaring the drift resolved.
- **Preventive action**: Propose changes to prevent recurrence (e.g., tighter material acceptance criteria, enhanced monitoring, PM procedure update, APC tuning).
- **Escalation path**: Define conditions under which the issue must be escalated to engineering management or the customer.
```

---

## Template 3: Yield Excursion RCA

### Applicability
Use when test yield drops below the established baseline, either suddenly (excursion) or gradually (erosion). The goal is to identify the process step, tool, or material source responsible for the yield loss and define corrective actions.

### Prompt Template

```markdown
# Yield Excursion Root Cause Analysis

## Context
A yield drop from [baseline_yield]% to [current_yield]% has been observed.
Time window: [start_date] to [end_date]
Affected products: [product_list or "all products"]
Affected process flow: [process_flow_name]
Bin map signature: [spatial_pattern_description or "to be analyzed"]
Detection source: [wafer test / final test / sort / probe]

## Analysis Steps

### 1. Excursion Characterization
- Build a yield loss Pareto chart: Rank test bins by fail count to identify the dominant failure mode(s).
- Calculate yield loss attribution: What percentage of total yield loss comes from the top bin? Top 3 bins? Top 5 bins?
- Analyze wafer-level bin map spatial patterns for failing lots:
  * Describe the pattern: Random/scattered, edge-dominant, center-dominant, ring, repeating die, clustered, or mixed.
  * Quantify pattern strength: Percentage of fails in the dominant spatial region vs. uniform distribution.
- Determine excursion onset profile:
  * Sudden step-drop (points to single event: recipe change, hardware failure, material lot)
  * Gradual decline (points to drift: hardware degradation, gradual contamination)
  * Intermittent (points to unstable process or tool-dependent issue)
- Check if yield loss is tool-specific, product-specific, layer-specific, or universal across the fab.

### 2. Spatial Signature Analysis
Interpret the wafer-level spatial failure pattern to narrow the root cause domain:

| Pattern | Typical Root Cause Category | Priority Investigations |
|---------|---------------------------|------------------------|
| **Random / Scattered** | Process parameter issue, material quality, blanket contamination | FDC alarms, material lots, recipe parameters |
| **Edge-dominant** | Chamber edge effect, etch non-uniformity, CMP edge effect, deposition edge exclusion | Chamber hardware, gas flow, endpoint detection |
| **Center-dominant** | Chamber center effect, deposition uniformity (center thick/thin), susceptor issue | Showerhead condition, gas distribution, susceptor flatness |
| **Ring pattern** | Chamber hardware issue, gas flow asymmetry, anodization wear, focus ring condition | Hardware inspection, matching study |
| **Repeating die pattern** | Mask/reticle defect, stepper/scanner issue, die-layout related | Reticle inspection, litho tool analysis, die size correlation |
| **Clustered / Hot spots** | Particle/contamination, localized defect source, handling damage | Defect inspection, particle mapping, AMHS path analysis |
| **Gradient (one-sided)** | Gas flow imbalance, thermal gradient, upstream/downstream effect | Chamber symmetry inspection, gas line verification |

For the observed pattern:
- Compare against historical excursions with similar signatures: Any known root causes from past events?
- Check if the pattern is consistent across all failing lots or varies (pattern consistency indicates single root cause; pattern variation may indicate multiple causes).

### 3. Temporal and Tool Correlation
- Build a lot-level timeline: Plot yield by lot sequence with tool assignments color-coded.
- Correlate yield drop with tool events:
  * PM events on suspected tools (timing relative to excursion onset)
  * Recipe changes or software updates
  * FDC alarm frequency during the excursion period (elevated alarms?)
  * Qualification results (any marginal or failing quals?)
- Perform tool commonality analysis:
  * Do failing lots share a specific tool or chamber? Calculate tool fail rate vs. baseline.
  * Use chi-square or Fisher's exact test to test statistical significance of tool-yield association.
  * Check chamber-to-chamber yield differences on multi-chamber tools.
- Check for multi-tool correlation: Do failing lots share multiple process steps on the same tools (indicating a broader issue)?

### 4. Inline Metrology Correlation
- Identify all inline metrics that are plausible leading indicators for the dominant failure mode.
- Correlate yield with inline metrics: CD, film thickness, uniformity (1-sigma, range), overlay, defect counts, particle counts.
- Build a correlation matrix (Pearson/Spearman) between yield and inline metrics to identify the strongest associations.
- Check for inline metric shifts that **precede** the yield drop (true leading indicators vs. coincident indicators).
- For the most correlated inline metrics: Determine the metric's own root cause — what is causing the inline shift?
- Check if inline metric control charts showed violations (Western Electric rules) before the yield excursion was detected.

### 5. Process Step Isolation
- If the product has multiple process steps: Determine which step is most likely the yield-loss source.
- Use lot process history to trace common process steps among failing lots:
  * Build a process step commonality matrix.
  * Identify steps where failing lots share the same tool while passing lots use different tools.
- Consider Q-time violations as a contributing factor: Did any failing lots experience extended queue time between critical steps?
- If available, use inline defect inspection data (e.g., KLA scans) to identify the process step where the defect signature first appears.
- Prioritize process steps based on: spatial pattern match (which step's known failure mode matches the bin map pattern?), inline correlation strength, and tool commonality.

### 6. Hypothesis Testing
Formulate testable hypotheses based on the spatial pattern, tool correlation, and inline data:

For each hypothesis:
1. State the hypothesized root cause.
2. Identify the expected evidence: What data pattern would confirm this hypothesis?
3. Collect the relevant data and compare against expectations.
4. Assign a confidence level:
   - **CONFIRMED**: Evidence overwhelmingly supports; alternative hypotheses ruled out.
   - **LIKELY**: Strong supporting evidence; consistent with physical mechanism; minor gaps.
   - **POSSIBLE**: Some supporting evidence; competing hypotheses have similar support.
   - **UNLIKELY**: Evidence contradicts or insufficient support.

Common hypothesis categories for yield excursions:
- Lithography: CD shift, overlay error, focus issue, reticle defect
- Etch: Etch depth shift, selectivity issue, chamber condition, endpoint error
- Deposition: Thickness shift, uniformity degradation, film quality (refractive index, stress)
- CMP: Over-polish, under-polish, dishing, erosion, pad condition
- Contamination: Particle source, metallic contamination, cross-contamination from shared tools
- Implant: Dose shift, energy shift, beam instability
- Thermal: RTP temperature non-uniformity, anneal time shift

### 7. Recommendations
- **Immediate containment**:
  * Define lot hold criteria based on tool commonality or inline metric thresholds.
  * Specify quarantine scope: Which lots are at risk? How far back to trace?
  * Recommend inspection/sampling increase for suspect lots.
- **Short-term corrective action**:
  * Targeted maintenance, recipe adjustment, or tool re-qualification for the identified root cause.
  * Material lot change if material is implicated.
  * Inline monitoring enhancement to catch future events earlier.
- **Long-term preventive action**:
  * SPC rule enhancement or new control chart for the identified leading indicator.
  * PM procedure update if hardware degradation is the root cause.
  * Process window tightening or design rule adjustment if applicable.
- **Verification plan**:
  * Define yield recovery monitoring period (typically 50-100 lots post-fix).
  * Specify success criteria: Yield return to baseline, bin Pareto normalization, spatial pattern resolution.
  * Define escalation triggers if yield does not recover as expected.
```

---

## Template 4: Q-time Violation RCA

### Applicability
Use when lots exceed the maximum allowed queue time (Q-time) between two process steps. Q-time violations can cause material degradation, process instability, and yield/reliability risk. The goal is to identify and eliminate the flow bottleneck causing the violations.

### Prompt Template

```markdown
# Q-time Violation Root Cause Analysis

## Context
Q-time violation detected for process step pair [step_A] to [step_B].
Q-time limit: [limit_value] [units] | Actual elapsed time: [actual_value] [units] | Overrun: [overrun_value] [units]
Affected lots: [lot_count] lots
Time period: [start_date] to [end_date]
Product type(s): [product_list]
Severity classification: [Minor / Major / Critical] based on overrun magnitude and material sensitivity.

## Analysis Steps

### 1. Violation Characterization
- Identify the process step pair with Q-time violation and its position in the overall process flow.
- Quantify violation severity: Maximum overrun, average overrun, and percentage of lots violating.
- Determine violation frequency pattern:
  * Batch/continuous: Are violations occurring in clusters (suggesting an event-driven cause)?
  * Intermittent: Sporadic violations (suggesting stochastic cause)?
  * Sustained: Persistent violations over a period (suggesting chronic capacity imbalance)?
- Check if violations are specific to: Product type, lot priority class (hot lot vs. normal), tool assignment, or shift.
- Calculate the business impact: Estimated WIP value at risk, potential yield/reliability impact, customer delivery risk.

### 2. WIP Flow Analysis
- Analyze WIP (Work In Process) inventory levels at the upstream step (step_A output) and the downstream step (step_B input) over the violation period.
- Check for WIP imbalance: Is upstream production rate (wafers/hour out of step_A) persistently higher than downstream processing rate (wafers/hour into step_B)?
- Identify bottlenecks in the process flow between the Q-time steps:
  * Calculate theoretical cycle time (processing time only) vs. actual average elapsed time.
  * Quantify queue time contribution at each intermediate step or buffer.
  * Identify the step with the longest queue time within the Q-time window.
- Check lot priorities: Are high-priority (hot, super-hot) lots jumping the queue and causing normal-priority lots to age past the Q-time limit?
- Analyze lot sequencing: Is the FIFO (First-In-First-Out) discipline being maintained, or is there significant out-of-sequence processing?

### 3. Equipment Availability Analysis
- Check equipment availability at the downstream step (step_B):
  * Total tool count and available tool count over time.
  * Scheduled and unscheduled downtime events (PM, quals, repairs).
  * Tool utilizations: Are tools running at or near 100% utilization (indicating capacity constraint)?
- Check equipment constraints:
  * Limited tool count for the specific product/recipe combination.
  * Chamber matching requirements that restrict which chambers can process which products.
  * Recipe/tool dedication constraints that reduce effective capacity.
- Check for equipment qualification delays: Are tools waiting for qualification after PM or repair?
- Check upstream equipment: Is upstream over-producing due to excess capacity or a recent throughput improvement?

### 4. AMHS (Automated Material Handling System) Analysis
- Check AMHS transport system status during the violation period:
  * Any AMHS congestion, loop stoppages, or OHT (Overhead Hoist Transport) vehicle shortages?
  * Average transport time between step_A and step_B vs. historical baseline.
- Analyze storage (stocker/buffer) status:
  * Any buffer-full conditions that prevent lots from moving out of upstream?
  * Stocker retrieval delays causing lots to wait before entering downstream?
- Check for AMHS path issues: Rerouting, blocked paths, or maintenance activities affecting specific transport segments.
- Check if lots are accumulating in manual transfer queues (bypassing AMHS) due to system issues.

### 5. Operational Factors
- Check shift patterns: Are violations concentrated in specific shifts (day, evening, night, weekend)?
- Check operator staffing levels: Are downstream tools understaffed during specific shifts?
- Check for dispatching rule changes: Has the dispatching policy or priority weighting been modified recently?
- Check for abnormal operational events during the violation window:
  * Power outages or facility events causing temporary tool shutdowns.
  * Emergency lots (engineering, customer priority) displacing production lots.
  * Quality holds or engineering experiments blocking normal flow.
- Check if the Q-time violation coincides with a known fab event (ramp-up, new product introduction, capacity expansion).

### 6. Impact Assessment
- Correlate Q-time violations with inline metrology data for violated lots:
  * Are violated lots showing parameter shifts compared to non-violated lots (same product, same tools)?
  * Quantify the metrology delta between violated and non-violated populations.
- Check if Q-time violations correlate with downstream yield or reliability test failures:
  * Compare yield of violated lots vs. non-violated lots processed through the same tools.
  * Perform statistical test (t-test, chi-square) for yield difference significance.
- Assess material degradation risk based on the specific process step pair:
  * Is the material surface sensitive to oxidation, contamination, or moisture?
  * What is the known degradation mechanism for this Q-time pair?
- Estimate the scrap/rework risk: At what overrun threshold does the lot become unrecoverable?

### 7. Root Cause and Recommendations
Synthesize findings to identify the primary root cause category:
- **Equipment bottleneck**: Downstream capacity insufficient for upstream throughput.
- **WIP imbalance**: Transient or sustained mismatch between upstream output and downstream input.
- **AMHS issue**: Transport or storage system limitation causing flow delays.
- **Operational issue**: Staffing, dispatching, or abnormal event causing flow disruption.
- **Multiple causes**: Combination of two or more factors.

For each root cause category, recommend:
- **Equipment bottleneck**: Capacity analysis report, tool addition recommendation, recipe sharing across tools, chamber dedication relaxation.
- **WIP imbalance**: WIP leveling via dispatching rules, upstream throttling, super-hot lot management policy revision.
- **AMHS issue**: Transport capacity analysis, stocker capacity expansion, AMHS maintenance schedule optimization.
- **Operational issue**: Shift staffing adjustment, dispatching rule update, cross-training, emergency response procedure update.

Define a monitoring plan:
- Q-time compliance dashboard metric with alert thresholds.
- Weekly trend review of Q-time violations by step pair.
- Review cadence and escalation rules.
```

---

## Template 5: Chamber Mismatch Issue RCA

### Applicability
Use when two or more chambers on the same tool show statistically significant differences in process output, detected via SPC rules, qualification failures, or inline metrology comparison. The goal is to restore chamber matching and ensure uniform processing across all chambers.

### Prompt Template

```markdown
# Chamber Mismatch Root Cause Analysis

## Context
Chamber mismatch detected on [tool_id]: [chamber_A] vs [chamber_B] (extend to additional chambers as applicable).
Mismatch parameter: [parameter_name] with units [units]
Measured delta: [delta_value] [units] vs matching specification of [spec_limit] [units]
Detection source: [SPC rule violation / Qualification failure / Inline metrology difference / Chamber matching study]
Product/layer affected: [product_list or "all products"]
Mismatch direction: [chamber_A higher / chamber_B higher / divergent trends]

## Analysis Steps

### 1. Mismatch Characterization
- Quantify the magnitude and direction of the chamber difference:
  * Absolute delta and delta as percentage of spec width.
  * Statistical significance: p-value from t-test or ANOVA comparing chamber populations.
- Determine which parameter(s) show mismatch:
  * Is the mismatch limited to one parameter or multiple parameters?
  * Are the mismatched parameters correlated (suggesting a common root cause)?
- Check if the mismatch is:
  * Constant: Fixed offset between chambers (suggesting hardware/setup difference).
  * Drifting: Diverging over time (suggesting differential degradation).
  * Intermittent: Appearing and disappearing (suggesting instability or conditional factor).
- Identify affected product layers: Is the mismatch more pronounced on certain products or layers?
- Assess impact: Which inline metrics or yield metrics are affected by this mismatch? Quantify the product impact.

### 2. Chamber History Comparison
- Compare PM history between chambers:
  * Time since last PM for each chamber (synchronized or staggered?).
  * PM items performed: Were identical procedures followed?
  * PM technicians: Different technicians for each chamber?
  * PM consumables: Different consumable part numbers, batches, or installation procedures?
- Compare consumable part records:
  * Parts that differ between chambers: Type, batch, installation date, accumulated cycles.
  * Wear-sensitive parts: Focus rings, showerheads, susceptors, liners, seals.
  * Flag any consumable with significantly different accumulated usage hours/cycles between chambers.
- Compare qualification results:
  * Historical matching trend: Has mismatch been growing gradually, or is this a sudden step?
  * Last matching qualification date and results for each chamber.
  * Any marginal passing results in recent quals.
- Compare equipment event logs:
  * Different error/warning frequencies or types between chambers.
  * Any unscheduled maintenance events on one chamber but not the other.

### 3. Sensor Trace Comparison
- Compare sensor traces for identical recipes run on each chamber:
  * Overlay traces for all available sensors (pressure, temperature, gas flow, RF, etc.).
  * Identify which sensors show the most significant divergence between chambers.
  * Calculate per-sensor delta and rank by magnitude.
- Compare process stability between chambers:
  * Calculate within-chamber variability (standard deviation) for each sensor.
  * Is one chamber noisier than the other (higher variance)?
  * Check for unusual transient behavior in either chamber (spikes, oscillations, delayed responses).
- Check for sensor calibration differences:
  * When was each sensor last calibrated?
  * Are there known calibration offsets between chambers?
  * Check raw sensor values vs. calibrated/processed values.
- Build a sensor divergence summary table:

| Sensor | Chamber A Mean | Chamber B Mean | Delta | % of Range | Significance |
|--------|---------------|---------------|-------|------------|--------------|
| [name] | [value] | [value] | [value] | [%] | [p-value] |

### 4. Physical Inspection Guidance
Based on sensor divergence analysis, generate targeted physical inspection recommendations for the maintenance team:

| Divergent Sensor | Likely Hardware Cause | Inspection Item | Priority |
|-----------------|----------------------|-----------------|----------|
| Pressure | Gas line leak, MFC calibration, throttle valve condition | Check gas lines, MFC calibration, valve response | [High/Med/Low] |
| Temperature | Heater condition, thermocouple drift, susceptor flatness | Inspect heater, verify thermocouple, check susceptor | [High/Med/Low] |
| Gas flow | MFC drift, gas line restriction, purge line condition | Calibrate MFCs, check filters, inspect lines | [High/Med/Low] |
| RF/power | Matcher condition, electrode condition, cable integrity | Inspect matcher, electrode, RF cable | [High/Med/Low] |
| [custom] | [custom] | [custom] | [High/Med/Low] |

For each high-priority inspection item:
- State the expected finding if the hypothesis is correct.
- Define the acceptance criteria for the inspection.
- Specify whether the inspection can be performed in-situ or requires chamber opening.

### 5. Recommendations
- **Immediate actions**:
  * Determine if chamber should be taken offline pending investigation (based on mismatch magnitude and product risk).
  * Define lot hold criteria: Which lots are at risk? Which chamber should be restricted?
  * Recommend increased inline sampling for lots processed on the suspect chamber.
- **Chamber re-matching procedure**:
  * Specify the matching qualification recipe and acceptance criteria.
  * Define the re-matching protocol: Parameter adjustment sequence, verification runs, statistical acceptance rules.
- **Hardware replacement suggestions**:
  * Based on inspection findings and sensor divergence, recommend specific parts for replacement or refurbishment.
  * Prioritize by expected impact on mismatch correction.
- **PM procedure alignment**:
  * Recommend changes to ensure synchronized PM timing between chambers.
  * Recommend standardized consumable part selection and installation procedures.
  * Recommend cross-chamber PM technician coordination.
- **Long-term monitoring**:
  * Recommend chamber matching control chart with control limits.
  * Define matching qualification frequency.
  * Set up automated alerts for matching drift exceeding a defined threshold.
```

---

## Template 6: General-Purpose RCA

### Applicability
Use when the problem type is unclear, the observed symptoms do not cleanly map to any of the specific templates above, or the initial report lacks sufficient detail for classification. This template provides an adaptive workflow that converges on the appropriate methodology.

### Prompt Template

```markdown
# General Semiconductor Root Cause Analysis

## Context
[User describes the observed problem, symptoms, and any initial data available.]
Problem description: [free-text description of what is wrong]
First observed: [timestamp or date range]
Scope: [which products, tools, process areas are involved]
Business impact: [yield impact, throughput impact, quality risk, customer risk]
Data sources available: [list of available data sources and systems]
Data sources unavailable: [list of data sources that cannot be accessed]

## Adaptive Analysis Workflow

### 1. Problem Classification
First, classify the problem along the following dimensions:

| Dimension | Options | Classification |
|-----------|---------|----------------|
| Onset pattern | Sudden (step) / Gradual (drift) / Intermittent / Unknown | [select] |
| Scope | Single tool / Multiple tools / All tools / Unknown | [select] |
| Product specificity | Single product / Multiple products / All products / Unknown | [select] |
| Detection source | Test yield / Inline metrology / FDC alarm / Customer complaint / Visual inspection / Other | [select] |
| Repeatability | Always occurs / Conditionally occurs / Random / Unknown | [select] |

Based on the classification, select the primary methodology:

| Classification Pattern | Recommended Primary Template | Secondary Template |
|----------------------|---------------------------|-------------------|
| Sudden + Single/Multi tool + FDC alarm | Template 1: FDC Alarm RCA | Template 3: Yield Excursion RCA |
| Gradual + All/Multi tool + Metrology drift | Template 2: Process Drift RCA | Template 5: Chamber Matching RCA |
| Sudden + Yield drop + Test fail | Template 3: Yield Excursion RCA | Template 1: FDC Alarm RCA |
| Q-time overrun + Flow delay | Template 4: Q-time Violation RCA | Template 2: Process Drift RCA |
| Chamber delta + Qual fail | Template 5: Chamber Matching RCA | Template 1: FDC Alarm RCA |
| Unclear / Mixed symptoms | Proceed to Phase 2 (Data Landscape Mapping) | — |

If a clear template match emerges, transition to that template and continue analysis there.
If the problem remains unclassified after Phase 1, proceed to Phase 2.

### 2. Data Landscape Mapping
Identify all available data sources and their relevance to the problem:

| Data Source | Available? | Relevance | Access Method | Data Latency |
|------------|-----------|-----------|---------------|--------------|
| FDC (Fault Detection and Classification) | [Y/N] | [High/Med/Low] | [system_name] | [real-time/hourly/daily] |
| SPC (Statistical Process Control) | [Y/N] | [High/Med/Low] | [system_name] | [real-time/hourly/daily] |
| Inline metrology (CD, thickness, etc.) | [Y/N] | [High/Med/Low] | [system_name] | [per lot / batch] |
| Test yield data (wafer probe / final test) | [Y/N] | [High/Med/Low] | [system_name] | [daily/weekly] |
| Defect inspection (KLA, AMI) | [Y/N] | [High/Med/Low] | [system_name] | [per lot] |
| Equipment event logs | [Y/N] | [High/Med/Low] | [system_name] | [real-time] |
| PM and maintenance records | [Y/N] | [High/Med/Low] | [system_name] | [manual entry] |
| MES (Manufacturing Execution System) lot history | [Y/N] | [High/Med/Low] | [system_name] | [per lot] |
| Material lot tracking | [Y/N] | [High/Med/Low] | [system_name] | [per lot] |
| Environmental monitoring | [Y/N] | [High/Med/Low] | [system_name] | [hourly] |
| APC (Run-to-Run) controller data | [Y/N] | [High/Med/Low] | [system_name] | [per lot] |
| AMHS (transport) status | [Y/N] | [High/Med/Low] | [system_name] | [real-time] |

For each available data source:
- Confirm data accessibility and coverage for the relevant time period.
- Note any data quality issues: Missing records, timestamp misalignment, unit inconsistencies.
- Prioritize data sources by expected information value for the problem at hand.

### 3. Exploratory Analysis
Perform broad-spectrum exploratory analysis to generate hypotheses:

- **Time series overview**: Plot the primary symptom metric over time. Mark all known events (PMs, recipe changes, material changes, facility events).
- **Tool disaggregation**: Break down the symptom by tool and by chamber. Identify any tool-specific patterns.
- **Product disaggregation**: Break down by product, layer, and recipe. Identify any product-specific patterns.
- **Correlation scan**: Compute correlations between the symptom metric and all available inline metrics, FDC sensors, and environmental parameters. Flag the top correlations for deeper investigation.
- **Event coincidence scan**: Check for any equipment, maintenance, material, or operational events that coincide with the symptom onset or major changes.
- **Historical analog search**: Query historical records for past events with similar symptom profiles. Review root causes and corrective actions from those events.

### 4. Hypothesis Generation and Prioritization
Based on exploratory analysis, generate a ranked list of hypotheses:

| Priority | Hypothesis | Supporting Evidence | Contradicting Evidence | Next Validation Step |
|----------|-----------|-------------------|----------------------|---------------------|
| 1 | [Hypothesis 1] | [Evidence] | [Evidence or None] | [Action] |
| 2 | [Hypothesis 2] | [Evidence] | [Evidence or None] | [Action] |
| 3 | [Hypothesis 3] | [Evidence] | [Evidence or None] | [Action] |

Prioritize hypotheses by:
- Strength of supporting evidence.
- Plausibility of the physical mechanism.
- Testability with available data.
- Potential impact if confirmed.

### 5. Targeted Analysis (Template Selection)
For the top-ranked hypothesis, select the most appropriate specific template:
- If the hypothesis points to an FDC-related issue -> Use Template 1.
- If the hypothesis points to a process drift -> Use Template 2.
- If the hypothesis points to a yield issue -> Use Template 3.
- If the hypothesis points to a flow/logistics issue -> Use Template 4.
- If the hypothesis points to a chamber hardware issue -> Use Template 5.

Execute the relevant template steps for hypothesis validation.

### 6. Synthesis and Reporting
If no specific template provides a definitive answer, synthesize findings using the Integrated 5-Phase Framework from `rca-methodology-framework.md`:

- **Phase 1 — Problem Definition**: Precise problem statement with quantified impact.
- **Phase 2 — Data Collection**: All data gathered, gaps identified.
- **Phase 3 — Hypothesis Generation**: All plausible hypotheses with evidence.
- **Phase 4 — Hypothesis Testing**: Test results for each hypothesis.
- **Phase 5 — Conclusion and Action**: Best-supported root cause with confidence level and recommendations.

Include a clear statement of:
- Most probable root cause with confidence level.
- Key evidence supporting the conclusion.
- Remaining uncertainties and data gaps.
- Recommended next steps, including any additional data collection needed.
```

---

## Appendix A: Prompt Construction Guidelines

When adapting any template to a specific RCA task, follow these construction guidelines to ensure the prompt is complete, actionable, and domain-appropriate.

### A.1 Problem Statement Construction

Always begin with a clear, specific problem statement that includes:
- **What** is wrong (specific metric, threshold violation, or observed symptom).
- **Where** it is occurring (tool, chamber, product, process step).
- **When** it started and the current time window of concern.
- **How much** impact (magnitude of deviation, business consequence).

Example of a well-constructed problem statement:
> "T^2 alarm on ETCH_03 Chamber B during Via Etch on Product X300 at 2024-01-15 08:32. T^2 = 47.3 vs. control limit of 25.0. Top contributing sensors: Bias Voltage (32%), Chamber Pressure (21%), RF Forward Power (18%). Inline CD measurement on subsequent lots shows +8nm shift vs. target. 3 lots at risk."

### A.2 Data Source Specification

For each template invocation, explicitly enumerate:
- Available data sources with system names and access paths.
- Data coverage: Time range, granularity, completeness.
- Known data quality issues: Missing fields, stale data, unit mismatches.
- Data latency: Real-time, near-real-time, or batch-updated.

### A.3 Output Format Specification

Define the expected output structure:
- Executive summary (2-3 sentences for management).
- Detailed analysis per template step.
- Causal chain narrative with evidence links.
- Confidence assessment with justification.
- Recommendation table with owner, timeline, and success criteria.
- Appendix: Supporting data tables, plots, and references.

### A.4 Domain-Specific Constraints

Include any constraints that affect the analysis:
- **Safety**: Actions that require safety clearance or lockout/tagout.
- **Quality**: Lots that must be held pending disposition.
- **Customer**: Customer notification requirements or contractual obligations.
- **Regulatory**: Compliance requirements for traceability or documentation.
- **Operational**: Fab schedule constraints, hot lot priorities, or planned downtime.

### A.5 Confidence Level Requirements

Define the threshold confidence level required for specific actions:

| Confidence Level | Permitted Actions |
|-----------------|-------------------|
| CONFIRMED | Tool shutdown, lot scrap, customer notification, unscheduled PM |
| LIKELY | Lot hold/quarantine, increased inspection, targeted maintenance, recipe adjustment |
| POSSIBLE | Enhanced monitoring, data collection plan, experiment design |
| INCONCLUSIVE | No containment action; continue monitoring; escalate for additional data/resources |

### A.6 Escalation Triggers

Define conditions that require escalation beyond the analysis team:
- Yield impact exceeding a defined threshold (e.g., >2% yield loss).
- Customer-facing product at risk.
- Safety or environmental hazard suspected.
- Root cause remains inconclusive after defined analysis period (e.g., 24 hours).
- Corrective action fails to resolve the issue within defined verification period.

---

## Appendix B: Quick Reference — Template Selection Decision Tree

```
START: What is the primary symptom?
|
|-- FDC alarm fired (T^2 or SPE exceeded)
|   |-- Single/multivariate alarm -> Template 1: FDC Alarm RCA
|
|-- Parameter trending out of control (SPC trend/drift)
|   |-- Sustained directional shift -> Template 2: Process Drift RCA
|
|-- Yield dropped below baseline
|   |-- Sudden drop or gradual erosion -> Template 3: Yield Excursion RCA
|
|-- Lots exceeded maximum queue time
|   |-- Q-time violation between process steps -> Template 4: Q-time Violation RCA
|
|-- Chambers show different process outputs
|   |-- Qualification failure or SPC split -> Template 5: Chamber Matching RCA
|
|-- Unclear symptoms / cannot classify
|   |-- Mixed or ambiguous indicators -> Template 6: General-Purpose RCA
|
|-- Multiple simultaneous symptoms
    |-- Start with Template 6 for classification, then branch to specific templates
```

---

## Appendix C: Glossary of Placeholder Variables

| Placeholder | Description | Example Values |
|-------------|-------------|----------------|
| `[equipment_id]` | Equipment identifier | `ETCH_03`, `CVD_12`, `LITH_07` |
| `[chamber_A]`, `[chamber_B]` | Chamber identifiers | `ChA`, `ChB`, `Ch1`, `Ch2` |
| `[product_type]` | Product or device identifier | `X300`, `Y500`, `Z1000` |
| `[process_step]` | Process step name | `Via Etch`, `Gate Oxide`, `Metal CMP` |
| `[timestamp]` | Event timestamp | `2024-01-15 08:32:00` |
| `[alarm_type]` | FDC alarm classification | `T2_Overload`, `SPE_Violation`, `Model_Misfit` |
| `[sensor_list_with_contributions]` | FDC sensor contributions | `Bias_Voltage: 32%, Pressure: 21%, RF_Power: 18%` |
| `[baseline_yield]` | Baseline yield percentage | `94.5%` |
| `[current_yield]` | Current yield percentage | `91.2%` |
| `[lookback_period]` | Historical analysis window | `30 days`, `90 days` |
| `[limit_value]` | Q-time limit | `24 hours`, `72 hours` |
| `[delta_value]` | Measured difference | `+2.3 nm`, `-1.8%` |
| `[spec_limit]` | Specification limit | `+/-3.0 nm`, `+/-2.0%` |
| `[tool_list]` | List of affected tools | `ETCH_03, ETCH_04, ETCH_07` |
| `[time_period]` | Analysis time range | `2024-01-01 to 2024-01-15` |
