# Dimension 02: Cl2/HBr化学计量比与Etch Profile控制机理

## 1. 维度概述

Cl2/HBr化学计量比是硅刻蚀profile控制中最关键的调控参数之一。Cl2提供高刻蚀速率和高氯原子通量，而HBr提供高选择性、更优的profile控制和更少的刻蚀缺陷。两者在刻蚀机理、sidewall protection layer (SPL)形成、离子角分布等方面的根本差异，决定了混合比例对profile distortion的深刻影响。本报告系统梳理了Cl2与HBr在硅刻蚀中的机理差异，解释了"为什么增加离子刻蚀比例反而改善形变"这一counter-intuitive现象，并总结了physical-to-chemical etch ratio的控制方法与profile响应关系。

---

## 2. 关键发现

### 2.1 Cl2 vs HBr在硅刻蚀中的根本差异

#### 2.1.1 表面吸附覆盖率差异

Cl原子在硅表面的饱和吸附覆盖率显著高于Br原子，这是导致两种气体体系刻蚀速率差异的根本原因之一。

```
Claim: Cl在硅表面的饱和吸附覆盖率为1.0x10^15 Cl/cm2，而Br的饱和吸附覆盖率为6.0x10^14 Br/cm2，Cl覆盖率是Br的1.6倍 [^1^]
Source: Cheng et al., J. Vac. Sci. Technol. A (1995); Cornell NNCI Etch Workshop
URL: http://www.columbia.edu/~iph1/Download/71.%20Cheng-HBrCl2PlasmaEtching-1994-JVA001970.pdf
Date: 1994/2016
Excerpt: "The saturated coverage of Cl, measured by XPS after etching Si in a Cl2 plasma was previously estimated to be 1.0x10^15 cm-2. Based on the Cl-to-Br XPS ratio of 1.6:1 measured in the present study, we therefore estimate that the saturated Br coverage is 6.0x10^14 cm-2 after etching in HBr plasmas."
Context: 通过XPS测量和激光诱导热脱附-激光诱导荧光(LD-LIF)技术，在混合HBr/Cl2等离子体中独立控制Cl+、Cl和Cl2束流，系统研究了硅表面的卤素覆盖行为
Confidence: High
```

```
Claim: Cl覆盖率高于Br的原因包括：(1)Br原子尺寸更大(原子半径Cl=0.97A, Br=1.12A)导致空间位阻效应；(2)Br吸附位点被共吸附的H原子部分阻塞 [^2^]
Source: Cheng et al., J. Vac. Sci. Technol. A (1995)
URL: http://www.columbia.edu/~iph1/Download/71.%20Cheng-HBrCl2PlasmaEtching-1994-JVA001970.pdf
Date: 1994
Excerpt: "The lower Br coverage is likely due in part to site blocking by coadsorbed H. Although we could not determine H coverages in this study, H atoms are present in the discharge and therefore are expected to adsorb on the surface during etching. In addition, adjacent adsorption sites could be blocked by the larger Br atom (atomic radii of Cl and Br are 0.97 and 1.12 A, respectively)."
Context: HBr等离子体中H原子参与表面吸附，进一步降低了Br的有效覆盖
Confidence: High
```

#### 2.1.2 离子通量差异

```
Claim: HBr等离子体中的离子通量比Cl2低40%，这是HBr刻蚀速率低的另一重要原因 [^3^]
Source: Cornell NNCI Etch Workshop / Genova (2016)
URL: https://nnci.net/sites/default/files/inline-files/HBr%20etching%20of%20silicon-Cornell-V.Genova-NNCI%20Etch%20Workshop%202016.pdf
Date: 2016
Excerpt: "Ion flux in HBr is 40% less than Cl2 due to a decreased ion density. Lower etch rates in HBr by 50% due to less adsorption and reduced ion flux."
Context: Cornell大学纳米加工中心的实验总结，对比了Cl2和HBr基硅刻蚀的基本特征
Confidence: High
```

```
Claim: HBr等离子体刻蚀Si更慢，主要因为在饱和覆盖条件下表面卤素较少，因此离子增强形成的挥发性产物(如SiBr2)的速率更低 [^4^]
Source: Cheng et al., J. Vac. Sci. Technol. A (1995)
URL: http://www.columbia.edu/~iph1/Download/71.%20Cheng-HBrCl2PlasmaEtching-1994-JVA001970.pdf
Date: 1994
Excerpt: "This comparison suggests that HBr plasmas etch Si more slowly than do Cl2 plasmas mainly because less halogen is present on the surface at saturated coverage and, hence, the ion-enhanced rate of formation of volatile products such as SiBr2 is lower."
Context: 通过比较纯Cl2和HBr等离子体中的刻蚀速率比(0.61)与卤素覆盖率比(0.60)和离子通量比(0.83)，得出此结论
Confidence: High
```

#### 2.1.3 刻蚀产额角分布的根本差异（核心发现）

这是解释Cl2和HBr profile差异最关键的发现——两种等离子体中硅刻蚀产额随离子入射角的变化规律截然不同。

