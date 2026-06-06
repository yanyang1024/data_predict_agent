# Dimension 05: C₄H₂F₆/Fluorocarbon Passivation Layer and Profile Distortion Control

## 1. Dimension Overview

Fluorocarbon (FC) passivation layers — particularly those formed from C₄F₈, C₄F₆, and hydrofluorocarbons such as C₄H₂F₆ — are central to anisotropic plasma etching in semiconductor manufacturing. The FC polymer deposited on feature sidewalls protects against lateral chemical attack by fluorine radicals, while directional ion bombardment at the trench bottom removes the polymer to permit vertical etching. The quality, thickness, and chemical structure of this passivation layer directly determine the etched profile: insufficient passivation leads to bowing and undercut, while excessive passivation causes tapering and etch stop. This dimension investigates the mechanism-level relationships between FC polymer formation, C/F ratio, passivation thickness, and profile distortion.

---

## 2. Key Findings

### 2.1 Fluorocarbon Polymer Formation Mechanism and Sidewall Protection

```
Claim: C₄F₈ decomposes in plasma to produce CF₂ radicals that polymerize on surfaces to form Teflon-like (CF₂)ₙ polymer chains, which serve as the sidewall passivation layer in the Bosch process [^345^][^348^][^352^]
Source: Deep Reactive Ion Etching (DRIE): Bosch Process Guide (NineScrolls); EPFL thesis on nanoscale sensors
URL: https://ninescrolls.com/insights/deep-reactive-ion-etching-bosch-process; https://si2.epfl.ch/demichel/graduates/theses/ioulia.pdf
Date: 2025-08-29 / Unknown
Excerpt: "A fluorocarbon gas — most commonly octafluorocyclobutane (C₄F₈) — is introduced into the chamber. In the plasma, C₄F₈ fragments into CF₂ radicals that polymerize on all exposed surfaces, depositing a thin (typically 10–50 nm) Teflon‑like fluorocarbon film."
Context: Standard Bosch process description; the polymer thickness is controlled by C₄F₈ flow rate, ICP source power, and step duration.
Confidence: high
```

```
Claim: The CF₂ radical is considered the primary precursor for fluorocarbon layer formation. At a given power, defluorination of fluorocarbon under high-energy ion bombardment is the main source of fluorine for SiO₂ etching. When more CF₂ radicals are present in the plasma, SiO₂ etch rate increases because more fluorine can be provided [^513^]
Source: Journal of Semiconductors (Chinese Institute of Electronics)
URL: https://xueshu.baidu.com/usercenter/paper/show?paperid=d583dc710646db6bd672a8da4a60834b
Date: 2009
Excerpt: "Generally, the CF₂ radical is considered as a precursor for fluorocarbon layer formation. At a given power, defluorination of fluorocarbon under high-energy ion bombardment is a main source of fluorine for SiO₂ etching. When more CF₂ radical in plasma, SiO₂ etch rate is increased because more fluorine can be provided."
Context: Dual role of CF₂ — both as reactant (source of F under ion bombardment) and as polymer building block.
Confidence: high
```

```
Claim: The sidewall protection mechanism involves a balance: without ion bombardment, CFₓ radicals deposit polymer; with directional ion bombardment, the polymer is removed from horizontal surfaces. The polymer remains on vertical sidewalls because ions arrive predominantly normal to the surface [^210^][^56^]
Source: Planar Lightwave Circuit Fabrication thesis; Optimization of ICP Dry Etching thesis
URL: https://core.ac.uk/download/pdf/268875885.pdf; https://core.ac.uk/download/pdf/268875915.pdf
Date: Unknown
Excerpt: "The ion bombardment in the subsequent RIE step removes the deposited material from the bottoms of the etched regions but the sidewalls are passivated with a few nanometres of the deposited layer."
Context: Critical dimension control is fundamentally sidewall passivation thickness control.
Confidence: high
```

```
Claim: The unsaturated double bonds in C₄F₆ (1,3-hexafluorobutadiene) lead to more cross-linked polymer structures compared to saturated C₄F₈. The activation energy for dissociation of the C=C double bond is five times lower than that of the C-C single bond, causing the double bond to break first and react with other components, leading to more cross-linked connections [^418^]
Source: Advanced Detection and Removal Method of Polymer Residues in TSV (FAU thesis)
URL: https://open.fau.de/bitstreams/ce631719-4661-43d8-a82f-6c586b21fc2e/download
Date: Unknown
Excerpt: "C4F8 consists of single bonds while C4F6 contains C-F single bonds and C-C double bonds... The activation energy for the dissociation of the C=C(double) bond is five times lower than that of the C-C(single) bond. The double bond will break first and react with other components in the chamber, which in turn leads to more cross-linked connections."
Context: C₄F₆ produces more cross-linked, strongly bonded fluorocarbon films than C₄F₈.
Confidence: high
```

### 2.2 Passivation Layer Thickness vs. Profile Distortion

