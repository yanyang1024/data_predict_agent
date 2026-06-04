# Etch Multi-Agent Usage Examples

## Example 1: Parameter Optimization

**User input:**
```
Layer type: LCH
Current RCP: pressure=50mTorr, source_power=800W, bias_power=120W
Target: reduce Row1 stripe from 15nm to <10nm, keep Bias CD within 80-100nm
Historical data: available at data/history_lch.xlsx
```

**Expected flow:**
1. Orchestrator detects `parameter_optimization`
2. Parallel: Mechanism (qualitative power/pressure effect) + Data (model + optimize)
3. Sequential: Constraint checks data agent output
4. Integration: evidence grading → Rank 1 candidate
5. Report: full recommendation + risk + next steps

---

## Example 2: DOE Design

**User input:**
```
Need a screening DOE for a new MCH recipe
4 factors (A/B/C/D), 2 levels each, max 20 runs
Responses: Row1 stripe, Bias CD
```

**Expected flow:**
1. Orchestrator detects `doe_design`
2. DOE Agent: recommend fractional factorial (2^(4-1) = 8 runs with some resolution)
3. Generate coded matrix → randomize → CSV output
4. Report: DOE plan + analysis protocol

---

## Example 3: Root-Cause Analysis

**User input:**
```
Row7 distortion rate jumped from 5% to 15% after increasing bias power from 100W to 140W
Layer: MCH, recipe: MCH_std_v3
No historical model available
```

**Expected flow:**
1. Orchestrator detects `mechanism_analysis`
2. Parallel: Mechanism (ion energy / profile risk) + Literature (similar cases)
3. No data agent (no historical model)
4. Integration: evidence Level C (mechanism + literature only)
5. Report: hypotheses + suggested DOE validation