```
Claim: Cl2等离子体中硅刻蚀产额在离子入射角大于60°时急剧下降，而HBr等离子体中刻蚀产额随离子角度变化更平缓 [^5^]
Source: Jin, Vitale & Sawin, MIT / AVS Symposium (2001/2002)
URL: https://www.electrochem.org/dl/ma/201/pdfs/0409.pdf
Date: 2002
Excerpt: "The dependence of the etching yield on ion bombardment angle is significantly different for Cl2 and HBr plasmas. The etching yield in Cl2 plasmas decreases rapidly for ion angles above 60°(measured from the surface normal), which results in significant ion scattering from the sidewall, and may cause the sidewall bowing and microtrenching seen when patterning polysilicon with Cl2 plasma. The etching yield in HBr plasmas decreases more gradually with the ion angle; resulting in less ion reflection from the feature sidewall, and may explain the much less pronounced sidewall bowing and microtrenching typically seen when patterning polysilicon with HBr plasmas."
Context: MIT的Jin等使用ICP束流装置直接测量了Cl2和HBr高密度等离子体中的硅刻蚀产额，建立了蒙特卡洛profile simulator
Confidence: High
```

```
Claim: 纯Cl2和纯HBr等离子体的刻蚀产额非常接近，差异在于角分布而非绝对值 [^6^]
Source: Vitale, Sawin et al., J. Vac. Sci. Technol. A (2001)
URL: https://ntrs.nasa.gov/api/citations/20020059586/downloads/20020059586.pdf
Date: 2001
Excerpt: "Pure Cl2 and pure HBr plasmas have very similar etching yields. Silicon etching rates are lower in HBr plasmas than in Cl2 plasmas due to lower ion fluxes, not lower etching yields."
Context: NASA技术报告引用的Vitale等人的束流实验结果
Confidence: High
```

```
Claim: Cl+离子增强刻蚀产额在60°和70°离正入射角时分别降低约30%和50% [^7^]
Source: Chang & Sawin, J. Vac. Sci. Technol. A (1997)
URL: https://ntrs.nasa.gov/api/citations/20020059586/downloads/20020059586.pdf
Date: 1997
Excerpt: "The angular dependence of ion-enhanced etching yield was also measured. The etching yield was reduced by approximately 30% and 50% when ion impingement angles of 60° and 70° off-normal were used, respectively."
Context: 使用Cl+、Cl和Cl2独立控制的束流散射装置系统测量
Confidence: High
```

#### 2.1.4 离子反射与散射机制差异

```
Claim: Br+在倾斜sidewall上的反射概率和反射能量分数比Cl+更小，这是HBr等离子体中tapering、footing和microtrenching减少的根本原因 [^8^]
Source: Mori, Irie, Osano, Ono et al., J. Vac. Sci. Technol. A (2021)
URL: https://doi.org/10.1116/6.0001025 (via ouci.dntb.gov.ua)
Date: 2021
Excerpt: "the smaller reflection probability and reflected energy fraction of Br+ on tapered sidewalls (compared to Cl+) are responsible for reduced tapering, footing, and microtrenching in HBr-containing plasmas; moreover, chemical etching effects of neutral H atoms at the feature bottom and sidewalls, arising from the larger reaction probability of H (compared to Cl), are also responsible for reduced microtrenching and for reduced tapering."
Context: 使用自研的原子尺度蜂窝模型(ASCeM)结合实验，在UHF-ECR刻蚀反应器中进行系统研究
Confidence: High
```

#### 2.1.5 离子能量分布差异

```
Claim: HBr等离子体有更窄的离子能量分布，因为主要离子HBr+和Br+的质量相近，导致更少的能量分散和更弱的microtrenching [^9^]
Source: Cornell NNCI Etch Workshop / Genova (2016)
URL: https://nnci.net/sites/default/files/inline-files/HBr%20etching%20of%20silicon-Cornell-V.Genova-NNCI%20Etch%20Workshop%202016.pdf
Date: 2016
Excerpt: "HBr has a narrower ion energy distribution due to similar masses of the principal ions of HBr+ and Br+ leading to less pronounced trenching."
Context: Cl2等离子体中主要离子(Cl+, Cl2+)质量差异更大，导致更宽的离子能量分布
Confidence: High
```

---

### 2.2 Sidewall Protection Layer (SPL) 差异：SiOCl vs SiOBr

#### 2.2.1 SPL形成机制

```
Claim: HBr/O2等离子体中，sidewall passivation layer由非挥发性硅刻蚀产物在sidewall上吸附后与氧反应形成SiOxBry类化合物。SPL厚度主要受氧通量控制 [^10^]
Source: Haass, Darnon, Cunge, Joubert, J. Vac. Sci. Technol. B (2015)
URL: https://hal.univ-grenoble-alpes.fr/hal-01878012v1/document
Date: 2015
Excerpt: "The SPL is created by nonvolatile Si species that adsorb on the sidewalls and react with oxygen to form stable SiBryOx like layers...the model given by Oehrlein et al. suggests two mechanisms that alone or in combination lead to the formation of the SPL. The flux may come from the gas phase (radicals or etch products) or from a line-of-sight deposition of strongly sticking, nonvolatile sputtered species."
Context: 系统研究了脉冲HBr/O2等离子体中SPL的厚度和化学组成，使用XPS和电子显微镜分析
Confidence: High
```

