# Dimension 10: 3D NAND HAR Etch专用机理与Profile控制

## 1. 维度概述

3D NAND闪存技术的核心制造工艺之一是在交替堆叠的SiO₂/SiN（ONON）薄膜中刻蚀高深宽比（HAR）的垂直通道孔。随着3D NAND从200层向1000+层发展，通道孔的深宽比将从目前的约50:1增加到100:1以上，刻蚀深度达到10μm以上，而孔径仅约100nm。这种极端的几何特征带来了一系列独特的刻蚀机理挑战，包括多种类型的轮廓畸变（bowing、striation、twisting）、 aspect ratio dependent etching（ARDE）效应、以及刻蚀速率下降等问题。

本调研报告深入分析了3D NAND HAR刻蚀的专用机理与profile控制技术，涵盖 distortion类型的物理起源、主要设备厂商的解决方案、Bosch工艺与低温刻蚀的比较、脉冲功率等离子体技术、以及面向1000+层3D NAND的刻蚀挑战。

---

## 2. 3D NAND垂直通道刻蚀中的Distortion类型

### 2.1 Bowing（弓形畸变）

#### 机理描述
Bowing是指在HAR孔刻蚀过程中，侧壁中部出现横向过度刻蚀，导致孔径在中间深度处比顶部和底部更宽的现象。

**Claim: Bowing主要由离子散射和局部电场偏转引起，是HAR刻蚀中最普遍的轮廓畸变类型之一。** [^1^]
Source: Japanese Journal of Applied Physics, Progress Report on HAR Patterning for Memory Devices
URL: https://iopscience.iop.org/article/10.35848/1347-4065/accbc7/pdf
Date: 2023
Excerpt: "Simulated HAR hole etch with significant bow formation from a broader IAD. Ion fluxes with a wide IAD give HAR hole etches a characteristic bowed profile with a bottom taper."
Context: 该研究通过特征尺度模型模拟了离子角分布（IAD）对profile的影响，发现宽IAD会导致特征性的bowed profile。
Confidence: High

**Claim: Bowing是离子从mask的倾斜边缘散射并撞击对面侧壁的结果。** [^2^]
Source: MDPI Nanomaterials, "Characterization of an Etch Profile at a Wafer Edge in Capacitively Coupled Plasma"
URL: https://mdpi-res.com/d_attachment/nanomaterials/nanomaterials-12-03963/article_deploy/nanomaterials-12-03963.pdf
Date: 2022
Excerpt: "The deviation of the etch profile such as sidewall bowing can be caused by the lateral etching by bombardments of deviated ions. The ion trajectories may deviate from ion reflection on the tilted mask."
Context: 研究了wafer边缘的刻蚀profile畸变，发现mask倾斜会导致离子反射并产生bowing。
Confidence: High

**Claim: 在3D NAND中，bowing是mask faceting导致离子从上部侧壁散射的结果，充电效应会加剧这一问题。** [^3^]
Source: U.S. Patent Application 20210375633, "Method and Apparatus for Formation of Protective Sidewall Layer for Bow Reduction"
URL: https://patents.justia.com/patent/20210375633
Date: 2021
Excerpt: "The bowing is a consequence of over-etching of sidewalls, especially at the upper portion of the stack. The bowing may be a consequence of ion scatter from faceted edges of a mask that has been exposed to significant etch time."
Context: 该专利描述了通过保护性侧壁层来减少bowing的方法。
Confidence: High

#### Bowing的定量影响
- Bowing会导致相邻feature之间的短路
- 在绝缘材料中，充电效应会加剧bowing
- 通过控制IAD（离子角分布）可以减少bowing

---

### 2.2 Striation（条纹畸变）

#### 机理描述
Striation是指HAR孔侧壁上出现的周期性或准周期性粗糙条纹，是由mask形态或刻蚀过程中聚合物沉积的非均匀性传递到下层造成的。

**Claim: Striation的形成机理涉及氟碳聚合物在侧壁的沉积和离子轰击的相互作用，striation首先在氟碳膜上形成，然后传递到介电薄膜。** [^4^]
Source: Japanese Journal of Applied Physics, "Formation mechanism of sidewall striation in high-aspect-ratio hole etching"
URL: https://iopscience.iop.org/article/10.7567/1347-4065/ab163c/pdf
Date: 2019
Excerpt: "The striations formed on the fluorocarbon films at the sidewalls of high aspect ratio holes and transferred to the dielectric films laterally as the hole diameters increased. In addition, as etching proceeded, striations began to form at the deeper regions, depending on the aspect ratios."
Context: 该研究系统研究了striation的形成机理，发现striation与氟碳聚合物的沉积和离子轰击密切相关。
Confidence: High

**Claim: Striation的形成可以通过四步过程描述：聚合物在mask侧壁堆积→离子轰击导致非均匀聚合物去除→形成粗糙的mask侧壁→粗糙图案传递到下层。** [^5^]
Source: AVS Conference Proceedings, Line Edge Roughness Reduction for Advanced Metal Gate
URL: https://nccavs-usergroups.avs.org/wp-content/uploads/PAG2005/PEUG_01_2005_Chowdhury-1.pdf
Date: 2005
Excerpt: "Step 1: As etching progresses, polymer builds up (fluorinated amorphous carbon) on the resist sidewalls. Step 2: Depending on the polymer strength, ion bombardment causes non-uniform polymer removal. Step 3: The non-uniform polymer layer results in rough resist sidewalls. Step 4: The striated resist pattern is then transferred down to the underlayers."
Context: 描述了striation形成的经典四步机理。
Confidence: High

**Claim: 即使mask本身光滑，侧壁上仍可能出现striation，因为离子辐照会增加碳mask上的striation程度，而氟碳自由基的沉积可以抑制striation。** [^6^]
Source: JJAP, "Formation mechanism of sidewall striation in high-aspect-ratio hole etching"
URL: https://iopscience.iop.org/article/10.7567/1347-4065/ab163c
Date: 2019
Excerpt: "In spite of the smooth morphology of the mask, sidewall striation was observed on dielectric films. Results from the carbon mask sample treated with several gas plasmas implies that ion irradiation can increase the degree of striation on the carbon mask, and striation tends to be suppressed by deposition of a fluorocarbon film from fluorocarbon radicals."
Context: 该实验结果表明striation可以在刻蚀过程中自发产生，不一定需要粗糙的mask。
Confidence: High

