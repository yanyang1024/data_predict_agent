# Etch Mechanism Agent — File Analysis

## File Inventory

| File | Type | Purpose |
|------|------|---------|
| `etch-multi-agent/SKILL.md` | Skill orchestration | Multi-agent coordination rules, evidence levels, dispatch tree |
| `etch-mechanism.md` | Subagent definition | Mechanism agent prompt, workflow, output format |
| `etch_mechanism_assumption.md` | Assumptions | Supported/unsupported reasoning, confidence definitions |
| `mechanism_input_output_contract.md` | I/O contract | JSON input/output schema |
| `mechanism_known_limitations.md` | Limitations | Phase 0 status, mock-only, risk warnings |
| `rcp_parameter_taxonomy.md` | Parameter taxonomy | RCP parameter groups and their typical impacts |
| `etch-mechanism-mock.ts` | Mock tool | Placeholder tool returning only generic hints |

## Current Mechanism Agent Capabilities

### Supported Reasoning (from assumptions)
- Plasma power impact on ion energy/CD
- Pressure impact on mean free path/uniformity
- Gas flow ratio impact on selectivity
- Bias-related ion energy impact
- Selectivity and profile tendency (qualitative)
- CD bias risk (directional)
- Microloading/pattern dependency hypothesis

### Output Structure
- Mechanism Summary
- Parameter-to-Effect Mapping (generic)
- Process Window Boundaries (hypothetical)
- Root-Cause Hypotheses
- Constraints for Optimization/DOE
- Confidence labels (HIGH/MEDIUM/LOW)

## Identified Gaps (7 Critical Mechanism Deficits)

### Gap 1: Distortion Physics
- Current: "ion energy → distortion" vague link
- Missing: Row7 distortion vs ratio_distortion distinct drivers
- Missing: Sidewall bowing mechanics in HAR etch
- Missing: Nanowire template deformation physics

### Gap 2: Cl₂/HBr Stoichiometry
- Current: Cl₂↑→distortion↑, HBr↓→distortion↑ (correlational)
- Missing: Why increased ion etch ratio improves distortion (counter-intuitive)
- Missing: Ion-to-chemical etch balance quantification
- Missing: Physical-to-chemical etch ratio control

### Gap 3: He Pressure / Thermal Stress
- Current: "He↑→thermal conduction↑→stress release" (hand-waving)
- Missing: Quantitative He pressure → temperature → stress relationship
- Missing: Backside heating effect on etch profile
- Missing: Thermal stress coefficient for SiN/SiO₂

### Gap 4: Bottom CD Constancy
- Current: No explanation for constant 86.70 across 500 BO trials
- Missing: Which parameters truly control bottom_cd
- Missing: Bottom CD control via ion energy mechanism
- Missing: ARDE (Aspect Ratio Dependent Etching) role

### Gap 5: C₄H₂F₆ Passivation Layer
- Current: "F-based passivation → etch suppression" (surface-level)
- Missing: Sidewall passivation thickness vs distortion quantitative link
- Missing: Fluorocarbon polymer thickness control
- Missing: C/F ratio impact on sidewall protection

### Gap 6: Distortion vs Striation Trade-off
- Current: Observed multi-parameter effects on both, but no mechanism
- Missing: Why same parameter affects two responses differently
- Missing: Competing mechanism pathways

### Gap 7: Aspect Ratio (AR) Effects
- Current: Completely unaddressed
- Missing: AR impact on distortion/striation/CD uniformity
- Missing: LCH vs MCH key difference (AR is different)
- Missing: Reactant depletion in high AR, micro-trenching, notch formation

## Cross-File Knowledge Map

| Knowledge Area | Primary Source | Gap Severity |
|----------------|---------------|--------------|
| Basic plasma physics | etch-mechanism.md, assumptions | Low |
| Parameter grouping | rcp_parameter_taxonomy.md | Low |
| Ion energy → CD | etch-mechanism.md | Medium |
| Distortion root-cause | etch-mechanism.md | Critical |
| Passivation chemistry | None | Critical |
| Thermal stress | None | Critical |
| AR-dependent effects | None | Critical |
| Trade-off mechanisms | None | Critical |

## Consolidated Theme List (for Phase 2 Dimension Decomposition)

1. **Distortion Physical Mechanics** — Bowing, deformation drivers, HAR effects
2. **Cl₂/HBr Etch Chemistry** — Stoichiometry, ion/chemical balance, profile control
3. **Fluorocarbon Passivation** — C₄H₂F₆ role, sidewall protection, thickness control
4. **Thermal Management** — He backside heating, thermal stress, temperature gradients
5. **CD Control Mechanisms** — Bottom CD control, ARDE, ion energy impact
6. **Multi-Response Trade-offs** — Distortion vs striation competing pathways
7. **Aspect Ratio Effects** — HAR etch challenges, reactant depletion, uniformity
8. **Plasma Physics Foundations** — Sheath dynamics, ion angular distribution, energy
9. **Profile Evolution** — Sidewall profile, micro-trenching, notch formation
10. **Process Window Boundaries** — Quantitative constraints, validated ranges