#### 2.2.2 SiOBr vs SiOCl的关键差异

```
Claim: SiOBr和SiOCl sidewall protection layers的差异是Cl2和HBr基刻蚀产生不同profile演化和缺陷的根本原因 [^11^]
Source: Cornell NNCI Etch Workshop / Genova (2016)
URL: https://nnci.net/sites/default/files/inline-files/HBr%20etching%20of%20silicon-Cornell-V.Genova-NNCI%20Etch%20Workshop%202016.pdf
Date: 2016
Excerpt: "Differences in sidewall protection layers of SiOBr and SiOCl responsible for different etch profile evolutions and artifacts."
Context: Cornell大学系统对比Cl2和HBr基硅刻蚀的实验总结
Confidence: High
```

```
Claim: HBr基SPL在刻蚀过程中经历动态变化——bromine被oxygen逐渐替代，早期形成的passivation层变为致密的SiO2，而后期形成的层保持富溴非晶态 [^12^]
Source: Klemenschits, TU Wien PhD Thesis (2022)
URL: https://repositum.tuwien.at/bitstream/20.500.12708/20001/1/Klemenschits%20Xaver%20-%202022%20-%20Emulation%20and%20simulation%20of%20microelectronic...pdf
Date: 2022
Excerpt: "the passivation layer undergoes a change during the process, as bromine is removed from the layer and replaced by oxygen. Therefore, a dense SiO2 layer is generated at passivation layers formed earlier, while an amorphous bromine rich material dominates the passivation layers formed later in the process."
Context: 维也纳工业大学博士论文，对HBr刻蚀中SPL的时间演化进行建模
Confidence: High
```

```
Claim: SPL厚度随aspect ratio增加而减小，且不(强)依赖于等离子体暴露时间，表明SPL由动态平衡控制 [^13^]
Source: Haass et al., J. Vac. Sci. Technol. B (2015)
URL: https://hal.univ-grenoble-alpes.fr/hal-01878012v1/document
Date: 2015
Excerpt: "the SPL thickness does not (strongly) depend upon the exposure time to the plasma, which means that the SPL might be controlled by a dynamic equilibrium."
Context: 对不同trench尺寸(45-100nm)和不同脉冲条件的XPS分析
Confidence: High
```

---

### 2.3 "为什么增加离子刻蚀比例反而改善形变"——Counter-Intuitive现象的物理解释

这是本研究维度最核心的科学问题。综合多项研究，该counter-intuitive现象的物理解释涉及多个相互关联的机制：

#### 2.3.1 机制一：高离子/中性比促进方向性刻蚀，抑制各向同性化学刻蚀

```
Claim: 离子/中性比是决定刻蚀profile的关键参数——更高的离子含量有利于方向性刻蚀，更高的中性含量促进各向同性刻蚀。增加离子比例使刻蚀更受离子通量和能量控制，减少随机性的化学横向刻蚀 [^14^]
Source: Eureka PatSnap / Various sources
URL: https://eureka.patsnap.com/article/how-to-control-ionneutral-ratio-in-etching-plasmas-pressure-and-power-balancing
Date: 2025
Excerpt: "higher ion content generally favoring directional etching and higher neutral content promoting isotropic etching"
Context: 关于刻蚀等离子体中离子/中性比控制的技术综述
Confidence: Medium
```

```
Claim: 在HBr/Cl2混合等离子体中，增加HBr比例会减少化学刻蚀（因为Cl和F原子比Br更活泼），但会增加离子溅射速率（因为HBr+和Br+密度更高），这种效应类似于Ar或He的稀释效应——更多物理溅射、更少化学刻蚀，有利于找到化学与物理刻蚀的适当平衡 [^15^]
Source: Numerical study, Physical Plasmas (2016)
URL: https://nano.uantwerpen.be/nanorefs/pdfs/OA_10.10880022-37274919195203.pdf
Date: 2016
Excerpt: "introducing more HBr in the plasma will result in reduced chemical etching due to a smaller amount of Cl and F atoms, which are more reactive than Br. In contrast, the ion sputter rate will significantly increase with rising HBr fraction due to the higher densities of HBr and Br in the plasma...it creates the same diluting effects as Ar or He, where an increased fraction results in less chemical etching but more(physical) sputtering, which is important for finding a proper balance between chemical etching and physical sputtering"
Context: HBr/Cl2/O2混合等离子体的CFD流体模型计算
Confidence: High
```

#### 2.3.2 机制二：高离子通量使刻蚀更"离子主导"，降低对离子聚焦效应的敏感性

```
Claim: 在HBr/O2脉冲等离子体中，低duty cycle时Br自由基/离子通量比增加，导致刻蚀越来越受离子通量和能量控制。在这种条件下，刻蚀速率对sidewall散射引起的离子通量局部增加更敏感——但 paradoxically，由于HBr的宽角度分布，离子散射不会导致强烈的聚焦效应 [^16^]
Source: Haass et al., J. Vac. Sci. Technol. B (2015)
URL: https://hal.univ-grenoble-alpes.fr/hal-01878012v1/document
Date: 2015
Excerpt: "the radical (Br) to ion flux ratio increases at low duty cycle, leading to conditions in which the etching becomes more and more affected by the ion flux and energy. In this case, the etch rate may be more susceptible to a local increase in the ion flux at the edges of the pattern, where ions are focused by scattering on the sidewalls."
Context: 研究脉冲HBr/O2等离子体对profile影响的实验
Confidence: Medium (此效应在Cl2等离子体中更明显，在HBr中因宽角度分布而被弱化)
```