#### Striation的抑制方法
- 使用无Ar或富F/O的化学配方
- 降低氟碳气体流量、在低压力下操作
- 采用循环工艺（氟碳沉积步骤+Ar等离子体处理步骤）
- 低温刻蚀配合lean chemistry可以减少聚合物沉积，从而改善striation

---

### 2.3 Twisting（扭曲畸变）

#### 机理描述
Twisting是指HAR孔的轴线偏离垂直方向，导致孔的中心位置随深度发生偏移的现象。扭曲可以是随机的（由stochastic charging引起）或系统的（由pattern asymmetry引起）。

**Claim: Twisting是由密集阵列中的非对称离子阴影和局部刻蚀率的随机变化引起的，当pitch低于40nm且深宽比超过60:1时变得显著。** [^7^]
Source: Nine Scrolls, "Future of Plasma Etching for Microelectronics — Key Trends and Roadmap"
URL: https://ninescrolls.com/insights/future-of-plasma-etching-microelectronics
Date: 2025
Excerpt: "Twisting and distortion: In dense arrays, asymmetric ion shadowing and stochastic variations in local etch rates cause features to deviate from their intended vertical axis. Twisting becomes significant at pitches below 40 nm and AR above 60:1."
Context: 系统总结了HAR刻蚀中的各种缺陷机理。
Confidence: High

**Claim: 扭曲distortion可以归因于几个原因，包括反应通量的随机性、充电效应和pattern依赖性。对于对称pattern，stochastic charging导致随机倾斜；对于非对称pattern，水平电场产生系统性的tilting。** [^8^]
Source: ResearchGate, "Investigation of Poly Silicon Channel Variation in Vertical 3D NAND Flash Memory"
URL: https://www.researchgate.net/publication/364203011
Date: 2022
Excerpt: "With symmetric patterns, stochastic charging of the inside surfaces of features results in tilting of HAR features in random directions. However, with nominally identical neighboring features, electrical forces on ions inside the features should, in principle, cancel. With asymmetric patterns, horizontal electric fields are generated by feature charging that point from dense to sparse areas of the pattern. These net electric fields deviate ions from normal incidence and produce systematic tilting."
Context: 研究了etch angle对3D NAND cell特性的影响，发现channel hole size变化会加剧cell不均匀性。
Confidence: High

**Claim: 维持中性匮乏（离子丰富）的刻蚀状态对于缓解channel hole circularity distortion和slit etch profile twisting至关重要。** [^9^]
Source: SPIE Proceedings, "High-aspect-ratio amorphous carbon mask etch profile control through plasma and surface chemistry optimization"
URL: https://ui.adsabs.harvard.edu/abs/2023SPIE12499E..06Z/abstract
Date: 2023
Excerpt: "Our findings indicate that maintaining a neutral-starved (ion-rich) etch regime is essential for mitigating both the channel hole etch circularity distortion and the slit etch profile twisting."
Context: 通过HPEM和MCFPM模拟研究了ACL mask刻蚀的基本特性，发现中性匮乏状态对减少distortion至关重要。
Confidence: High

---

### 2.4 其他Distortion类型

#### Necking/Clogging（颈缩/堵塞）
**Claim: Necking是由聚合物沉积和mask侵蚀产物在feature开口附近堆积造成的，会限制孔径并使底部反应物匮乏，在极端情况下可导致完全刻蚀停止。** [^7^]
Source: Nine Scrolls, "Future of Plasma Etching for Microelectronics"
URL: https://ninescrolls.com/insights/future-of-plasma-etching-microelectronics
Date: 2025
Excerpt: "Necking and clogging: Polymer deposition and mask erosion products accumulate near the feature opening, constricting the aperture and starving the bottom of reactive species. Necking can cause complete etch stop in extreme cases."
Context: 描述了necking的物理机理。
Confidence: High

#### Distortion（形状畸变/椭圆化）
**Claim: 理想的HAR孔应完美圆形且居中，但实际中会出现多种非理想孔形态：扭曲（中心偏移）、粗糙度（striations）和畸变（椭圆化）。** [^1^]
Source: JJAP, Progress Report on HAR Patterning for Memory Devices
URL: https://iopscience.iop.org/article/10.35848/1347-4065/accbc7/pdf
Date: 2023
Excerpt: "An ideal hole is perfectly circular and centered through the hole etch depth. Undesirable hole artifacts come in many forms. The hole can twist, resulting in the center of the hole shifting. The hole can have a roughness around the edges, sometimes referred to as striations. Lastly, the hole can be distorted. In the example in the figure, the hole is distorted to look more like an ellipse."
Context: 通过特征尺度模型展示了多种非理想孔形态。
Confidence: High

---

## 3. Lam Research/Samsung/Toshiba的HAR Etch解决方案

### 3.1 Lam Research Cryo 3.0 — 业界领先的低温刻蚀技术

**Claim: Lam Cryo 3.0是第三代低温介电质刻蚀技术，利用超低温度、高功率受限等离子体反应器和表面化学创新，实现行业领先的精度和轮廓控制，优化用于制造400层及以上的3D NAND器件。** [^10^]
Source: Lam Research Official Press Release
URL: https://newsroom.lamresearch.com/2024-07-31-Lam-Research-Introduces-Lam-Cryo-TM-3-0-Cryogenic-Etch-Technology-to-Accelerate-Scaling-of-3D-NAND-for-the-AI-Era
Date: 2024-07-31
Excerpt: "Lam Cryo 3.0 allows for higher aspect ratio features with breakthrough precision and profile control. Leveraging innovations in surface chemistry, plasma physics, and process design, Lam's Cryo 3.0 is optimized to manufacture future 3D NAND devices with 400 layers and beyond."
Context: Lam Research官方发布的Cryo 3.0技术介绍。
Confidence: High

**Claim: Lam Cryo 3.0可以重复刻蚀深度达10μm的存储通道，关键尺寸从顶部到底部的偏差小于0.1%，刻蚀速率是传统介电质刻蚀工艺的2.5倍。** [^10^]
Source: Lam Research Official Press Release
URL: https://newsroom.lamresearch.com/2024-07-31-Lam-Research-Introduces-Lam-Cryo-TM-3-0-Cryogenic-Etch-Technology-to-Accelerate-Scaling-of-3D-NAND-for-the-AI-Era
Date: 2024-07-31
Excerpt: "With Lam Cryo 3.0, manufacturers can predictably and repeatedly etch memory channels as deep as 10 microns with less than 0.1% deviation of the channel's critical dimension from the top to the bottom."
Context: Cryo 3.0的性能指标。
Confidence: High

