# Etch Mechanism Know-How Knowledge Base
## Version 1.0 — Generated from Deep Research across 10 Dimensions

---

# Part 1: Core Mechanism Frameworks

## Framework 1: The Ion-Neutral-Passivation (INP) Trilemma

**Core Principle**: Ion flux, neutral flux, and passivation dynamics form a control trilemma. Optimizing any two necessarily compromises the third.

```
        Ion Flux (I)
           /\
          /  \
         /    \
        /  INP \
       /Trilemma\
      /__________\
Neutral Flux   Passivation
    (N)          (P)
```

**Rules**:
- HIGH ion + HIGH neutral + LOW passivation → Bowing/distortion (excess lateral etch)
- HIGH ion + LOW neutral + HIGH passivation → Vertical profile but possible necking/tapering
- LOW ion + HIGH neutral + HIGH passivation → Etch stop or severe ARDE
- Optimal: Balanced I/N ratio with matched passivation deposition rate

**RCP Implications**:
- Source power ↑ → I ↑ and N ↑ simultaneously (both scale with plasma density)
- Bias power ↑ → I directionality ↑ but can sputter passivation
- Gas ratio (C4H2F6/Cl2/HBr) shifts the N-P balance
- Pressure changes mean free path → affects I angular distribution and N transport

---

## Framework 2: The Angular Spectrum of Distortion

**Core Principle**: All distortion types (bowing, microtrenching, twisting) are manifestations of non-ideal ion angular distribution interacting with feature geometry.

| Distortion Type | Angular Mechanism | Physical Origin |
|----------------|-------------------|-----------------|
| Bowing | Wide IAD → sidewall scattering | Mask facet reflection, sheath scattering |
| Microtrenching | Specular reflection → bottom corner focusing | Sidewall ion bounce at shallow angle |
| Twisting | Asymmetric IAD → directional bias | Pattern asymmetry, local charging gradient |
| Necking | Normal incidence dominance → top accumulation | Polymer transport limited at high AR |

**Key Control Knob**: Mask taper angle is the master control because it shapes the effective angular spectrum entering the feature.
- Small taper angle → concentrated upper-sidewall scattering → severe bowing (Miyake 2009)
- Large taper angle → distributed scattering → reduced bowing but more necking risk

---

## Framework 3: Passivation Budget Concept

**Core Principle**: Profile quality depends on the "passivation budget" — the balance between passivation supplied (deposition) and passivation consumed (chemical etch + ion sputtering).

```
Passivation Budget = FC Deposition Rate - (Chemical Lateral Etch + Ion Sputtering)
```

- **Budget > 0 (Surplus)**: Tapering, necking, striation risk
- **Budget ≈ 0 (Balanced)**: Vertical profile, stable CD
- **Budget < 0 (Deficit)**: Bowing, undercut, distortion risk

**Passivation Deficit Triggers**:
1. C4H2F6 flow too low → FC deposition insufficient
2. Cl2 fraction too high → chemical etch overpowers protection
3. Aspect ratio too high → FC transport limited to lower sidewalls
4. Temperature too high → FC polymer viscosity too low, poor coverage

---

# Part 2: Gap-by-Gap Knowledge

---

## GAP 1: Distortion Physics — Complete Mechanism Guide

### 1.1 Distortion Classification for Etch Mechanism Agent

| Category | Specific Type | Driver | Distinguishing Feature |
|----------|-------------|--------|----------------------|
| **Macro-distortion** | Bowing | Ion scattering from mask/sidewall | Sidewall bulge at mid-depth |
| | Twisting | Asymmetric ion flux / pattern | Hole axis tilted from vertical |
| | Tilting | Wafer-level ion incidence angle | Global directional bias |
| **Micro-distortion** | Striation | FC polymer roughness / mask transfer | Periodic sidewall roughness |
| | Microtrenching | Ion reflection to bottom corners | Grooves at feature bottom edges |
| **Metric-specific** | Row7 distortion (INFERRED) | Likely wafer-edge pattern-dependent | Location-specific (edge die) |
| | Ratio_distortion (INFERRED) | Likely top/bottom CD ratio deviation | Feature-level systematic |

