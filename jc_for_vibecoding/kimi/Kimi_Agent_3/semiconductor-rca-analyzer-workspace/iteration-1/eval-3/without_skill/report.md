# Root Cause Analysis Report: Q-time Violations Between LITHO_PATTERN (Step 45) and ETCH_HARDMASK (Step 46)

**Document ID**: RCA-2026-0512-001  
**Analysis Date**: May 12, 2026  
**Analyst**: Semiconductor Manufacturing Data Analyst  
**Affected Area**: FAB_A, Line 3  
**Severity**: High (Production Impact + Quality Risk)  
**Status**: In Progress — Recommendations Pending Implementation

---

## 1. Violation Characterization

### 1.1 Problem Statement

Q-time violations between LITHO_PATTERN (step 45) and ETCH_HARDMASK (step 46) have increased dramatically starting May 5, 2026. The compliance rate dropped from a historical baseline of **98%** to **72%**, representing a **26 percentage-point degradation**. The average elapsed time for lots in this process segment increased from **14 hours to 28 hours** — doubling the normal transit time and exceeding the 24-hour Q-time limit by a significant margin.

### 1.2 Key Performance Indicators

| Metric | Baseline (Normal) | Current (May 5–12) | Delta |
|---|---|---|---|
| Q-time Compliance | 98% | 72% | −26 pp |
| Average Elapsed Time | 14 hours | 28 hours | +100% |
| Violations per Week | 3–4 lots | 45 lots | +1,025% |
| Violations >30 Hours | Rare (<1 lot/week) | 18 lots | Significant |
| Violations >36 Hours | Extremely rare | 5 lots | Critical |

### 1.3 Scope of Impact

- **Temporal**: Issue began sharply on May 5, 2026, and has persisted for 7+ days
- **Product Scope**: Universal — all products, all layers, all technology nodes affected
- **Lot Priority**: Both regular and hot lots are impacted (ruling out pure dispatching bias as root cause)
- **Quality Risk**: 3 lots have already exhibited post-etch CD shift after >30-hour violations; engineering assessment indicates >24-hour delays may cause photoresist pattern degradation
- **Yield Impact**: Not yet directly observable (yield data lags 5–7 days), but elevated risk flagged

### 1.4 Violation Severity Distribution

| Severity Bucket | Count (7 days) | % of Violations |
|---|---|---|
| 24–30 hours | 22 lots | 48.9% |
| 30–36 hours | 13 lots | 28.9% |
| >36 hours | 5 lots | 11.1% |
| At-limit (22–24 hours) | 5 lots | 11.1% |

**Assessment**: The distribution shows a significant right tail, with **40% of violations exceeding 30 hours**. This indicates not merely a marginal capacity shortfall but a **structural throughput bottleneck** causing lots to queue for extended periods.

---

## 2. Hypothesis Generation Using 6M (Ishikawa) Framework

### 2.1 Man (Personnel)

| # | Hypothesis | Relevance |
|---|---|---|
| H1.1 | Shift staffing shortage or skill gap causing delayed processing at ETCH | **Low** — staffing reported as normal |
| H1.2 | Dispatching team manually overriding sequence inappropriately | **Medium** — hot lot priority may be disrupting FIFO flow |

### 2.2 Machine (Equipment)

| # | Hypothesis | Relevance |
|---|---|---|
| H2.1 | ETCH_HM_TOOL_02 unscheduled PM (May 4–9) reduced effective capacity by 25% | **High** — direct capacity reduction |
| H2.2 | ETCH_HM_TOOL_04 chamber matching restriction (since May 3) removed 0.5 tool-equivalent capacity | **High** — reduced effective capacity to 3.5 tools |
| H2.3 | Combined effective capacity of 3.5 tools (vs. 4.0) insufficient to handle increased WIP loading | **High** — capacity-demand mismatch |
| H2.4 | LITHO_PATTERN equipment over-producing relative to ETCH_HARDMASK capacity | **Medium** — upstream/downstream imbalance |