#### 2.3.3 机制三：Br+的低反射概率意味着即使增加离子比例，也不会产生强烈离子聚焦

```
Claim: 在Cl2等离子体中，microtrenching主要由sidewall散射离子造成——离子从弯曲的sidewall散射后聚焦在trench底部靠近侧壁的位置。Br+在倾斜sidewall上的反射概率和能量分数远小于Cl+，因此即使增加离子通量，也不会产生Cl2等离子体中那样的聚焦效应 [^17^]
Source: Mori et al., J. Vac. Sci. Technol. A (2021)
URL: https://doi.org/10.1116/6.0001025
Date: 2021
Excerpt: "Microtrenching is caused by the ion reflection from feature sidewalls on incidence, being reduced with increasing oxygen flux (partly due to surface oxidation of the feature bottom) and being enhanced and then reduced with increasing ion energy and neutral reactant flux."
Context: 使用原子尺度蜂窝模型(ASCeM)的蒙特卡洛模拟，结合UHF-ECR实验验证
Confidence: High
```

#### 2.3.4 机制四：H原子的化学刻蚀效应平衡了microtrenching

```
Claim: H原子在HBr等离子体中起关键作用——H原子比Cl原子有更大的反应概率，其化学刻蚀效应在feature底部和sidewall上减少了microtrenching的形成 [^18^]
Source: Mori et al., J. Vac. Sci. Technol. A (2021)
URL: https://doi.org/10.1116/6.0001025
Date: 2021
Excerpt: "chemical etching effects of neutral H atoms at the feature bottom and sidewalls, arising from the larger reaction probability of H (compared to Cl), are also responsible for reduced microtrenching and for reduced tapering"
Context: 同一研究的另一关键发现
Confidence: High
```

#### 2.3.5 综合物理解释

综合以上机制，"为什么增加离子刻蚀比例（即增加HBr/Cl2比）反而改善形变"的完整物理图像如下：

1. **当Cl2比例高时**：化学刻蚀成分强，Cl原子大量横向刻蚀sidewall → sidewall变弯曲(bowing) → bowed sidewall将入射离子聚焦到trench底部角落 → microtrenching形成。同时，Cl+在倾斜表面的高反射概率加剧了离子聚焦。

2. **当HBr比例增加时**：
   - 化学刻蚀减弱（Br反应性低于Cl，HBr+密度更高但化学活性更低）
   - Br+的低反射概率减少了离子聚焦效应
   - H原子的化学刻蚀平滑了底部形貌
   - HBr的宽离子角分布意味着离子更均匀地分布，而不是集中在特定角度
   - 更窄的离子能量分布（HBr+/Br+质量相近）减少了能量分散造成的散射

---

### 2.4 Ion-Assisted Etch vs Chemical Etch平衡对Profile的影响

#### 2.4.1 总刻蚀速率的构成

```
Claim: 总刻蚀速率可表示为化学刻蚀速率与离子增强刻蚀速率之和：ER = ηN*ΦN + kenh*ΦI，其中ηN是自由基反应速率系数，ΦN是自由基通量，kenh是离子增强系数，ΦI是离子通量 [^19^]
Source: "The application of secondary effects in high aspect ratio dry etching for the fabrication of MEMS"
URL: https://www.sciencedirect.com/science/article/abs/pii/S0167931701004968
Date: 2002
Excerpt: "The total etching rate of silicon can be written as the sum of the chemical etching rate and the ion enhanced etching rate, which correspond to the contribution of the neutral and the ion flux: ER=ηNΦN+kenhΦI"
Context: MEMS制造中高aspect ratio干法刻蚀的综述
Confidence: High
```

#### 2.4.2 刻蚀产额随中性/离子通量比的变化

```
Claim: 刻蚀产额随中性/离子通量比增加而增加，但在高比率时逐渐饱和，因为表面被卤素饱和。在低Cl通量时，刻蚀反应受表面氯化过程限制；在高比率时，刻蚀产额饱和，变为离子通量限制 [^20^]
Source: Chang & Sawin, J. Vac. Sci. Technol. A (1997)
URL: https://ntrs.nasa.gov/api/citations/20020059586/downloads/20020059586.pdf
Date: 1997
Excerpt: "The etching yield increased with the increase of Cl/Cl+ flux ratio but gradually saturated at higher flux ratios as the surface became saturated with chlorine. At low Cl flux (small ratio), the rapid increase of the etching yield with increasing Cl flux indicates that the etching reaction is limited by the surfacechlorination process. At large ratio, however, the etching yield saturates, and becomes limited by ion flux."
Context: 使用独立控制的Cl+、Cl和Cl2束流系统进行的系统测量
Confidence: High
```

#### 2.4.3 中性/离子通量比对profile缺陷的影响