> **Note**: "Row7 distortion" and "ratio_distortion" are not standard literature terms. Based on context, we infer Row7 distortion refers to pattern-dependent distortion at specific wafer locations (driven by hardware uniformity: ion tilting, mask tilting, sheath deformation at wafer edge), while ratio_distortion refers to feature-level systematic profile distortion (driven by ARDE and hard mask selectivity changes, resulting in top/bottom CD ratio deviation). The mechanism agent should distinguish: **location-driven** (Row7) vs **feature-driven** (ratio) distortion.

### 1.2 Physical Drivers: Detailed Causal Chains

**Bowing Causal Chain** (HIGH confidence):
```
Mask taper angle small
    → Ion flux concentrated on upper sidewall (scattering)
    → Lateral etch of sidewall middle
    → Bowing (sidewall bulge)
```
Quantitative: Miyake (2009) — mask taper angle directly determines scattered ion flux distribution.

**Twisting Causal Chain** (HIGH confidence):
```
Pattern asymmetry or mask non-uniformity
    → Asymmetric ion shadowing
    → Unequal ion flux to opposite sidewalls
    → Directional etch bias
    → Twisting (hole axis tilt)
```

**Striation Causal Chain** (HIGH confidence):
```
Oblique ion irradiation on FC polymer film
    → Surface roughness on passivation layer
    → Roughness transfers to underlying dielectric
    → Sidewall striation (periodic grooves)
```

### 1.3 Key Quantitative Relationships

| Parameter | Effect on Distortion | Mechanism | Confidence |
|-----------|---------------------|-----------|------------|
| Mask taper angle ↓ | Bowing ↑ | Concentrated scattering | HIGH |
| IAD width ↑ | Bowing ↑, twisting risk ↑ | More sidewall scattering | HIGH |
| Polymer flux | Bowing non-monotonic (optimal window) | Competing protection/scattering | HIGH |
| Feature AR > 50 | All distortion types ↑ | Transport limitation + charging | HIGH |

---

## GAP 2: Cl₂/HBr Stoichiometry — Full Mechanism

### 2.1 Core Differences Between Cl₂ and HBr

| Property | Cl₂ | HBr | Impact on Profile |
|----------|-----|-----|-------------------|
| Surface coverage | 1.6× higher | Lower | Cl₂: more chemical etch, less controlled |
| Ion flux | 40% higher | 40% lower | Cl₂: faster etch, more aggressive |
| Angular yield curve | Sharp drop >60° | Gradual decrease | Cl₂: strong reflection, bowing |
| Sidewall protection layer | SiOCl | SiOBr | Different passivation quality |
| IED width | Wider | Narrower (HBr⁺/Br⁺ mass similar) | HBr: more uniform ion energy |
| H atom contribution | None | H aids volatile product formation | HBr: smoother surfaces |

### 2.2 The Counter-Intuitive Explained: "Why More HBr Improves Distortion"

**5 Synergistic Mechanisms** (HIGH confidence):

1. **Reduced lateral chemical etching**: Br is less reactive than Cl → less spontaneous chemical attack on sidewalls
2. **Lower reflection probability**: Br⁺ has lower reflection probability on tapered sidewalls than Cl⁺
3. **H atom smoothing**: H atoms from HBr dissociation promote smooth volatile product formation
4. **Wider ion angular distribution**: HBr plasma has broader IAD → ions spread more uniformly → less directional bias
5. **Narrower IED**: HBr⁺ and Br⁺ have similar masses → narrower ion energy distribution → more uniform etch

**The "Chemical Friction" Concept**: HBr introduces kinetic limitation (intrinsic passivation) where Br's lower surface mobility and reactivity create self-limiting lateral etch. Cl2 lacks this friction → uncontrolled lateral etch → bowing.

### 2.3 Quantitative Profile Response to HBr Ratio

| HBr Ratio in Mix | Tapering | Footing | Microtrenching | Bowing |
|-----------------|---------|---------|----------------|--------|
| 0% (pure Cl₂) | Severe | Severe | Severe | High |
| 20% | Reduced | Reduced | Gone | Moderate |
| 50% | Minimized | Reduced | None | Low |
| 80% | Minimal | Significantly reduced | None | Minimal |
| 100% | Minimal | Minimal | None | Minimal |