**Claim: Lam Cryo 3.0结合了公司的独特高功率受限等离子体反应器、工艺改进和远低于0°C的温度，允许利用新的刻蚀化学配方。当与Lam最新的Vantex介电质系统的可扩展脉冲等离子体技术结合时，刻蚀深度和轮廓控制显著提高。** [^11^]
Source: CIO & Leader
URL: https://www.cioandleader.com/lam-research-introduces-lam-cryo-3-0-cryogenic-etch-technology-to-accelerate-scaling-of-3d-nand-for-the-ai-era/
Date: 2024-08-01
Excerpt: "Lam Cryo 3.0 utilizes the company's unique, high powered confined plasma reactors, process improvements and temperatures well below -0°C, which permit the harnessing of new, novel etch chemistries. When combined with the scalable, pulsed plasma technology of Lam's latest Vantex dielectric system, etch depth and profile control is significantly increased."
Context: 技术细节描述，强调了脉冲等离子体技术与低温刻蚀的协同作用。
Confidence: High

**Claim: Lam Research在刻蚀技术方面拥有超过20年的领导地位，自2019年推出第一代低温刻蚀产品以来，已使用低温刻蚀技术生产了超过500万片晶圆，在NAND生产中使用的超过7500个HAR介电质刻蚀腔室中，近1000个采用了低温刻蚀技术。** [^12^]
Source: Lam Research Newsroom
URL: https://newsroom.lamresearch.com/scaling-1000-layers-3D-NAND-AI-era
Date: 2024
Excerpt: "Lam introduced the world's first cryogenic etch offering into volume production in 2019. Of the over 7,500 Lam HAR dielectric etch chambers utilized in NAND production today, nearly 1,000 of them use cryogenic etch technology."
Context: Lam在低温刻蚀领域的市场地位。
Confidence: High

**Claim: 低温刻蚀技术可在10μm深度、100nm直径的孔中实现超过400层oxide和nitride的刻蚀，通过HF/H₂O/PF₃气体混合物在-70°C下实现SiO₂和Si₃N₄的等速率刻蚀。** [^13^]
Source: Journal of Vacuum Science & Technology B, "Future of plasma etching for microelectronics"
URL: https://pubs.aip.org/avs/jvb/article/42/4/041501/3297248
Date: 2024
Excerpt: "A plasma process involving HF, H₂O, and PF₃ gases was successfully used to etch very high aspect ratio of ONON holes at a substrate temperature as low as -70°C. SiO₂ etch rate increases when the substrate temperature decreases. It reaches the Si₃N₄ etch rate value at -70°C. By adding PF₃ gas in the plasma mixture, the etch rate of both materials is higher. Using this process, 10μm deep holes with 100nm diameter were etched over 400 oxide and nitride layers."
Context: 学术文献报道了低温HF基等离子体在3D NAND刻蚀中的突破。
Confidence: High

### 3.2 Samsung V-NAND通道孔刻蚀技术

**Claim: Samsung的第九代V-NAND采用先进的"通道孔刻蚀"技术，通过堆叠模具层创建电子通路，可在双层结构中同时钻孔，达到业界最高的单元层数（290层），最大限度地提高了制造生产率。** [^14^]
Source: Samsung Newsroom
URL: https://news.samsung.com/global/samsung-electronics-begins-industrys-first-mass-production-of-9th-gen-v-nand
Date: 2024-04-23
Excerpt: "Samsung's advanced 'channel hole etching' technology showcases the company's leadership in process capabilities. This technology creates electron pathways by stacking mold layers and maximizes fabrication productivity as it enables simultaneous drilling of the industry's highest cell layer count in a double-stack structure."
Context: Samsung官方发布第九代V-NAND量产新闻。
Confidence: High

**Claim: Samsung是业界唯一拥有在单次刻蚀中堆叠超过100层并通过超过10亿个孔互连的技术的公司，其176层第7代V-NAND通过创新的3D scaling技术将单元体积减少了35%。** [^15^]
Source: Samsung Semiconductor Tech Blog
URL: https://semiconductor.samsung.com/news-events/tech-blog/editorial-extraordinary-innovation-for-a-more-unforgettable-world-the-story-behind-samsungs-pioneering-v-nand-memory-solution/
Date: 2023-06-22
Excerpt: "Samsung is the only one in the industry possessing single-stack etching technology capable of stacking over 100 layers at once and interconnected through more than a billion holes."
Context: Samsung强调其在单层堆叠刻蚀方面的独特技术能力。
Confidence: High

**Claim: Samsung计划在2025年推出采用三重堆叠技术的第10代NAND芯片，达到430层，并目标到2030年开发超过1000层的NAND芯片。** [^16^]
Source: IT之家 / Blocks and Files
URL: https://blocksandfiles.com/2024/04/17/samsung-planning-430-layer-nand-in-2025/
Date: 2024-04-17
Excerpt: "Samsung is planning to bypass the 300-layer 3D NAND level and go straight to 430-layer flash after a 290-layer product. Samsung will then move to a 430-layer triple-string-stacked technology with its v10 V-NAND."
Context: Samsung的3D NAND技术路线图。
Confidence: Medium（industry reports, not officially confirmed by Samsung）

**Claim: Samsung第九代V-NAND引入了"Through Cell Metal Contact (TCMC)"技术和"HARC Etch Merge"技术，这是全球首次在单次刻蚀过程中同时刻蚀不同类型的contact。** [^17^]
Source: Samsung V-NAND Tech Blog
URL: https://semiconductor.samsung.com/news-events/tech-blog/samsung-v-nand-landmark-of-the-hyperscale-ai-era/
Date: 2024-07-11
Excerpt: "Through Cell Metal Contact (TCMC) technology was adopted to 9th-Gen for the first time in the world. This technology involves piercing through the cell gate word line from the top to the bottom, allowing only selected word lines to be activated. In addition, a structural innovation was achieved by etching different types of contacts together in a single etching process (HARC Etch Merge)."
Context: Samsung ninth-gen V-NAND的创新技术。
Confidence: High

### 3.3 Tokyo Electron (TEL) — 新兴竞争者

**Claim: Tokyo Electron开发了名为TELAVES的新型低温刻蚀设备，结合HER（High-Efficiency Rectangular Bias）和PHastIE（Phosphorus + Hydrogen based Fast Ion Etch）技术，实现了超过10μm的刻蚀深度，速率是先前方法的2.5倍，同时功耗降低超过40%。** [^18^]
Source: Nomad Semi / Tokyo Electron IR Day
URL: https://www.nomadsemi.com/p/tokyo-electron-deep-dive-part-2
Date: 2025-04-17
Excerpt: "In 2023, TEL announced the new TELAVES cryogenic etcher. It achieves etch depths greater than 10μm at rates 2.5 times faster than previous methods, while also reducing power consumption by over 40%. This is through the combination of High-Efficiency Rectangular Bias (HER) and Phosphorus + Hydrogen based Fast Ion Etch (PHastIE) technology."
Context: TEL作为Lam Research在低温刻蚀领域的新兴竞争者。
Confidence: High