```
Claim: 高中性/离子通量比导致microtrench形成。低比率(<50)出现RIE lag，高比率出现inverse RIE lag。窄图案(<70nm)的刻蚀速率随中性/离子通量比增加而显著增加 [^21^]
Source: La Magna et al., J. Vac. Sci. Technol. B (2002)
URL: https://www.researchgate.net/publication/260507481
Date: 2002
Excerpt: "high neutral-to-ion flux ratios result in microtrench formation. Moreover, RIE lag tends to occur at low neutral-to-ion flux ratios (<50), whereas inverse RIE lag occurs at high neutral-to-ion flux ratios in typical low-pressure and high-density plasmas. In particular, the etch rates for narrow patterns (<70 nm) increase significantly with increasing neutral-to-ion flux ratio."
Context: 使用原子尺度蜂窝模型(ASCeM)的模拟研究
Confidence: High
```

---

### 2.5 Physical-to-Chemical Etch Ratio的控制方法与Profile响应

#### 2.5.1 通过气体比例控制

```
Claim: 在Cl2/O2/HBr混合等离子体中，随着HBr混合比增加：tapering减少并在80% HBr时最小化，footing逐渐减少，microtrenching在>20% HBr时消失 [^22^]
Source: Mori et al., J. Vac. Sci. Technol. A (2021)
URL: https://doi.org/10.1116/6.0001025
Date: 2021
Excerpt: "with increasing HBr mixing ratio in Cl2/O2/HBr plasmas, the tapering is reduced and minimized at 80% HBr where slight lateral or side etching tends to occur, the footing is reduced gradually, and the microtrenching fades away at more than 20% HBr."
Context: 在UHF-ECR刻蚀反应器中系统改变HBr混合比的实验
Confidence: High
```

#### 2.5.2 通过压力控制

```
Claim: 较高压力导致更多粒子碰撞，降低离子能量，从而降低离子/中性比，更适合需要更多化学刻蚀的工艺。较低压力增加离子平均自由程，产生更有能量的离子和更高的离子/中性比 [^23^]
Source: Eureka PatSnap
URL: https://eureka.patsnap.com/article/how-to-control-ionneutral-ratio-in-etching-plasmas-pressure-and-power-balancing
Date: 2025
Excerpt: "At lower pressures, the mean free path of particles increases, leading to more energetic ions and a higher ion/neutral ratio...Conversely, higher pressures lead to more frequent collisions among the particles, reducing the energy of ions, thus lowering the ion/neutral ratio."
Context: 等离子体刻蚀中离子/中性比控制的技术综述
Confidence: Medium
```

#### 2.5.3 通过功率控制

```
Claim: 增加RF功率通常增强气体物种的电离，提高离子/中性比。降低功率减少电离率，有利于更高浓度的中性粒子 [^24^]
Source: Eureka PatSnap
URL: https://eureka.patsnap.com/article/how-to-control-ionneutral-ratio-in-etching-plasmas-pressure-and-power-balancing
Date: 2025
Excerpt: "Increasing the RF power typically enhances the ionization of the gas species, thereby raising the ion/neutral ratio...reducing the power decreases the ionization rate, favoring a higher concentration of neutrals."
Context: 同上
Confidence: Medium
```

#### 2.5.4 有效反应概率模型

```
Claim: 在HBr+Cl2+O2三元体系中，Si刻蚀动力学可以用氧原子通量敏感的有效反应概率来充分描述，后者与氧原子通量/离子能量通量比直接相关 [^25^]
Source: Lee, Efremov, Kwon et al., Plasma Chemistry and Plasma Processing (2019)
URL: https://discovery.researcher.life/article/peculiarities-of-si-and-sio2-etching-kinetics-in-hbr-cl2-o2-inductively-coupled-plasma/cee3e137068f3c30bb2c52b88fdebda8
Date: 2019
Excerpt: "the influence of input process parameters (HBr/Cl2 mixing ratio, input power, and bias power) on the Si and SiO2 etching kinetics may be adequately described in terms of the oxygen atom flux-sensitive reaction probability. The latter directly correlates with the oxygen atom flux/ion energy flux ratio."
Context: 结合Langmuir探针诊断和零维等离子体建模的系统研究
Confidence: High
```

---

### 2.6 Cl2/HBr比例对Ion Angular Distribution和SPL厚度的影响

#### 2.6.1 HBr的宽离子角分布

```
Claim: HBr等离子体中刻蚀产额对离子入射角的依赖性较弱——具有"更宽的角度分布"，导致离子从sidewall散射后"更少的散射和更少的缺陷" [^26^]
Source: Cornell NNCI Etch Workshop / Genova (2016)
URL: https://nnci.net/sites/default/files/inline-files/HBr%20etching%20of%20silicon-Cornell-V.Genova-NNCI%20Etch%20Workshop%202016.pdf
Date: 2016
Excerpt: "Ion bombardment angle induced etch yields are different with HBr having a wider angle distribution leading to less scattering and fewer artifacts."
Context: Cornell大学系统对比Cl2和HBr基刻蚀的总结
Confidence: High
```