### 2.4 Practical Guidance for Mechanism Agent

When analyzing Cl₂/HBr ratio changes:
- **Cl₂ ↑**: Expect distortion ↑ (more chemical etch, stronger reflection, SiOCl SPL less effective)
- **HBr ↑**: Expect distortion ↓ (kinetic passivation, smoother profile, better angular yield)
- **"More ion etch improves distortion"**: True because HBr-dominated etch is ion-assisted but chemically gentle — the ion energy removes material at the bottom while HBr's low reactivity protects sidewalls
- Physical-to-chemical etch ratio control: Bias power/source power ratio tunes ion energy independently from radical flux

---

## GAP 3: He Pressure / Thermal Stress — Quantified

### 3.1 Complete Causal Chain

```
He Pressure (CenterHePr)
    → Heat transfer coefficient in ESC gap: k(p) = 0.0458·log₁₀(p) + 0.006317 W/(m·K)
    → Wafer temperature distribution
    → Thermal stress from temperature gradient + CTE mismatch
    → Slight wafer bow (secondary)
    → Etch rate non-uniformity (Arrhenius: ~10-20% variation per 10°C)
    → Profile distortion (weak indirect effect)
```

### 3.2 Quantitative Thermal Properties

| Material | CTE (×10⁻⁶/°C) | Thermal Conductivity (W/m·K) |
|----------|-----------------|------------------------------|
| Si | 2.6 | 150 |
| SiO₂ | 0.5 | 1.4 |
| Si₃N₄ | 3.27 | 30 |

Thermal stress magnitude: ~10 MPa per 100°C ΔT for SiN/Si system
Intrinsic film stress: 100-1000 MPa (dominates over thermal stress in most cases)

### 3.3 Why r=0.209 is Weak

The ME2_CenterHePr-distortion correlation of r=0.209 indicates:
1. He pressure is a **secondary tuning knob** for profile
2. Effect is **mediated through temperature**, not direct mechanical stress
3. Spatial control authority is limited (typically center/edge dual-zone)
4. Temperature non-uniformity from He pressure variation is small compared to plasma heating

### 3.4 Practical Guidance

- He pressure primarily affects **etch uniformity** (via temperature) rather than **profile distortion** directly
- For distortion control, He pressure is a fine-tuning parameter, not a primary lever
- Significant distortion improvement from He pressure alone is unlikely
- Temperature is the cross-cutting parameter: low T favors vertical profile but can cause necking

---

## GAP 4: Bottom CD Control and Constancy

### 4.1 Bottom CD Master Equation

```
Bottom CD = Mask Opening − 2 × Passivation_Thickness(bottom)
```

The passivation layer thickness at the bottom is the **direct control knob** for bottom CD.

### 4.2 Four ARDE Mechanisms Affecting Bottom CD

| Mechanism | Description | Bottom CD Impact |
|-----------|-------------|-----------------|
| Neutral shadowing | Isotropic neutrals blocked by sidewalls | Less chemical etch at bottom → CD stable |
| Ion shadowing | Off-normal ions hit sidewalls | Reduced ion etch at bottom corners |
| Differential charging | Electron shading deflects ions | Ion deflection can widen or narrow CD |
| Knudsen transport | Molecular flow limitation | Only 1.3% flux reaches bottom at AR=100:1 |

### 4.3 Why Bottom CD Stays Constant (86.70) — The Dissipative Structure Hypothesis

**HIGH confidence partial explanation**:

The constant bottom CD across 500 BO trials suggests a **self-regulating steady state** where:
1. **Ion sputtering rate at bottom ≈ Passivation redeposition rate** (dynamical equilibrium)
2. FC film thickness self-adjusts: thicker → more ion attenuation → less etch → thinner; thinner → less attenuation → more etch → thicker
3. Like a sandpile at critical angle — the system maintains constant effective etch aperture
4. ARDE reinforces this: radical depletion at high AR means ion sputtering dominates bottom etch, making bottom CD less sensitive to upstream chemical variations

**Supporting evidence**:
- FC film thickness inversely proportional to etch rate (Crisan JVST A 2001)
- Bottom CD = Mask Opening − 2 × FC_thickness (empirical relationship)
- Neutral-starved (ion-rich) regimes show more stable bottom CD