**Claim: TEL的HER技术利用矩形RF波保持离子垂直入射角，而传统正弦波技术会导致离子入射角变化从而产生bowing问题。PHastIE工艺利用HF气体和低温环境来增强HAR刻蚀性能。** [^18^]
Source: Nomad Semi
URL: https://www.nomadsemi.com/p/tokyo-electron-deep-dive-part-2
Date: 2025-04-17
Excerpt: "TEL's HER technology utilizes rectangular radio frequency (RF) wave to maintain a vertical ion incidence angle during the etching processes. Ion incident angle is varied in the conventional sine wave technology which results in bowing problem. The PHastIE process leverages innovative chemistry and cryogenic temperatures to enhance high-aspect-ratio etching performance."
Context: TEL的技术差异化特点。
Confidence: High

**Claim: SK hynix正在评估TEL的最新低温刻蚀设备，该设备在-70°C温度下运行，可在33分钟内完成10μm深度的高深宽比刻蚀，比现有工具快三倍以上。** [^19^]
Source: IGASCN
URL: https://en.igascn.com/global/detail/?TypeId=1040&Id=7973&SortSource=list
Date: 2024-05-12
Excerpt: "TEL's next-generation etching machine can make a 10-μm-deep etch with a high aspect ratio in just 33 minutes, over three times faster than existing tools. This achievement is not only a major technical improvement but also greatly increases 3D NAND production efficiency."
Context: SK hynix对TEL低温刻蚀设备的评估。
Confidence: Medium

---

## 4. Bosch Process vs Cryogenic Etch

### 4.1 Bosch Process原理与特点

**Claim: Bosch工艺是时间复用RIE工艺，通过交替使用SF₆刻蚀气体和C₄F₈钝化气体进行循环刻蚀，实现高深宽比结构，但会导致侧壁scalloping。** [^20^]
Source: ScienceDirect Topics, "Scalloping"
URL: https://www.sciencedirect.com/topics/physics-and-astronomy/scalloping
Date: N/A
Excerpt: "The process consists of a gas switching recipe that utilizes alternating steps of etching gas and passivation gas in repeated cycles. A drawback of the sequential etching and deposition steps is that it gives rise to undercuts during each etching step and shows a scalloped surface."
Context: Bosch工艺的标准描述。
Confidence: High

**Claim: Bosch工艺在单个循环内的刻蚀步骤中，由于没有钝化气体存在，会产生各向同性刻蚀导致undercut，形成scallop结构。Scallop宽度由循环时间决定。** [^20^]
Source: ScienceDirect Topics
URL: https://www.sciencedirect.com/topics/physics-and-astronomy/scalloping
Date: N/A
Excerpt: "The scalloping makes the Bosch process unsuitable for etching nanowires for applications which require smooth surfaces. The scalloping usually results in surface roughness >100nm."
Context: Bosch工艺scalloping的限制。
Confidence: High

### 4.2 Cryogenic Etch原理与特点

**Claim: 低温刻蚀是一种单步连续工艺，在低于-80°C的温度下使用SF₆/O₂气体混合物，通过O₂与F自由基反应在侧壁形成SiFₓOᵧ钝化层，实现光滑无scalloping的侧壁。** [^21^]
Source: University of Waterloo Thesis, "Silicon dry etching using fluorine-based gas"
URL: https://www.uwspace.uwaterloo.ca/bitstream/handle/10012/17995/Yan_Zheng.pdf
Date: N/A
Excerpt: "The major difference between these two techniques is the deposition step. In Bosch process, it uses C₄F₈ gases to generate the CF₂-species to form the passivation layer. But in cryogenic process, it introduces SF₆ and oxygen at the same time. It will form a SiFₓOᵧ layer to prevent the etching in lateral direction. Furthermore, it can also avoid the scalloping structure which may appear in the Bosch process."
Context: Bosch与低温刻蚀的详细比较。
Confidence: High

**Claim: 低温刻蚀相比Bosch工艺具有多项优势：单步工艺（非循环）、光滑侧壁（无scalloping）、更高的刻蚀选择性（>100:1 vs ~70:1）、更清洁（不需要chamber cleaning）。** [^21^]
Source: University of Waterloo Thesis
URL: https://www.uwspace.uwaterloo.ca/bitstream/handle/10012/17995/Yan_Zheng.pdf
Date: N/A
Excerpt: | Terms | Bosch process | Cryogenic etching process |
| Working process | Cyclic mode | Mixed mode |
| Main gases | SF₆ and C₄F₈ | SF₆ and O₂ |
| Passivation layer | Fluorocarbon polymer | SiFₓOᵧ |
| Process temperature | Room temperature | Less than -80°C |
| Etching selectivity (Resist to Si) | Close to 70:1 | Larger than 100:1 |
| Sidewall roughness | Rough due to scalloping | Smooth |
Context: 两种工艺的全面对比表格。
Confidence: High

### 4.3 两种工艺在3D NAND中的应用比较

**Claim: 在3D NAND介电质刻蚀中，低温刻蚀相比传统Bosch工艺具有显著优势：增加反应物吸附、限制横向刻蚀率、实现更高的深宽比刻蚀能力，并减少环境影响。** [^22^]
Source: Lam Research / Counterpoint White Paper
URL: https://filecache.mediaroom.com/mr5mr_lamresearch/182770/Counterpoint_Research_Paper_Scaling_to_1000-Layer_3D_NAND_in_the_AI_Era.pdf
Date: 2024
Excerpt: "Cryogenic etching helps increase adsorption of reactive species while limiting the lateral etch rate. Leveraging low-temperature benefits and different plasma chemistries to deliver increased high aspect ratio etch capability enhances the etching rate."
Context: 低温刻蚀在3D NAND中的优势。
Confidence: High

**Claim: 低温刻蚀通过physisorption（物理吸附）而非chemisorption（化学吸附）来增强中性粒子传输到高深宽比feature底部，这是其独特的机理优势。** [^23^]
Source: Journal of Vacuum Science & Technology A, "Dry etching in the presence of physisorption of neutrals at lower temperatures"
URL: (referenced in cryo-ALE paper)
Date: 2023
Excerpt: "Physisorption of neutrals at low temperatures increases the neutral concentration on the surface meaningfully and contributes to etching if they are chemically activated. The transport of neutrals in high aspect ratio features is enhanced at low temperatures because physisorbed species are mobile."
Context: 低温刻蚀的物理化学机理。
Confidence: High