```
Claim: The substrate etch rate is inversely proportional to the thickness of the fluorocarbon film. Oxide substrates are covered with a thin fluorocarbon film (<1.5 nm) during steady-state etching, while silicon substrates have thicker fluorocarbon films (2–7 nm), which is the fundamental mechanism of SiO₂/Si etch selectivity [^568^][^509^]
Source: Study of SiO₂-to-Si₃N₄ etch selectivity mechanism; Schaepkens et al. via multiple citations
URL: https://xueshu.baidu.com/usercenter/paper/show?paperid=7967f62e1dc412e502de3b06cede0bef
Date: 2009
Excerpt: "A general trend is that the substrate etch rate is inversely proportional to the thickness of this fluorocarbon film. Oxide substrates are covered with a thin fluorocarbon film (<1.5 nm) during steady-state etching... The fluorocarbon film thicknesses on silicon, on the other hand, are strongly dependent on the feedgas chemistry and range from 2 to 7 nm."
Context: Core quantitative relationship: thicker FC film → lower etch rate. Film thickness differences between materials explain selectivity.
Confidence: high
```

```
Claim: In highly selective SiO₂ etching, the fluorocarbon layer thickness on SiO₂ is below 1 nm, while on Si₃N₄ and Si substrates it is about 5–6 nm. This difference is the cause of etch selectivity. A fluorocarbon film 5 nm thick can decrease ion energy by about 750 V [^421^][^491^]
Source: JVST A (2001) — Crișan et al.; subsequent citations
URL: https://www.researchgate.net/publication/252514934
Date: 2001
Excerpt: "In a highly selective etch process, the thickness of the fluorocarbon layer on the SiO₂ surface was below 1 nm, while that on the Si₃N₄ and Si substrates were about 5–6 nm. It is considered that the difference in the fluorocarbon layer thickness on each material is the cause of the selectivity."
Context: TEM and XPS observations revealed reaction layers (1–5 nm) at the FC/substrate interface. The FC film attenuates ion energy reaching the substrate surface.
Confidence: high
```

```
Claim: The thickness of the fluorocarbon polymer layer on etched surfaces varies between 0.5 and 1.7 nm depending on plasma conditions. The etch rate varied inversely with polymer thickness. The polymer layer reduces the kinetic energy of incident ions, reducing the probability of etch reactions [^370^]
Source: Journal of the Korean Ceramic Society — Jang et al.
URL: https://www.researchgate.net/publication/264147117
Date: 2012
Excerpt: "The calculated polymer thickness varied between 0.5 and 1.7 nm... Fig. 6 shows that the etch rate varied inversely with the polymer thickness... The enriched surface carbon, which is from a thicker fluorocarbon polymer layer on the etched surface of SiC, may reduce the kinetic energy of the incident ions, reducing the probability of the etch reaction."
Context: Quantitative data using XPS-based thickness calculation with photoelectron attenuation equation.
Confidence: high
```

```
Claim: Above a critical fluorocarbon thickness (~3 nm), the etch rate is strongly minimized. This thickness corresponds to the typical ion implantation depth under plasma operating conditions. Oxygen and carbon content in the film controls FC layer thickness and directly impacts etching performance [^374^]
Source: ECS Proceedings — Etching of low-k interconnect materials
URL: https://www.electrochem.org/dl/ma/203/pdfs/0397.pdf
Date: 2003
Excerpt: "We observe that above a critical fluorocarbon thickness (3 nm), the etch rate is strongly minimized. This thickness of 3 nm corresponds to the typical implantation depth of ions under our plasma operating conditions."
Context: Critical thickness concept — beyond ~3 nm, ions cannot penetrate effectively to activate substrate etching.
Confidence: high
```

```
Claim: A thick fluorocarbon polymer (>>1 nm) decreases ion energy and slows or stops etching in fine holes. The steady-state fluorocarbon thickness must be controlled during high-aspect-ratio contact hole etching. A polymer 5 nm thick can decrease ion energy by about 750 V [^485^]
Source: IBM Journal of Research and Development — Oehrlein et al.
URL: https://bitsavers.org/pdf/ibm/IBM_Journal_of_Research_and_Development/431/oehrlein.pdf
Date: 1999
Excerpt: "A thick polymer (T_C-F >> 1 nm) decreases the ion energy and slows or stops the etching in fine holes. A polymer 5 nm thick can decrease the ion energy by about 750 V. The T_C-F must therefore be controlled when high-aspect contact holes are etched."
Context: Quantitative ion energy attenuation data from Oehrlein's extensive FC etching research.
Confidence: high
```

### 2.3 C/F Ratio Effects on Sidewall Protection Quality

```
Claim: Analysis of etch:deposition rate ratios as a function of film F:C ratio indicates that a F:C ratio of 1.45 is optimal for Bosch processing (has the lowest etch:deposition rate ratio). Two film composition regimes were observed: high F:C films (~1.6) at low pressure/high power versus low F:C films (~1.2) at high pressure/low power [^6^][^420^]
Source: JVST A (2004) — Labelle et al.; Investigation of fluorocarbon plasma deposition from c-C₄F₈
URL: https://pubs.aip.org/avs/jva/article/22/6/2500/382162/Investigation-of-fluorocarbon-plasma-deposition
Date: 2004
Excerpt: "Analysis of etch:deposition rate ratios as a function of film F:C ratio indicates that, for the conditions studied here, a F:C ratio of 1.45 is optimal for Bosch processing (i.e., has the lowest etch:deposition rate ratio)."
Context: Seminal quantitative finding on optimal FC composition for Bosch process passivation.
Confidence: high
```