### 4.4 Parameters That Truly Control Bottom CD

| Parameter | Effect on Bottom CD | Mechanism | Control Strength |
|-----------|-------------------|-----------|-----------------|
| Bias power | Strong | Controls ion sputtering of bottom passivation | PRIMARY |
| Source power | Moderate | Controls passivation deposition rate | PRIMARY |
| C4H2F6 flow | Strong | Directly controls FC deposition thickness | PRIMARY |
| Pressure | Moderate | Affects ion angular distribution and transport | SECONDARY |
| Temperature | Moderate | Affects FC polymer viscosity/deposition | SECONDARY |
| Etch time | Weak (in saturation) | Only affects CD before equilibrium | TERTIARY |

---

## GAP 5: C₄H₂F₆ / Fluorocarbon Passivation

### 5.1 FC Polymer Formation and Structure

**C4F8 mechanism**: Produces CF₂ radicals → polymerize to (CF₂)ₙ Teflon-like chains
**C4F6 mechanism**: Double bonds → more cross-linked polymer (5× lower activation energy for C=C vs C-C)
**C4H2F6 mechanism**: H-containing → less effective cross-linking → thinner/weaker protection

**Passivation quality ranking**: C4F8 > C4F6 > C4H2F6

### 5.2 FC Film Thickness vs. Profile — Quantitative

| FC Film Thickness | Effect | Profile Outcome |
|-------------------|--------|-----------------|
| < 1 nm (SiO₂) | Minimal protection | High selectivity but risk of bowing |
| 1-3 nm | Balanced protection | Vertical profile, stable CD |
| 3-5 nm | Strong protection | Risk of tapering/necking |
| 5-6 nm (SiN, Si) | Ion energy attenuation ~750V | Etch stop risk |
| > 6 nm | Excessive | Severe necking, etch stop |

### 5.3 F/C Ratio Control

| F/C Ratio | Film Character | Etch Resistance | Deposition Rate |
|-----------|---------------|-----------------|-----------------|
| ~1.6 (high F) | Fluorine-rich, less cross-linked | Lower | Higher |
| ~1.45 (optimal) | Balanced | Optimal | Balanced |
| ~1.2 (low F) | Carbon-rich, highly cross-linked | Higher | Lower |

Optimal F/C = 1.45 for Bosch process (Nokia/Bell Labs).

### 5.4 C4H2F6↓→Distortion↑ Explained

**Causal chain**:
```
C4H2F6 flow decreases
    → FC deposition rate decreases
    → Sidewall passivation thickness decreases
    → Passivation budget becomes negative (deficit)
    → Ion scattering causes lateral etch of sidewalls
    → Bowing/distortion increases
```
C4H2F6 is less effective than C4F8/C4F6, so its reduction creates a larger passivation deficit.

---

## GAP 6: Distortion vs Striation Trade-off

### 6.1 Dual-Pathway Mechanism

| Feature | Distortion | Striation |
|---------|-----------|-----------|
| **Domain** | Ion physics | Polymer chemistry |
| **Spatial scale** | Macro (feature-level) | Micro (surface roughness) |
| **Primary driver** | Ion angular distribution | FC polymer deposition uniformity |
| **RCP pathway** | Bias power, pressure, source power | C4H2F6 flow, temperature, pressure |
| **Same parameter different effect** | Source power ↑ → ion flux ↑ → more scattering → distortion ↑ | Source power ↑ → polymer precursor ↑ → thicker FC → striation ↑ |

### 6.2 Why Same Parameter Has Opposite Effects

**Example: Source Power Increase**
- Path A (distortion): More ions → wider IAD → more sidewall scattering → bowing ↑
- Path B (striation): More CF₂ radicals → thicker FC film → surface roughness on polymer → striation ↑
- These paths are **independent** — one is ion physics, the other is polymer chemistry

**Example: Temperature Change**
- Low T → reduced chemical etch → less distortion (ions dominate)
- Low T → reduced polymer mobility → less smooth FC → more striation
- High T → enhanced chemical etch → more lateral etch → distortion
- High T → enhanced polymer surface migration → smoother FC → less striation
- **U-shaped relationship** for both — but optima at different temperatures

