---
name: semiconductor-rca-analyzer
description: >
  Root Cause Analysis (RCA) methodology skill for semiconductor manufacturing engineering data.
  Covers equipment/tool data, sensor data, FDC (Fault Detection & Classification),
  Q-time (queue time), inline metrology, SPC/APC data. Guides agents through systematic
  causal reasoning using structured analytical frameworks: 5 Whys, Ishikawa diagrams,
  hypothesis testing, correlation-confounding analysis, temporal sequencing,
  and counterfactual validation. Use when: analyzing semiconductor fab data for
  fault diagnosis, yield loss investigation, process drift root cause identification,
  equipment anomaly investigation, or any manufacturing data RCA task.
---

# semiconductor-rca-analyzer

## Skill Overview

This skill enables an agent to perform systematic, evidence-based Root Cause Analysis on semiconductor manufacturing data. The agent applies structured analytical frameworks to trace observed failures or anomalies to their underlying root causes across equipment, process, material, metrology, and environmental dimensions.

**Trigger conditions:** Use this skill when the task involves investigating semiconductor fab anomalies, diagnosing yield loss, identifying process drift causes, analyzing equipment faults, or performing RCA on any manufacturing engineering dataset.

---

## Core Analysis Workflow

Execute RCA using this 6-step workflow. Do not skip steps. Iterate between steps as evidence warrants.

```
Step 1: Data Landscape Mapping -- Identify data types, temporal scope, granularity
Step 2: Symptom Characterization -- Quantify the problem (magnitude, frequency, time bounds, spatial distribution)
Step 3: Hypothesis Generation  -- Brainstorm potential causes using Ishikawa 6M framework adapted for semiconductor
Step 4: Evidence Evaluation    -- Test hypotheses against data (correlation, temporal precedence, mechanistic plausibility)
Step 5: Root Cause Validation  -- Confirm through counterfactual reasoning, elimination of alternatives, reproducibility
Step 6: Recommendation Formulation -- Corrective actions, preventive measures, monitoring improvements
```

**Step 1: Data Landscape Mapping**
Read all provided data. Identify each dataset's type (see Semiconductor Data Types Reference below). Map: data granularity (lot, wafer, die, recipe-run), temporal coverage (date range, sampling rate), relevant process steps and equipment IDs, and data quality (missing values, outliers, alignment issues).

**Step 2: Symptom Characterization**
Quantify the failure or anomaly precisely: affected entity count (lots, wafers, dies), time window of occurrence, magnitude of deviation versus specification or historical baseline, and spatial pattern (random, clustered, trending, drifting across tools/chambers/wafers).

**Step 3: Hypothesis Generation**
Brainstorm potential causes using the Ishikawa 6M framework adapted for semiconductor (see Pillar A). For each category, generate 2-4 specific hypotheses grounded in the observed symptom patterns. Focus on mechanisms, not vague guesses.

**Step 4: Evidence Evaluation**
Test each hypothesis against available data. For each test, state the expected data pattern if the hypothesis were true, then check actual data for that pattern. Use statistical and causal inference methods (see Pillars B and C). Document confounding variables and alternative interpretations.

**Step 5: Root Cause Validation**
Consolidate findings into a coherent causal chain. Confirm the root cause using counterfactual reasoning, elimination of alternative explanations, and reproducibility checks. The cause must have temporal precedence and mechanistic plausibility.

**Step 6: Recommendation Formulation**
Formulate specific, actionable corrective actions for immediate containment, preventive measures to eliminate recurrence, and monitoring improvements (SPC limit adjustments, FDC rule enhancements, APC recipe tuning).

---

## Semiconductor Data Types Reference

### Equipment/Tool Data
Chamber-level operational parameters: recipe settings (pressure setpoints, gas flows, RF power levels, temperature profiles), tool configuration parameters, PM (Preventive Maintenance) logs, tool events (alarms, interrupts, interlocks). **RCA relevance:** Recipe deviations, PM-induced parameter shifts, chamber-to-chamber mismatch, and tool event sequences are primary causal candidates for process excursions.

### Sensor Data
Real-time time-series data collected during wafer processing: chamber temperature, chamber pressure, gas flow rates, RF forward/reflected power, ESC voltage, helium backside cooling pressure, slit valve positions. **RCA relevance:** Non-stationary behavior, auto-correlated drift, step-change transients, and sensor saturation events provide direct evidence of process-state anomalies during fault occurrences.

### FDC Data (Fault Detection & Classification)
Two components: **Fault Detection** -- multivariate anomaly flags from MSPC, PCA, or Hotelling T-squared models that signal when a process run deviates from the nominal operating space; **Fault Classification** -- variable importance rankings and SHAP/LIME explanations from tree-based classifiers (XGBoost, Random Forest) identifying which sensor traces or derived features drove the fault flag. **RCA relevance:** Detection timestamps establish temporal bounds; classification outputs rank candidate variables and guide hypothesis generation toward the most influential process parameters.

