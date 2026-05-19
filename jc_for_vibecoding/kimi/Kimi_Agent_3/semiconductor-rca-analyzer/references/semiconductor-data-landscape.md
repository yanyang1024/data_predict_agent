# Semiconductor Data Landscape for Root Cause Analysis

## Reference Document — Methodology & Data Taxonomy

**Version:** 1.0
**Scope:** Comprehensive classification of semiconductor manufacturing data types, their analytical logic, integration patterns, and quality assessment criteria for root cause analysis (RCA) workflows.
**Audience:** RCA analysts, yield engineers, process/integration engineers, data scientists supporting semiconductor manufacturing.

---

## Section 1: Data Taxonomy Overview

Semiconductor manufacturing generates a multi-layered data ecosystem captured across equipment, sensors, metrology systems, and test platforms. For RCA purposes, all engineering data can be classified into six top-level categories, each with distinct analytical properties, temporal characteristics, and causal relevance.

### 1.1 Hierarchical Classification

```
Semiconductor Engineering Data
├── Operational Data (Operation Logic)
│   ├── Equipment/Tool Parameters
│   │   ├── Recipe parameters (temperature setpoints, pressure setpoints, gas flows, RF power, timing)
│   │   ├── Chamber configuration (chamber ID, config version, matched pair settings)
│   │   └── Equipment state logs (idle, processing, maintenance, PM cycle counts)
│   ├── Process Sequence Data
│   │   ├── Process flow (step sequence, skip patterns, rework loops)
│   │   ├── Q-time constraints (queue time limits, elapsed time between steps)
│   │   └── Lot/wafer tracking (current location, history, hold status)
│   └── Maintenance & Qualification Data
│       ├── PM (Preventive Maintenance) records
│       ├── Qualification results (chamber matching, baseline verification)
│       └── Equipment event logs (alarms, errors, warnings, operator actions)
├── Sensor Data (Time-Series Signals)
│   ├── Process Sensor Traces (traces collected during wafer processing)
│   │   ├── Thermal (chamber temperature, heater power, susceptor temp)
│   │   ├── Gas (MFC flow rates, chamber pressure, valve positions)
│   │   ├── Plasma (RF forward/reflected power, DC bias, matching network)
│   │   ├── Mechanical (throttle valve position, susceptor lift, robot position)
│   │   └── Optical (OES/EPM signals, endpoint detection traces)
│   ├── Equipment Health Sensors (continuous monitoring)
│   │   ├── Vibration, motor current, pump status
│   │   └── Environmental (cleanroom temp/humidity, facility gases)
│   └── Sensor Data Characteristics
│       ├── High-frequency sampling (Hz to kHz range)
│       ├── Non-stationary (mean/variance shifts over time)
│       ├── Auto-correlated (temporal dependencies)
│       ├── Cross-correlated (multiple sensors interact)
│       └── Multi-step profiles (ramp, stabilize, process, purge cycles)
├── FDC Data (Fault Detection & Classification)
│   ├── Fault Detection Outputs
│   │   ├── Univariate alarms (individual sensor threshold violations)
│   │   ├── Multivariate alarms (T² statistic, SPE/Q statistic from PCA)
│   │   ├── Model-based alarms (prediction residuals, drift scores)
│   │   └── Alarm metadata (severity, confidence, triggered sensors)
│   ├── Fault Classification Outputs
│   │   ├── Fault category (equipment part, process step, unknown)
│   │   ├── Variable importance rankings (which sensors contributed most)
│   │   ├── Contribution plots (per-sensor contribution to fault score)
│   │   └── Explanation reports (SHAP values, LIME explanations, rule-based)
│   └── FDC Model Metadata
│       ├── Model type (PCA, PLS, autoencoder, one-class SVM)
│       ├── Training window and drift status
│       └── False positive/negative history
├── Metrology Data (Inline & Offline)
│   ├── Inline Metrology (measured during fab flow)
│   │   ├── Critical Dimension (CD) — line width, space, height
│   │   ├── Film Thickness — oxide, nitride, metal layers
│   │   ├── Overlay — layer-to-layer alignment accuracy
│   │   ├── Defect Inspection — particle counts, pattern defects, electrical signatures
│   │   └── Electrical Parametric — threshold voltage, leakage current, resistance
│   ├── SPC Control Chart Data
│   │   ├── Chart type (X-bar, R, I-MR, CUSUM, EWMA)
│   │   ├── Control limits (UCL, LCL, spec limits)
│   │   └── Rule violations (Western Electric rules, custom rules)
│   └── Virtual Metrology (VM)
│       ├── Predicted values from sensor-based models
│       └── Prediction confidence intervals
├── Yield & Electrical Test Data
│   ├── Wafer Sort (CP) Data
│   │   ├── Die-level pass/fail per test item
│   │   ├── Bin maps (spatial distribution of failures)
│   │   └── Test parameters (voltage, frequency, temperature conditions)
│   ├── Final Test (FT) Data
│   │   ├── Package-level test results
│   │   └── Burn-in / reliability test data
│   └── Yield Analytics
│       ├── Yield loss pareto (which tests contribute most to yield loss)
│       ├── Defect density trends
│       └── Yield correlation to process parameters
└── Q-time & WIP Data
    ├── Q-time Monitoring
    │   ├── Q-time limits per process step (specifications)
    │   ├── Actual elapsed times (from MES/track systems)
    │   ├── Q-time violation flags (over-limit events)
    │   └── Accumulated Q-time (total time in queue across steps)
    ├── WIP (Work In Process) Data
    │   ├── WIP levels per process step
    │   ├── Lot aging reports
    │   └── Priority/hot lot status
    └── Temporal Pattern Data
        ├── Time-of-day/day-of-week patterns
        ├── Shift-change effects
        └── Seasonal/campaign patterns
```