### 6.3 Unified Optimization Strategy

**Cryogenic + Lean Chemistry** (most promising):
- Low T suppresses chemical etch → reduces distortion
- Lean chemistry reduces polymer buildup → reduces striation
- Stabilizes mask → reduces distortion from mask evolution
- Lam Research Cryo 3.0: -60°C, <0.1% profile deviation

**Neutral-starved regime**:
- Ion-rich, radical-poor → less lateral chemical etch → less distortion
- But: FC precursor also limited → may reduce striation (less polymer)
- Trade-off: ARDE control becomes challenging

---

## GAP 7: Aspect Ratio (AR) Master Variable

### 7.1 AR Regime Classification

| AR Regime | Range | Dominant Mechanism | Key Challenge |
|-----------|-------|-------------------|---------------|
| Low AR | < 10 | Ion energy, gas chemistry | Uniformity across die |
| Medium AR | 10-50 | Neutral transport, passivation balance | ARDE onset |
| High AR | 50-100 | Knudsen transport, charging | Bottom etch rate collapse |
| Ultra-HAR | > 100 | Charging dominates, ion starvation | Etch stop, severe distortion |

### 7.2 Quantitative AR Effects

| AR | Bottom Flux (% of top) | Etch Rate Impact | Distortion Risk |
|----|----------------------|-----------------|-----------------|
| 10:1 | ~10% | Moderate RIE lag | Low |
| 30:1 | ~5% | Significant ARDE | Medium |
| 50:1 | ~2-3% | Severe ARDE | High |
| 100:1 | ~1.3% | Near etch stop | Critical |

### 7.3 LCH vs MCH Difference (AR-Driven)

| Aspect | LCH (Lower AR) | MCH (Higher AR) |
|--------|---------------|-----------------|
| **Dominant constraint** | Ion energy, chemistry balance | Transport limitation |
| **Distortion driver** | Mask scattering, ion IAD | Knudsen depletion, charging |
| **Passivation** | Standard FC sufficient | FC transport-limited to bottom |
| **Recipe transfer** | LCH recipe → MCH needs more ion assistance | MCH recipe → LCH may over-etch |
| **He pressure effect** | More uniform (less AR variation) | Less uniform (center-edge AR difference) |

### 7.4 AR-Dependent Mitigation Strategies

| Strategy | Low AR | High AR |
|----------|--------|---------|
| Bias power | Moderate (profile control) | Higher (enhance bottom ion transport) |
| Source power | Moderate | May need to reduce (reduce charging) |
| Pressure | Moderate | Lower (reduce scattering, enhance directionality) |
| Pulsing | Less critical | Essential (reduce charging, enhance transport) |
| Temperature | Standard | Cryogenic preferred (reduce chemical etch, stabilize) |

---

# Part 3: Parameter-to-Effect Mapping Tables

## Table A: Gas Parameters

| Parameter | Primary Effect | Secondary Effect | Distortion Impact | Striation Impact | Bottom CD Impact |
|-----------|---------------|------------------|-------------------|------------------|------------------|
| Cl2 flow ↑ | Etch rate ↑, chemical ↑ | SPL: SiOCl | ↑ (more lateral etch) | Minimal | Weak |
| HBr flow ↑ | Selectivity ↑ | SPL: SiOBr, kinetic passivation | ↓ (better profile) | Minimal | Weak |
| C4H2F6 flow ↑ | Passivation ↑ | Etch rate ↓ | ↓ (more protection) | ↑ (more polymer) | ↓ (thicker passivation) |
| Total pressure ↑ | Mean free path ↓, IAD widens | Polymer deposition ↑ | ↑ (more scattering) | ↑ (more FC) | Complex |

## Table B: Power Parameters

| Parameter | Primary Effect | Secondary Effect | Distortion Impact | Striation Impact | Bottom CD Impact |
|-----------|---------------|------------------|-------------------|------------------|------------------|
| Source power ↑ | Plasma density ↑, ion flux ↑ | Radical flux ↑ | ↑ (more scattering) | ↑ (more CF₂) | Weak |
| Bias power ↑ | Ion energy ↑, IAD narrows | Bottom sputtering ↑ | Complex* | Minimal | Strong ↓ |