```
Claim: HBr等离子体创建近乎理想的硅各向异性profile，因为Br原子对Si sidewall的刻蚀速率低，且从sidewall散射的离子具有更宽的角分布(相比Cl+) [^27^]
Source: PhD Thesis, University of Houston
URL: https://uh-ir.tdl.org/bitstreams/f6afb12c-2dbc-41ff-9e90-a89120a65876/download
Date: Unknown
Excerpt: "HBr plasmas create nearly ideal anisotropic profiles in Si compared with Cl2 and SF6 plasmas due to the low etching rate of Br atoms for Si sidewalls (compared with F-atoms), and the wider angular spread of ions that scatter off the sidewalls (compared to Cl+)."
Context: 关于Cl2/HBr/O2等离子体中硅刻蚀的博士论文综述
Confidence: High
```

#### 2.6.2 SPL厚度随Cl2/HBr比的变化

```
Claim: 氧在SPL形成中起主要作用——无外部氧流时，SPL厚度急剧减小，sidewall出现bowed profile和microtrenching [^28^]
Source: Haass et al., J. Vac. Sci. Technol. B (2015)
URL: https://hal.univ-grenoble-alpes.fr/hal-01878012v1/document
Date: 2015
Excerpt: "A reduction of the oxygen flow in the CW process results in a strong decrease of the SPL thickness, which suggests that the oxygen limits the SPL formation in this case...At a reduced oxygen flow, bowed sidewalls can be observed, indicating an increased erosion rate of silicon. This is attributed to a decreased formation of the SPL that is formed by nonvolatile etch products."
Context: HBr/O2等离子体中系统改变氧流量的实验
Confidence: High
```

```
Claim: 增加HBr比例会改变等离子体化学，使得SiOBr SPL的形成特性和稳定性不同于SiOCl SPL。SiOBr SPL对氧稀释更敏感，在HBr基等离子体中SPL更厚 [^29^]
Source: Cunge, Joubert et al., J. Vac. Sci. Technol. A (2005)
URL: https://www.researchgate.net/publication/277962389_Chamber_wall_interactions_with_HBrCl2O2_plasmas
Date: 2005
Excerpt: "Sidewall passivation films are thicker under HBr based chemistry than under chlorine containing chemistries. In addition, the film thickness seems to be highly sensitive to oxygen dilution in HBr based plasma."
Context: XPS分析0.1μm硅栅刻蚀中形成的sidewall passivation film
Confidence: High
```

---

## 3. 定量关系汇总

### 3.1 刻蚀速率相关

| 参数 | Cl2等离子体 | HBr等离子体 | 来源 |
|------|-------------|-------------|------|
| 硅刻蚀速率 | ~2170 A/min | ~1330 A/min | Cheng et al. (1995) [^4^] |
| 离子通量 | 基准 | 低17-40% | Cheng (1995); Cornell (2016) [^3^] |
| 饱和卤素覆盖 | 1.0x10^15 Cl/cm2 | 6.0x10^14 Br/cm2 | Cheng et al. (1995) [^1^] |
| Cl/Br覆盖比 | 1.6:1 | - | Cheng et al. (1995) [^1^] |
| 刻蚀阈值能量 | ~10 eV | ~10 eV | Chang & Sawin (1997) [^20^] |
| 纯Br2阈值能量 | - | ~44 eV | Cornell (2016) |

### 3.2 刻蚀产额角分布

| 入射角 | Cl2刻蚀产额变化 | HBr刻蚀产额变化 | 来源 |
|--------|-----------------|-----------------|------|
| 0-60° | 相对恒定 | 缓慢递减 | Jin et al. (2002) [^5^] |
| 60° | 降低~30% | 缓慢递减 | Chang (1997) [^7^] |
| >60° | 急剧下降 | 继续缓慢递减 | Jin et al. (2002) [^5^] |
| 70° | 降低~50% | 缓慢递减 | Chang (1997) [^7^] |

### 3.3 Profile随HBr混合比的变化（Mori et al. 2021）[^22^]

| HBr混合比 | Tapering | Footing | Microtrenching |
|-----------|----------|---------|----------------|
| 0% (纯Cl2) | 严重 | 严重 | 严重 |
| 20% | 减少 | 减少 | **消失** |
| 80% | **最小化** | 显著减少 | 无 |
| >80% | 轻微增加（side etching） | 减少 | 无 |

### 3.4 有效反应概率的关键比率

```
Claim: Si+Cl/Br异相反应的有效反应概率直接与氧原子通量/离子能量通量比相关 [^25^]
Source: Lee, Efremov, Kwon, Plasma Chem. Plasma Process. (2019)
Date: 2019
Excerpt: "the effective reaction probability for Si+Cl/Br heterogeneous reaction depends on the flux of oxidative species - oxygen atoms and OH radicals. The reasons may be 1) the oxidation of silicon resulting in higher reaction threshold energy; and 2) the decreasing fraction of free adsorption sites for Cl/Br atoms due to the oxidation of reaction products into the lower volatile SiBrxOy and SiClxOy compounds."
Context: HBr+Cl2+O2三元体系中刻蚀动力学的模型分析
Confidence: High
```

---

## 4. 争议与矛盾发现

### 4.1 刻蚀产额角分布的实验误差

