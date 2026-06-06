# Etch Mechanism Cross-Verification Report

## Verification Summary
10 dimension reports analyzed, 200+ evidence blocks cross-referenced.

---

## High Confidence Findings (Confirmed by ≥2 dimensions from independent sources)

### HC-01: Ion Scattering is the Primary Distortion Driver
- **Confirmed by**: Dim01, Dim07, Dim08, Dim09
- **Evidence**: UT Austin lecture notes [^4^], Miyake (JJAP 2009) [^5^], Lam Research feature-scale model (JJAP 2023) [^2^]
- **Mechanism**: Mask facet/sidewall ion scattering → lateral etching of sidewall middle → bowing. Mask taper angle controls scattering distribution.
- **Confidence**: **HIGH**

### HC-02: Cl2/HBr Etch Yield Angular Dependence Explains Profile Differences
- **Confirmed by**: Dim02, Dim01, Dim09
- **Evidence**: Jin, Vitale & Sawin (MIT/AVS 2002) [^5^], Cornell NNCI [^3^]
- **Mechanism**: Cl2 etch yield drops rapidly >60° → strong ion reflection → bowing + microtrenching. HBr yield decreases gradually → less reflection → vertical profiles.
- **Confidence**: **HIGH**

### HC-03: HBr Improves Distortion via 5 Synergistic Mechanisms
- **Confirmed by**: Dim02, Dim01, Dim06
- **Evidence**: MIT beam experiments [^5^], Cornell chamber studies [^3^], TEL/SPIE (2023) [^197^]
- **Mechanisms**: (1) Reduced chemical lateral etching, (2) Lower Br+ reflection probability, (3) H atom smoothing effect, (4) Wider ion angular distribution, (5) Narrower ion energy distribution
- **Confidence**: **HIGH**

### HC-04: Coburn-Winters Model Describes ARDE Neutral Transport
- **Confirmed by**: Dim04, Dim07, Dim08
- **Evidence**: Coburn & Winters (APL 1989), Panagopoulos & Lill (JVST A 2023) [^52^][^56^]
- **Mechanism**: F(AR)/F(0) = K/(K + Sn - K*Sn); at AR=100:1 only 1.3% flux reaches bottom
- **Confidence**: **HIGH**

### HC-05: FC Film Thickness Inversely Proportional to Etch Rate
- **Confirmed by**: Dim05, Dim04, Dim02
- **Evidence**: Crisan et al. (JVST A 2001) [^421^], Jang et al. (2012) [^370^], Schaepkens et al.
- **Mechanism**: 5nm FC film attenuates ion energy by ~750V; thicker film → lower etch rate
- **Confidence**: **HIGH**

### HC-06: F/C Ratio ~1.45 Optimal for Bosch Passivation
- **Confirmed by**: Dim05, Dim10
- **Evidence**: Nokia/Bell Labs [^16^], Lam Research process data
- **Mechanism**: Low F/C films have higher etch resistance; high F/C films etch faster; 1.45 balances deposition/etch
- **Confidence**: **HIGH**

### HC-07: Micro-trenching from Ion Reflection + Charging
- **Confirmed by**: Dim09, Dim01, Dim08
- **Evidence**: Schaepkens & Oehrlein (Appl. Phys. Lett. 1998) [^76^], MIT numerical simulations [^52^]
- **Mechanism**: Sidewall ion reflection focuses ions into bottom corners; differential charging enhances deflection
- **Confidence**: **HIGH**

### HC-08: He Pressure → Temperature → Etch Uniformity (Indirect)
- **Confirmed by**: Dim03, Dim04
- **Evidence**: k(p) = 0.0458*log10(p) + 0.006317 W/(m·K); 10°C ΔT → ~20% etch rate non-uniformity
- **Mechanism**: He pressure modulates chuck thermal conductivity → wafer temperature → Arrhenius-rate non-uniformity
- **Confidence**: **HIGH**

