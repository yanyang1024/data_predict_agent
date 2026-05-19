# Root Cause Analysis Report

## FDC Multivariate T2 Alarm — CVD_TOOL_03, Chamber B

| **Field** | **Value** |
|-----------|-----------|
| **Report ID** | RCA-CVD-2026-0515-001 |
| **Equipment** | CVD_TOOL_03, Chamber B |
| **Alarm Time** | 2026-05-15 14:32:00 |
| **Alarm Type** | Hotelling T2 Violation |
| **T2 Statistic** | 28.5 (Control Limit: 15.0) |
| **Product** | LOGIC_7NM_METAL_2 |
| **Recipe** | M2_CVD_WF6_Standard_v2.3 |
| **Analyst** | Semiconductor Manufacturing Data Analyst |
| **Date of Analysis** | 2026-05-15 |

---

## 1. Alarm Characterization

### 1.1 Alarm Severity Assessment

The Hotelling T2 statistic of **28.5** represents a **severe multivariate process deviation** — the alarm exceeds the control limit (15.0) by a factor of **1.9x**. This is classified as a **critical process excursion** requiring immediate investigation and lot hold action.

### 1.2 Sensor Contribution Breakdown

| Rank | Sensor | Contribution | Actual Value | Normal Range | Deviation Direction | Severity |
|------|--------|-------------|--------------|--------------|---------------------|----------|
| 1 | WF6_MFC_Flow | 32% | 45 sccm | 42–44 sccm | +2.3% above upper limit | Moderate |
| 2 | Chamber_Pressure | 24% | 12.5 Torr | 10.0–11.0 Torr | +13.6% above upper limit | **Severe** |
| 3 | Heater_Temp | 18% | 445 C | 440–442 C | +1.4% above upper limit | Moderate |
| 4 | N2_Purge_Flow | 15% | 85 sccm | 80–82 sccm | +3.7% above upper limit | Moderate |
| 5 | Throttle_Valve_Position | 11% | 68% | 55–60% | +13.3% above upper limit | **Severe** |

**Key Observation**: All five top-contributing sensors are deviating in the **same direction** (elevated above their respective upper control limits). This **unidirectional, correlated excursion pattern** is the hallmark of a **single root cause driving a cascading failure chain**, not independent sensor drift or random noise.

### 1.3 Process Impact Assessment

| Metric | Alarm Lot Value | Target/Normal | Assessment |
|--------|----------------|---------------|------------|
| Film Thickness | 52.3 nm | 50.0 nm | **OUT OF SPEC** (spec: 48–52 nm) |
| Previous 10 lots (v2.2) | 50.1 nm avg | 50.0 nm | In spec |
| Chamber A (same recipe) | 50.2 nm avg | 50.0 nm | In spec, T2 = 8.2 |

**Critical Finding**: The alarm lot's film thickness of **52.3 nm exceeds the upper spec limit of 52.0 nm**, making this a **yield-impacting excursion**. The previous 10 lots processed under recipe v2.2 averaged 50.1 nm (all within spec). Chamber A processing the same v2.3 recipe averages 50.2 nm with a normal T2 of 8.2.

### 1.4 Timeline of Relevant Events

```
2026-05-10  Chamber B Preventive Maintenance (throttle valve clean, heater inspect, MFC cal)
2026-05-12  Recipe v2.3 deployed to production
2026-05-15  14:32  T2 ALARM (28.5) — Chamber B, Lot with thickness 52.3nm
```

---

## 2. Hypothesis Generation (6M Method)

The 6M framework (Man, Machine, Material, Method, Measurement, Mother Nature) is applied to systematically identify potential root cause categories.

### 2.1 Man (Human Factors)