```
Claim: HBr刻蚀产额在大角度的实验误差约为±53%，而Cl2中角度范围的误差为±17%。两种卤素的角分布在彼此的误差范围内重叠，使得确定整体形状是否正确变得困难 [^30^]
Source: NASA Technical Report (2002)
URL: https://ntrs.nasa.gov/api/citations/20020059586/downloads/20020059586.pdf
Date: 2002
Excerpt: "the experimental error is significant for larger angles (approximately ±53% for HBr compared to ±17% for Cl2). The angular dependencies for etch yields for chlorine and HBr fall within each other's error ranges, making it difficult to determine if the overall shapes are correct."
Context: NASA关于HBr等离子体高aspect ratio刻蚀的模拟与实验报告
Confidence: Medium (误差范围大，但趋势已被多方验证)
```

### 4.2 HBr比例增加与tapering的非单调关系

```
Claim: 在Cl2/HBr混合比从0%增加到100%时，linewidth shift（sidewall tapering程度）先线性减小，通过一个最小值，然后在~80%以上时显著增加 [^31^]
Source: Tuda et al., J. Vac. Sci. Technol. A (2001)
URL: https://www.researchgate.net/publication/230967069
Date: 2001
Excerpt: "As the HBr percentage in Cl2/HBr is increased from 0 to 100%, the linewidth shift ΔL of poly-Si relative to the mask width (or the degree of sidewall tapering of poly-Si lines) first decreased linearly, passed through a minimum, and then increased considerably at above ~80%."
Context: ECR Cl2/HBr/O2等离子体中0.18μm oxide-masked poly-Si栅刻蚀
Confidence: High
```

**争议解释**：>80% HBr时tapering增加的原因是等离子体中的刻蚀抑制剂沉积到sidewall上（预测stick probability ~O(0.1)），而非来自微结构中的etch product redeposition。

### 4.3 增加HBr是否总是改善profile？

增加HBr改善profile存在一个最优区间。当HBr比例过高(>80%)时：
- 刻蚀速率过低，影响产能
- 可能出现过度passivation导致的lateral etching
- 对chamber seasoning条件更敏感
- 微loading效应更明显（ΔL随line spacing和open space增加而增加）

---

## 5. 尚存的空白

### 5.1 三元体系中Cl2/HBr/O2的协同效应机理

虽然Efremov等建立了有效反应概率与氧通量/离子能量通量比的关联[^25^]，但三元体系中Cl、Br、O三种活性物种在表面的竞争吸附和反应机理仍需更精细的原位研究。特别是：
- Cl和Br在混合等离子体中硅表面的竞争吸附动态
- SiOClxBry混合passivation layer的形成和演化动力学
- 不同Cl2/HBr比例下离子能量分布的详细变化

### 5.2 纳米尺度下的profile控制极限

随着特征尺寸进入sub-10nm regime：
- 离子角分布的微小变化如何影响profile仍需更精细的模拟
- stochastic效应（单个离子的随机散射）在profile演化中的角色
- 低能离子(<50eV)在HBr/Cl2混合体系中的角分布数据仍然稀缺

### 5.3 Counter-intuitive现象的完整定量模型

虽然定性解释已经建立，但"增加离子刻蚀比例改善形变"的完整定量预测模型仍缺失。需要一个统一的模型，能够：
- 同时耦合离子散射、化学刻蚀、passivation形成三个过程
- 预测任意Cl2/HBr比例下的profile演化
- 考虑stochastic效应的蒙特卡洛模拟

### 5.4 SiOBr SPL的原位表征

```
Claim: 由于Br在暴露于大气时会被O交换，SPL厚度<几纳米时，从ex situ测量很难推断in situ SPL组成 [^32^]
Source: III-V laser waveguide etching paper, J. Vac. Sci. Technol. A
URL: https://iopscience.iop.org/article/10.1149/1.2965790/meta
Date: 2008
Excerpt: "Cl or Br desorption and exchange with O take place when a Si surface covered by a SiOCl or SiOBr passivation layer is brought back to ambient air after etching. For this reason, when the passivation layer thickness is less than a few nanometers, it becomes difficult to extrapolate the in situ composition of the passivation layer"
Context: GaAs ridge waveguide HBr刻蚀中的TEM-EDX分析
Confidence: High
```

---

## 6. 机理洞察总结

### 6.1 Cl2/HBr比例影响Profile的核心机理链

1. **气体比例 → 等离子体化学**：Cl2提供更多Cl自由基（化学刻蚀），HBr提供更多HBr+/Br+离子（离子刻蚀）和H原子
2. **等离子体化学 → 表面吸附**：Cl覆盖率高(1.6x)但Br/H共吸附导致有效Br位点减少
3. **表面吸附 + 离子轰击 → 刻蚀产额**：Cl2和HBr的绝对刻蚀产额相近，但角分布截然不同
4. **刻蚀产额角分布 → 离子散射行为**：Cl+在>60°急剧下降导致强反射和聚焦；Br+平缓下降减少散射
5. **离子散射 + passivation → profile**：Cl2→bowing→microtrenching；HBr→垂直sidewall→flat bottom

### 6.2 "增加离子刻蚀比例改善形变"的关键物理

该counter-intuitive现象的本质是：**离子刻蚀比例的增加并不是简单增加了"物理溅射"，而是通过以下协同效应改变了profile演化**：