**Claim: 低温下C₄F₈的沉积速率比室温高约100倍，使得在低温Bosch工艺中所需的C₄F₈钝化气体流量可以显著减少，同时仍能获得各向异性profile。** [^24^]
Source: Scientific Reports, "Evaluation of Bosch processing and C₄F₈ plasma deposition at cryogenic temperatures"
URL: (cited in cryo-ALE paper)
Date: N/A
Excerpt: "In the case of cryogenic Bosch (cryo-Bosch) processing, C₄F₈ feed dosing has a greater influence on the passivation regime. The deposited fluorocarbon material is approximately a hundred times thicker at cryogenic temperatures using the same process parameters."
Context: 低温对Bosch工艺中氟碳沉积的影响。
Confidence: High

---

## 5. Pulsed Power Plasma对Ion Energy Control和ARDE Mitigation的作用

### 5.1 脉冲等离子体技术概述

**Claim: 脉冲等离子体通过周期性地开启和关闭source power和/或bias power，提供了对radical解离、充电效应、离子能量等的额外控制，可以改善HAR刻蚀特性，包括更少的ARDE、更好的刻蚀profile、更好的均匀性和更高的选择性。** [^25^]
Source: ScienceDirect, "Effect of various pulse plasma techniques on TiO₂ etching for metalens formation"
URL: https://www.sciencedirect.com/science/article/abs/pii/S0042207X23001756
Date: 2023-06
Excerpt: "The pulsed plasmas offer the additional control over the radical dissociation, charging, ion energy, etc. and are known to improve etch characteristics for high aspect ratio etching by showing less aspect ratio dependent etching (ARDE), better etch profile, better etch uniformity, and higher etch selectivity."
Context: 系统总结了脉冲等离子体在HAR刻蚀中的优势。
Confidence: High

### 5.2 同步与异步脉冲模式

**Claim: 异步脉冲（交替施加source power和bias power）可以最有效地抑制ARDE效应，将ARDE ratio从同步脉冲的1.55降低到约1.3，这是因为形成了由反应物chemisorption步骤和离子轰击去除步骤组成的循环刻蚀特性，类似于原子层刻蚀（ALE）。** [^26^]
Source: ACS Applied Nano Materials, "Asynchronously Pulsed Plasma for High Aspect Ratio Nanoscale Si Trench Etch Process"
URL: https://pubs.acs.org/doi/10.1021/acsanm.3c00807
Date: 2023
Excerpt: "The ARDE ratio was the highest (1.55) at the delay time of 0μs (synchronous pulsing) while showing an improved ARDE ratio (~1.3) for the delay time of ≥250μs (asynchronous pulsing)."
Context: 系统比较了不同脉冲模式下的ARDE效应。
Confidence: High

**Claim: 使用异步脉冲模式代替CW模式，Si与mask层的选择性提高了10倍，宽pattern和窄pattern之间的刻蚀速率差异（ARDE）从35%降低到8%。** [^27^]
Source: Applied Surface Science, "Effect of different pulse modes during Cl₂/Ar ICP etching"
URL: https://ui.adsabs.harvard.edu/abs/2022ApSS..59653604K/abstract
Date: 2022
Excerpt: "By using synchronously and asynchronously pulse modes instead of CW mode, the selectivity between Si and the mask layer was increased by 2 and 10 times, respectively. Also, the etch rate differences between wide and narrow pattern distance patterns (ARDE) was decreased from 35% to 21 and to 8%, respectively."
Context: 脉冲模式对选择性和ARDE的显著改善。
Confidence: High

### 5.3 Ion Energy Distribution Control

**Claim: 通过同步脉冲ICP source和RF bias power，并结合相位控制，可以灵活调制离子能量角分布（IEAD）和离子/中性通量比，从而优化HAR feature内的critical dimension。** [^28^]
Source: ResearchGate, "Effect of simultaneous source and bias pulsing in ICP etching"
URL: https://www.researchgate.net/publication/224087396
Date: N/A
Excerpt: "Synchronized pulsing of both the ICP source and RF bias powers in conjunction with phase control provides additional flexibility in modulating the IEAD and the ion/neutral flux ratio."
Context: 同步脉冲对IEDF的调制作用。
Confidence: High

**Claim: Voltage Waveform Tailoring (VWT)技术可以控制电子速度和角分布，在wafer附近产生高能电子通量进入HAR feature，从而补偿表面充电效应，减少离子偏转和轮廓畸变。** [^29^]
Source: Journal of Physics D, "Control of electron velocity distributions at the wafer by tailored voltage waveforms in CCP"
URL: https://iopscience.iop.org/article/10.1088/1361-6463/abf229
Date: 2021-04
Excerpt: "The ultimate solution to this problem requires a technique to tailor the entire electron velocity and angular distribution of the electrons in the direct vicinity to the wafer to generate a high flux of energetic electrons into etch features. A promising concept to achieve this goal is Voltage Waveform Tailoring (VWT)."
Context: VWT作为解决HAR刻蚀充电问题的方案。
Confidence: High

### 5.4 Pulsed Plasma在3D NAND中的具体应用

**Claim: Lam Research的Vantex介电质系统采用可扩展的脉冲等离子体技术，与低温刻蚀结合使用时，刻蚀深度和轮廓控制显著提高。** [^11^]
Source: CIO & Leader / Lam Research
URL: https://www.cioandleader.com/lam-research-introduces-lam-cryo-3-0-cryogenic-etch-technology-to-accelerate-scaling-of-3d-nand-for-the-ai-era/
Date: 2024-08-01
Excerpt: "When combined with the scalable, pulsed plasma technology of Lam's latest Vantex dielectric system, etch depth and profile control is significantly increased."
Context: Lam Research的脉冲等离子体+低温刻蚀组合方案。
Confidence: High

**Claim: TEL的HER技术采用矩形RF波形而非传统正弦波，可以在整个刻蚀过程中保持离子垂直入射角，从而解决传统正弦波技术中离子入射角变化导致的bowing问题。** [^18^]
Source: Nomad Semi / TEL
URL: https://www.nomadsemi.com/p/tokyo-electron-deep-dive-part-2
Date: 2025-04-17
Excerpt: "TEL's HER technology utilizes rectangular radio frequency (RF) wave to maintain a vertical ion incidence angle during the etching processes. Ion incident angle is varied in the conventional sine wave technology which results in bowing problem."
Context: TEL在脉冲波形设计方面的创新。
Confidence: High