### 1.2 Category Definitions & Temporal Profiles

| Data Category | Primary Source | Typical Volume | Temporal Resolution | Latency to Availability |
|---|---|---|---|---|
| **Operational Data** | MES, EAP, equipment logs | Medium (10^3-10^4 records/day) | Event-based (seconds to minutes) | Near-real-time to minutes |
| **Sensor Data** | Equipment sensors, DCS | Very high (10^6-10^9 samples/day) | Milliseconds to seconds | Seconds to minutes |
| **FDC Data** | FDC platform (computed from sensor data) | Medium (10^2-10^3 alarms/day) | Per-process-cycle summary | Minutes to hours |
| **Metrology Data** | Metrology tools (CD-SEM, OVL, thickness) | Medium (10^3-10^4 measurements/day) | Per-measurement event | Hours to days |
| **Yield/Test Data** | ATE (Automated Test Equipment) | High (10^6-10^9 die results/day) | Per-die test (~ms per die) | Days to weeks |
| **Q-time/WIP Data** | MES, dispatching systems | Medium (10^3-10^4 lot records/day) | Event-based (lot moves) | Near-real-time |

### 1.3 RCA Information Value by Category

| Data Category | Causal Proximity | RCA Function | Typical Use Frequency |
|---|---|---|---|
| **Operational Data** | Direct cause | Identify recipe changes, tool events, PM triggers | Every investigation |
| **Sensor Data** | Direct cause / Strong indicator | Detect process drift, identify deviation signatures | High — core evidence |
| **FDC Data** | Aggregated indicator | Prioritize which tools/chambers to investigate | High — first filter |
| **Metrology Data** | Effect measurement | Quantify process output shifts, confirm causality | Every investigation |
| **Yield/Test Data** | Ultimate effect | Define problem magnitude, spatial characterization | Problem definition phase |
| **Q-time/WIP Data** | Contributing / Confounding factor | Identify queue-related degradation, temporal bias | Supporting analysis |

---

## Section 2: Per-Data-Type Analysis Logic

### 2.1 Equipment Parameter Analysis Logic

#### 2.1.1 RCA Relevance

Equipment parameters encode the intended process conditions. Any deviation between specified (recipe) and actual (measured) parameters represents a direct process change. Parameter analysis is typically the first investigative layer because it provides the most direct causal evidence.

#### 2.1.2 Key Analytical Dimensions

| Dimension | Analysis Focus | RCA Question Answered |
|---|---|---|
| **Recipe version changes** | Track recipe parameter revisions over time | Did a recipe change coincide with the yield excursion? |
| **Setpoint vs. actual** | Compare commanded values to measured feedback | Is the equipment failing to achieve its target? |
| **Chamber-to-chamber matching** | Cross-chamber parameter consistency | Is the affected chamber running differently from matched peers? |
| **PM-to-PM drift** | Parameter trends across PM cycles | Is there progressive degradation between maintenance events? |
| **Operator/shift variation** | Parameter differences by operator or shift | Is human variation contributing to process spread? |

#### 2.1.3 Common Patterns Indicating Root Causes

| Pattern Observed | Likely Root Cause Category | Follow-up Actions |
|---|---|---|
| Step timing increased by >5% | Gas delivery problem, exhaust restriction, or endpoint drift | Inspect MFC, check throttle valve, verify OES endpoint |
| Pressure setpoint changed without CR | Unauthorized recipe modification, software update | Review recipe change control, audit trail |
| Temperature actual consistently below setpoint | Heater degradation, thermocouple drift, power supply issue | Check heater resistance, calibrate thermocouple |
| RF reflected power trending upward | Matching network drift, chamber coating change, electrode wear | Inspect matching network, check chamber condition |
| Gas flow actual oscillating around setpoint | MFC valve instability, pressure coupling, controller tuning | Verify MFC calibration, check upstream pressure |
| Parameter shift after specific PM | PM procedure error, part replacement with wrong version, reassembly issue | Review PM checklist, compare to previous PM records |