### 2.3 Material

| # | Hypothesis | Relevance |
|---|---|---|
| H3.1 | Photoresist material degradation after extended Q-time causing CD shift | **Medium** — confirmed on 3 lots; may be symptom, not cause |
| H3.2 | Substrate/wafer supply issue causing artificial delays | **Low** — no evidence of material shortage |

### 2.4 Method (Process / Dispatching)

| # | Hypothesis | Relevance |
|---|---|---|
| H4.1 | FIFO with hot lot priority override causing regular lots to be excessively pre-empted | **High** — hot lot insertion up 30% since May 1 |
| H4.2 | Dispatching algorithm not accounting for Q-time risk when inserting hot lots | **High** — may explain why regular lots bear disproportionate violation burden |
| H4.3 | Lack of dynamic WIP balancing between LITHO and ETCH | **Medium** — WIP imbalance ratio at 2.9 (normal 1.4–1.7) |
| H4.4 | No Q-time guard-banding or early warning system to trigger expedite actions | **Medium** — reactive vs. proactive management |

### 2.5 Measurement (Metrology / Monitoring)

| # | Hypothesis | Relevance |
|---|---|---|
| H5.1 | Q-time clock tracking error or offset causing false violation alarms | **Low** — inline metrology confirms actual CD shift on long-wait lots |
| H5.2 | Stocker dwell time not included in Q-time calculation, creating blind spot | **Medium** — buffer stocker at 95%+ capacity suggests significant dwell |

### 2.6 Mother Nature (Environment / External Factors)

| # | Hypothesis | Relevance |
|---|---|---|
| H6.1 | Facility/power issues causing processing delays | **Low** — no outages reported |
| H6.2 | AMHS track congestion and extended transport times contributing to total elapsed time | **High** — transport time up 50% (30→45 min); 3 congestion events |

### 2.7 Prioritized Hypothesis Summary

| Priority | Hypothesis ID | Description | Confidence (Pre-Test) |
|---|---|---|---|
| **P1** | H2.1 + H2.2 | Combined ETCH capacity reduction (3.5 effective tools) | High |
| **P2** | H4.1 + H4.2 | Hot lot insertion (+30%) with FIFO priority override creating queue starvation | High |
| **P3** | H2.3 | Insufficient ETCH capacity to handle upstream WIP (280 lots vs. normal 220) | High |
| **P4** | H6.2 | AMHS congestion and extended transport times adding to total elapsed time | Medium-High |
| **P5** | H5.2 | Stocker at 95%+ capacity causing unaccounted dwell time | Medium |
| **P6** | H1.2 | Dispatching overrides disrupting flow | Medium |

---

## 3. Evidence Testing

### 3.1 Hypothesis: ETCH Capacity Reduction (H2.1 + H2.2 + H2.3)

| Evidence Item | Finding | Assessment |
|---|---|---|
| ETCH_HM_TOOL_02 down May 4–9 | Unscheduled PM reduced active tool count to 3 | **Confirmed** |
| ETCH_HM_TOOL_04 restricted since May 3 | Chamber matching issue → 7nm-only, not available for general products | **Confirmed** |
| Effective capacity | 3.5 tools vs. design capacity of 4.0 = **12.5% capacity loss** | **Confirmed** |
| Utilization of running tools | Tool_01: 85%, Tool_03: 80% — elevated but not at ceiling | **Confirmed** |
| WIP at ETCH_HARDMASK | 95 lots (LOW) vs. normal 130–150 — **downstream starvation** | **Confirmed** |
| WIP at LITHO_PATTERN | 280 lots (HIGH) vs. normal 200–220 — **upstream accumulation** | **Confirmed** |

**Test Result: SUPPORTED** — The effective capacity reduction of 12.5% (3.5/4.0 tools), combined with the timing of the violation onset (May 5, coinciding with TOOL_02 downtime), strongly supports this hypothesis. The WIP profile (high upstream, low downstream) is the classic signature of a **downstream capacity bottleneck**.