### HC-09: Distortion (Ion Physics) and Striation (Polymer Chemistry) are Dual-Pathway
- **Confirmed by**: Dim06, Dim01, Dim05
- **Evidence**: Lam Research (JJAP 2023), JJAP (2019), TEL/SPIE (2023)
- **Mechanism**: Distortion driven by ion scattering physics; striation driven by FC polymer deposition chemistry. Same RCP parameter affects both through independent pathways.
- **Confidence**: **HIGH**

### HC-10: Neutral-Starved (Ion-Rich) Regime Mitigates Distortion
- **Confirmed by**: Dim06, Dim07, Dim04
- **Evidence**: TEL/SPIE (2023), Lam Research ARDE studies
- **Mechanism**: Low neutral/ion ratio reduces distortion (less lateral chemical etch) but challenges ARDE control
- **Confidence**: **HIGH**

---

## Medium Confidence Findings (1 authoritative source)

### MC-01: He Pressure-Distortion r=0.209 is Secondary Effect
- **Source**: Dim03 analysis
- **Rationale**: Direct He→distortion coupling weak; effect mediated through temperature non-uniformity
- **Confidence**: **MEDIUM**

### MC-02: 4 Hypotheses for Constant Bottom CD (86.70)
- **Source**: Dim04 analysis
- **Hypotheses**: (1) Self-limiting passivation equilibrium, (2) Ion-neutral synergy, (3) Neutral-starved regime, (4) Process-induced self-regulation
- **Confidence**: **MEDIUM** (no direct experimental validation)

### MC-03: C4H2F6 Less Effective than C4F8/C4F6 for Passivation
- **Source**: Dim05
- **Rationale**: H-containing FC produces less cross-linked polymer; ranking: C4F8 > C4F6 > C4H2F6
- **Confidence**: **MEDIUM**

### MC-04: Cryogenic + Lean Chemistry as Unified Solution
- **Source**: Dim10, Dim06
- **Evidence**: Lam Research Cryo 3.0, 10μm depth <0.1% profile deviation
- **Confidence**: **MEDIUM** (industry data promising but limited peer review)

---

## Low Confidence Findings

### LC-01: Row7 Distortion vs Ratio_Distortion Definitions
- **Source**: Dim01 inference
- **Note**: These terms not found in open literature; inferred as hardware-uniformity vs profile-level distortion metrics
- **Confidence**: **LOW**

### LC-02: Mechanical Stress Model for TSV Notching
- **Source**: Dim09
- **Note**: Possible contribution but poorly characterized
- **Confidence**: **LOW**

---

## Conflict Zones

### CZ-01: Micro-trenching Bias Power Effect (Material Dependent)
- **Conflict**: Bias power increase → deeper microtrench in SiO2 but → less microtrench in SiC
- **Resolution**: Material-dependent; more anisotropic etch in SiC smooths sidewalls, while SiO2 sputtering enhances reflection
- **Status**: **RESOLVED** (material specificity)

### CZ-02: ARDE Dominant Mechanism
- **Conflict**: Neutral depletion vs ion transport vs charging — which dominates?
- **Resolution**: Regime-dependent; at high pressure neutral depletion dominates, at low pressure ion shadowing dominates, charging significant with insulating materials
- **Status**: **RESOLVED** (regime-dependent)

### CZ-03: Temperature Effect on LER (U-shaped)
- **Conflict**: Some studies show lower T improves smoothness; others show optimum at 15-20°C
- **Resolution**: U-shaped relationship — competing mechanisms (reduced chemical etch vs polymer mobility)
- **Status**: **PARTIALLY RESOLVED**

### CZ-04: Pure Cl2 vs Pure HBr Etch Yield
- **Conflict**: Dim02 reports "very similar yields" from NASA report; Dim01 implies different sputtering behavior
- **Resolution**: Absolute yields similar at normal incidence; angular dependencies fundamentally different
- **Status**: **RESOLVED** (different metrics)