#### 2.1.4 Correlation Logic

```
Equipment Parameter Changes
         |
         v
  [Parameter drift detected]
         |
         +---> Correlate to FDC alarm triggers (did FDC catch the drift?)
         +---> Correlate to sensor trace deviations (what did sensors show?)
         +---> Correlate to inline metrology shifts (how did output change?)
         +---> Correlate to yield impact (magnitude and spatial signature)
         +---> Correlate to PM/qualification events (what preceded the change?)
```

---

### 2.2 Sensor Trace Analysis Logic

#### 2.2.1 RCA Relevance

Sensor traces capture the actual process dynamics in real time. Unlike discrete parameter summaries, traces reveal transient behaviors, stability characteristics, and subtle drift patterns invisible to parameter logs. They are the richest source of causal evidence in semiconductor RCA.

#### 2.2.2 Key Analytical Dimensions

| Dimension | Analysis Focus | RCA Question Answered |
|---|---|---|
| **Trace shape/profile** | Compare full trace morphology (good vs. bad lots) | Is the process dynamics signature different? |
| **Steady-state stability** | Variance and noise characteristics during the stable phase | Is the process exhibiting increased variability? |
| **Transient behavior** | Ramp rates, overshoot, settling time | Are the transitions between phases degrading? |
| **Cross-sensor relationships** | Correlation patterns between multiple sensors | Are the interacting process variables decoupling? |
| **Inter-wafer trends** | Trace evolution across consecutive wafers | Is there a progressive drift (e.g., seasoning effect)? |

#### 2.2.3 Common Patterns Indicating Root Causes

| Pattern | Affected Sensor(s) | Likely Root Cause | Verification Path |
|---|---|---|---|
| Slow rise time at process start | Temperature, pressure | Heater degradation, gas line restriction | Compare to historical baseline traces |
| Periodic oscillation (1-10 Hz) | Pressure, gas flow | Controller instability, valve stiction | Check PID tuning, inspect valve |
| Gradual upward/downward slope | RF power, DC bias | Electrode consumption, chamber coating buildup | Correlate with PM cycle count |
| Abrupt step change mid-trace | Any sensor | Equipment event (alarm, gas switch, mode change) | Check equipment event log for timestamp alignment |
| Increased trace-to-trace variance | All sensors | Loose connection, intermittent electrical fault | Check cable connections, grounding |
| Endpoint detection delayed | OES/EPM trace | Chamber condition change, film property shift | Compare to thickness/endpoint reference |
| Dual-mode distribution (bimodal) | Temperature, pressure | Two distinct process states (e.g., with/without seasoning) | Split by wafer sequence number |
| Spike/noise burst | Single sensor | Sensor electrical interference, connector issue | Swap sensor cable, check shielding |

#### 2.2.4 Correlation Logic

```
Sensor Trace Anomalies
         |
         v
  [Shape/instability/drift detected]
         |
         +---> Map to specific process step (which step trace changed?)
         +---> Map to specific chamber hardware (which sensor cluster?)
         +---> Map to equipment parameter deltas (did setpoints change?)
         +---> Map to FDC model triggers (which statistics exceeded limits?)
         +---> Map to metrology spatial signature (center vs. edge pattern?)
         +---> Map to yield bin map pattern (correlates spatially?)
```

#### 2.2.5 Trace Comparison Methodology

| Comparison Type | Description | When to Use |
|---|---|---|
| **Golden trace overlay** | Overlay suspect trace on known-good historical trace | Quick visual assessment of deviation magnitude |
| **Statistical profile comparison** | Mean, variance, slope, integral features compared via t-test / F-test | Quantitative significance testing |
| **Shape similarity metrics** | DTW (Dynamic Time Warping), correlation distance, area-between-curves | Subtle shape changes not captured by summary stats |
| **Frequency domain analysis** | FFT / wavelet analysis of trace residuals | Detecting periodic instabilities, noise characterization |
| **PCA on trace ensemble** | Reduce dimensionality of trace sets, compare in score space | Multi-variate trace pattern changes |

---

### 2.3 FDC Alarm Interpretation Logic

#### 2.3.1 RCA Relevance

FDC systems provide pre-filtered anomaly detection, reducing billions of sensor samples to actionable alarm events. However, FDC outputs are **indicators**, not root causes. The analytical value lies in interpreting alarm patterns, not treating alarms as conclusions.

#### 2.3.2 Key Analytical Dimensions