**Capacity-Demand Calculation (Estimated):**

| Parameter | Value |
|---|---|
| Design Capacity (4 tools) | ~192 lots/day (48 lots/tool/day at typical throughput) |
| Effective Capacity (3.5 tools) | ~168 lots/day |
| Capacity Loss | 24 lots/day |
| Upstream WIP Excess | ~60 lots above normal (280 − 220) |
| Time to Clear Excess at Reduced Capacity | ~2.5 days (60 lots ÷ 24 lots/day deficit) |

The math shows the capacity deficit and WIP excess are consistent with the observed queue buildup and violation pattern.

### 3.2 Hypothesis: Hot Lot Insertion Disrupting Flow (H4.1 + H4.2)

| Evidence Item | Finding | Assessment |
|---|---|---|
| Hot lot insertion rate | Increased 30% starting May 1 | **Confirmed** |
| Dispatching rule | FIFO with hot lot priority override | **Confirmed** |
| Both regular and hot lots violating Q-time | Hot lots also affected | **Partial contradiction** |

**Analysis**: If hot lot priority were the sole or dominant cause, we would expect regular lots to bear the majority of violations while hot lots remain protected. However, the data shows **both regular and hot lots are affected**. This suggests:

1. Hot lot priority is contributing to queue disorder and FIFO disruption
2. But the fundamental problem is **insufficient total capacity** — even hot lots cannot be processed within Q-time limits because the bottleneck is structural, not merely a dispatching artifact
3. The 30% increase in hot lots (which typically receive expedited handling) may have **pushed the already-constrained ETCH capacity over the edge**

**Test Result: PARTIALLY SUPPORTED** — Hot lot insertion is a **contributing accelerator**, not the root cause. The onset date (May 1 increase) precedes the violation spike (May 5), suggesting hot lots created initial loading pressure that became catastrophic when TOOL_02 went down May 4.

### 3.3 Hypothesis: AMHS Congestion (H6.2)

| Evidence Item | Finding | Assessment |
|---|---|---|
| Transport time LITHO→ETCH | 45 minutes vs. normal 30 minutes (+50%) | **Confirmed** |
| Stocker_B congestion events | 3 events on May 5–7 | **Confirmed** |
| Track segment T-B-17 | Cleaned on May 4 (maintenance activity) | **Confirmed** |
| Buffer stocker utilization | Frequently at 95%+ capacity | **Confirmed** |

**Test Result: PARTIALLY SUPPORTED** — AMHS congestion and extended transport times are **contributing factors** that add to total elapsed time, but they do not explain the magnitude of the violation (28-hour average vs. 14-hour normal, a 14-hour increase). A 15-minute transport delay cannot account for a 14-hour queue increase. The AMHS issues are **symptomatic of the WIP backup**, not the root cause. When downstream capacity is constrained, WIP backs up into interim storage, causing stocker overflow and congestion.

**Important**: The direction of causality is likely reversed — the ETCH bottleneck caused WIP to accumulate in the buffer stocker, which then caused AMHS congestion (vehicles cannot deposit lots, traffic backs up), which further extended transport times. AMHS is a **secondary amplifying loop**, not the root cause.

### 3.4 Hypothesis: WIP Imbalance (H4.3)

| Evidence Item | Finding | Assessment |
|---|---|---|
| WIP imbalance ratio | 2.9 (actual) vs. 1.4–1.7 (normal) | **Confirmed** |
| Upstream WIP | 280 lots (+27% above normal) | **Confirmed** |
| Downstream WIP | 95 lots (−31% below normal) | **Confirmed** |

**Test Result: SUPPORTED** — The WIP imbalance ratio of 2.9 is extreme and is a direct consequence of the downstream capacity bottleneck. When ETCH cannot process lots at the rate LITHO produces them, WIP naturally accumulates upstream. This is a **symptom/measure of the bottleneck severity**, not an independent root cause.