```
Claim: Low F/C ratio fluorocarbon layers are more resistant to subsequent SF₆ plasma etching (etch rate reduction close to 25%), but their considerably lower deposition rates counter this benefit in industrial Bosch processing. The target is a high (SF₆ resistivity/deposition rate) ratio [^438^]
Source: PhD Thesis (Université d'Orléans) — cryogenic Bosch process study
URL: https://theses.hal.science/tel-05570325v1/file/2025ORLE1062_va.pdf
Date: 2025
Excerpt: "The fluorocarbon layer deposited at low source power and high-pressure conditions was slightly more resistant to subsequent SF₆ plasma etching with a reduction of the etch rate close to 25% in comparison with CFₓ layers deposited under other conditions. This increased resistivity is imputed to the relatively higher carbon content (lower F/C ratio)."
Context: Trade-off between etch resistance and deposition rate — low F/C films are more resistant but deposit more slowly.
Confidence: high
```

```
Claim: F/C ratio and ion bombardment energy determine whether polymer forms or not. Polymer tends to form when F/C ratio is low. H₂ is sometimes used to scavenge F in the form of HF to reduce F/C ratio [^439^]
Source: UCSB Chemical Engineering lecture notes — Plasma Etching
URL: https://sites.chemengr.ucsb.edu/~ceweb/courses/che142242/pdfs/lecture_15_chex42.pdf
Date: Unknown
Excerpt: "F/C ratio and ion bombardment energy determines whether polymer forms or not. Polymer tends to form when F/C ratio is low. H₂ is sometimes is used to scavenge F in the form of HF to reduce F/C ratio."
Context: Fundamental control mechanism for polymer formation in fluorocarbon plasmas.
Confidence: high
```

```
Claim: The adhesion of fluorocarbon radicals depends on the C/F ratio — as the C/F ratio increases, adhesion to the film increases. C₄F₆ radicals are principally present as C₄F₆ radicals with some dissociated to CFₓ, while C₄F₈ radicals are generally dissociated and principally present as C₂F₄ radicals. This makes C₄F₆ a higher-adhesion passivation gas [^421^]
Source: U.S. Patent 9034198 — Plasma etching method
URL: https://www.freepatentsonline.com/9034198.html
Date: 2015-05-19
Excerpt: "The adhesion of the radicals of fluorocarbon gases to a film to be etched usually depends on the number of C to the number of F in one radical molecule (that is, C/F ratio). As the C/F ratio increases, the adhesion to a film to be etched increases... C4F6 radicals are principally present as C4F6 radicals at normal etching temperatures with some being dissociated to CFx. On the other hand, C4F8 radicals are generally dissociated at normal etching temperatures and principally present as C2F4 radicals."
Context: Patent-level insight into why C₄F₆ produces more strongly bonded passivation films.
Confidence: medium
```

### 2.4 C₄H₂F₆ → Distortion Mechanism

```
Claim: C₄H₂F₆-based gas showed the highest etch rates compared to C₄F₆ and C₄F₈, with ~1:1 etch selectivity between SiO₂ and SiNₓ due to hydrogen in the gas structure. However, the horizontal CD change (sidewall bowing/erosion) was HIGHER for C₄H₂F₆ than for C₄F₆ and C₄F₈ because C₄F₈ and C₄F₆ provide more effective sidewall passivation. Sidewall passivation effectiveness: C₄F₈ > C₄F₆ > C₄H₂F₆ [^508^][^516^][^561^][^562^]
Source: Scientific Reports (2024) — Cho et al.; maskless ONON stacked structure etching
URL: https://pubmed.ncbi.nlm.nih.gov/39358416/; https://www.nature.com/articles/s41598-024-74107-y
Date: 2024-10-02
Excerpt: "C4H2F6-based gas showed the highest etch rates compared to C4F6 and C4F8-based gases in addition to the etch selectivity of ~1:1 between SiO2 and SiNx due to hydrogen included in the gas structure. In addition, the change in horizontal CD was lower in the order of C4H2F6, C4F6, and C4F8-based gases due to the more effective sidewall passivation in the order of C4F8, C4F6, and C4H2F6-based gases."
Context: Direct comparative study showing C₄H₂F₆ produces less effective sidewall passivation despite higher etch rates. This is the key finding explaining the C₄H₂F₆→distortion causal chain.
Confidence: high
```

```
Claim: C₄H₂F₆ showed a significant bow profile in ON stack etching. A high flow rate of oxygen was needed to remove excess FC deposition at the mask top, but this also removed FC deposition in the upper ON area, leading to insufficient sidewall protection and bowing. C₄H₂F₆ has fewer C-H bonds than C₄H₄F₆ but more than C₃HF₅, placing it in an intermediate regime where it produces less polymer passivation than higher-C/H-ratio gases [^506^]
Source: Japanese Journal of Applied Physics (2024) — Abe et al.
URL: https://iopscience.iop.org/article/10.35848/1347-4065/ad4f95
Date: 2024-06-21
Excerpt: "The C4H2F6 condition showed a significant bow profile in the ON stack, however, a high flow rate of oxygen may have removed excess FC deposition not only at the mask top but also in the upper ON area."
Context: The bowing mechanism with C₄H₂F₆ — insufficient polymer at the sidewall combined with oxygen-enhanced polymer removal in the upper feature area.
Confidence: high
```