| Dimension | Analysis Focus | RCA Question Answered |
|---|---|---|
| **Alarm frequency trend** | Alarms per day/week trending up or down | Is the process becoming less stable over time? |
| **Alarm type distribution** | Which fault categories dominate | Which equipment subsystems are most problematic? |
| **Alarm-to-alarm correlation** | Co-occurrence of multiple alarm types | Are multiple symptoms from a single root cause? |
| **Alarm suppression effectiveness** | False alarm rate, nuisance alarm patterns | Is the FDC model still relevant, or has it drifted? |
| **Post-alarm process behavior** | Process recovery patterns after alarm events | Does the process self-correct, or does it require intervention? |

#### 2.3.3 Alarm Pattern Interpretation

| Alarm Pattern | Interpretation | Recommended Action |
|---|---|---|
| Univariate threshold alarm on single sensor | Isolated sensor issue or genuine single-parameter excursion | Verify sensor health; if genuine, investigate parameter control |
| Multivariate T² alarm without SPE alarm | Process moved to a new operating region (known correlation structure) | Check recipe parameters, chamber matching status |
| Multivariate SPE alarm without T² alarm | Unusual correlation breakdown between variables (new failure mode) | High priority — potential new failure mode not in training data |
| Both T² and SPE alarms simultaneously | Process operating outside normal space with broken correlations | Critical — likely equipment malfunction |
| Repeating alarms at same process step | Systematic issue tied to that step's recipe or hardware | Focus investigation on that specific step |
| Alarms only on specific chamber(s) | Chamber-specific hardware issue | Compare chamber configurations, maintenance histories |
| Alarms only on first wafer after PM | PM recovery / seasoning issue | Extend seasoning recipe, review PM procedures |
| Gradual increase in alarm frequency before excursion | Process drift not caught by SPC | Review FDC model sensitivity; tighten thresholds |

#### 2.3.4 Contribution Plot Analysis

When FDC triggers, contribution plots rank sensors by their contribution to the fault statistic:

| Contribution Pattern | Meaning | Root Cause Direction |
|---|---|---|
| Single sensor dominates | Clear single-parameter excursion | Focus on that sensor's hardware and control loop |
| Multiple sensors in same subsystem cluster | Subsystem-level issue (e.g., gas delivery) | Inspect shared components: manifold, supply line, controller |
| Sensors from multiple subsystems | Complex process shift or recipe change | Compare recipe parameters to baseline |
| All sensors contribute equally | Global process disturbance or model issue | Check facility conditions, recipe version, model validity |

#### 2.3.5 Correlation Logic

```
FDC Alarm Events
         |
         v
  [Alarm triggered — univariate, multivariate, or model-based]
         |
         +---> Retrieve contribution plot — which sensors drove the alarm?
         +---> Retrieve underlying sensor traces for contributing sensors
         +---> Check equipment parameter changes at alarm time
         +---> Check if alarm correlates with known PM/qualification schedule
         +---> Correlate to inline metrology measurements on alarmed wafers
         +---> Cross-reference to yield data (if inline metrology shifted)
         +---> Review FDC model metadata (is model current? training window valid?)
```

---

### 2.4 Q-time Violation Analysis Logic

#### 2.4.1 RCA Relevance

Q-time violations are a frequently overlooked root cause category. Many semiconductor processes are sensitive to elapsed time between steps (oxidation, contamination absorption, moisture uptake, photoresist degradation). Q-time analysis identifies time-dependent degradation mechanisms.

#### 2.4.2 Key Analytical Dimensions

| Dimension | Analysis Focus | RCA Question Answered |
|---|---|---|
| **Violation rate by step-pair** | Which Q-time constraints are most frequently violated | Where is the process flow bottlenecked? |
| **Elapsed time vs. parametric drift** | Correlation between actual elapsed time and inline metrology shifts | Is extended Q-time causing measurable process degradation? |
| **Violation-to-yield correlation** | Do lots with Q-time violations show worse yield? | Is the Q-time limit correctly specified? |
| **WIP profile at violation** | WIP levels and queue composition during violations | Is factory loading causing the violations? |

#### 2.4.3 Common Patterns

| Pattern | Mechanism | Indicators |
|---|---|---|
| Violations concentrated at specific step-pair | Localized bottleneck (tool downtime, capacity constraint) | Check tool availability logs, WIP profile |
| Violations correlate with specific metrology shift | Time-sensitive process degradation | Film thickness change, increased particles, CD shift |
| Violations during specific shifts only | Dispatching/operator practice differences | Compare shift SOP adherence, hot lot handling |
| Seasonal/cyclical violation patterns | Campaign-based loading, customer mix changes | Correlate to factory output plans, product mix |
| Long elapsed time but no parametric shift | Q-time limit may be overly conservative | Propose limit extension based on data evidence |
| Short elapsed time but parametric shift | Q-time limit may be too loose, or other cause dominates | Do not assume causality; investigate other factors |