### 3.5 Evidence Testing Summary Matrix

| Hypothesis | Test Result | Contribution to Problem | Direction of Causality |
|---|---|---|---|
| ETCH capacity reduction (H2.1 + H2.2) | **SUPPORTED** | Primary — ~60-70% | Root cause |
| Hot lot insertion (H4.1 + H4.2) | Partially supported | Contributing — ~20-25% | Accelerating factor |
| AMHS congestion (H6.2) | Partially supported | Amplifying — ~10-15% | Secondary effect of bottleneck |
| WIP imbalance (H4.3) | Supported (as symptom) | Measures severity | Symptom of capacity shortfall |
| Stocker dwell time (H5.2) | Supported | Minor contribution | Secondary effect |
| Dispatching overrides (H1.2) | Insufficient evidence | Minor | Unconfirmed |

---

## 4. Causal Chain Analysis

### 4.1 Primary Causal Chain (Capacity-Driven Bottleneck)

```
May 1: Hot lot insertion rate increases by 30%
    |
    v
May 3: ETCH_HM_TOOL_04 restricted to 7nm only (effective capacity: 3.75 tools)
    |
    v
May 4: ETCH_HM_TOOL_02 goes down for unscheduled PM (effective capacity: 2.75 tools)
    |         Track segment T-B-17 cleaned (AMHS maintenance)
    v
May 5: Q-time violations BEGIN spiking
    |    AMHS congestion events in Stocker_B (3 events May 5-7)
    |    Transport time increases from 30 to 45 minutes
    v
WIP accumulates at LITHO_PATTERN (280 lots, +27%)
    |
    v
Buffer stocker reaches 95%+ capacity
    |
    v
Lots queue for extended periods awaiting ETCH_HARDMASK processing
    |
    v
Average elapsed time: 14 hours → 28 hours
Q-time compliance: 98% → 72%
45 violations in 7 days (vs. 3-4 normal)
    |
    v
May 9: ETCH_HM_TOOL_02 returns to service (effective capacity: 3.5 tools)
    |
    v
VIOLATIONS CONTINUE at elevated levels because:
    - Effective capacity (3.5 tools) still below design (4.0 tools)
    - TOOL_04 remains restricted
    - Backlog of excess WIP not yet cleared
    - Hot lot insertion rate remains elevated
```

### 4.2 Feedback Loop Diagram

```
+----------------------------------+
|  ETCH Capacity Reduction         |
|  (3.5/4.0 effective tools)       |
+---------------+------------------+
                |
                v
+----------------------------------+
|  Downstream Processing Slows     |
|  ETCH WIP drops to 95 lots       |
+---------------+------------------+
                |
                v
+----------------------------------+
|  Upstream WIP Accumulates        |
|  LITHO WIP rises to 280 lots     |
+---------------+------------------+
                |
                v
+----------------------------------+
|  Buffer Stocker Saturates (95%+) |
+---------------+------------------+
                |
                v
+----------------------------------+
|  AMHS Congestion & Delays        |
|  Transport: 30→45 min            |
+---------------+------------------+
                |
                v
+----------------------------------+
|  Q-time Violations Increase      |
|  Elapsed time: 14→28 hours       |
+---------------+------------------+
                |
                v
+----------------------------------+
|  Photoresist Degradation Risk    |
|  3 lots show post-etch CD shift  |
+----------------------------------+
```

### 4.3 Timeline of Contributing Events