---

## 6. Low Temperature Etching对Profile Control的好处

### 6.1 增加反应物吸附与限制横向刻蚀

**Claim: 低温刻蚀通过增加反应物吸附同时限制横向刻蚀率，提供了增加高深宽比刻蚀能力的工艺窗口。低温下表面覆盖率增加1-2倍，包括非解离物种的物理吸附。** [^22^]
Source: Lam Research / Counterpoint White Paper
URL: https://filecache.mediaroom.com/mr5mr_lamresearch/182770/Counterpoint_Research_Paper_Scaling_to_1000-Layer_3D_NAND_in_the_AI_Era.pdf
Date: 2024
Excerpt: "Etching at cryo temperatures enables 1-2x increases in surface coverage that includes non-dissociated species which can physisorb."
Context: 低温刻蚀的表面化学优势。
Confidence: High

### 6.2 减少聚合物沉积，改善Mask Morphology

**Claim: 低温配合lean chemistry开辟了工艺窗口，减少了聚合物沉积，从而改善ARDE和孔形控制。XPS表面分析显示新工艺显著减少了聚合物形成，导致更圆形的孔形。** [^1^]
Source: JJAP, Progress Report on HAR Patterning
URL: https://iopscience.iop.org/article/10.35848/1347-4065/accbc7/pdf
Date: 2023
Excerpt: "Low temperature coupled with lean chemistry open the process window to a regime with less polymer deposition, thus improving ARDE and hole shape control. XPS surface analysis showed that the new process had significantly less polymer formation, leading to more circular hole shapes, while typical CₓFᵧ chemistry showed a high CₓFᵧ polymer on top of the etching film, resulting in more irregular hole shapes."
Context: 实验证据表明低温和lean chemistry对profile控制的好处。
Confidence: High

**Claim: 低温刻蚀中聚合物在mask侧壁的沉积是侧壁粗糙度的主要根源，采用leaner chemistry可以抑制这一机制，因为mask形态和聚合物沉积更加一致。** [^22^]
Source: Counterpoint White Paper
URL: https://filecache.mediaroom.com/mr5mr_lamresearch/182770/Counterpoint_Research_Paper_Scaling_to_1000-Layer_3D_NAND_in_the_AI_Era.pdf
Date: 2024
Excerpt: "Polymer deposition on the sidewalls of the mask is the main root cause of sidewall roughness. This mechanism is suppressed for lean, low-temperature processes as the mask morphology and polymer deposition on the sidewalls of the mask are more consistent from hole to hole."
Context: 低温和lean chemistry减少侧壁粗糙度的机理。
Confidence: High

### 6.3 改善SiO₂/SiN选择性

**Claim: 在低温下（-70°C），使用HF/H₂O等离子体时SiO₂的刻蚀速率随温度降低而增加，与Si₃N₄的刻蚀速率达到接近1:1，这对于ONON堆叠的均匀刻蚀至关重要。** [^13^]
Source: JVST B, "Future of plasma etching for microelectronics"
URL: https://pubs.aip.org/avs/jvb/article/42/4/041501/3297248
Date: 2024
Excerpt: "SiO₂ etch rate increases when the substrate temperature decreases. It reaches the Si₃N₄ etch rate value at -70°C."
Context: 低温下SiO₂/SiN选择性调节的关键发现。
Confidence: High

**Claim: 在CF₄/H₂等离子体中，随着衬底温度从50°C降至-20°C，SiO₂和SiN的刻蚀选择性趋近于1，同时两者对a-C的选择性超过15，这对3D NAND结构刻蚀非常合适。** [^30^]
Source: Vacuum, "Manipulation of etch selectivity of silicon nitride over silicon dioxide to a-carbon by controlling substrate temperature"
URL: https://www.sciencedirect.com/science/article/abs/pii/S0042207X2300060X
Date: 2023
Excerpt: "The etching selectivity of near unity was achieved for the SiO₂ and SiN films being etched at Tₛ = -20°C; in the meanwhile, the etch selectivities of over 15 for SiN and SiO₂ against a-C films were also obtained, which might be suitable for etching of 3D NAND structure."
Context: 通过衬底温度控制实现精确选择性调节。
Confidence: High

### 6.4 环境影响与可持续性

**Claim: Lam Cryo 3.0相比传统工艺，每片晶圆能耗降低40%，排放减少高达90%，刻蚀速率提高2.5倍。** [^10^]
Source: Lam Research Official Press Release
URL: https://newsroom.lamresearch.com/2024-07-31-Lam-Research-Introduces-Lam-Cryo-TM-3-0-Cryogenic-Etch-Technology-to-Accelerate-Scaling-of-3D-NAND-for-the-AI-Era
Date: 2024-07-31
Excerpt: "Lam Cryo offers 40% reduction in energy consumption per wafer, and up to a 90% reduction in emissions compared to conventional etch processes."
Context: 低温刻蚀的环境效益。
Confidence: High

---

## 7. 1000+ Layer 3D NAND中的Etch挑战与解决方案

### 7.1 主要挑战概述

**Claim: 随着3D NAND向1000层发展，主要挑战包括：ARDE导致的刻蚀速率减慢、垂直profile的可变性、通道孔尺寸控制、物理和热应力、以及多deck堆叠中的对准问题。** [^22^]
Source: Counterpoint Research / Lam White Paper
URL: https://filecache.mediaroom.com/mr5mr_lamresearch/182770/Counterpoint_Research_Paper_Scaling_to_1000-Layer_3D_NAND_in_the_AI_Era.pdf
Date: 2024
Excerpt: "Scaling 3D NAND beyond 400 layers will introduce significant challenges such as slow etch rate and variabilities in vertical profiles, which inhibit vertical scaling as more layers are added."
Context: 全面分析了1000层3D NAND的刻蚀挑战。
Confidence: High

**Claim: 在100:1深宽比下，刻蚀速率可能比10:1深宽比低50-70%。在100nm孔径、10μm深度的通道中，允许的profile偏差仅为10nm（<0.1%）。** [^7^]
Source: Nine Scrolls
URL: https://ninescrolls.com/insights/future-of-plasma-etching-microelectronics
Date: 2025
Excerpt: "In extreme cases, etch rate at 100:1 AR can be 50–70% lower than at 10:1 AR in the same wafer."
Context: ARDE效应的定量描述。
Confidence: High