#### 2.4.4 Correlation Logic

```
Q-time Violations
         |
         v
  [Violation detected for lot between Step A and Step B]
         |
         +---> Check inline metrology at Step B (did the process output shift?)
         +---> Check if violation correlates with yield loss on that lot
         +---> Check WIP level at Step A during violation period (bottleneck?)
         +---> Check if affected lots share equipment at Step A (common tool?)
         +---> Check for concurrent equipment downtime at Step B destination
         +---> Compare violation lots to non-violation lots (matched pair analysis)
```

---

### 2.5 Inline Metrology SPC Analysis Logic

#### 2.5.1 RCA Relevance

Inline metrology provides the earliest measurable evidence of process output shifts. SPC (Statistical Process Control) transforms individual measurements into trend indicators and alarm signals. SPC analysis bridges equipment/process causes with yield effects.

#### 2.5.2 Key Analytical Dimensions

| Dimension | Analysis Focus | RCA Question Answered |
|---|---|---|
| **Control chart rule violations** | Which Western Electric or custom rules triggered | What type of process change occurred (shift, trend, cycle)? |
| **Violation spatial signature** | Within-wafer pattern (center, edge, left-right, radial) | Which chamber hardware component is suspect? |
| **Violation temporal clustering** | When did violations start, how long did they persist | Align to equipment events, PM schedules, recipe changes |
| **Magnitude of excursion** | How far from target, how severe vs. historical | Is this a minor drift or a major process upset? |
| **Single vs. multi-parameter shift** | One metrology parameter or several simultaneously | Is the root cause isolated or systemic? |

#### 2.5.3 SPC Rule Violation Patterns

| Rule Violation | Pattern Description | Likely Root Cause Interpretation |
|---|---|---|
| **Rule 1**: Point beyond 3σ | Single extreme measurement | Sudden process upset, measurement error, or rare event |
| **Rule 2**: 9 points same side of center | Sustained process shift | Recipe change, chamber hardware change, raw material lot change |
| **Rule 3**: 6 points steadily increasing/decreasing | Process trend | Progressive wear, consumable depletion, seasoning buildup |
| **Rule 4**: 14 points alternating up/down | Oscillation / over-control | Controller instability, operator over-adjustment |
| **Rule 5**: 2 of 3 points beyond 2σ | Early warning of shift | Developing issue, often precedes Rule 1 or Rule 2 |
| **Rule 6**: 4 of 5 points beyond 1σ | Reduced process stability | Increased variability source (gas, power, mechanical) |
| **Rule 7**: 15 points within 1σ | Unnatural lack of variability | Measurement system issue (insensitive gauge, data clipping) |
| **Rule 8**: 8 points beyond 1σ (both sides) | Bimodal process | Two process states mixing (mixed chambers, mixed recipes, before/after PM) |

#### 2.5.4 Within-Wafer Spatial Pattern Interpretation

| Spatial Pattern | Affected Region | Likely Chamber Hardware Component |
|---|---|---|
| Center-high, edge-low (or reverse) | Radial gradient | Gas flow uniformity, showerhead condition, susceptor temperature uniformity |
| Left-right asymmetry | Half-wafer gradient | Gas inlet orientation, asymmetric pumping, chamber alignment |
| Donut / ring pattern | Annular region | Edge ring condition, focus ring wear, chamber wall proximity effect |
| Random / no pattern | No spatial structure | Non-chamber cause (previous process step, material, random noise) |
| Repeating die pattern | Die-level structure | Lithography / etch interaction, mask issue, stepper grid error |
| Gradual radial gradient | Full radial range | Heater zone imbalance, gas distribution drift, pressure uniformity |

#### 2.5.5 Correlation Logic

```
Inline Metrology SPC Violation
         |
         v
  [Rule violation on metrology parameter X at step Y]
         |
         +---> Identify spatial signature (within-wafer pattern)
         +---> Identify temporal window (when did violations begin?)
         +---> Map to specific chamber (which chamber processed the violating wafers?)
         +---> Retrieve sensor traces from that chamber in the violation window
         +---> Check FDC alarms from that chamber in the violation window
         +---> Check equipment parameters / recipe changes in the violation window
         +---> Check PM / qualification history for that chamber
         +---> Correlate to yield bin maps (same spatial pattern?)
         +---> Back-propagate to upstream steps (is the cause at step Y or earlier?)
```

---

### 2.6 Yield Loss Correlation Logic

#### 2.6.1 RCA Relevance