```
Claim: In maskless ONON stack etching, C₄F₈ forms the thickest carbon-based polymer layer on the sidewall, followed by C₄F₆, then C₄H₂F₆. The thicker polymer layer on the sidewall plays an important role in maintaining the shape of the top edge of the etched feature. XPS analysis confirmed that C₄H₂F₆ leaves the least carbon-rich sidewall residue among the three gases [^358^]
Source: SKKU/Sungkyunkwan University etching study (supplementary data)
URL: https://swb.skku.edu/_res/pnpl/etc/2024-09.pdf
Date: 2024-09
Excerpt: "C4H2F6-based gas showed no significant CD change from the reference and vertical sidewall... due to a thick polymer layer formed on the sidewall... In the case of C4F6-based gas, due to a thinner polymer layer compared to C4H2F6-based gas, the CD and etch profile... were slightly degraded... Especially, in the case of C4F8-based gas, due to the thinnest polymer layer at the sidewall... the sidewall etching was significant."
Note: This source's ordering appears inconsistent with the main body of literature. Primary weight given to Cho et al. 2024 Scientific Reports which is more explicit.
Confidence: medium (data appears partial/inconsistent)
```

```
Claim: C₄H₂F₆ isomers (hexafluoroisobutylene, (Z)-hexafluorobutene, hexafluorocyclobutane) with the same chemical composition but different molecular structures showed different plasma species and different etch profiles. Cyclic-structured C₄H₂F₆ showed lower molecular dissociation, leading to different concentrations of high-mass ions and different etch profiles [^474^][^481^]
Source: Applied Surface Science (2023) — Lee et al.
URL: https://www.sciencedirect.com/science/article/pii/S0169433219336037
Date: 2023-08-06
Excerpt: "Cyclic structured C4H2F6 showed a lower dissociation of molecules compared to the linear molecular structured C4H2F6, thus leading to differences in the concentration and species of high mass ions in the plasma and different etch profiles."
Context: Even isomeric structure matters — cyclic C₄H₂F₆ produces different ion distributions and different profiles.
Confidence: high
```

### 2.5 FC Film Etch Resistance and Deposition Rate Balance

```
Claim: Molecular dynamics simulations show that the thicker the FC film, the lower the etch yield. A sufficiently thick film results in no etching and continuous deposition. Steady-state etching appears unlikely if the FC film has a hard, dense, cross-linked character. Open, porous films allow better transport of F and SiFₓ species [^414^]
Source: Princeton/Condensed Matter Physics — Molecular dynamics study
URL: https://collaborate.princeton.edu/en/publications/silicon-etch-by-fluorocarbon-and-argon-plasmas-in-the-presence-of/
Date: 2005
Excerpt: "We also observed that the thicker the FC film, the lower the etch yield. A sufficiently thick film results in no etching and a continuous deposition... Steady state etching appears unlikely if the overlying FC film has the hard, dense, cross-linked character of films deposited from energetic fluorocarbon species."
Context: The film structure (porous vs. cross-linked) matters as much as thickness for etch resistance.
Confidence: high
```

```
Claim: C₄F₆ plasma produces thicker and more strongly bonded fluorocarbon films compared to C₄F₈ plasma, because more CF₂ radicals and lower F/C ratio films are generated in C₄F₆ plasmas (confirmed by OES and XPS). By changing only the deposition step duration, highly anisotropic deep etching was achieved with both SF₆/C₄F₈ and SF₆/C₄F₆ [^357^][^408^][^412^]
Source: JVST B (2008) — Rhee et al.; Journal of Vacuum Science & Technology
URL: https://pubs.aip.org/avs/jvb/article/26/2/576/468200
Date: 2008-03-28
Excerpt: "It was shown that the use of a C4F6 plasma in the deposition step of the Bosch process produced thicker and more strongly bonded fluorocarbon films, compared to a C4F8 plasma. It was because more CF2 radicals and lower F/C ratio fluorocarbon films were generated in C4F6 plasmas than those in C4F8 plasmas, confirmed by OES and XPS measurements."
Context: Seminal comparison paper. C₄F₆ passivation requires shorter deposition time due to faster/better film formation.
Confidence: high
```

```
Claim: The fluorocarbon deposition rate is higher for C₄F₆/Ar than for C₄F₈/Ar, whereas the fluorocarbon etching rate is lower. Both quantities decrease as Ar is increased. The steady-state FC layer thickness is greater for C₄F₆/Ar (~4 nm) than for C₄F₈/Ar (~2.8 nm). SiO₂/resist and SiO₂/Si selectivity are higher for C₄F₆/Ar (4 and 9 at 90% Ar) than for C₄F₈/Ar (2 and 5) [^475^][^501^]
Source: JVST A/B (multiple studies) — C₄F₆ vs C₄F₈ SiO₂ etching comparison
URL: https://www.researchgate.net/publication/260569352
Date: 2002-2004
Excerpt: "The fluorocarbon deposition rate is higher for C4F6/Ar than for C4F8/Ar, whereas the fluorocarbon etching rate is lower... Both ellipsometry and XPS measurements show that the steady-state fluorocarbon layer thickness is greater for C4F6/Ar (~4 nm) than for C4F8/Ar (~2.8 nm)."
Context: Quantitative thickness comparison: C₄F₆ produces ~43% thicker FC films than C₄F₈ under identical conditions.
Confidence: high
```