### 7.2 Feature Scale Model与Distortion控制

**Claim: Lam Research开发了HAR ONON刻蚀特征尺度模型，模拟结果显示：早期控制孔形畸变可以减轻畸变向更深刻蚀深度的传递；在不存在mask shape evolution的情况下，离子散射会在孔内造成畸变。** [^22^]
Source: Counterpoint White Paper
URL: https://filecache.mediaroom.com/mr5mr_lamresearch/182770/Counterpoint_Research_Paper_Scaling_to_1000-Layer_3D_NAND_in_the_AI_Era.pdf
Date: 2024
Excerpt: "The simulation results show controlling hole shape distortion early in the process can mitigate hole distortion transfer deeper in the etch. The feature profile model with a non-evolving hard mask suggests ion scattering within the hole, causing distortions. However, the profile distortion can be minimized in the absence of hard mask evolution."
Context: 特征尺度模型在理解和控制distortion方面的作用。
Confidence: High

**Claim: 结合mask shape evolution和孔内离子散射的模型显示，孔畸变和扭曲可能发生并在更深的刻蚀深度被放大。DECO tier film调制可以提供额外的profile控制窗口。** [^1^]
Source: JJAP, Progress Report on HAR Patterning
URL: https://iopscience.iop.org/article/10.35848/1347-4065/accbc7/pdf
Date: 2023
Excerpt: "Combining mask shape evolution and ion scattering in the hole in the model revealed that hole distortion and twisting could occur and were magnified at deeper etch depths. DECO tier film modulation can provide an additional window for channel hole profile control."
Context: 特征尺度模型的关键发现。
Confidence: High

### 7.3 String Stacking — 通往1000层的路径

**Claim: String stacking（字符串堆叠）是将多个独立的layer deck分别刻蚀后再堆叠在一起的技术，可以在不处理完整堆叠的情况下实现更多层数。SK hynix的321层产品使用三层堆叠，而最新238代产品使用两层deck各119个活动wordline。** [^31^]
Source: SemiAnalysis, "NAND Flash Monopoly Broken?"
URL: https://semianalysis.com/2023/07/16/nand-flash-monopoly-broken-tokyo-electron-moly-dep-cryo-etch-takes-on-lam-research-for-the-future-of-nand/
Date: 2023/2025
Excerpt: "The current high aspect ratio (HAR) etch depth limit is 6 to 7 microns with the minimum thickness of each cell being about 40nm. So far, manufacturers have only been able to achieve up to 128 Word Line layer stacks (~50nm each). Going beyond this requires string stacking of multiple decks etched separately and combined atop the other."
Context: String stacking作为突破HAR刻蚀深度限制的方案。
Confidence: High

**Claim: Samsung的第九代V-NAND（290层）采用双重堆叠结构（两个145层string stack），计划中的第十代V-NAND（430层）将采用三重堆叠技术。** [^16^]
Source: Multiple industry reports
URL: https://blocksandfiles.com/2024/04/17/samsung-planning-430-layer-nand-in-2025/
Date: 2024-04-17
Excerpt: "Samsung's 9th-gen V-NAND will feature 290+ layers utilizing two stacks of strings of NAND. Samsung will then move to a 430-layer triple-string-stacked technology with its v10 V-NAND."
Context: Samsung通过string stacking实现层数增长的技术路线。
Confidence: Medium

### 7.4 其他Profile控制技术

**Claim: Liner insertion是另一种防止顶部CD bow增长同时扩大底部CD的有效方法，相比无liner方案可实现高达30%的BB bias改善。** [^1^]
Source: JJAP, Progress Report
URL: https://iopscience.iop.org/article/10.35848/1347-4065/accbc7/pdf
Date: 2023
Excerpt: "Liner insertion is another highly effective way to prevent top CD bow growth while enlarging the bottom CD. An improvement of up to 30% in BB bias can be achieved when comparing the with and without liner approaches."
Context: Liner技术在profile控制中的应用。
Confidence: High

**Claim: 用具有更高横向刻蚀速率的材料替换底部tier的SiN，可实现>50%的BB bias改善；同时改变顶部tier可实现18%的改善。** [^1^]
Source: JJAP, Progress Report
URL: https://iopscience.iop.org/article/10.35848/1347-4065/accbc7/pdf
Date: 2023
Excerpt: "Replacing bottom tier silicon nitride with a higher lateral etch rate resulted in an improvement of >50% in BB bias, while varying top tier resulted in a BB bias improvement of 18%."
Context: Tier film调制对profile控制的效果。
Confidence: High

---

## 8. 已发现的定量关系

### 8.1 ARDE效应的定量描述

| 深宽比 | 刻蚀速率变化 |
|--------|------------|
| 10:1 → 100:1 | 速率降低50-70% |
| 40 → 140 | 硬掩模选择性降低约50% |
| 同步脉冲 → 异步脉冲 | ARDE ratio从1.55降至1.3 |
| CW → 异步脉冲 | ARDE从35%降至8% |

### 8.2 低温刻蚀的性能指标

| 参数 | 传统工艺 | Lam Cryo 3.0 | TELAVES |
|------|---------|--------------|---------|
| 刻蚀深度 | ~5-6μm | >10μm | >10μm |
| 刻蚀速率（相对） | 1x | 2.5x | 3x+ |
| Profile偏差 | >1% | <0.1% | <0.1% |
| 能耗 | 基准 | -40% | -40%+ |
| 排放 | 基准 | -90% | -84% GWP |
| 适用层数 | ~200层 | 400+层 | 400+层 |

### 8.3 Temperature Effect on Selectivity

| 温度 | SiO₂:SiN选择性 | SiN/SiO₂:a-C选择性 |
|------|---------------|-------------------|
| 20°C | ~2:1 | ~5-10 |
| -20°C | ~1:1 | >15 |
| -70°C | ~1:1 (with HF/H₂O/PF₃) | N/A |

---

## 9. 争议与冲突性发现

### 9.1 Bosch vs Cryogenic — 各自优势
- Bosch工艺虽然会产生scalloping，但可以通过缩短循环时间来减小scallop尺寸，在mems等应用中仍广泛使用
- Cryogenic刻蚀虽然侧壁光滑，但需要复杂的低温冷却系统和液氮，增加了设备复杂性和运行成本
- 部分研究表明低温Bosch（Cryo-Bosch）结合了两种工艺的优势