Yield data represents the ultimate business impact. All upstream RCA activity converges on explaining yield loss. Yield analysis defines the **problem magnitude** (how much loss?), **problem scope** (which tests, which dies?), and **problem timing** (when did it start?).

#### 2.6.2 Key Analytical Dimensions

| Dimension | Analysis Focus | RCA Question Answered |
|---|---|---|
| **Bin map pattern** | Spatial distribution of failing dies on wafer | Is the failure spatially correlated (chamber signature) or random (process variation)? |
| **Yield loss pareto** | Which test bins contribute most to total loss | Which electrical parameters are affected? |
| **Yield trend timing** | When did yield drop begin, when did it recover | Align to equipment events, material changes, recipe changes |
| **Test-to-test correlation** | Which tests fail together | What circuit blocks or process steps are implicated? |
| **Die-size / design dependency** | Yield differences by product, reticle, or layer | Is the issue design-sensitive or process-generic? |

#### 2.6.3 Bin Map Pattern Interpretation

| Bin Map Pattern | Interpretation | Likely Process Root Cause Direction |
|---|---|---|
| **Center cluster** | Radial process issue | Chamber gas flow, temperature uniformity, deposition uniformity |
| **Edge ring** | Edge-specific process issue | Edge exclusion, focus ring condition, bevel etch, chamber wall effect |
| **Left-right split** | Asymmetric process | Gas flow asymmetry, chamber alignment, single-sided hardware issue |
| **Repeating reticle pattern** | Lithography / mask related | Stepper/scanner issue, mask defect, overlay error |
| **Scribe line concentration** | Scribe-specific issue | Scribe test structure sensitivity, scribe process variation |
| **Random distribution** | Non-spatial process variation | Parametric drift, material variation, random defectivity |
| **Streaks / comet patterns** | Contamination or handling | Particle event, robot handling damage, transport contamination |
| **Gradual radial gradient** | Uniformity degradation | Process uniformity drift (deposition, etch, CMP) |

#### 2.6.4 Test Bin-to-Process Mapping

| Yield Test Category | Electrical Parameter | Implicated Process Steps |
|---|---|---|
| **Contact resistance** | Via/chain resistance | Contact etch, barrier deposition, W-plug CMP, litho overlay |
| **Gate leakage** | I<sub>g</sub>, I<sub>off</sub> | Gate oxide growth, poly deposition, spacer formation, RTA |
| **Drive current** | I<sub>d,sat</sub>, I<sub>d,lin</sub> | Channel implant, gate oxide, poly CD, spacer width, S/D implant |
| **Threshold voltage** | V<sub>th</sub> | Channel implant, gate oxide thickness, poly CD, halo implant |
| **Metal resistance** | R<sub>sheet</sub>, via resistance | Metal deposition (PVD/CVD), CMP, etch profile, barrier integrity |
| **Capacitance** | C<sub>ox</sub>, interconnect C | Dielectric thickness, dielectric constant (porosity), line spacing |
| **SRAM stability** | Static noise margin | Mismatch-sensitive: V<sub>th</sub> variation, CD variation, local loading |

#### 2.6.5 Correlation Logic

```
Yield Loss Detected
         |
         v
  [Bin map pattern + Pareto of failing tests]
         |
         +---> Characterize spatial signature (random vs. patterned vs. clustered)
         +---> Identify primary failing test(s) — what electrical parameter?
         +---> Map electrical parameter to process step(s)
         +---> Identify process step chambers that processed affected wafers
         +---> Check inline metrology at those steps (SPC violations?)
         +---> Check sensor traces from those chambers in the yield-loss window
         +---> Check FDC alarms from those chambers
         +---> Check equipment parameters / recipe changes
         +---> Check Q-time violations on affected lots
         +---> Narrow to common equipment + common time window
         +---> Formulate hypothesis: [specific equipment event] caused 
         |     [specific process shift] which caused [specific yield loss]
         +---> Validate hypothesis with matched-pair or DOE confirmation
```

---

## Section 3: Data Integration Logic

Effective RCA requires combining multiple data types into a coherent causal narrative. Data integration follows four logical dimensions: temporal, spatial, causal, and confound-aware.

### 3.1 Temporal Alignment

All semiconductor manufacturing data must be aligned to a common temporal reference frame. Different data sources use different timestamp conventions.

| Data Source | Timestamp Type | Alignment Key | Latency Consideration |
|---|---|---|---|
| Equipment parameters | Event timestamp (process start/end) | Lot ID + step sequence | Near-real-time |
| Sensor traces | Sample timestamp (high-frequency clock) | Trace start time aligned to process start | Seconds |
| FDC alarms | Alarm generation timestamp | Aligned to process cycle end | Minutes |
| Inline metrology | Measurement timestamp | Lot ID + measurement step | Hours to days |
| Yield data | Test timestamp (wafer sort / final test) | Lot ID + wafer ID | Days to weeks |
| Q-time data | Lot move timestamps (from/to steps) | Lot ID + step pair | Near-real-time |