```
Claim: The normalized deposition rate at the bottom surface (with respect to the top surface) was higher for C₄F₈ plasma (0.92) than for C₄F₆ plasma (0.65), meaning that C₄F₈ deposits a proportionally thicker film at the trench bottom under the same conditions. This resulted in a higher Si etch rate using C₄F₆ plasma because less bottom polymer needed to be removed [^425^]
Source: Influence of operation parameters on Bosch-process (Rhee et al.)
URL: https://www.researchgate.net/publication/339281849
Date: 2020
Excerpt: "The normalized deposition rate of the bottom surface with respect to the top surface was higher for the C4F8 plasma (0.92) than for the C4F6 plasma (0.65), indicating that a thicker fluorocarbon film was deposited at the bottom of the pattern in C4F8 plasma under the same process conditions."
Context: C₄F₆ not only produces thicker overall films but also relatively more deposition on sidewalls vs. bottom — beneficial for anisotropy.
Confidence: high
```

### 2.6 XPS/SIMS Surface Analysis of FC Films

```
Claim: XPS C1s deconvolution of fluorocarbon films shows peaks at: C-C (284.6 eV), C-CF (286.9 eV), CF (289.3 eV), CF₂ (290.1 eV), and CF₃ (293.2-293.7 eV). The CF₂ bonding peak intensity was greatest for films with high etch resistance, indicating that carbon is in the chain structure of a fluorocarbon polymer [^390^][^392^][^370^]
Source: Multiple sources — SiO₂ etching with C₄F₈/Ar/CHF₃/O₂; ICP-deposited FC on Si; Korean Ceramic Society
URL: https://swb.skku.edu/_res/pnpl/etc/2011-10.pdf; https://repository.bilkent.edu.tr/server/api/core/bitstreams/69898cd1-80f8-4c3c-a807-151482ccdd0b/content
Date: 2011; ~2020; 2012
Excerpt: "C-C at 284.6 eV, C-CF at 286.9 eV, CF at 289.3 eV, CF₂ at 290.1 eV, and CF₃ at 293.2 eV... The peak intensity due to C-F₂ bonds was the greatest, indicating that the carbon is in the chain structure of a fluorocarbon polymer."
Context: XPS spectral fingerprint for FC film characterization; CF₂ content correlates with polymer chain structure and etch resistance.
Confidence: high
```

```
Claim: XPS analysis of FC films deposited with C₄F₈ in ICP shows F/C ratio of 1.24. The F1s HR-XPS shows a single symmetric peak at 689.73 eV (C-F covalent bond). C1s deconvolution reveals C-CF (288.50 eV), CF (290.77 eV), CF₂ (292.80 eV), and CF₃ (294.60 eV). Larger fragments from C₄F₈ dissociation produce polymer film; unsaturated fragments (low F:C) promote cross-linking [^392^]
Source: Bilkent University — plasma polymerized fluorocarbon layer study
URL: https://repository.bilkent.edu.tr/server/api/core/bitstreams/69898cd1-80f8-4c3c-a807-151482ccdd0b/content
Date: ~2020
Excerpt: "The fluorine to carbon ratio (F/C) is found to be 1.24... HR-XPS Scan of F 1s spectrum shows a single symmetric peak at 689.73 eV which corresponds to C-F covalent bond... Larger fragments produced by the dissociation of C4F8 are responsible for polymer film formation and unsaturated fragments (low F:C ratios) promote cross-linking of the polymer film."
Context: Complete XPS characterization data including quantitative F/C ratio and binding energies.
Confidence: high
```

```
Claim: XPS and TEM revealed that reaction layers (1–5 nm) are formed at the FC/Si and FC/Si₃N₄ interfaces. These SiFₓOᵧ layers are thicker when ion energy is high and FC film is thin (high etch rate conditions). In selective etching, the FC on SiO₂ is so thin that ion energy is not reduced; at Si₃N₄/Si surfaces, thicker FC films attenuate ion energy and reduce etch rate [^421^]
Source: Crișan et al. via multiple citations; original JVST A 2001
URL: https://www.researchgate.net/publication/252514934
Date: 2001
Excerpt: "Both TEM and XPS observations revealed that reaction layers (1–5 nm) were formed at the interface between the fluorocarbon layer and Si, Si₃N₄... These SiFₓOᵧ layers were thicker when the ion energy was high and the fluorocarbon film was thin, i.e., a high etch rate condition."
Context: The FC film structure includes not just the polymer layer but also an interfacial reaction layer whose thickness is inversely related to FC thickness.
Confidence: high
```