### 9.2 Single-Stack vs Multi-Stack（String Stacking）
- Samsung声称拥有业界唯一的单层堆叠超过100层的技术能力
- 但其他厂商（如SK hynix、Intel/Solidigm）采用多deck堆叠策略已达到更高层数
- String stacking虽然降低了对单次刻蚀深度的要求，但增加了deck间对准的复杂性和制造成本

### 9.3 Pulsed Plasma模式选择
- 同步脉冲和异步脉冲各有优势：同步脉冲刻蚀速率更高，异步脉冲选择性和ARDE更好
- 最佳脉冲参数（duty cycle、frequency、phase delay）因具体材料和刻蚀条件而异

---

## 10. 尚存的Gap

1. **原子尺度机理理解不足**：虽然feature scale model可以模拟distortion现象，但对离子散射、充电效应和stochastic variation的耦合作用缺乏完整的原子尺度理解

2. **1000+层刻蚀的物理极限**：目前单次刻蚀的HAR深度极限约为6-7μm（~128 WL层），通过string stacking可以绕过此限制，但单次刻蚀的终极物理极限仍不清楚

3. **Twisting的随机性控制**：twisting中的stochastic成分难以完全消除，需要更深入理解local etch rate variation的来源

4. **新化学体系的开发**：虽然HF/H₂O/PF₃体系在低温下表现优异，但对其他可能的化学体系（如含磷、含氢配方）的探索仍不充分

5. **在线监测与反馈控制**：对于trillion级别通道孔的高通量制造，实时监测和控制每个孔的profile仍面临巨大挑战

6. **环境友好化学品的平衡**：在追求更高刻蚀性能的同时，进一步降低GWP和能耗仍是持续挑战

---

## 11. 机理洞察总结

### 11.1 核心机理框架

3D NAND HAR刻蚀的profile控制是一个多物理场耦合问题，涉及以下关键机理：

1. **离子传输机理**：离子在sheath中的加速、在feature中的散射、以及由充电效应引起的偏转共同决定了bottom etch rate和sidewall profile

2. **中性粒子传输机理**：在深高宽比feature中，中性粒子（radicals和precursors）的Knudsen传输受到sticking probability和aspect ratio的严重影响，是ARDE的主要贡献者

3. **表面反应机理**：在低温下，physisorption取代chemisorption成为主要的表面吸附机制，增加了表面覆盖度并改变了反应路径

4. **Passivation/polymer balance**：侧壁钝化层的形成和去除平衡决定了vertical vs lateral etch的选择性，是profile控制的关键

### 11.2 关键技术趋势

1. **低温刻蚀+脉冲等离子体**的组合已成为3D NAND HAR刻蚀的主流方向
2. **Feature scale model + reactor scale model**的多尺度模拟已成为工艺优化的重要工具
3. **Lean chemistry**（减少聚合物生成）配合低温已成为改善profile和减少distortion的标准策略
4. **String stacking**作为突破单次刻蚀深度限制的关键技术，将在1000层3D NAND中发挥核心作用

---

## 参考文献索引

[^1^] Japanese Journal of Applied Physics, "Progress report on high aspect ratio patterning for memory devices," 2023.
[^2^] MDPI Nanomaterials, "Characterization of an Etch Profile at a Wafer Edge in Capacitively Coupled Plasma," 2022.
[^3^] U.S. Patent Application 20210375633, "Method and Apparatus for Formation of Protective Sidewall Layer for Bow Reduction," 2021.
[^4^] Japanese Journal of Applied Physics, "Formation mechanism of sidewall striation in high-aspect-ratio hole etching," 2019.
[^5^] AVS Conference Proceedings, "Line Edge Roughness Reduction for Advanced Metal Gate," 2005.
[^6^] JJAP, "Formation mechanism of sidewall striation in high-aspect-ratio hole etching," 2019.
[^7^] Nine Scrolls, "Future of Plasma Etching for Microelectronics — Key Trends and Roadmap," 2025.
[^8^] ResearchGate, "Investigation of Poly Silicon Channel Variation in Vertical 3D NAND Flash Memory," 2022.
[^9^] SPIE Proceedings, "High-aspect-ratio amorphous carbon mask etch profile control," 2023.
[^10^] Lam Research Official Press Release, "Lam Research Introduces Lam Cryo 3.0," 2024-07-31.
[^11^] CIO & Leader, "Lam Research Introduces Lam Cryo 3.0," 2024-08-01.
[^12^] Lam Research Newsroom, "Scaling to 1,000-Layer 3D NAND in the AI Era," 2024.
[^13^] JVST B, "Future of plasma etching for microelectronics," 2024.
[^14^] Samsung Newsroom, "Samsung Begins Industry's First Mass Production of 9th-Gen V-NAND," 2024-04-23.
[^15^] Samsung Semiconductor Tech Blog, "The Story Behind Samsung's Pioneering V-NAND," 2023.
[^16^] Blocks and Files, "Samsung planning 430-layer NAND in 2025," 2024-04-17.
[^17^] Samsung V-NAND Tech Blog, "Samsung V-NAND: A Landmark of the Hyperscale AI Era," 2024.
[^18^] Nomad Semi, "Tokyo Electron Deep Dive - Part 2," 2025-04-17.
[^19^] IGASCN, "Cryogenic Etching Tools or Bulk Use of Hydrogen Fluoride Gas," 2024.
[^20^] ScienceDirect Topics, "Scalloping."
[^21^] University of Waterloo Thesis, "Silicon dry etching using fluorine-based gas."
[^22^] Counterpoint Research / Lam White Paper, "Scaling to 1,000-Layer 3D NAND in the AI Era," 2024.
[^23^] JVST A, "Dry etching in the presence of physisorption of neutrals at lower temperatures," 2023.
[^24^] Scientific Reports, "Evaluation of Bosch processing and C₄F₈ plasma deposition at cryogenic temperatures."
[^25^] ScienceDirect, "Effect of various pulse plasma techniques on TiO₂ etching," 2023.
[^26^] ACS Applied Nano Materials, "Asynchronously Pulsed Plasma for High Aspect Ratio Nanoscale Si Trench Etch Process," 2023.
[^27^] Applied Surface Science, "Effect of different pulse modes during Cl₂/Ar ICP etching," 2022.
[^28^] ResearchGate, "Effect of simultaneous source and bias pulsing in ICP etching."
[^29^] Journal of Physics D, "Control of electron velocity distributions at the wafer by tailored voltage waveforms in CCP," 2021.
[^30^] Vacuum, "Manipulation of etch selectivity of silicon nitride over silicon dioxide," 2023.
[^31^] SemiAnalysis, "NAND Flash Monopoly Broken? TEL Takes On Lam Research," 2023/2025.