| ID | Hypothesis | Rationale |
|----|-----------|-----------|
| H-M1 | **Throttle valve improperly reinstalled during PM** | Throttle valve was cleaned and reinstalled on 2026-05-10. Incorrect reassembly (misaligned seal, wrong torque, damaged O-ring) could cause gas leakage, explaining elevated chamber pressure and increased throttle valve opening. |
| H-M2 | **MFC calibration error during PM** | WF6 MFC was calibrated during PM. An incorrect calibration offset could cause the MFC to deliver 45 sccm when commanded to deliver a lower setpoint. |
| H-M3 | **Incorrect recipe parameter entry during v2.3 deployment** | Recipe v2.3 was deployed 3 days before alarm. A data entry error during recipe creation could have set one or more setpoints to incorrect values. |

### 2.2 Machine (Equipment Factors)

| ID | Hypothesis | Rationale |
|----|-----------|-----------|
| H-MA1 | **Throttle valve mechanical degradation** | Post-PM throttle valve may have a damaged seal, worn bellows, or actuator malfunction preventing proper closure, causing chamber pressure to rise uncontrollably. |
| H-MA2 | **Heater control loop malfunction** | Heater controller may be drifting high, causing temperature to exceed setpoint. Higher temperature increases deposition rate, contributing to over-thickness. |
| H-MA3 | **Pressure gauge/transducer drift** | Chamber pressure sensor may be reading falsely high, causing the throttle valve to open excessively in a feedback loop. |
| H-MA4 | **Vacuum pump degradation** | Reduced pumping efficiency would raise base pressure and make throttle valve position climb to maintain setpoint. |

### 2.3 Material (Consumables & Gases)

| ID | Hypothesis | Rationale |
|----|-----------|-----------|
| H-MA5 | **WF6 gas supply contamination/purity issue** | Impurities in WF6 could affect deposition chemistry, potentially altering film properties and chamber conditions. |
| H-MA6 | **N2 purge gas pressure regulator drift** | Elevated N2 purge (85 vs 80–82 sccm) could indicate upstream regulator delivering higher pressure. |

### 2.4 Method (Process & Recipe)

| ID | Hypothesis | Rationale |
|----|-----------|-----------|
| H-ME1 | **Recipe v2.3 setpoint change incompatible with Chamber B** | Recipe v2.3 may have changed one or more setpoints (pressure, flow, temperature) that Chamber A tolerates but Chamber B cannot, due to hardware differences. |
| H-ME2 | **Recipe v2.3 parameter validation gap** | Recipe v2.3 may not have been fully qualified on Chamber B before production release. |

### 2.5 Measurement (Metrology & Sensors)

| ID | Hypothesis | Rationale |
|----|-----------|-----------|
| H-MS1 | **Chamber B sensor calibration drift** | Multiple sensors reading high could indicate a systematic calibration bias in Chamber B's sensor suite. |
| H-MS2 | **Inline film thickness metrology error** | The 52.3 nm reading may be a metrology artifact, not a true process excursion. |

### 2.6 Mother Nature (Environmental Factors)

| ID | Hypothesis | Rationale |
|----|-----------|-----------|
| H-EN1 | **Fab ambient temperature/humidity excursion** | Unusual environmental conditions affecting chamber thermal behavior or gas delivery. |
| H-EN2 | **Facility N2 or WF6 supply pressure fluctuation** | Upstream facility gas supply pressure variation. |

---

## 3. Evidence Testing

### 3.1 Elimination by Comparative Evidence

#### Test 1: Chamber A vs. Chamber B Comparison (Critical Test)

| Evidence | Finding | Impact on Hypotheses |
|----------|---------|---------------------|
| Chamber A runs identical recipe v2.3 | T2 = 8.2 (normal), film thickness = 50.2 nm | **Eliminates H-ME1, H-ME2**: Recipe v2.3 is not inherently problematic; the issue is Chamber B-specific. |
| | | **Eliminates H-MA5, H-MA6**: Material/supply issues would affect both chambers. |
| | | **Eliminates H-EN1, H-EN2**: Environmental/facility issues would affect both chambers. |

**Conclusion from Test 1**: The root cause is **localized to Chamber B hardware or its recent maintenance/recipe interaction**. This is the single most discriminating evidence in this case.