### Q-Time Data (Queue Time)
Wafer sojourn times between sequential process steps, including queue time violations (exceeding allowed time windows). **RCA relevance:** Q-time violations cause material degradation (oxide growth, moisture absorption, photoresist aging) that manifests as downstream process drift or defectivity increases. Map violation patterns to downstream symptom onset times.

### Inline Metrology
Post-process measurement data: Critical Dimension (CD), film thickness, overlay (registration error), defect counts (by type and bin), review-classified defect images. **RCA relevance:** SPC control chart patterns (trend, shift, cycle, outlier) on metrology data define the symptom quantitatively; spatial signatures (wafer map patterns, edge vs center, radial symmetry) constrain the set of plausible root causes.

### APC/SPC Data
Run-to-run (R2R) controller outputs: feedback adjustments (recipe parameter modifications based on post-process metrology), feedforward corrections, EWMA (Exponentially Weighted Moving Average) traces, CUSUM (Cumulative Sum) sequences, and raw control chart statistics (X-bar, R-chart, I-MR). **RCA relevance:** SPC rule violations (Western Electric rules) flag the timing of process shifts; APC controller saturation or oscillation indicates tuning or metrology issues; CUSUM/EWMA trends reveal gradual drift onset.

---

## RCA Methodology Framework

Apply these four pillars in combination. No single pillar is sufficient alone.

### Pillar A: Structured Decomposition

**5 Whys Technique.** Drill iteratively through the causal chain by asking "why?" at each level until reaching a fundamental, addressable root cause. Typically requires 3-7 iterations. Stop when the answer identifies a controllable factor (equipment setting, material specification, procedure). Document each causal layer.

**Ishikawa 6M for Semiconductor.** Adapt the standard fishbone categories:
- **Machine**: Equipment degradation, chamber contamination, hardware drift, calibration offset, spare part quality, PM effectiveness, matching difference between chambers/tools
- **Method**: Recipe parameter drift, software version change, process sequence error, SOP deviation, recipe upload/download mismatch, run-to-run controller tuning
- **Material**: Incoming wafer quality, chemical purity, consumable condition (ceramic parts, O-rings, liners), gas purity, photoresist age/expiry, reticle quality
- **Measurement**: Metrology tool drift, gauge R&R degradation, sampling plan inadequacy, measurement algorithm change, calibration expiration, reference wafer shift
- **Man**: Operator training gap, maintenance technician procedure deviation, setup error, alarm response delay, shift-to-shift practice variation, human error in recipe selection
- **Milieu**: Cleanroom particle level, humidity/temperature excursion, facility gas supply fluctuation, power quality event, electromagnetic interference, vibration source

**Fault Tree Analysis (FTA).** Decompose the top-level failure event using Boolean logic (AND/OR gates) into contributing sub-events. Identify minimal cut sets -- the smallest combination of basic events that guarantee the top event. Use FTA when multiple interacting factors are suspected.

### Pillar B: Statistical Evidence

**Correlation Analysis.** Compute pairwise and partial correlations between candidate causal variables and the symptom metric. Always test for confounding: a third variable may explain the observed correlation. Use lagged correlations to assess temporal lead-lag relationships.

**Temporal Precedence Validation.** A necessary condition for causation: the candidate cause must occur before or simultaneously with the effect. Reject hypotheses where the candidate variable changes after the symptom appears. Use time-series alignment and change-point detection to establish precedence.

**SPC Pattern Analysis.** Examine control charts for: trends (7+ consecutive points rising/falling), shifts (9+ consecutive points on one side of centerline), cycles (repeating patterns), stratification (unnatural clustering), and outliers (beyond 3-sigma). Map pattern onset times to candidate cause event times.

**Multivariate Analysis.** Decompose PCA score contributions and Hotelling T-squared values to identify which original variables drive multivariate excursions. Examine PCA loading vectors for variable groupings that co-vary. Use contribution plots (squared prediction error and score contributions) to isolate the fault direction in variable space.

**Variable Importance Ranking.** Leverage FDC classification model outputs (XGBoost feature importance, SHAP summary plots, LIME local explanations) to rank variables by their predictive power for the fault condition. Cross-reference with domain knowledge to assess mechanistic plausibility.

### Pillar C: Causal Inference

**Counterfactual Reasoning.** For each candidate root cause, ask: "If this factor had been at its nominal value, would the fault still have occurred?" Construct the counterfactual by comparing lots/wafers with the factor present versus absent, matched on other covariates. A true root cause should satisfy the counterfactual test.

**Difference-in-Differences (DiD).** Compare affected lots/chambers (treatment group) with unaffected lots/chambers (control group) before and after a suspected event or change. The DiD estimator isolates the causal effect by subtracting the pre-existing trend. Valid when treatment and control groups have parallel trends prior to the intervention.

**Elimination of Alternative Explanations.** Systematically evaluate and rule out competing hypotheses. For each alternative: state the expected evidence pattern, check the data, and explicitly document whether the alternative is supported, inconclusive, or refuted. The final root cause should be the only hypothesis consistent with all evidence.