**Temporal Alignment Principles:**

1. **Forward tracing**: Start from a known equipment event and trace forward to find the first affected metrology and yield measurements.
2. **Backward tracing**: Start from a yield excursion and trace backward to find the most recent equipment event that could explain it.
3. **Window overlap analysis**: For a given time window, collect all data types and identify coincident events.

### 3.2 Spatial Alignment

Spatial alignment connects data at different granularity levels.

| Data Granularity | Identifier | Spatial Alignment Logic |
|---|---|---|
| **Fab-level** | Factory + date range | Factory-wide events (facility, materials, software) |
| **Area/Bay-level** | Process area + date range | Shared resources (bulk gas, exhaust, power) |
| **Tool-level** | Tool ID + date range | Tool-specific events (PM, recipe, hardware) |
| **Chamber-level** | Chamber ID + date range | Chamber-specific variation (matched pair comparison) |
| **Lot-level** | Lot ID | All data for a specific lot across its process flow |
| **Wafer-level** | Wafer ID (within lot) | Within-wafer spatial patterns, wafer-specific handling |
| **Die-level** | Die X,Y coordinates | Spatial bin maps, within-wafer pattern correlation |

**Spatial Aggregation Rules for RCA:**

- **Yield-to-chamber mapping**: Use tracking history to identify which chamber processed each wafer; aggregate yield by chamber to find chamber-specific signatures.
- **Metrology-to-sensor mapping**: Use lot ID and step sequence to retrieve sensor traces from the same process run.
- **FDC-to-yield mapping**: Link FDC alarm events to the specific wafers processed during the alarmed cycle.
- **Cross-chamber comparison**: Compare data across matched chambers to isolate chamber-specific from process-wide effects.

### 3.3 Causal Linking

Causal linking constructs evidence chains connecting equipment events through process changes to yield impact.

#### Standard Causal Chain Template

```
[EQUIPMENT EVENT]  -->  [PROCESS CHANGE]  -->  [METROLOGY SHIFT]  -->  [YIELD IMPACT]

Recipe change      -->  Parameter drift     -->  CD out-of-spec      -->  Ioff fail
PM completed       -->  Seasoning effect    -->  Thickness shift     -->  Cshift fail
MFC degradation    -->  Gas instability     -->  Film property shift -->  Via resistance
RF matching drift  -->  Plasma non-uniform  -->  Etch profile change -->  Contact fail
```

#### Causal Link Validation Criteria

| Criterion | Description | Evidence Required |
|---|---|---|
| **Temporal precedence** | Cause must occur before effect | Event timestamp < effect timestamp |
| **Covariation** | Cause and effect must co-vary | Effect present when cause present; absent when cause absent |
| **Non-spuriousness** | No alternative explanation confounds the link | Ruled out competing hypotheses via matched-pair or DOE |
| **Mechanistic plausibility** | Physical mechanism links cause to effect | Domain knowledge confirms the causal pathway is physically reasonable |
| **Dose-response** | Stronger cause produces stronger effect | Magnitude of parameter change correlates to magnitude of yield loss |

### 3.4 Confounding Identification

Not all correlations are causal. RCA must actively identify and control for confounding factors.

| Confounding Type | Description | Example | Mitigation Strategy |
|---|---|---|---|
| **Shared cause** | Two effects share a common root cause, appearing correlated | Both CD and thickness shift due to same temperature change | Analyze each effect's independent sensitivity |
| **Cascading effect** | One root cause triggers secondary changes, creating multiple symptoms | Gas flow issue causes pressure alarm, then endpoint delay, then thickness shift | Trace the symptom chain to the earliest anomaly |
| **Coincidental correlation** | Two events occur simultaneously by chance | Yield excursion coincides with recipe change, but root cause is upstream contamination | Hold the recipe change; verify the excursion persists or resolves |
| **Temporal confounding** | Seasonal, shift, or campaign patterns create false associations | All bad lots processed on night shift (because most production is night shift) | Normalize by proportion, use rate-based metrics |
| **Survivorship bias** | Only certain data is available for analysis | Only metrology-measured wafers have data; skip-pattern wafers are excluded | Track skip patterns explicitly; account for sampling plans |
| **Chamber aliasing** | Multiple chambers produce similar symptoms | All chambers drift together due to consumable lot change | Distinguish chamber-specific from consumable-specific effects |
| **Product mix confounding** | Different products have different yield baselines | Excursion appears as yield drop, but is actually higher mix of low-yield product | Stratify analysis by product; use normalized yield metrics |

---

## Section 4: Data Quality & Trust Assessment