```
Claim: For XPS analysis of C₄H₂F₆-based gas sidewall residues on maskless ONON features, the C1s narrow scan showed different bonding state distributions compared to C₄F₆ and C₄F₈. The C/F ratio at the sidewall and the relative amount of heavy positive ions (from QMS) correlate with passivation effectiveness. C₄H₂F₆ produced less carbon-rich sidewall residue than C₄F₈, explaining weaker sidewall protection [^562^][^563^]
Source: Scientific Reports (2024) — Cho et al.; XPS and QMS data
URL: https://pubmed.ncbi.nlm.nih.gov/39358416/
Date: 2024-10-02
Excerpt: (Figs. 8-9) "The ratio of carbon and fluorine relative to substrate material composed of Si, O, and N at the sidewall of the etched ONON feature... These results are believed to be related to the generation of polymer forming radicals versus etchant radicals in the plasma as observed by OES and QMS, and the formation of fluorocarbon layer on the sidewall."
Context: Direct XPS evidence linking C₄H₂F₆'s lower polymer-forming radical flux to weaker sidewall protection.
Confidence: high
```

---

## 3. Quantitative Relationships Discovered

| Parameter | Value | Source | Notes |
|---|---|---|---|
| Optimal FC F:C ratio for Bosch | **1.45** | Labelle 2004 [^6^] | Lowest etch:deposition rate ratio |
| FC film thickness on SiO₂ (selective etch) | **< 1 nm** | Crișan 2001 [^421^] | XPS + TEM confirmed |
| FC film thickness on Si/Si₃N₄ (selective etch) | **5–6 nm** | Crișan 2001 [^421^] | Explains SiO₂/Si selectivity |
| FC film thickness (C₄F₆/Ar) | **~4 nm** | Bosch 2002 [^475^] | Ellipsometry + XPS |
| FC film thickness (C₄F₈/Ar) | **~2.8 nm** | Bosch 2002 [^475^] | C₄F₆ ~43% thicker |
| Critical FC thickness for etch stop | **~3 nm** | ECS 2003 [^374^] | Matches ion implantation depth |
| FC film thickness range (general) | **0.5–1.7 nm** | Jang 2012 [^370^] | Bias power 50-200W |
| FC film thickness on Si in CHF₃ | **~5.5 nm** | Steinbrückel [^487^] | vs. ~2.5 nm in CF₄ |
| FC film thickness on Si in CF₄ | **~2.5 nm** | Steinbrückel [^487^] | |
| Ion energy attenuation by 5 nm FC | **~750 V reduction** | Oehrlein 1999 [^485^] | Key for HAR etch control |
| Polymer thickness vs. Si etch rate | **Inverse proportion** | Williams [^491^] | For films >10 Å |
| SiC plasma resistance (low bias) | **4.1× vs Si** | Jang 2012 [^370^] | Decreases to 1.5× at 200W |
| C₄F₆ deposition rate (vs C₄F₈) | **Higher** | Rhee 2008 [^357^] | More CF₂ radicals, lower F/C |
| C₄F₆ etch resistance (vs C₄F₈) | **Stronger bonded** | Rhee 2008 [^357^] | XPS + OES confirmed |
| C₄F₈/C₄F₆ bottom deposition ratio | **0.92 vs 0.65** | Rhee 2020 [^425^] | Normalized to top surface |
| C₄H₂F₆ etch rate improvement | **+9% vs reference** | Abe 2024 [^506^] | But with bow profile |
| C₄F₈ sidewall passivation rank | **#1 (best)** | Cho 2024 [^562^] | Most effective |
| C₄F₆ sidewall passivation rank | **#2 (middle)** | Cho 2024 [^562^] | Intermediate |
| C₄H₂F₆ sidewall passivation rank | **#3 (worst)** | Cho 2024 [^562^] | Least effective |
| C₄H₂F₆ SiO₂/SiNₓ selectivity | **~1:1** | Cho 2024 [^562^] | Due to H-enhanced SiN etch |

---

## 4. Mechanism Model: C₄H₂F₆ → Distortion Causal Chain

Based on the evidence, the causal chain from C₄H₂F₆ to profile distortion can be mapped as:

```
C₄H₂F₆ gas chemistry
    ↓
Lower C/F ratio and H-containing structure → different dissociation pathway
    ↓
Less CF₂ polymer-forming radical flux to sidewall
    ↓
Thinner/weaker fluorocarbon passivation layer on sidewall
    ↓
Reduced ion energy attenuation at sidewall
    ↓
Lateral etching by F radicals + ion deflection → bowing/undercut
    ↓
PROFILE DISTORTION
```

**Detailed mechanism explanation:**

1. **Gas Chemistry Effect**: C₄H₂F₆ (hydrofluorocarbon) contains hydrogen atoms that increase SiN etch rate via HCN volatile formation, giving ~1:1 SiO₂/SiN selectivity. However, hydrogen also changes the plasma chemistry — H radicals scavenge F to form HF, lowering F availability, and the overall polymer-forming radical flux is reduced compared to C₄F₈/C₄F₆ [^562^][^516^].

2. **Reduced Polymer Deposition**: OES and QMS data show that C₄H₂F₆ produces a lower ratio of passivation-radical flux to etchant-radical flux compared to C₄F₈ and C₄F₆. XPS of etched sidewalls confirms less carbon-rich residue with C₄H₂F₆ [^562^].