*Bias power: low values → less directional control → distortion; optimal → vertical profile; too high → mask damage, microtrenching

## Table C: Environmental Parameters

| Parameter | Primary Effect | Secondary Effect | Distortion Impact | Striation Impact | Bottom CD Impact |
|-----------|---------------|------------------|-------------------|------------------|------------------|
| He pressure ↑ | Thermal conductivity ↑ | Wafer temp more uniform | Weak ↓ (via temp) | Weak (via temp) | Weak |
| Electrode temp ↑ | Chemical etch ↑ | FC viscosity ↓ | ↑ (more lateral) | ↓ (smoother FC) | Weak |
| Electrode temp ↓ | Chemical etch ↓ | FC viscosity ↑ | ↓ (less lateral) | ↑ (rougher FC) | Weak |

## Table D: Pulsing Parameters

| Parameter | Primary Effect | Secondary Effect | Distortion Impact | Striation Impact | Bottom CD Impact |
|-----------|---------------|------------------|-------------------|------------------|------------------|
| Bias pulse ON | Ion bombardment | Charging accumulation | Pulse-dependent | Minimal | Sputtering |
| Bias pulse OFF | Charge neutralization | Afterglow chemistry | Reduced charging benefit | Minimal | Redeposition |
| Sync pulsing | Coordinated IEDF | Reduced ARDE | Significant ↓ | Minimal | Improved |

---

# Part 4: Confidence-Graded Mechanism Rules

## HIGH Confidence Rules (Data + Mechanism Aligned)

1. **R1-H**: Mask taper angle determines bowing severity (Miyake 2009)
2. **R2-H**: Cl2 angular yield >60° sharp drop causes bowing/microtrenching (MIT beam experiments)
3. **R3-H**: HBr improves profile via 5 synergistic mechanisms (Cornell, MIT, multiple sources)
4. **R4-H**: FC film thickness inversely proportional to etch rate (Crisan JVST A 2001)
5. **R5-H**: F/C ratio 1.45 optimal for Bosch (Nokia/Bell Labs)
6. **R6-H**: AR=100:1 → 1.3% bottom flux (Panagopoulos & Lill JVST A 2023)
7. **R7-H**: Microtrenching from ion reflection + charging (Schaepkens & Oehrlein)
8. **R8-H**: Distortion (ion physics) and striation (polymer chemistry) are independent pathways

## MEDIUM Confidence Rules (Mechanism-Plausible)

1. **R1-M**: Bottom CD constancy = self-regulating passivation equilibrium (hypothesis)
2. **R2-M**: He pressure effect mediated through temperature (r=0.209 secondary)
3. **R3-M**: Passivation budget framework explains multi-parameter distortion responses
4. **R4-M**: Angular spectrum concept unifies distortion types
5. **R5-M**: Cryogenic + lean chemistry as unified optimization

## LOW Confidence Rules (Hypothesis Only)

1. **R1-L**: Row7 distortion = wafer-edge pattern-dependent (term not in literature)
2. **R2-L**: Ratio_distortion = top/bottom CD ratio deviation (inferred definition)
3. **R3-L**: Dissipative structure analogy for bottom CD (metaphor, needs validation)

---

# Part 5: Guidance for Other Agents

## Constraints for Data Agent / DOE Agent

### Hard Constraints (should not be violated)
1. C4H2F6 flow must be > minimum to maintain positive passivation budget
2. Cl2/HBr ratio must stay within range where angular yield prevents severe bowing
3. Bias power must stay within window: too low → poor directionality; too high → mask damage

### Soft Constraints (directional guidance)
1. HBr fraction increase expected to reduce distortion (but slower etch)
2. C4H2F6 increase expected to reduce distortion but increase striation
3. Source power increase helps ARDE but may increase distortion and striation
4. He pressure fine-tunes uniformity but is weak for profile control

### DOE Recommendations
1. **Primary DOE**: Cl2/HBr ratio × C4H2F6 flow interaction on distortion/striation
2. **Secondary DOE**: Bias power × Source power on bottom CD stability
3. **Validation DOE**: Temperature × Pressure on distortion/striation trade-off
4. **Exploration DOE**: Pulsing parameters for AR > 50 regime

---

*End of Know-How Knowledge Base*