#### Test 2: Pre-Recipe-Change vs. Post-Recipe-Change Comparison

| Evidence | Finding | Impact on Hypotheses |
|----------|---------|---------------------|
| Previous 10 lots (recipe v2.2) on Chamber B | Average thickness 50.1 nm, all in spec | Recipe v2.3 + Chamber B combination is problematic, but v2.2 + Chamber B was fine. |
| | | **Weakens H-ME1 alone** but does not eliminate it because Chamber A proves v2.3 can work. |

**Conclusion from Test 2**: The issue requires **both** recipe v2.3 **and** Chamber B's current condition to manifest. This suggests an **interaction effect** between the recipe change and a Chamber B hardware/maintenance condition.

#### Test 3: PM Proximity Analysis

| Evidence | Finding | Impact on Hypotheses |
|----------|---------|---------------------|
| PM performed 5 days before alarm | Throttle valve cleaned & reinstalled; heater checked; MFC calibrated | Strongly supports H-M1, H-MA1, H-M2. |
| No errors in 48h before alarm | Alarm is not due to sudden component failure; it is a gradual/parametric drift | Supports gradual degradation (leak, drift) rather than sudden failure. |

**Conclusion from Test 3**: The recent PM is highly correlated with the alarm. The **throttle valve cleaning/reinstallation** is the most suspicious PM activity given that Chamber_Pressure and Throttle_Valve_Position are the two most severely deviated parameters.

### 3.2 Hypothesis Scoring Matrix

| Hypothesis | Chamber A Test | Pre/Post Recipe Test | PM Proximity | Sensor Pattern Match | Inline Metrology Match | **Overall Confidence** |
|-----------|:------------:|:--------------------:|:------------:|:--------------------:|:----------------------:|:----------------------:|
| H-M1: Throttle valve improperly reinstalled | Pass | Pass | **Strong** | **Strong** | **Strong** | **HIGH** |
| H-M2: MFC calibration error | Pass | Pass | **Strong** | Moderate | Moderate | Medium |
| H-M3: Recipe entry error | **FAIL** | Pass | N/A | Moderate | Moderate | **ELIMINATED** |
| H-MA1: Throttle valve mechanical failure | Pass | Pass | **Strong** | **Strong** | **Strong** | **HIGH** |
| H-MA2: Heater control malfunction | Pass | Pass | Moderate | Weak | Moderate | Low-Medium |
| H-MA3: Pressure transducer drift | Pass | Pass | N/A | Moderate | Requires verification | Medium |
| H-MA4: Vacuum pump degradation | Pass | Pass | N/A | Moderate | Moderate | Medium |
| H-MA5: Gas supply contamination | **FAIL** | N/A | N/A | Weak | Weak | **ELIMINATED** |
| H-ME1: Recipe v2.3 incompatible | **FAIL** | Pass | N/A | N/A | N/A | **ELIMINATED** |
| H-ME2: Recipe validation gap | **FAIL** | Pass | N/A | N/A | N/A | **ELIMINATED** |
| H-MS1: Sensor calibration drift | Pass | Pass | N/A | Weak | Requires verification | Low |
| H-MS2: Metrology error | N/A | N/A | N/A | N/A | Unlikely | Low |
| H-EN1/EN2: Environmental | **FAIL** | N/A | N/A | Weak | Weak | **ELIMINATED** |

### 3.3 Leading Hypothesis Deep-Dive: H-M1 / H-MA1 (Throttle Valve Issue)

**Why this is the leading hypothesis:**

1. **Sensor pattern alignment**: Chamber_Pressure (12.5 Torr, +13.6%) and Throttle_Valve_Position (68%, +13.3%) are the two **most severely deviated** non-flow parameters. Both relate directly to the pressure control loop of which the throttle valve is the primary actuator.