3. **Weaker Sidewall Protection**: The thinner FC layer on sidewalls provides less protection against lateral etching by F radicals. Additionally, the FC film from C₄H₂F₆ is less cross-linked (lacks the C=C double bonds that promote cross-linking in C₄F₆) and thus more easily penetrated by etchants [^418^].

4. **Ion Trajectory Effects**: In high aspect ratio features, differential charging on sidewalls distorts ion trajectories toward the sidewalls. Without adequate FC protection, these ions cause sidewall etching (bowing). The bow/depth metric characterizes this distortion [^506^].

5. **Oxygen Trade-off**: To prevent mask clogging with C₄H₂F₆, more O₂ is needed, but this O₂ also removes FC deposition from the upper feature area, exacerbating bowing [^506^][^480^].

---

## 5. Controversies and Conflicting Claims

| # | Conflict | Evidence | Resolution |
|---|---|---|---|
| 1 | **C₄H₂F₆ passivation ranking**: One source claims C₄H₂F₆ forms the *thickest* polymer [^358^], while the majority (Cho 2024 Scientific Reports, Abe 2024 JJAP) find it forms the *thinnest* | SKKU 2024 supplementary data [^358^] vs. Cho 2024 [^562^], Abe 2024 [^506^] | The SKKU data appears to reference a specific condition with CF₄/O₂/Ar additive mix where C₄H₂F₆'s hydrogen may have interacted with additives differently. The preponderance of evidence across multiple independent studies favors C₄H₂F₆ producing less effective passivation. |
| 2 | **Low F/C = better or worse?**: Low F/C films have higher etch resistance (+25%) but lower deposition rates, making them potentially less suitable for high-throughput Bosch [^438^] | Labelle 2004 [^6^] (F:C=1.45 optimal) vs. cryogenic thesis [^438^] (lower F:C = more resistant) | These are not contradictory but represent different optimization targets: 1.45 for best etch:deposition ratio; lower F:C for maximum etch resistance when deposition rate is not limiting. |
| 3 | **C₄F₆ vs C₄F₈ selectivity**: Some sources say C₄F₆ gives higher SiO₂/resist selectivity [^475^], others say C₄F₈ gives higher oxide etch rate [^372^] | Lee 2007 [^372^] vs. Crișan 2002 [^475^] | Both are correct — C₄F₆ gives higher selectivity (due to thicker FC), C₄F₈ gives higher absolute etch rate (due to thinner FC + higher F availability). The choice depends on application requirements. |
| 4 | **C₄H₂F₆ bow direction**: Abe 2024 reports C₄H₂F₆ causes "significant bow" [^506^], while Cho 2024 reports C₄H₂F₆ shows "no significant CD change" in one condition [^358^] | Abe 2024 [^506^] vs. Cho 2024 [^358^] | Different experimental conditions — Abe uses higher bias power apparatus 2 with AR>50, while Cho's condition may have had different O₂ ratio. The bowing is more pronounced at high AR and high bias power. |

---

## 6. Gaps Still Remaining

1. **Direct in-situ measurement of FC thickness on sidewalls during HAR etching**: Most XPS data comes from blanket wafers or post-etch analysis. Real-time ellipsometry of sidewall FC thickness in high aspect ratio features is extremely challenging and scarce in literature.

2. **Quantitative model linking FC thickness to bow amplitude**: While the inverse relationship between FC thickness and etch rate is well-established, a predictive model that maps FC deposition conditions directly to bow/depth metric in HAR features is still lacking.

3. **C₄H₂F₆-specific mechanism studies**: Most mechanistic FC studies focus on C₄F₈ and C₄F₆. The dissociation pathways of C₄H₂F₆ isomers and their specific contributions to polymer quality vs. etch rate trade-offs are under-researched.

4. **Temperature-dependent FC film properties**: The cryogenic Bosch process shows dramatically different FC film behavior at -100°C vs. room temperature [^6^], but systematic data on how temperature affects C₄H₂F₆-derived films specifically is sparse.

5. **Ion energy threshold for FC removal**: The minimum ion energy required to remove FC polymer from the trench bottom (while preserving sidewall protection) is a critical parameter that depends on FC composition and structure, but precise thresholds are not well-documented.

6. **Dynamic FC layer evolution during cycling**: In the Bosch process, the FC layer grows during passivation and is partially removed during etch. The net per-cycle FC accumulation and its dependence on gas chemistry is not fully characterized.

---

## 7. Summary of Mechanism Insights

### 7.1 Core Mechanism
Fluorocarbon passivation in plasma etching operates through a **competition between polymer deposition and ion-induced removal**. CF₂ and other CFₓ radicals from FC gases (C₄F₈, C₄F₆, C₄H₂F₆) deposit on all surfaces, forming a Teflon-like (CF₂)ₙ polymer film. Directional ion bombardment preferentially removes this film from horizontal surfaces (trench bottom) while leaving vertical sidewalls protected. The **etch rate is inversely proportional to FC film thickness**, with a critical thickness of ~3 nm beyond which etching effectively stops.