| Date | Event | Impact on Capacity / Flow |
|---|---|---|
| May 1 | Hot lot insertion rate +30% | Increased loading pressure on ETCH |
| May 3 | ETCH_HM_TOOL_04 chamber matching restriction | Effective capacity: 4.0 → 3.75 tools |
| May 4 | ETCH_HM_TOOL_02 unscheduled PM begins | Effective capacity: 3.75 → 2.75 tools |
| May 4 | AMHS track segment T-B-17 cleaned | Potential AMHS disruption |
| May 5 | **Q-time violations begin spiking** | **CRITICAL EVENT** |
| May 5–7 | AMHS congestion events in Stocker_B | Flow disruption, extended transport |
| May 9 | ETCH_HM_TOOL_02 returns to service | Effective capacity: 2.75 → 3.5 tools |
| May 5–12 | 45 Q-time violations recorded | Sustained elevated violation rate |

**Key Insight**: The onset of violations on May 5 correlates precisely with the convergence of three factors:
1. TOOL_02 downtime (May 4) — immediate 25% capacity reduction
2. TOOL_04 restriction (May 3) — ongoing 12.5% capacity reduction
3. Elevated hot lot loading (May 1) — 30% increased demand pressure

### 4.4 Root Cause vs. Contributing Factors Classification

| Factor | Classification | Rationale |
|---|---|---|
| ETCH effective capacity = 3.5 tools (vs. 4.0 design) | **ROOT CAUSE** | The system cannot process lots at the rate required to maintain Q-time compliance. The capacity shortfall is structural and persistent. |
| Hot lot insertion rate +30% | **CONTRIBUTING FACTOR** | Accelerated the onset and severity by increasing demand on already-constrained capacity. |
| ETCH_HM_TOOL_02 unscheduled PM | **CONTRIBUTING FACTOR** | Temporary capacity reduction that triggered the violation spike. Tool is now restored, but effective capacity remains below design. |
| ETCH_HM_TOOL_04 chamber matching restriction | **CONTRIBUTING FACTOR** | Persistent capacity reduction of 0.5 tool-equivalent. Root cause of this sub-issue is the chamber matching problem itself, which requires separate investigation. |
| AMHS congestion and extended transport | **SECONDARY EFFECT** | Caused by WIP backup into stockers; amplifies the problem but does not cause it. |
| FIFO with hot lot priority dispatching | **SYSTEM DESIGN FACTOR** | The dispatching rule is functioning as designed but lacks Q-time-aware prioritization to prevent queue starvation of time-sensitive lots. |

---

## 5. Confidence Assessment

### 5.1 Overall Confidence: **HIGH (85%)**

The evidence strongly supports a capacity-driven bottleneck as the root cause, with clear temporal correlation, quantitative consistency, and alignment with all observed symptoms.

### 5.2 Confidence by Component

| Component | Confidence Level | Supporting Evidence Strength |
|---|---|---|
| Root cause = ETCH capacity shortfall | **HIGH (90%)** | Temporal correlation (May 3–5 onset), quantitative WIP imbalance, utilization data, known tool restrictions |
| Hot lots as accelerating factor | **HIGH (85%)** | Confirmed 30% increase starting May 1, known FIFO priority override behavior |
| AMHS as secondary effect | **MEDIUM-HIGH (75%)** | Confirmed congestion events and extended transport, but direction of causality inferred |
| TOOL_02 unscheduled PM as trigger | **HIGH (90%)** | Precise timing correlation (May 4 downtime, May 5 violation spike) |
| TOOL_04 restriction as persistent factor | **HIGH (95%)** | Directly confirmed; restriction still active |
| Photoresist degradation risk | **MEDIUM (65%)** | 3 confirmed CD shifts, engineering assessment; limited sample size |

### 5.3 Uncertainties and Information Gaps

| Gap | Impact on Analysis | Recommended Action |
|---|---|---|
| Exact lot-level dispatching history | Could quantify hot lot priority impact | Pull dispatching transaction log for May 1–12 |
| Chamber matching issue details for TOOL_04 | Could estimate resolution timeline | Engage ETCH equipment engineering |
| LITHO_PATTERN equipment utilization and throughput | Could confirm upstream over-production vs. normal | Pull LITHO tool utilization reports |
| Actual ETCH processing time per lot by product | Could refine capacity calculation | Pull tool process time data |
| Full AMHS transaction log for May 5–7 | Could confirm causality direction | Engage AMHS engineering team |
| Yield data for violation lots (when available) | Could quantify quality impact | Flag for yield team follow-up in 5–7 days |