Data quality directly determines RCA reliability. Before drawing conclusions, the analyst must assess the trustworthiness of each data source used in the investigation.

### 4.1 Missing Data Impact Assessment

| Data Type | Common Missing Data Patterns | Impact on RCA | Mitigation |
|---|---|---|---|
| **Sensor traces** | Dropped packets, communication errors, trace truncated | Incomplete process picture; may miss critical transient | Flag trace quality; use backup sensors; interpolate if appropriate |
| **Inline metrology** | Sampling plan (not all wafers measured), tool downtime, queue overflow | Limited statistical power; may miss excursions | Account for sampling rate; verify measurement coverage is representative |
| **Equipment parameters** | Log gaps, parameter not logged (unmonitored setpoint) | Unexplained process changes | Identify critical unmonitored parameters; request logging |
| **FDC outputs** | Model not deployed on specific chamber, model offline | Undetected process excursions | Track FDC coverage; flag chambers without FDC protection |
| **Yield data** | Test program error, wafer breakage, incomplete sort | Biased yield estimate | Exclude incomplete lots from analysis; note exclusion rationale |
| **Q-time data** | MES communication lag, manual lot moves not logged | Inaccurate elapsed time calculation | Validate against actual process timestamps; flag manual moves |

### 4.2 Measurement System Analysis (MSA)

| MSA Aspect | Relevance to RCA | Assessment Method |
|---|---|---|
| **Gauge R&R** | Is metrology variation due to the process or the measurement tool? | Use %R&R < 30% as acceptable; < 10% preferred. High R&R masks true process shifts. |
| **Measurement bias** | Is the metrology tool reading consistently offset from true value? | Compare to reference standard; check calibration history |
| **Measurement resolution** | Is the measurement tool sensitive enough to detect relevant shifts? | Verify resolution < 1/10 of process tolerance |
| **Reproducibility** | Do different operators/tools/chambers give consistent measurements? | Track chamber-to-chamber measurement bias; operator GRR studies |
| **Stability over time** | Has the measurement tool itself drifted? | Control chart the measurement standard; track calibration results |

### 4.3 Data Freshness and Latency Effects

| Data Freshness Category | Latency | RCA Impact |
|---|---|---|
| **Real-time** (sensor data, FDC alarms, MES events) | Seconds to minutes | Enables rapid containment; essential for excursion response |
| **Near-real-time** (WIP updates, parameter summaries) | Minutes to hours | Supports daily monitoring; sufficient for most inline investigations |
| **Delayed** (inline metrology) | Hours to 1-2 days | Limits speed of detection; batch processing may delay identification |
| **Significantly delayed** (yield data, final test) | Days to weeks | Problem definition lag; often the trigger for RCA initiation |
| **Retrospective** (historical baselines, archived traces) | Days to retrieve | Essential for baseline comparison; may have retrieval latency for old data |

**Latency-Related RCA Risks:**
- **Containment delay**: Delayed yield data lets affected lots continue through downstream steps, amplifying the excursion.
- **Baseline contamination**: Delayed detection means baseline data may already include affected material.
- **Trace expiration**: Sensor trace archival policies may delete traces before RCA retrieval. Know the retention policy.

### 4.4 Sensor Calibration Status Relevance

| Calibration Aspect | Why It Matters for RCA | Verification Action |
|---|---|---|
| **Calibration due date** | Overdue sensors may produce biased readings | Check calibration schedule; flag overdue sensors |
| **Post-calibration shift** | Some sensors exhibit post-calibration adjustment | Compare pre- and post-calibration measurements on known standard |
| **Calibration standard traceability** | Is the calibration standard itself accurate? | Verify NIST-traceable standards; check standard certification |
| **In-situ vs. external calibration** | In-situ calibration may not detect drift under process conditions | Prefer process-relevant calibration methods |
| **Sensor swap events** | Swapped sensors change measurement characteristics | Track sensor serial numbers; flag swap events in analysis |

### 4.5 Data Quality Checklist for RCA Investigations

Before concluding an RCA investigation, verify:

- [ ] All relevant data sources accessed — no gaps in the investigation window
- [ ] Timestamps validated and aligned across sources (no timezone or clock-skew errors)
- [ ] Sensor/metrology calibration status verified (no overdue or post-calibration anomalies)
- [ ] Sampling plans understood (metrology coverage, test sampling, skip patterns accounted for)
- [ ] FDC model currency verified (model trained on relevant baseline, not stale)
- [ ] Confounding factors considered and ruled out; causal chain has temporal precedence
- [ ] Alternative hypotheses eliminated with evidence; conclusions supported by multiple data types

---

*This document is a living methodology reference. Update when new data types are introduced, process technologies evolve, or analytical methods are enhanced.*