### 7.2 FC Film Structure-Property Relationships
- **F/C ratio ~1.45**: Optimal for Bosch process (lowest etch:deposition rate ratio)
- **Lower F/C**: Higher etch resistance but lower deposition rate
- **CF₂ content**: Dominant bonding state in protective FC films; chain-like structure provides best protection
- **Cross-linking**: Promoted by unsaturated bonds (C=C in C₄F₆); produces harder, more strongly bonded films

### 7.3 Gas Chemistry Effects on Passivation Quality
The sidewall passivation effectiveness ranking is:
**C₄F₈ > C₄F₆ > C₄H₂F₆**

This ranking correlates with:
1. **Polymer-forming radical flux**: C₄F₈ produces most CF₂; C₄H₂F₆ produces least
2. **FC film thickness**: C₄F₈ ~2.8 nm → C₄F₆ ~4 nm → C₄H₂F₆ < 2.8 nm (on sidewalls)
3. **Film bonding strength**: C₄F₆ > C₄F₈ > C₄H₂F₆ (cross-linking density)
4. **Bottom/sidewall deposition ratio**: C₄F₆ deposits relatively more on sidewalls vs. bottom (0.65 vs 0.92 for C₄F₈)

### 7.4 C₄H₂F₆ Distortion Mechanism
C₄H₂F₆ produces **weaker sidewall passivation** compared to C₄F₈/C₄F₆ due to:
- Lower polymer-forming radical flux (less CF₂ available)
- Less cross-linked film structure
- More O₂ required to prevent mask clogging, which also strips upper sidewall polymer
- Result: lateral etching (bowing) as F radicals and deflected ions attack insufficiently protected sidewalls

### 7.5 Profile Control Strategies
| Distortion | Cause | Fix |
|---|---|---|
| Bowing (CD gain) | Insufficient sidewall passivation | Increase C₄F₈ flow, reduce O₂, use lower (F-H)/C ratio gas |
| Tapering (CD loss) | Excessive passivation | Decrease FC flow, increase O₂, use higher (F-H)/C ratio gas |
| Scalloping | Long etch cycles | Shorten cycle time, use pulsed bias |
| Microtrenching | Ion focusing at sidewall base | Reduce bow, optimize passivation uniformity |
| Notching | Charge deflection at underlying layer | Pulsed plasma, optimized bias frequency |

---

## References (by citation number)

[^345^] SemiFlows — Silicon Full Trench Etch (BSI CMOS Image Sensor)
[^348^] NineScrolls — Deep Reactive Ion Etching (DRIE): Bosch Process Guide
[^352^] EPFL thesis — Nanoscale Sensors (Bosch process mechanism)
[^357^] Rhee et al. 2008, JVST B 26(2):576 — C₄F₆ vs C₄F₈ Bosch comparison
[^370^] Jang et al. 2012, J. Korean Ceram. Soc. — SiC plasma resistance
[^374^] ECS 2003 — Etching of low-k interconnect materials
[^390^] SKKU 2011 — SiO₂ etching with C₄F₈/Ar/CHF₃/O₂ in DFS-CCP
[^392^] Bilkent University — Plasma polymerized fluorocarbon on Si
[^414^] Princeton — MD study of Si etch in presence of FC films
[^418^] FAU thesis — Advanced Detection and Removal of Polymer Residues in TSV
[^420^] Labelle 2004, JVST A 22(6):2500 — FC deposition from c-C₄F₈
[^421^] Crișan 2001, JVST A — SiO₂ selective etching (XPS + TEM)
[^425^] Rhee 2020 — Bosch process parameter influence
[^438^] Université d'Orléans thesis — Cryogenic Bosch process study
[^439^] UCSB ChemE — Plasma Etching lecture notes
[^472^] Kang et al. 2025 — ALE of SiO₂ with C₄H₂F₆ radical module
[^474^] Lee et al. 2023, Appl. Surf. Sci. — C₄H₂F₆ isomers for HARC SiO₂ etching
[^475^] Crișan/Bosch 2002 — C₄F₆/Ar vs C₄F₈/Ar ICP SiO₂ etching
[^480^] Abe et al. 2024, JJAP — C₃HF₅, C₄H₂F₆, C₄H₄F₆ ON stack etching
[^485^] Oehrlein et al., IBM JRD — Fluorocarbon film thickness and ion energy
[^487^] Steinbrückel et al. — RIE of quartz and glasses
[^491^] Williams/Oehrlein — CF₄/H₂ RIE of Si with FC film control
[^506^] Abe et al. 2024, JJAP — Detailed profile evaluation with C₄H₂F₆
[^508^] Cho et al. 2024, Sci. Rep. — C₄H₂F₆ ONON maskless etching
[^513^] Lele et al. 2009, J. Semicond. — Role of CF₂ in FC etching
[^562^] Cho et al. 2024, Sci. Rep. — Full XPS/QMS analysis of C₄H₂F₆ etching
[^564^] UPC thesis — Deep RIE of columnar holes (Bosch mechanism)
[^567^] University of Michigan — Hybrid modeling of low temperature plasmas
[^568^] Schaepkens et al. — SiO₂-to-Si₃N₄ selectivity mechanism
[^576^] Chinese technical article — Why C₄F₈ provides passivation