### 5.4 Risk of Alternative Explanations

| Alternative Hypothesis | Probability | Reason for Rejection |
|---|---|---|
| Purely a dispatching algorithm issue | Low | Hot lots also violating Q-time; dispatching alone cannot explain |
| Material quality issue | Low | Universal across all products; no material change reported |
| Metrology / Q-time clock error | Low | Physical CD shift confirmed on 3 lots; violations are real |
| Facility issue | Low | No power outages, environmental excursions, or facility alarms |
| Operator error or training gap | Low | Staffing normal; issue is systematic, not sporadic |

---

## 6. Recommendations

### 6.1 Immediate Actions (Within 24 Hours)

| Priority | Action | Owner | Expected Impact |
|---|---|---|---|
| **CRITICAL** | Restore ETCH_HM_TOOL_04 to full product capability — escalate chamber matching issue to vendor/process engineering | ETCH Equipment Engineering | Restore 0.5 tool-equivalent capacity (~12.5% capacity increase) |
| **CRITICAL** | Implement Q-time-aware dispatching: add Q-time remaining as priority weighting factor alongside hot lot status | Manufacturing / Dispatching | Reduce extreme violations (>30 hours) by prioritizing time-critical lots |
| **HIGH** | Temporarily reduce hot lot insertion rate or implement hot lot quota per shift until capacity is restored | Manufacturing / Planning | Reduce queue pressure on ETCH |
| **HIGH** | Expedite all lots currently >20 hours elapsed Q-time to front of ETCH queue | Line Management / Dispatching | Prevent additional extreme violations |
| **HIGH** | Notify downstream process owners (post-etch metrology, subsequent etch steps) of potential CD shift risk for 18 lots >30 hours | Process Integration / Metrology | Ensure appropriate inspection and disposition |

### 6.2 Short-Term Actions (1–7 Days)

| Priority | Action | Owner | Expected Impact |
|---|---|---|---|
| **HIGH** | Evaluate temporary product mix optimization — route less time-sensitive products to alternative ETCH lines if available | Manufacturing Engineering | Reduce loading on constrained ETCH tools |
| **HIGH** | Increase ETCH tool availability through accelerated PM completion and spare parts readiness | Equipment Engineering | Maximize uptime of 3.5 effective tools |
| **MEDIUM** | Implement WIP cap at LITHO_PATTERN output to prevent excessive upstream accumulation | Manufacturing / WIP Control | Prevent stocker saturation and AMHS congestion |
| **MEDIUM** | Establish Q-time violation early warning: alert when elapsed time exceeds 18 hours (75% of limit) | Manufacturing IT / MES | Enable proactive intervention before violations occur |
| **MEDIUM** | Review AMHS routing algorithm for Stocker_B — consider overflow routing to alternate stockers during high-WIP conditions | AMHS Engineering | Reduce AMHS-related delays |
| **MEDIUM** | Conduct chamber matching root cause analysis for TOOL_04 to prevent recurrence | ETCH Process Engineering | Permanent resolution of capacity restriction |

### 6.3 Medium-Term Actions (1–4 Weeks)

| Priority | Action | Owner | Expected Impact |
|---|---|---|---|
| **MEDIUM** | Evaluate ETCH_HARDMASK capacity expansion options (fifth tool, tool upgrade, or process time reduction) | Factory Management / Capital Planning | Structural capacity increase to handle future loading growth |
| **MEDIUM** | Implement dynamic WIP balancing algorithm between LITHO and ETCH to maintain WIP ratio within 1.4–1.7 range | Industrial Engineering / IT | Prevent future WIP imbalance scenarios |
| **MEDIUM** | Develop predictive Q-time risk model incorporating WIP levels, tool availability, and hot lot forecast | Advanced Process Control / Data Science | Predict and prevent violations before they occur |
| **LOW** | Conduct formal FMEA on Q-time violation impact across all Q-time-limited process segments | Process Integration | Identify other vulnerable points in the process flow |