**Mechanistic Plausibility Check.** Validate the proposed causal mechanism against semiconductor process physics and engineering first principles. The link between candidate cause and observed effect must be explainable through known physical, chemical, or electrical mechanisms (e.g., pressure drift affects deposition rate and thus film thickness; chamber residue causes particle defects).

### Pillar D: Temporal-Spatial Analysis

**Timeline Reconstruction.** Build a chronological event sequence: symptom first detection, process parameter changes, equipment events (PMs, parts replacement, alarm history), material lot changes, recipe changes, metrology drift onset. Identify the earliest anomaly and work forward.

**Process Drift Detection.** Use change-point detection (CUSUM, Bayesian change-point, or moving window regression) on key sensor and metrology parameters to identify when gradual drift began. The drift onset time constrains the search window for root causes to events occurring before or at that time.

**Spatial Pattern Analysis.** Examine wafer-level maps for radial, edge, center, bullseye, random, or repeating signatures. Map patterns to chamber hardware configurations (gas injection port locations, showerhead pattern, ESC electrode geometry, exhaust positions). Compare chamber-level and tool-level signatures to isolate the spatial source.

**Q-Time Violation Impact Assessment.** Correlate Q-time violation events (which lots, which step-to-step transitions, violation magnitude) with downstream symptom data. Use time-lagged analysis: the effect of a Q-time violation appears at the next process step where the material property matters (e.g., gate oxidation after surface contamination during a long queue).

---

## Agent Analysis Prompt Template

When given an RCA task, follow this structured prompt template. Fill in each section with data-derived findings.

```markdown
## RCA Task: [Problem Statement]

### 1. Context Ingestion
Read and understand all provided data sources. Map each to its data type category.
Identify: data granularity, temporal coverage, relevant process steps, equipment IDs.

### 2. Symptom Definition
Quantify the problem:
- Affected lots/wafers: [count/IDs]
- Time window: [start] to [end]
- Magnitude of deviation: [quantify vs spec/normal]
- Pattern: [random/clustered/trend/drift]

### 3. Hypothesis Generation (Ishikawa 6M)
For each M category, brainstorm 2-4 potential causes based on data patterns:
- **Machine**: [equipment-related hypotheses]
- **Method**: [recipe/process hypotheses]
- **Material**: [wafer/chemical hypotheses]
- **Measurement**: [metrology/measurement hypotheses]
- **Man**: [operator/maintenance hypotheses]
- **Milieu**: [environment/facility hypotheses]

### 4. Evidence Testing
For each hypothesis:
- State expected data pattern if hypothesis is true
- Check actual data for that pattern
- Assign: STRONG SUPPORT / MODERATE SUPPORT / WEAK SUPPORT / REFUTED
- Note confounding factors

### 5. Root Cause Synthesis
- Consolidate findings into causal chain
- Identify primary root cause(s) and contributing factors
- Validate: temporal precedence, mechanistic plausibility, reproducibility

### 6. Recommendations
- Immediate corrective actions
- Preventive measures
- Monitoring improvements (SPC/FDC threshold adjustments)
```

---

## Analysis Quality Checklist

Before finalizing RCA output, verify every item:

- [ ] Problem quantified with specific numbers (lot count, wafer count, deviation magnitude, time bounds)
- [ ] All 6M categories considered for hypotheses (no category skipped without justification)
- [ ] Each hypothesis has evidence-based assessment with data references (not opinion-based)
- [ ] Correlation distinguished from causation explicitly in reasoning
- [ ] Temporal precedence established between candidate cause and observed effect
- [ ] Alternative explanations eliminated or acknowledged with evidence
- [ ] Causal chain is logically coherent from root cause through contributing factors to symptom
- [ ] Recommendations are specific and actionable (not generic statements)
- [ ] Confidence level stated for each root cause finding (HIGH / MEDIUM / LOW)

---

## References

Detailed methodology references are available in the `references/` directory:

- `references/semiconductor-data-landscape.md` -- Detailed data type definitions, data quality checks, and analysis logic for each semiconductor data source
- `references/rca-methodology-framework.md` -- Full methodology catalog with decision trees, statistical test selection guide, and causal inference protocol
- `references/agent-prompt-templates.md` -- Reusable prompt templates for common RCA scenarios (yield loss, equipment fault, process drift, defect excursion, metrology shift)

---

## Important Constraints

- **Methodology only:** This skill provides reasoning frameworks and analytical logic. It does NOT include code, scripts, SQL queries, or data processing implementations. The agent reasons about data logic and operation logic, not data pipeline construction.
- **Evidence-based conclusions:** All findings must be grounded in data evidence. Do not speculate. If data is insufficient to resolve between competing hypotheses, state this explicitly.
- **Correlation is not causation:** Distinguish the two explicitly in every analysis. Correlation supports a hypothesis; it does not prove it. Require temporal precedence and mechanistic plausibility to claim causation.
- **Confidence levels:** State a confidence level (HIGH, MEDIUM, LOW) for every root cause finding and explain the basis for that rating.
- **No implementation:** The agent analyzes data and produces findings. Data extraction, transformation, and visualization are outside this skill's scope.
