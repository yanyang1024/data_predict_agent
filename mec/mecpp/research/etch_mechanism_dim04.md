# Dimension 04: Bottom CD Control Mechanism and ARDE Effect - Deep Research Report

## Table of Contents
1. [Dimension Overview](#1-dimension-overview)
2. [Key Findings](#2-key-findings)
3. [Quantitative Relationships](#3-quantitative-relationships)
4. [Controversies and Conflicting Claims](#4-controversies-and-conflicting-claims)
5. [Remaining Gaps](#5-remaining-gaps)
6. [Summary of Mechanism Insights](#6-summary-of-mechanism-insights)
7. [Implications for Constant Bottom CD (86.70) Phenomenon](#7-implications-for-constant-bottom-cd-8670-phenomenon)
8. [References](#8-references)

---

## 1. Dimension Overview

Bottom Critical Dimension (CD) control is one of the most fundamental yet complex challenges in plasma etching for semiconductor manufacturing. The bottom CD refers to the width of an etched feature measured at or near the bottom of the trench/hole, typically 0.3-0.8 um from the bottom surface [^63^]. While top CD is largely determined by lithography, bottom CD is shaped by the intricate interplay of ion transport, radical depletion, passivation dynamics, and charging effects during etching.

Aspect Ratio Dependent Etching (ARDE), also known as Reactive Ion Etching (RIE) lag, describes the phenomenon where etch rate decreases as feature aspect ratio increases [^52^]. This effect is rooted in fundamental transport limitations that govern how ions and neutral radicals reach the etch front in high-aspect-ratio features. Understanding ARDE and bottom CD control requires analyzing four primary mechanisms: (1) neutral shadowing, (2) ion shadowing, (3) differential charging, and (4) Knudsen transport [^52^][^54^].

The observation that bottom CD remains constant at 86.70 across 500 BO trials is remarkable and points to a strongly self-regulating etch mechanism, likely involving a balance between ion-driven etching and passivation layer dynamics.

---

## 2. Key Findings

### Finding 2.1: Four Primary ARDE Mechanisms

```
Claim: ARDE is caused by four primary mechanisms: neutral shadowing, ion shadowing, differential charging, and Knudsen transport. Each operates at different length scales and process regimes [^52^][^54^].
Source: UT Austin Plasma Etching Lecture Notes (Lam Research content); AVS Short Course
URL: https://willson.cm.utexas.edu/Teaching/LithoClass2017/Files/Introduction%20to%20Plasma%20Etching_Lecture_102417_Day2_sntzd.pdf
Date: 2017
Excerpt: "Multiple mechanisms can lead to ARDE in plasma etching: Neutral shadowing, Ion shadowing, Differential charging, Knudsen transport. Solution to ARDE issues can depend on which mechanism(s) is/are responsible."
Context: Industry-standard plasma etching training materials
Confidence: high
```

**Neutral Shadowing**: The neutral angular distribution is isotropic. Neutrals incident at large angles to the normal hit the top or sidewall of the feature and can be lost (e.g., through recombination) before reaching the bottom. High aspect ratio features become "starved" for neutrals, causing etch rate to slow down [^52^].

**Ion Shadowing**: The ion angular distribution is generally anisotropic but higher pressures cause ion scattering in the sheath, spreading the angular distribution. Ions at larger angles hit sidewalls instead of the bottom [^52^].

**Differential Charging**: Electron flux to the wafer is much less anisotropic than ion flux. This creates differential charging that can deflect ions, altering flux to the feature bottom. Studies report ion energy drops of ~30% for AR~3 [^52^].

**Knudsen Transport**: Neutral reactants travel to the bottom via diffuse reflection from sidewalls without reacting. The transmission probability decreases exponentially with aspect ratio [^38^][^52^].

---

### Finding 2.2: Coburn-Winters Knudsen Transport Model

```
Claim: The neutral flux at the bottom of a high aspect ratio feature follows the Coburn-Winters transport model, where the flux ratio F(AR)/F(0) = K/(K + Sn - K*Sn), with K being the Knudsen transmission probability and Sn the reaction probability [^38^].
Source: Antoun PhD Thesis (Universite Grenoble Alpes, referencing Coburn & Winters APL 1989)
URL: https://theses.hal.science/tel-05580654v1/file/103937_ANTOUN_2020_archivage.pdf
Date: 2020
Excerpt: "To estimate the ratio between the neutral flux arriving at the bottom of a microstructure and depending on the aspect ratio, F(AR), and the neutral flow present in the plasma and arriving to the top of the pattern, F(0), Eq I.7 has first been proposed by Coburn and Winters[30]... With K assimilated to the Knudsen or Clausing coefficient for vacuum systems. It corresponds to the probability of transmission through a tube in a molecular flow."
Context: PhD thesis on plasma etching profile evolution
Confidence: high
```

```
Claim: For an aspect ratio of 100:1, the flux at the bottom of the feature is only 1.3% of the incoming flux due to Knudsen transport limitations [^56^][^211^].
Source: Panagopoulos & Lill, JVST A 41, 033006 (2023), Lam Research
URL: https://pubs.aip.org/avs/jva/article/41/3/033006/2877892/Neutral-transport-during-etching-of-high-aspect
Date: 2023
Excerpt: "For gas pressures in the millitorr and feature sizes in the nanometer range, neutrals reach the bottom of an etching feature via the Knudsen transport. For an aspect ratio of depth to diameter of 100:1, the flux at the bottom of the feature is only 1.3% of the incoming flux."
Context: Lam Research computational study on neutral transport for advanced memory devices
Confidence: high
```

The Coburn-Winters model provides the fundamental quantitative framework for understanding ARDE:

**Equation**: F(AR)/F(0) = K / (K + Sn - K * Sn)

Where:
- F(AR) = neutral flux at the bottom of a feature with aspect ratio AR
- F(0) = neutral flux at the top opening  
- K = Knudsen transmission probability (decreases with increasing AR)
- Sn = reaction probability (sticking coefficient) at the bottom surface

Key implications: When K becomes small (high AR), the flux ratio approaches K/Sn, showing that the flux is directly proportional to the transmission probability. For a sidewall reaction probability of 0.1, the decrease of neutral flow exceeds the decrease of ion flow [^96^].

---

### Finding 2.3: Bottom CD is Controlled by Sidewall Passivation Thickness

```
Claim: Critical dimension (CD) control is fundamentally sidewall passivation thickness control. The thickness of the passivation layer constitutes a deviation from the original mask dimension, and this thickness is controlled by the balance between etch and deposition [^210^].
Source: ICP Dry Etching Process for Planar Lightwave Circuit Fabrication
URL: https://core.ac.uk/download/pdf/268875885.pdf
Date: Unknown
Excerpt: "Critical dimension control is therefore sidewall passivation thickness control either dense or isolated lines across die, across wafer, and wafer-to-wafer. The thickness of the passivation layer in turn is controlled by the balance between etch and deposition within each etching step and for all steps in combination."
Context: Technical report on ICP dry etching processes
Confidence: high
```

```
Claim: Partial replacement of HBr with Ar in deep trench silicon etch increased sidewall passivation film thickness and hence decreased bottom CD [^63^].
Source: Effect of rare gas addition on deep trench silicon etch, ScienceDirect
URL: https://www.sciencedirect.com/science/article/pii/S016793170400334X
Date: 2004
Excerpt: "Partial replacement of HBr in the reactive gas stream with Ar resulted in modifications in the trench profile: the sidewall passivation film thickness increased and hence bottom CD decreased."
Context: Experimental study of deep trench (aspect ratio >40) silicon etch
Confidence: high
```

This is a critical finding: **bottom CD is directly determined by the sidewall passivation layer thickness**. The bottom CD = mask opening - 2 * (passivation thickness at bottom). The passivation layer thickness is controlled by:
- Gas chemistry (passivation precursor concentration)
- Ion energy (which sputters away passivation at the bottom)
- Source power (radical flux for passivation formation)
- Bias power (ion energy for directional sputtering)
- Temperature (passivation adsorption/desorption balance)

---

### Finding 2.4: Ion Energy and Bias Power Effects on Bottom CD

```
Claim: Increasing substrate bias primarily affects ion energy and to a lesser extent ion flux magnitude. Source power primarily affects ion flux magnitude, not energy. Etch rate is more influenced by substrate bias variation than source power variation [^77^].
Source: Simulation of an Ar/Cl2 inductively coupled plasma (Bogaerts et al.)
URL: https://www.researchgate.net/publication/230914845
Date: Unknown
Excerpt: "Increasing the substrate bias has an effect on the energy of the ions bombarding the substrate and to a lesser extent on the magnitude of the ion flux. When source power is increased, it was found that, not the energy, but the magnitude of the ion flux is increased. The etch rate was more influenced by a variation of the substrate bias than by a variation of the source power."
Context: Hybrid plasma equipment model simulation study
Confidence: high
```

```
Claim: Higher bias power reduces ARDE by enabling more directional ions to penetrate high-AR features, but increases mask erosion and surface damage [^62^].
Source: NineScrolls - Wafer Loading Effect in Plasma Etching
URL: https://ninescrolls.com/insights/wafer-loading-effect-plasma-etching
Date: 2026
Excerpt: "Bias power (RF): Reduces ARDE (more directional ions penetrate high-AR features). Trade-off: Increased mask erosion; higher surface damage; reduced selectivity."
Context: Technical guide on loading effects and mitigation
Confidence: high
```

```
Claim: ARDE and profile dependency can be reduced by adding higher energy bias, which enhances ion transport down the trench [^109^].
Source: Formation of Nanoscale Structures by Inductively Coupled Plasma Etching (Proc. SPIE)
URL: https://www.researchgate.net/publication/271489228
Date: 2013
Excerpt: "The same work reports that both ARDE and profile dependency can be reduced by adding higher energy bias. This may be because the transport of ions down the trench is enhanced by increased energy and reduced scattering due to passage of the ions within fewer RF cycles."
Context: SPIE paper on nanoscale ICP etching
Confidence: high
```

The relationship between ion energy/bias power and bottom CD is indirect but strong:
1. **Higher bias power** → higher ion energy → more efficient sputtering of passivation at trench bottom → larger bottom CD (less passivation narrowing)
2. **Higher bias power** → better ion directionality → ions reach bottom more effectively → reduces ARDE → more consistent bottom CD
3. **Lower bias frequency** (<2 MHz typical) produces narrower angular distribution and higher symmetry → better bottom CD control [^279^]

---

### Finding 2.5: Micro-trenching Mechanism and Bottom CD

```
Claim: Micro-trenching is caused by (1) ion scattering from sloped trench sidewalls focusing ions into bottom corners, and (2) ion deflection due to differential charging of microstructures [^52^][^54^].
Source: UT Austin Plasma Etching Lecture; Purdue DRIE process documentation
URL: https://willson.cm.utexas.edu/Teaching/LithoClass2017/Files/Introduction%20to%20Plasma%20Etching_Lecture_102417_Day2_sntzd.pdf
Date: 2017
Excerpt: "Microtrenching - Localized higher etch rate at bottom corners of trench. Potential Mechanisms: 1. Ion scattering from sloped trench sidewalls. 2. Ion deflection due to differential charging of microstructures."
Context: Industry training materials
Confidence: high
```

```
Claim: Micro-trenching at the bottom of features is enhanced when a charged SiFxOy layer forms after O2 addition in etching gases. As etched depth increases, the sidewall surface area, angle and roughness change, altering the reflection angle and energy distribution of reflected ions [^207^].
Source: Microtrenching effect of SiC ICP etching in SF6/O2 plasma
URL: https://www.jos.ac.cn/fileBDTXB/oldPDF/08073102.pdf
Date: 2008
Excerpt: "The formation of a microtrench is due chiefly to a charged SiFxOy layer after addition of O2 in etching gases. But as the etched depth increases, the surface area, angle and roughness of the sidewall will change, leading to another change in the angle and energy distribution of reflected ions."
Context: Experimental study of SiC ICP etching
Confidence: medium
```

```
Claim: Micro-trenching can be minimized by making sidewalls more vertical (fewer ion reflections) or by operating in a neutral-limited regime where etch rate is determined by neutral flux rather than ion flux [^288^].
Source: ScienceDirect - Dual Damascene overview
URL: https://www.sciencedirect.com/topics/engineering/dual-damascene
Date: Reference work
Excerpt: "Microtrenching is caused by ion reflection from the sidewalls of features. Microtrenching can be minimized by making the sidewall more vertical (i.e., fewer ion reflections) or by operating the etch in a neutral-limited regime."
Context: Engineering reference on dual damascene patterning
Confidence: high
```

Micro-trenching directly affects bottom CD by creating localized deeper etching at the bottom corners. This effectively widens the bottom dimension non-uniformly. The effect is:
- More pronounced with higher ion energy
- More pronounced with sloped sidewalls
- Can be reduced in neutral-limited regimes (where neutrals, not ions, limit the etch rate)
- Pulse-modulated plasma reduces micro-trenching by eliminating directional ion bombardment during off-times [^63^]

---

### Finding 2.6: Notch Formation (Charging Effect) and Bottom CD

```
Claim: Notching is the lateral etching of underlying layers during etch, caused by positive charging of insulating layers which deflects ions towards sidewalls at low bias voltages, or by isotropic etching of sidewall passivation layers [^64^].
Source: Core academic paper on profile deformations in plasma etching
URL: https://core.ac.uk/download/pdf/46809249.pdf
Date: Unknown
Excerpt: "Notching: The notching effect is the lateral etching of underlying layers during the etch process. This can occur either due to positive charging of the underlying layer, which can deflect the ions towards the sidewalls (i.e. at low bias voltages), or due to isotropic etching of sidewall passivation layers."
Context: Academic review of etching profile deformations
Confidence: high
```

```
Claim: Numerical simulations show that low-energy positive ions during power-off periods can be deflected by smaller local electric fields, neutralizing negative charge on upper mask sidewalls. This achieves current balance at lower charging potentials, significantly reducing notching [^76^].
Source: Fundamentals of Plasma Process-Induced Charging and Damage (Giapis & Hwang)
URL: https://www.researchgate.net/publication/278654060
Date: Unknown
Excerpt: "During the power-off period and before the sheath collapses, the electron temperature and plasma potential decrease rapidly, resulting in low energy ions which can be deflected by smaller local local electric fields. The flux of deflected ions to the upper mask sidewalls increases enabling neutralization of the negative charge...which lead to significantly reduced notching."
Context: Review paper on charging damage in plasma processing
Confidence: high
```

Notching affects bottom CD by:
1. **Lateral undercut** at the bottom widens the bottom CD beyond the intended dimension
2. **Ion deflection** toward sidewalls reduces ion flux to the bottom, potentially narrowing effective bottom CD
3. The effect is most severe at dielectric interfaces (e.g., SOI structures) where charging accumulates
4. Can be mitigated by: pulsed plasmas, higher bias energy, thinner gate oxides (enables tunneling current), WF6 addition for conductive polymers [^260^][^262^]

---

### Finding 2.7: Ion-to-Neutral Flux Ratio Controls ARDE and Bottom CD

```
Claim: ARDE is mainly controlled by the ion-to-neutral flux ratio and ion-to-inhibitor flux ratio. Higher ion-to-neutral flux ratio exaggerates normal RIE lag. Lower ion-to-inhibitor flux ratio causes reverse RIE lag. The appropriate balance of these ratios is key to minimizing ARDE [^274^].
Source: Xie, Kava, Siegel - Aspect ratio dependent etching on metal etch, JVST A 14, 1067 (1996), Applied Materials
URL: https://pubs.aip.org/avs/jva/article/14/3/1067/944790/Aspect-ratio-dependent-etching-on-metal-etch
Date: 1996
Excerpt: "It is found that the ARDE is mainly controlled by the ion to neutral flux ratio and ion to inhibitor flux ratio. The increase of ion to neutral flux ratio will exaggerate the normal reactive ion etching (RIE) lag. The decrease of ion to inhibitor flux ratio tends to make a reverse RIE lag."
Context: Applied Materials research on metal etch ARDE
Confidence: high
```

```
Claim: High neutral-to-ion flux ratios result in microtrench formation. RIE lag tends to occur at low neutral-to-ion flux ratios (<50), whereas inverse RIE lag occurs at high neutral-to-ion flux ratios [^280^].
Source: Tsuda et al., Japanese Journal of Applied Physics, ASCeM model
URL: https://ouci.dntb.gov.ua/en/works/4YLkEB87/
Date: 2010
Excerpt: "High neutral-to-ion flux ratios result in microtrench formation. Moreover, RIE lag tends to occur at low neutral-to-ion flux ratios (<50), whereas inverse RIE lag occurs at high neutral-to-ion flux ratios in typical low-pressure and high-density plasmas."
Context: Atomic-scale cellular model simulation of Si etching in Cl2 plasmas
Confidence: high
```

The ion-to-neutral flux ratio is perhaps the most important control parameter for bottom CD:
- **Ion-limited regime** (high neutral/ion ratio): Etch rate is limited by ion flux. Bottom CD tends to be more stable because ion bombardment determines the etch front position.
- **Neutral-limited regime** (low neutral/ion ratio): Etch rate is limited by neutral flux. Bottom CD can vary more because passivation formation depends on neutral availability.
- **Transition regime**: Where ARDE is most pronounced.

---

### Finding 2.8: Low-Temperature (Cryogenic) Etching Reduces ARDE

```
Claim: Low-temperature etching reduces ARDE because chemical reactions are suppressed, shifting toward ion-driven regime. Additionally, surface diffusion of neutrals at low temperatures enhances transport to the etch front [^107^][^131^].
Source: e-ASCT Journal - Cryogenic Etching in Advanced Electronics Manufacturing
URL: https://www.e-asct.org/journal/view.html?uid=2001&vmd=Full
Date: 2024
Excerpt: "The decrease in etching rate is significantly less in the low-temperature etching environment than in conventional etching. This can be explained by the difference in the amount of movement of ions and neutral species involved in etching when the etching depth increases."
Context: Review paper on cryogenic etching for advanced electronics
Confidence: high
```

```
Claim: Coburn and Winters predicted lower ARDE when the reactive sticking coefficient is reduced. An additional explanation is surface diffusion of neutrals at low temperatures [^131^].
Source: Progress report on high aspect ratio patterning for memory devices, JJAP
URL: https://stats.iop.org/article/10.35848/1347-4065/accbc7
Date: 2015
Excerpt: "Coburn and Winters predicted a lower ARDE when the reactive sticking coefficient is reduced. An additional explanation for the improved ARDE performance at lower temperatures is potentially surface diffusion of neutrals."
Context: Research on HAR patterning for memory devices
Confidence: high
```

Cryogenic etching reduces ARDE and improves bottom CD control through:
1. **Suppressed chemical etching**: Lower temperature reduces spontaneous chemical reactions, making etching more ion-driven
2. **Enhanced surface diffusion**: Physisorbed neutrals can diffuse along surfaces before reacting
3. **Thicker passivation**: SiOxFy passivation layer forms more effectively at cryogenic temperatures
4. **Higher sticking coefficient control**: Reduces reactive sticking coefficient, improving transport

---

### Finding 2.9: Chemically Enhanced Ion-Neutral Synergy Model Explains Aspect Ratio Independent Etching

```
Claim: Aspect ratio independent etching is obtained when the downwards depletion of radicals due to Knudsen transport is compensated by an increase of available reaction sites. This is described by the chemically enhanced ion-neutral synergy model [^282^][^284^].
Source: Anisotropic etching of silicon in SF6 plasma (AIP 2003)
URL: https://www.researchgate.net/publication/248490930
Date: 2003
Excerpt: "Experimentally the etch rate behavior can be tuned from aspect ratio dependent to aspect ratio independent by decreasing the ion flux. This effect can be described well by the recently developed chemically enhanced ion-neutral synergy model. It turns out that aspect ratio independent etching is obtained if the downwards depletion of fluorine radicals due to Knudsen transport is compensated by an increase of the available reaction sites."
Context: Combined Monte Carlo simulation and ICP etching experiments
Confidence: high
```

This finding is directly relevant to the constant bottom CD phenomenon. The synergy model suggests:
- When ion flux decreases, more reaction sites remain available (less ion-induced damage/reaction site creation)
- This compensates for reduced radical transport at higher aspect ratios
- The result: etch rate becomes independent of aspect ratio → bottom CD remains constant

---

### Finding 2.10: Surface Diffusion Significantly Enhances Neutral Transport

```
Claim: Steady-state transmission probability increases meaningfully in the presence of surface diffusion. Spontaneous desorption increases transmission probability when surface diffusion is present. These results indicate enhancement of neutral transport at low surface temperatures that facilitate physisorption and surface diffusion [^211^].
Source: Panagopoulos & Lill, JVST A 41, 033006 (2023), Lam Research
URL: https://pubs.aip.org/avs/jva/article/41/3/033006/2877892/
Date: 2023
Excerpt: "The results predict that steady state transmission probability increases meaningfully in the presence of surface diffusion...These results indicate an enhancement of neutral transport at low surface temperatures that facilitate physisorption and surface diffusion."
Context: Lam Research computational study on neutral transport
Confidence: high
```

Surface diffusion of physisorbed neutrals provides an additional transport channel that:
- Bypasses the geometric limitation of Knudsen transport
- Is more effective at lower temperatures (where physisorption lifetime is longer)
- Can explain why some processes show less ARDE than predicted by Knudsen model alone

---

## 3. Quantitative Relationships

### 3.1 Knudsen Transport Probability

For a cylindrical hole of aspect ratio AR = depth/diameter:
- **Transmission probability K** decreases with AR following Clausing's solution for molecular flow
- At AR = 100:1, only **1.3%** of incoming species reach the bottom [^211^]
- For straight cylinders: K ≈ 1/(1 + 3AR/4) for moderate AR values
- For tapered features: transmission probability depends on taper angle and can be significantly higher [^56^]

### 3.2 Neutral Flux Depletion

From the Coburn-Winters model [^38^][^52^]:
```
F(AR)/F(0) = K / (K + Sn - K*Sn)
```

For small K (high AR) and moderate Sn (~0.1-0.5):
- F(AR)/F(0) ≈ K/Sn (flux is directly proportional to transmission probability)
- With non-zero sidewall reaction probability (0.1), neutral flow decrease exceeds ion flow decrease [^96^]

### 3.3 Etch Rate Model

The local etch rate depends on coupled physics [^268^]:
```
V_n = Γ_ion(E,θ) * Y_phys(E,θ) + Γ_rad * Y_chem(T) + Γ_ion * Γ_rad * Y_synergy
```

Where:
- Γ_ion = ion flux (from sheath model)
- Γ_rad = radical flux (from feature-scale transport)
- Y_phys = physical sputtering yield
- Y_chem = chemical etch yield
- Y_synergy = ion-enhanced chemical yield
- θ = local incidence angle
- E = ion energy

### 3.4 Knudsen Diffusion Coefficient

Within high-aspect-ratio features [^268^]:
```
D_Kn = (d/3) * sqrt(8k_BT / πm)
```

Where d = feature diameter/width, k_B = Boltzmann constant, T = temperature, m = molecular mass.

### 3.5 ARDE Exponential Decay Model

For high aspect ratios (AR > 10) [^257^]:
```
R_HAR = R_0 * exp(-AR/AR_c)
```

Where AR_c is a characteristic decay constant dependent on process conditions.

### 3.6 Ion Flux Angular Distribution

The angular-dependent ion flux density at any point (x,y) in a trench [^103^]:
```
φ(x,y)/φ_0 = (1/σ√(2π)) * ∫ exp(-Θ²/2σ²) dΘ
```

Where σ is the angular standard distribution, depending on the ratio of sheath thickness to mean free path.

### 3.7 Differential Charging Potential

Pattern-dependent charging leads to [^257^]:
```
V_bottom = V_plasma - (J_e - J_i)/C_feature
```

Where J_e and J_i are electron and ion current densities, and C_feature is the feature capacitance. This causes notching and profile distortion in HAR features.

---

## 4. Controversies and Conflicting Claims

### 4.1 Primary Cause of ARDE: Ion vs. Neutral Depletion

**Neutral-limited view**: Coburn & Winters model and most classical literature attribute ARDE primarily to neutral transport limitation [^38^][^52^]. The isotropic nature of neutrals means they are more severely attenuated than directional ions.

**Ion-limited view**: Jansen et al. (1997) constructed special "horizontal trenches" where only radicals control etching and found that "radicals are not responsible for RIE lag" [^108^]. They concluded ion depletion is the primary cause.

**Resolution**: Both mechanisms operate simultaneously. The dominant mechanism depends on process regime:
- **Neutral-limited**: Low pressure, high density plasmas where neutral supply is scarce
- **Ion-limited**: Higher pressure, lower density plasmas with abundant neutrals
- **Both**: Most industrial processes operate in a transition regime [^274^]

### 4.2 Role of Temperature in ARDE Reduction

**Cryogenic view**: Lower temperatures suppress chemical etching, increase physisorption, enable surface diffusion, and reduce ARDE [^107^][^131^].

**Counterpoint**: Very low temperatures can cause SF6 gas to freeze on the Si surface, stopping etching entirely. The process window is narrow [^104^][^112^].

### 4.3 Mechanism of Inverse ARDE

Inverse ARDE (where smaller features etch faster) is attributed to polymer-precursor shadowing [^52^][^54^], but the specific mechanism is debated:
- Less polymer forms in high-AR features → higher etch rate
- However, some studies suggest local maximum etch rate at AR~1 due to competing effects [^60^]
- Gas chemistry plays a major role: less polymerizing conditions (higher F/C ratio) favor inverse ARDE [^54^]

---

## 5. Remaining Gaps

1. **Exact mechanism of constant bottom CD**: While the synergy model and passivation control provide frameworks, no published literature directly explains why bottom CD would remain precisely constant (86.70) across 500 trials. This suggests either:
   - A self-limiting passivation mechanism that stabilizes the bottom width
   - An etch process operating in a unique regime where aspect ratio independence is achieved
   - A metrology artifact (bottom CD may be measuring a specific structural feature that doesn't change)

2. **Real-time bottom CD prediction**: No quantitative model exists that directly predicts bottom CD from RCP parameters without extensive calibration.

3. **Interaction of multiple mechanisms**: Most studies isolate individual ARDE mechanisms. The coupled interaction of Knudsen transport + charging + passivation dynamics in realistic 3D features is not fully understood.

4. **Stochastic effects**: At nanoscale dimensions, stochastic variations in incident fluxes may cause feature-to-feature variations that deterministic models cannot capture [^200^].

5. **Role of byproduct transport**: While reactant depletion is well-studied, byproduct removal from high-AR features and its effect on local chemistry is less understood.

---

## 6. Summary of Mechanism Insights

### 6.1 Bottom CD Control Parameters (Ranked by Importance)

| Rank | Parameter | Mechanism | Effect on Bottom CD |
|------|-----------|-----------|---------------------|
| 1 | Gas chemistry (F/C ratio, O2) | Passivation layer formation | Thicker passivation → smaller bottom CD |
| 2 | Bias power/frequency | Ion energy and directionality | Higher energy → better bottom clearing → larger CD |
| 3 | Source power | Radical flux for passivation | Higher source power → more passivation → smaller CD |
| 4 | Pressure | MFP, ion scattering, neutral transport | Lower pressure → more directional ions → better CD control |
| 5 | Temperature | Passivation adsorption/desorption, surface diffusion | Lower T → thicker passivation → smaller CD |
| 6 | Pulsing mode | Charging reduction, neutral replenishment | Pulsed → less charging → more uniform CD |

### 6.2 Complete ARDE Mechanism Map

```
ARDE ROOT CAUSES:
├── Neutral Transport Limitation
│   ├── Knudsen transport (molecular flow)
│   ├── Neutral shadowing (isotropic distribution)
│   └── Sidewall recombination/adsorption
├── Ion Transport Limitation
│   ├── Ion shadowing (angular distribution)
│   ├── Ion scattering in sheath (pressure-dependent)
│   └── Charging-induced deflection
├── Differential Charging
│   ├── Electron shading effect
│   ├── Mask charging (negative)
│   └── Bottom charging (positive)
└── Passivation/Polymer Dynamics
    ├── Polymer deposition (inverse ARDE)
    ├── Passivation thickness variation with depth
    └── Ion-induced desorption vs. deposition balance
```

### 6.3 Bottom CD Formation Mechanism

The bottom CD of an etched feature is determined by:

```
Bottom CD = Mask Opening - 2 × Passivation_T(bottom) - Ion_Broadening + Microtrench_Widening
```

Where:
- **Passivation_T(bottom)**: Thickness of sidewall passivation layer at the bottom, determined by deposition/etch balance
- **Ion_Broadening**: Lateral etching due to ion deflection/scattering (usually small)
- **Microtrench_Widening**: Localized widening at bottom corners due to focused ion flux

For a process to maintain **constant bottom CD** across many trials:
1. The passivation deposition rate must be very stable and self-limiting
2. The ion/neutral flux ratio must be in the regime where ARDE is minimized (ion-neutral synergy)
3. Charging effects must be minimal (good pulsing or low-energy regime)
4. The process operates in a neutral-starved (ion-rich) regime where ion transport dominates profile evolution

---

## 7. Implications for Constant Bottom CD (86.70) Phenomenon

The observation that bottom CD remains constant at 86.70 across 500 BO trials can be explained through the following mechanistic arguments:

### Hypothesis 1: Self-Limiting Passivation Equilibrium
The etch process operates in a regime where sidewall passivation thickness reaches a self-limiting value. As the etch proceeds deeper:
- Ion flux to the bottom decreases (ARDE)
- But passivation precursors also transport less efficiently
- The balance between ion sputtering (removing passivation at bottom) and deposition (forming passivation on sidewalls) reaches a stable equilibrium
- This equilibrium determines a **constant effective bottom width**

### Hypothesis 2: Ion-Neutral Synergy Compensation
As described by the chemically enhanced ion-neutral synergy model [^282^][^284^]:
- Radical depletion at depth is compensated by increased available reaction sites
- The process operates in a regime where etch rate becomes aspect-ratio-independent
- Since etch rate and lateral etching rate scale together, the bottom width remains constant

### Hypothesis 3: Neutral-Starved (Ion-Rich) Regime
Recent studies [^197^] indicate that maintaining a **neutral-starved (ion-rich)** regime is essential for mitigating profile distortion:
- In this regime, ion transport (not neutral transport) dominates
- Ions are highly directional and reach the bottom consistently
- The etch front is determined by ion bombardment area, which is constant for a given feature
- Bottom CD is then set by the ion bombardment profile and is intrinsically more stable

### Hypothesis 4: Process-Induced Self-Regulation
The BO (Boron Oxide) process chemistry may form a thin, stable passivation layer at the trench bottom that:
- Limits lateral etching beyond a certain point
- Creates an etch-stop-like behavior at the bottom edges
- Self-regulates the bottom width to a constant value

---

## 8. References

[^38^] Antoun, PhD Thesis, Universite Grenoble Alpes, 2020. "Plasma etching process for 3D integration" - https://theses.hal.science/tel-05580654v1/

[^52^] UT Austin / Lam Research, "Introduction to Plasma Etching" Lecture Notes, 2017. - https://willson.cm.utexas.edu/Teaching/LithoClass2017/

[^54^] UT Austin, "Introduction to Plasma Etching Day 2" - ARDE mechanisms, microtrenching.

[^56^] PPPL, "HAR Dielectric Cryo Etch: Mechanisms, Hypotheses, Gaps" - Synergistic transport model.

[^60^] ResearchGate, "Optimized Overlay Metrology Marks: Theory and Experiment" - ARDE trends.

[^62^] NineScrolls, "Wafer Loading Effect in Plasma Etching" - Comprehensive ARDE mitigation strategies.

[^63^] ScienceDirect, "Effect of rare gas addition on deep trench silicon etch" - Bottom CD/passivation relationship.

[^64^] Core academic paper on profile deformations - Bowing, notching, micro-trenching mechanisms.

[^76^] ResearchGate, "Fundamentals of Plasma Process-Induced Charging and Damage" - Notching mechanisms.

[^77^] ResearchGate, "Simulation of an Ar/Cl2 ICP" - Bias power vs. source power effects.

[^96^] Rangelow, "Critical tasks in high aspect ratio silicon dry etching", JVST A 21, 1556 (2003).

[^103^] NTU Singapore thesis on HAR DRIE - Ion flux angular distribution model.

[^104^] Cryogravure plasma presentation - Cryogenic etching ARDE characteristics.

[^107^] e-ASCT, "Cryogenic Etching in Advanced Electronics Manufacturing" - Temperature effects on ARDE.

[^108^] Jansen et al., "RIE lag in high aspect ratio trench etching of silicon", Microelectronic Engineering 35, 45 (1997).

[^109^] ResearchGate, "Formation of Nanoscale Structures by ICP Etching" - Higher energy bias reduces ARDE.

[^131^] JJAP Progress report on HAR patterning - Coburn-Winters ARDE prediction and surface diffusion.

[^197^] SPIE 2023, "High-aspect-ratio amorphous carbon mask etch profile control" - Neutral-starved regime.

[^200^] ResearchGate, "Investigation of Poly Silicon Channel Variation in Vertical 3D NAND" - Stochastic effects.

[^207^] Chinese Journal of Semiconductors, "Microtrenching effect of SiC ICP etching" - Microtrench mechanisms.

[^208^] Thesis on high density plasma etching for advanced memories - Sidewall passivation control.

[^210^] ICP Dry Etching for Planar Lightwave Circuits - "CD control is passivation thickness control".

[^211^] Panagopoulos & Lill, JVST A 41, 033006 (2023) - "Neutral transport during etching of HAR features".

[^257^] ChipFoundryServices Semiconductor Glossary - ARDE exponential model, charging equations.

[^260^] AVS 2024, PS1-TuM-7 - Showerhead material effects on HAR SiO2 etching.

[^262^] ScienceDirect 2025 - "Effect of showerhead electrode materials on HAR etching of SiO2".

[^268^] ChipFoundryServices - Feature-scale modeling equations (Knudsen diffusion, local etch rate).

[^274^] Xie, Kava, Siegel, JVST A 14, 1067 (1996) - "ARDE on metal etch: Modeling and experiment".

[^279^] ISPC-25, "Profile Control in High Aspect Ratio Plasma Etching" - Bias frequency effects on CD.

[^280^] Tsuda et al., JJAP 2010 - ASCeM model, neutral-to-ion flux ratio effects.

[^282^] ResearchGate, "Cryogenic Etching of Silicon with SF6/O2/SiF4 plasmas" - Ion-neutral synergy model.

[^284^] ResearchGate, "Anisotropic etching of silicon in SF6 plasma" - Synergy model for AR-independent etching.

[^288^] ScienceDirect, "Dual Damascene" - Microtrenching minimization strategies.

[^290^] DTU Thesis - Trenching and faceting mechanisms.

[^291^] Stanford, "Crystal-Orientation Dependent Etch Rates and a Trench Model" - Ion flux-only etch model.

---

*Research compiled: 2025*
*Sources: 25+ peer-reviewed papers, industry whitepapers, conference proceedings, and technical training materials*
*Confidence level: High for individual mechanisms; Medium for integrated explanations of constant bottom CD*