1. **减少了化学横向刻蚀**（Br的反应性低于Cl，减少了sidewall的各向同性刻蚀）
2. **改变了离子-表面相互作用**（Br+的低反射概率意味着更少的离子聚焦）
3. **H原子的"平滑"效应**（H比Cl更大的反应概率均匀化了底部形貌）
4. **更窄的离子能量分布**（HBr+/Br+质量相近，减少了能量分散导致的散射）
5. **SPL组成的改变**（SiOBr vs SiOCl具有不同的保护特性和动态演化）

### 6.3 Profile控制的设计准则

| 目标Profile | 推荐Cl2/HBr比 | 关键控制参数 |
|-------------|---------------|--------------|
| 高刻蚀速率 | Cl2为主(>70%) | 高Cl2流量，高偏压 |
| 最少microtrenching | HBr>20% | 氧流量控制SPL厚度 |
| 最垂直sidewall | HBr~80% | 平衡化学与离子刻蚀 |
| 最高SiO2选择性 | HBr为主+O2 | O2含量>10% |
| 最少footing | HBr>50% | 高离子能量，低化学刻蚀 |

---

## 参考文献索引

[^1^]: C.C. Cheng et al., "Competitive halogenation of silicon surfaces in HBr/Cl2 plasmas studied by XPS and in-situ real-time pulsed laser-induced thermal-desorption," J. Vac. Sci. Technol. A 13, 1970 (1995).

[^2^]: 同上

[^3^]: V. Genova, "HBr Etching of Silicon," NNCI ETCH WORKSHOP, Cornell University (2016). https://nnci.net/sites/default/files/inline-files/HBr%20etching%20of%20silicon-Cornell-V.Genova-NNCI%20Etch%20Workshop%202016.pdf

[^4^]: Cheng et al., J. Vac. Sci. Technol. A (1995).

[^5^]: W. Jin, S.A. Vitale, H.H. Sawin, "Beam study of plasma-surface kinetics and simulation of feature profile evolution in Cl2 and HBr etching of polysilicon," MIT/AVS (2002). https://www.electrochem.org/dl/ma/201/pdfs/0409.pdf

[^6^]: S.A. Vitale, H.H. Sawin, "Silicon etch yields in F2, Cl2, Br2, and HBr high density plasmas," J. Vac. Sci. Technol. A (2001). Via NASA NTRS (2002).

[^7^]: J.P. Chang, H.H. Sawin, "Chlorine ion-enhanced etching of polysilicon in the low ion energy regime," J. Vac. Sci. Technol. A 15, 610 (1997).

[^8^]: M. Mori, S. Irie, Y. Osano, K. Eriguchi, K. Ono, "Model analysis of the feature profile evolution during Si etching in HBr-containing plasmas," J. Vac. Sci. Technol. A (2021). https://doi.org/10.1116/6.0001025

[^9^]: Cornell NNCI (2016).

[^10^]: M. Haass, M. Darnon, G. Cunge, O. Joubert, "Silicon etching in a pulsed HBr/O2 plasma. II. Pattern transfer," J. Vac. Sci. Technol. B 33, 032203 (2015).

[^11^]: Cornell NNCI (2016).

[^12^]: X. Klemenschits, "Emulation and simulation of microelectronic..." PhD Thesis, TU Wien (2022).

[^13^]: Haass et al., J. Vac. Sci. Technol. B (2015).

[^14^]: Eureka PatSnap, "How to Control Ion/Neutral Ratio in Etching Plasmas" (2025).

[^15^]: Numerical study of CF4/CHF3/H2/Cl2/O2/HBr gas phase plasma chemistry, Physical Plasmas (2016).

[^16^]: Haass et al., J. Vac. Sci. Technol. B (2015).

[^17^]: Mori et al., J. Vac. Sci. Technol. A (2021).

[^18^]: 同上

[^19^]: "The application of secondary effects in high aspect ratio dry etching for the fabrication of MEMS," (2002).

[^20^]: Chang & Sawin, J. Vac. Sci. Technol. A (1997).

[^21^]: La Magna et al., via ASCeM simulations, J. Vac. Sci. Technol. B (2002).

[^22^]: Mori et al., J. Vac. Sci. Technol. A (2021).

[^23^]: Eureka PatSnap (2025).

[^24^]: 同上

[^25^]: B.J. Lee, A. Efremov, K.-H. Kwon, "Peculiarities of Si and SiO2 Etching Kinetics in HBr+Cl2+O2 Inductively Coupled Plasma," Plasma Chemistry and Plasma Processing 39, 339-358 (2019).

[^26^]: Cornell NNCI (2016).

[^27^]: PhD Thesis, University of Houston.

[^28^]: Haass et al., J. Vac. Sci. Technol. B (2015).

[^29^]: G. Cunge et al., "Plasma-wall interactions during silicon etching processes in high-density HBr/Cl2/O2 plasmas," Plasma Sources Sci. Technol. (2005).

[^30^]: NASA NTRS Report (2002).

[^31^]: M. Tuda, K. Shintani, H. Ootera, J. Vac. Sci. Technol. A (2001).

[^32^]: III-V laser waveguide HBr etching paper, J. Vac. Sci. Technol. A (2008).