2. **Causal mechanism match**: If the throttle valve has a seal leak or misalignment after PM reinstallation:
   - The valve must open **wider** (68% vs. normal 55–60%) to attempt maintaining pressure setpoint
   - Despite increased opening, chamber pressure **still rises** to 12.5 Torr (leak overwhelms the throttle valve's capacity)
   - Higher chamber pressure changes the **gas dynamics** in the chamber
   - The MFC responds to maintain flow setpoint in a higher-pressure environment, reading higher (45 sccm)
   - The **heater runs hotter** (445 C) due to altered thermal transfer at elevated pressure
   - **N2 purge increases** (85 sccm) as the system attempts to stabilize the process
   - The combined effect produces a **thicker film** (52.3 nm vs. 50.0 nm target) due to excess precursor and elevated temperature

3. **Chamber A confirmation**: Chamber A has an **unaffected throttle valve** (not subject to the same PM on the same day) and processes normally under v2.3.

4. **Timing correlation**: The PM on 2026-05-10 involved direct handling of the throttle valve. The alarm occurred 5 days later — consistent with a **gradual leak or degradation** rather than an immediate catastrophic failure.

### 3.4 Secondary Hypothesis: H-M2 (MFC Calibration Error)

While the WF6_MFC_Flow has the highest single-sensor contribution (32%), an MFC delivering excess flow alone would not explain:
- Why chamber pressure is **also** severely elevated (+13.6%)
- Why the throttle valve position is **also** severely elevated (+13.3%)

An MFC calibration error could be a **contributing factor** but is unlikely to be the **primary root cause** because it does not explain the full sensor correlation pattern.

### 3.5 Tertiary Hypothesis: H-MA3 (Pressure Transducer Drift)

If the pressure transducer were reading falsely high, the control system would open the throttle valve more to compensate. However:
- The **inline film thickness is genuinely out of spec** (52.3 nm), confirming a real process shift, not just a measurement artifact
- The **correlated deviation of all 5 sensors** in the same direction makes independent transducer drift statistically unlikely

**Verdict**: Eliminated as primary root cause.

---

## 4. Causal Chain

### 4.1 Primary Causal Chain (Most Probable)

```
+---------------------------------------------------------------+
|  ROOT CAUSE: Throttle valve improperly reinstalled during PM  |
|  (likely damaged O-ring, misaligned seal, or incorrect torque) |
+---------------------------------------------------------------+
                                |
                                v
+---------------------------------------------------------------+
|  1st EFFECT: Gas leak past throttle valve seal                |
|  -> Chamber pressure cannot be maintained at setpoint         |
+---------------------------------------------------------------+
                                |
                                v
+---------------------------------------------------------------+
|  2nd EFFECT: Throttle valve opens to 68% (vs. normal 55-60%)  |
|  attempting to compensate and maintain pressure               |
+---------------------------------------------------------------+
                                |
                                v
+---------------------------------------------------------------+
|  3rd EFFECT: Chamber pressure rises to 12.5 Torr              |
|  (+13.6% above normal 10-11 Torr)                             |
+---------------------------------------------------------------+
                                |
                                v
+---------------------------------------------------------------+
|  4th EFFECT: Altered gas dynamics at elevated pressure        |
|  -> MFC delivers 45 sccm (vs. normal 42-44)                   |
|  -> Heater temp rises to 445 C (altered thermal transfer)     |
|  -> N2 purge increases to 85 sccm (system stabilization)      |
+---------------------------------------------------------------+
                                |
                                v
+---------------------------------------------------------------+
|  FINAL EFFECT: T2 = 28.5 alarm + film thickness 52.3nm        |
|  (OVER SPEC -> yield-impacting excursion)                     |
+---------------------------------------------------------------+
```

### 4.2 Why Recipe v2.3 Exposed the Issue

Recipe v2.3 likely introduced a **slightly different process window** (e.g., different pressure setpoint, flow profile, or step timing) compared to v2.2. Chamber A accommodated this change without issue. However, Chamber B's **already-compromised throttle valve** (from the 2026-05-10 PM) could not maintain control under the v2.3 process conditions, pushing it past the T2 control limit. Under v2.2, the compromised throttle valve may have been operating near the edge of stability but not yet crossing the alarm threshold.

This is a **latent defect** that was **activated by the recipe change**.

### 4.3 Alternative Causal Chain (Less Probable)

```
ROOT CAUSE: Throttle valve mechanical damage (bellows fatigue, actuator wear)
    |
    v
Same cascading effects as above, but due to pre-existing hardware degradation
rather than PM-induced error. Less likely because:
- PM was only 5 days before alarm (strong temporal correlation)
- No prior alarms or warnings on Chamber B (sudden onset suggests trigger event)
- Heater resistance checked OK during PM (some hardware was verified good)
```

---

## 5. Confidence Assessment

### 5.1 Confidence in Root Cause Identification

| Aspect | Confidence Level | Justification |
|--------|-----------------|---------------|
| **Root Cause Category** | **85%** | Throttle valve integrity compromised during PM |
| **Specific Mechanism** | **70%** | Seal leak/misalignment (vs. other mechanical damage) |
| **Recipe as Trigger** | **75%** | Recipe v2.3 exposed latent throttle valve defect |
| **Overall RCA Confidence** | **80%** | High confidence based on strong discriminating evidence |

### 5.2 Confidence Drivers

**Factors INCREASING confidence:**
- Chamber A normal operation under identical recipe eliminates recipe, material, and environmental causes
- All 5 sensors deviate unidirectionally, consistent with single root cause cascade
- Strong temporal correlation between PM (throttle valve handling) and alarm
- Film thickness over-spec confirms real process impact, not sensor artifact
- Sensor deviation pattern (pressure + throttle valve most severe) matches throttle valve failure signature

**Factors DECREASING confidence (remaining uncertainty):**
- No direct physical inspection of throttle valve yet performed
- Cannot definitively distinguish between human reinstallation error (H-M1) and pre-existing mechanical failure (H-MA1) without valve inspection
- Recipe v2.3 vs. v2.2 parameter delta not yet reviewed to confirm trigger mechanism
- MFC calibration data from PM not yet reviewed to rule out H-M2 as contributing factor

### 5.3 Risk of Alternative Root Causes

| Alternative | Residual Probability | Key Outstanding Test |
|-------------|:--------------------:|---------------------|
| MFC calibration error (H-M2) | 15% | Review PM calibration certificate; compare MFC actual vs. commanded |
| Pressure transducer drift (H-MA3) | 5% | Cross-check with independent pressure gauge |
| Pre-existing throttle valve wear (H-MA1 variant) | 10% | Physical valve inspection upon removal |

---

## 6. Recommendations

### 6.1 Immediate Actions (Within 4 Hours)

| Priority | Action | Owner | Rationale |
|----------|--------|-------|-----------|
| P0 | **HOLD all WIP lots on Chamber B** | Production | Prevent further yield loss and out-of-spec material movement |
| P0 | **Quarantine the alarm lot** for disposition review | Quality | Lot is over spec (52.3 nm); requires scrap/rework decision |
| P0 | **Verify Chamber A continues to run normally** under v2.3 | Equipment Engineering | Confirm that matched-pair chamber remains stable |

### 6.2 Short-Term Actions (Within 24 Hours)

| Priority | Action | Owner | Rationale |
|----------|--------|-------|-----------|
| P1 | **Remove and inspect Chamber B throttle valve** | Equipment Maintenance | Visually inspect for: damaged O-ring, misalignment, seal contamination, bellows integrity, actuator coupling |
| P1 | **Perform throttle valve leak check** (helium leak test) | Equipment Maintenance | Quantify leak rate to confirm seal integrity hypothesis |
| P1 | **Review recipe v2.3 vs. v2.2 parameter delta** | Process Engineering | Identify which setpoint changes may have exposed the latent valve defect |
| P1 | **Re-check MFC calibration** against PM certificate | Equipment Maintenance | Rule out calibration offset as contributing factor |
| P1 | **Re-calibrate Chamber B pressure transducer** | Equipment Maintenance | Rule out sensor drift |

### 6.3 Corrective Actions (Before Chamber B Return to Production)

| Priority | Action | Owner | Rationale |
|----------|--------|-------|-----------|
| P2 | **Replace throttle valve O-ring/seal kit** with new parts | Equipment Maintenance | Address most probable physical root cause |
| P2 | **Reinstall throttle valve with proper torque procedure** and witness check | Equipment Maintenance | Prevent reoccurrence of human error |
| P2 | **Perform chamber leak rate verification** (full leak-up test) | Equipment Maintenance | Confirm chamber integrity post-repair |
| P2 | **Run Chamber B qualification wafers** under v2.3 recipe | Process Engineering | Verify process returns to control before production release |

### 6.4 Preventive Actions (Within 2 Weeks)

| Priority | Action | Owner | Rationale |
|----------|--------|-------|-----------|
| P3 | **Add post-PM throttle valve position baseline check** to PM procedure | Equipment Engineering | Catch similar issues before production impact |
| P3 | **Implement recipe change sensitivity check**: compare Chamber A/B T2 for 5 lots post-recipe deployment | FDC/Process Engineering | Early detection of chamber-specific recipe sensitivities |
| P3 | **Update PM checklist**: add "throttle valve stroke test and leak check" after reinstallation | Equipment Maintenance | Strengthen PM quality control |
| P3 | **Review FDC T2 control limits** for Chamber B to ensure adequate sensitivity | FDC Engineering | Confirm alarm would trigger before out-of-spec material |

### 6.5 Risk Assessment if Actions Not Taken

| Risk | Impact | Likelihood |
|------|--------|------------|
| Continued out-of-spec film thickness production | Scrap of LOGIC_7NM_METAL_2 wafers (~$50K–$100K per lot) | High |
| Potential downstream yield impact at metal etch/ CMP | Additional yield loss at subsequent process steps | Medium |
| Customer delivery impact if material cannot be salvaged | Schedule and revenue risk | Medium |
| Chamber degradation if run in uncontrolled state | More extensive damage requiring longer downtime | Medium |

---

## Appendix A: Sensor Correlation Analysis

The following correlation matrix logic supports the causal chain:

| Sensor Pair | Expected Correlation Under Throttle Valve Leak | Observed | Match? |
|-------------|-----------------------------------------------|----------|--------|
| Chamber_Pressure vs. Throttle_Valve_Position | Positive (both rise as valve tries to compensate) | Both elevated | **YES** |
| Chamber_Pressure vs. WF6_MFC_Flow | Positive (higher pressure changes flow dynamics) | Both elevated | **YES** |
| Chamber_Pressure vs. Heater_Temp | Positive (altered thermal transfer at high P) | Both elevated | **YES** |
| Throttle_Valve_Position vs. N2_Purge_Flow | Positive (system compensates) | Both elevated | **YES** |

All pairwise correlations are consistent with the throttle valve leak hypothesis and inconsistent with independent sensor failures.

## Appendix B: Decision Logic Summary

```
T2 Alarm on Chamber B
    |
    +---> All sensors elevated in SAME direction? ----> YES ---> Single root cause likely
    |                                                          |
    +---> Chamber A normal on same recipe? ------------> YES ---> Problem is Chamber B specific
    |                                                          |
    +---> Recent PM on Chamber B? ---------------------> YES ---> PM activity is prime suspect
    |                                                          |
    +---> PM involved throttle valve? -----------------> YES ---> Throttle valve is prime suspect
    |                                                          |
    +---> Pressure + Throttle Valve most deviated? ----> YES ---> Confirms throttle valve hypothesis
    |                                                          |
    +---> Film thickness genuinely out of spec? --------> YES ---> Real process impact, not sensor artifact
    |                                                          |
    v
ROOT CAUSE: Throttle valve integrity compromised during PM
TRIGGER: Recipe v2.3 process window exposed latent defect
```

---

*Report prepared by: Semiconductor Manufacturing Data Analyst*
*Analysis Date: 2026-05-15*
*Classification: Internal Use — Production Quality*