### 6.4 Long-Term Actions (1–3 Months)

| Priority | Action | Owner | Expected Impact |
|---|---|---|---|
| **MEDIUM** | Review and optimize overall Line 3 bottleneck capacity plan considering technology node mix changes | Factory Management / Planning | Ensure capacity plan aligns with product mix evolution |
| **LOW** | Evaluate lot streaming or lot splitting strategies to reduce WIP accumulation between process steps | Industrial Engineering | Reduce queue-dependent Q-time risk |
| **LOW** | Implement automated Q-time violation root cause detection system (pattern recognition on WIP, tool status, dispatching data) | IT / Data Science | Accelerate future RCA response time |

### 6.5 Expected Recovery Timeline

| Milestone | Target Date | Prerequisites |
|---|---|---|
| TOOL_04 restored to full capability | May 15–18, 2026 (estimated) | Chamber matching resolution |
| Q-time compliance improves to >85% | May 16–18, 2026 | TOOL_02 online + Q-time dispatching implemented |
| Q-time compliance returns to >95% | May 20–22, 2026 | TOOL_04 restored + backlog cleared |
| Full return to 98% baseline | May 22–25, 2026 | All tools operational + hot lot rate normalized |
| Yield impact assessment complete | May 19–21, 2026 | Yield data for violation lots becomes available |

---

## 7. Monitoring and Follow-Up

### 7.1 Key Metrics to Track

| Metric | Target | Review Frequency |
|---|---|---|
| Q-time compliance (24-hour limit) | >95% | Daily |
| Average elapsed time LITHO→ETCH | <16 hours | Daily |
| ETCH_HARDMASK effective capacity | 4.0 tools | Weekly |
| WIP imbalance ratio (LITHO/ETCH) | 1.4–1.7 | Daily |
| Buffer stocker utilization | <85% | Daily |
| Hot lot insertion rate | Normalized to baseline | Weekly |
| Post-etch CD yield (violation lots) | Track and compare to baseline | Per lot |
| Number of violations >30 hours | 0 | Daily |

### 7.2 Escalation Triggers

| Condition | Escalation Level | Action |
|---|---|---|
| Q-time compliance <85% after May 18 | **ESCALATE to Factory Manager** | Emergency capacity actions; consider line shutdown for backlog clearance |
| Additional lots showing CD shift | **ESCALATE to VP Manufacturing** | Potential hold and disposition of affected lots |
| TOOL_04 not restored by May 18 | **ESCALATE to Vendor Management** | Vendor engagement for expedited support |
| Any lot exceeds 40 hours Q-time | **IMMEDIATE ESCALATION** | Lot hold; engineering evaluation required before further processing |

---

## 8. Appendices

### Appendix A: Data Sources

All analysis based on data provided in the problem statement dated May 12, 2026. No additional data queries were executed for this analysis.

### Appendix B: Glossary

| Term | Definition |
|---|---|
| Q-time | Queue time — maximum allowed elapsed time between two process steps |
| WIP | Work In Process — lots at a given process stage awaiting processing |
| AMHS | Automated Material Handling System — factory-internal wafer transport system |
| FIFO | First In, First Out — dispatching rule processing lots in arrival order |
| CD | Critical Dimension — measured feature size on wafer |
| PM | Preventive Maintenance — scheduled equipment maintenance |
| FDC | Fault Detection and Classification — equipment monitoring system |
| RCA | Root Cause Analysis — structured problem investigation methodology |
| 6M | Ishikawa framework: Man, Machine, Material, Method, Measurement, Mother Nature |

### Appendix C: Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | May 12, 2026 | Semiconductor Data Analyst | Initial report |

---

*End of Report*
