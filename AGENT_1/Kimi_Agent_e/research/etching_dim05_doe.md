## 维度：DOE（小样本数据实验）SubAgent

---

### 1. 技术领域调研

#### 1.1 DOE方法论概述

实验设计（Design of Experiments, DOE）是一种通过科学规划实验来最大化信息获取、最小化实验次数的统计方法论。在半导体晶圆制造领域，DOE扮演着关键角色，因为"单次工艺涉及数百个顺序步骤且公差极紧"[^214^]，传统单因子实验方法（OFAT）无法捕捉等离子体、热过程和化学过程中固有的多变量交互作用[^214^]。

**核心概念体系：**

DOE的核心要素包括**因子（Factors）**、**水平（Levels）**和**响应（Responses）**[^214^]。在等离子体蚀刻中，因子包括RF功率、腔室压力、气体流量等；水平代表这些因子的离散设置值（如RF功率设于300W和400W）；响应则是刻蚀速率、薄膜厚度均匀性或关键尺寸（CD）变异等测量结果[^214^]。

DOE的基本原则包括**随机化（Randomization）**——通过随机排列实验顺序减少偏差，确保未控制变量均匀分布[^214^]；**重复（Replication）**——在相同条件下重复实验运行以增强估计精度[^214^]。

**经典DOE设计类型在半导体制造中的应用：**

1. **全因子设计（Full Factorial Design）**：系统调查所有因子水平组合，提供最全面的系统洞察，可同时估计主效应和交互效应。但其资源需求（时间、成本、晶圆）随因子数量呈指数增长，仅适用于小实验空间[^214^]。典型应用是光刻聚焦-曝光矩阵（FEM），用于评估工艺窗口[^214^]。

2. **部分因子设计（Fractional Factorial Design）**：评估所有可能因子组合中经过精心选择的子集，远更高效。例如，研究6个蚀刻参数的全因子需要64次运行，而部分因子设计仅需16次即可捕获关键效应[^214^]。

3. **Plackett-Burman设计**：特别适用于因子筛选阶段，以最小实验量估计主效应。评估11个等离子体蚀刻参数的完整因子设计需要2048次运行，而Plackett-Burman设计仅需12次运行，大幅节省时间、晶圆和成本[^214^]。

**混合实验设计（Mixture Design）**在蚀刻工艺中具有特殊重要性。当气体混合比例构成设计变量时（如SF6、He和N2的分压），由于系统总压力固定，这三个变量构成混合物的组分，形成约束实验设计空间[^273^][^301^]。Shumate等人的经典研究中，采用两阶段实验方法：第一阶段使用部分因子筛选实验识别关键因子，第二阶段使用混合实验进行工艺优化，为TiW等离子体蚀刻过程开发了二次和特殊三次响应面模型[^273^][^301^]。

> **原始摘录**："The fractional factorial experiment was initially used to study the effects of reactor pressure, RF power, SF6/He gas-mixture ratio, overetch time, and hard bake. The results of this initial experiment were used to identify the appropriate levels for the main process parameters. Then, at these parameter levels, a mixture experiment was conducted using the partial pressures of SF6, He, and the nitrogen ballast as the design variables." [^273^]

#### 1.2 小样本DOE策略

半导体蚀刻实验的核心痛点在于**实验成本极高**——单次蚀刻实验可能消耗数千美元的测试晶圆成本[^167^]。因此，小样本策略不是可选偏好，而是工业必需。

**（1）D-最优设计（D-Optimal Design）**

D-最优设计旨在选择测试位置以渐近最小化Fisher信息矩阵的逆的行列式，即最大化|X'X|，这被称为回归系数的广义方差[^232^]。该统计量出现在每个回归系数方差的分母中，最大化它可降低估计回归系数的方差[^232^]。

D-效率（D-Efficiency）是跨不同样本量比较设计的重要指标：

$$DE = 100 \times \frac{|X'X|^{1/p}}{N}$$

其中p是模型中自由度总数，N是设计中的点数[^232^]。

对于小样本实验，D-最优设计的核心优势在于：
- 允许非标准模型（如二次模型、含交互项模型）的精确指定
- 支持约束设计空间（如混合比例约束、物理可行性边界）
- 在给定运行次数下最小化参数估计的不确定性

**（2）田口方法（Taguchi Method）与正交试验**

田口方法通过正交表减少试验规模，以最少实验运行获取最大信息量[^297^][^309^]。在SiC等离子体蚀刻辅助化学机械抛光（CMP）研究中，研究者采用L16(4^3)正交阵列研究施加功率、喷嘴-基板距离和蚀刻时间三个参数对蚀刻速率的影响[^215^][^216^]。

正交试验的关键实践洞察：
- 水平间距设置应采用**等比数列而非等差数列**，例如在蚀刻时间优化中，尝试1min、2min、4min的水平设置比1min、2min、3min能更快定位最佳时间窗口[^297^]
- 对于多指标优化，需采用综合平衡法确定最优参数组合[^305^][^307^]

> **原始摘录**："实验基于Taguchi方法设计，以研究等离子体在不同加工参数下的蚀刻速率，包括施加功率、喷嘴到基板的距离和蚀刻时间。实验结果表明，蚀刻速率与施加功率成正比，在3-5mm范围内随喷嘴到基板距离增加而增加，而与蚀刻时间无关。在最佳条件下实现了5.99μm/min的最大蚀刻速率。" [^216^]

**（3）响应面方法（RSM）**

响应面方法（Response Surface Methodology, RSM）是建模过程响应曲率和识别最优操作条件的强大工具。与筛选设计不同，RSM拟合捕捉非线性效应和交互作用的二次模型[^214^]。

常用RSM设计包括：
- **中心复合设计（Central Composite Design, CCD）**：通过补充因子点、中心点和轴点来估计二阶效应[^214^]
- **Box-Behnken设计（BBD）**：高效替代方案，减少极端设置需求[^214^][^332^]

在半导体制造中，RSM被广泛应用于优化CMP平面化均匀性、调谐等离子体蚀刻选择性和微调氧化物沉积厚度均匀性[^214^]。

对于多响应优化，**Derringer-Suich期望函数方法**是工业界最广泛使用的技术[^341^][^343^]。该方法将每个响应转换为0到1之间的个体期望度值，通过几何平均组合为总体期望度函数：

$$D = (d_1 \times d_2 \times \cdots \times d_n)^{1/n}$$

其中d_i为第i个响应的个体期望度[^341^]。

> **原始摘录**："Numerical optimization is driven by a mathematical calculation called desirability... The overall (multi-response) desirability (D) is the geometric mean of the individual desirability (di) for each response." [^341^]

**（4）方差分析（ANOVA）与模型验证**

RSM模型的充分性评估需通过完整回归分析检验多个关键指标：模型p值应小于0.05，失拟检验p值应大于0.10（如有重复数据），调整R方和预测R方越高越好[^214^][^341^]。

#### 1.3 序贯与自适应实验设计

**（1）序贯DOE方法论**

现代半导体工艺开发越来越强调**序贯、自适应和基于模型的方法**[^212^]。序贯DOE的基本流程为：经典DOE建立基线因子-响应关系 → 序贯实验迭代细化条件 → 高斯过程建模和贝叶斯优化实现不确定性感知预测和高效搜索[^212^]。

在蚀刻工艺中，选择平衡轮廓控制、选择性和损伤的配方需要导航RF功率、压力、气体组成和偏压之间的非线性交互。GP引导的序贯实验可以加速向多目标空间中可行权衡的收敛[^212^]。

**（2）贝叶斯优化（Bayesian Optimization, BO）**

贝叶斯优化是"智能实验规划"方法，核心思想是：利用现有实验数据构建"代理模型"，再使用"采集函数"确定最有价值的下一个实验[^167^]。

**代理模型**通常采用高斯过程（Gaussian Process, GP），它不仅提供预测值，还提供该预测的不确定性——这是关键特征。例如，在5个温度点运行蚀刻速率实验后，GP可以告诉我们："在350°C时，蚀刻速率约为120nm/min，但我对此预测信心较低，因为附近没有实验数据点"[^167^]。

**采集函数**平衡两种策略：
- **利用（Exploitation）**：在目前已知最佳区域附近进行更精细搜索
- **探索（Exploration）**：在高不确定性区域采样以避免错过全局最优

常用采集函数包括期望改进（Expected Improvement, EI）、上置信界（UCB）和知识梯度（Knowledge Gradient）。在半导体工艺应用中，EI因稳定性和直观可解释性而被最广泛采用[^167^]。

> **原始摘录**："贝叶斯优化的核心思想可以概括为一句话：利用已有的实验数据来构建一个'代理模型'，然后利用一个'采集函数'来确定最有价值的下一个实验。" [^167^]

**（3）人机协作优化策略**

Lam Research在《Nature》上发表的里程碑研究表明：人类工程师在开发早期阶段表现出色，而算法在接近目标严格公差时效率更高。采用"人类优先-计算机收尾"（human first-computer last）策略可以将达到目标的成本降低一半[^224^][^342^][^344^]。

> **原始摘录**："We find that human engineers excel in the early stages of development, whereas the algorithms are far more cost-efficient near the tight tolerances of the target. Furthermore, we show that a strategy using both human designers with high expertise and algorithms in a human first-computer last strategy can reduce the cost-to-target by half compared with only human designers." [^342^]

**（4）多重启贝叶斯优化（MRBORI）**

针对传统BO的初始化偏差问题，多重启策略引入多次独立重启和随机初始化，每次重启从一个随机初始化点开始，确保参数空间获得多样化覆盖。经过N次重启后，遗漏全局最优解的概率呈指数级衰减[^112^]。

> **原始摘录**："MRBORI通过引入多次独立重启和随机初始化，结合EI（期望改进）采集函数，在探索与利用之间取得平衡，从而应对上述局限。经过N次重启后，遗漏全局最优解x*的概率呈指数级衰减。" [^112^]

**（5）虚拟实验设计（Virtual DOE, vDOE）**

数字孪生技术为半导体生产设备创建虚拟副本，无需制作物理原型即可获取关键信息[^298^]。SEMulator3D建模和执行虚拟DOE已用于优化DED钨填充工艺，成功减少空洞体积，加速工艺开发并降低硅晶圆测试成本[^225^]。

> **原始摘录**："借助半导体生产设备的数字孪生，我们能够观察、分析并预测设备设计与工艺条件实时变化所产生的影响。这意味着无需制作物理原型，就能获取关键硬件信息；在实际晶圆加工前，也可探索不同的工艺条件。" [^298^]

---

### 2. SubAgent能力设计建议

#### 2.1 核心能力

基于上述调研，DOE SubAgent应具备以下分层能力体系：

**Tier 1: 基础实验设计能力**

| 能力模块 | 具体功能 | 适用场景 |
|---------|---------|---------|
| 因子筛选设计 | 生成Plackett-Burman设计、2^(k-p)部分因子设计 | 工艺开发初期，从大量候选因子中识别关键因子 |
| 全因子/部分因子设计 | 生成2^k全因子或分辨率IV/V的部分因子设计 | 因子数≤6时全面评估主效应和交互作用 |
| 正交试验设计 | 基于田口正交表（L9, L16, L27等）生成设计方案 | 快速多因子初步探索 |
| RSM设计生成 | 生成CCD、BBD等响应面设计 | 建立二次模型，寻找最优工艺窗口 |
| D-最优设计 | 基于指定模型（线性/二次/含交互）生成D-最优设计 | 小样本约束下的最优参数估计 |
| 混合实验设计 | 处理组分约束（如气体流量比例之和固定）的混合设计 | 蚀刻气体配比优化 |

**Tier 2: 小样本与自适应DOE能力**

| 能力模块 | 具体功能 | 适用场景 |
|---------|---------|---------|
| 序贯实验规划 | 设计多阶段实验策略（筛选→表征→优化） | 分阶段迭代优化，降低总实验量 |
| 贝叶斯实验设计 | 基于GP代理模型和采集函数推荐下一个实验点 | 极少量昂贵实验的高效利用 |
| 人机协作优化 | 整合工程师先验知识引导优化方向 | 早期开发阶段利用专家经验 |
| 小样本效能评估 | 评估给定设计在小样本下的统计功效 | 实验前验证设计方案可行性 |

**Tier 3: 多目标与约束优化能力**

| 能力模块 | 具体功能 | 适用场景 |
|---------|---------|---------|
| 多响应优化 | 使用Derringer-Suich期望函数同时优化多个响应 | 平衡蚀刻速率、选择性、均匀性 |
| 约束处理 | 处理物理约束（如温度范围、压力上限） | 确保推荐方案设备可执行 |
| Pareto前沿分析 | 识别多目标间的最优权衡集合 | 为工程师提供可选方案集 |
| 稳健参数设计 | 田口稳健参数设计，最小化噪声因子影响 | 提高工艺对设备漂移的鲁棒性 |

**Tier 4: 模型与验证能力**

| 能力模块 | 具体功能 | 适用场景 |
|---------|---------|---------|
| 响应面建模 | 拟合线性/二次/含交互项的回归模型 | 建立工艺参数-响应的预测模型 |
| ANOVA分析 | 方差分析识别显著因子和交互作用 | 从实验数据中提取统计洞察 |
| 模型诊断 | 残差分析、失拟检验、R²评估 | 验证模型可靠性 |
| 优化验证 | 预测最优点的确认实验设计 | 验证模型预测的最优条件 |

#### 2.2 输入规范

DOE SubAgent的输入应包括以下结构化信息：

```json
{
  "process_context": {
    "etch_type": "plasma_etch|RIE|ICP|DRIE|ALE",
    "material_system": "target_material|mask_material",
    "objective": "screening|characterization|optimization|robustness",
    "experiment_budget": "integer (max number of runs)"
  },
  "factors": [
    {
      "name": "string (e.g., RF_power)",
      "type": "continuous|categorical|mixture_component",
      "levels": ["low", "center", "high"],
      "unit": "string (e.g., W, mTorr, sccm)",
      "is_constrained": "boolean",
      "constraints": "string (e.g., sum=650 for mixture)"
    }
  ],
  "responses": [
    {
      "name": "string (e.g., etch_rate)",
      "type": "continuous|binary|ordinal",
      "objective": "maximize|minimize|target",
      "target_value": "float (optional)",
      "lower_bound": "float",
      "upper_bound": "float",
      "weight": "float (0-1, for multi-response optimization)"
    }
  ],
  "prior_knowledge": {
    "historical_data": "dataframe (optional)",
    "expert_guess": "dict of factor-response relationships",
    "known_interactions": ["list of known factor interactions"]
  },
  "constraints": {
    "physical_constraints": ["e.g., pressure > 0"],
    "budget_constraints": "max_total_cost",
    "time_constraints": "max_experiment_duration"
  },
  "design_preferences": {
    "design_type": "auto|fractional_factorial|CCD|BBD|D_optimal|Taguchi|Bayesian",
    "resolution": "III|IV|V (for fractional factorial)",
    "replicates": "integer",
    "center_points": "integer",
    "randomization": "boolean",
    "blocking": "boolean"
  }
}
```

#### 2.3 输出规范

```json
{
  "design_summary": {
    "design_type": "string",
    "total_runs": "integer",
    "design_efficiency": "float (D-efficiency for optimal designs)",
    "alias_structure": "string (for fractional designs)",
    "power_analysis": "dict (expected power for each effect)"
  },
  "design_matrix": {
    "run_order": [1, 2, 3, ...],
    "factor_settings": "dataframe",
    "randomized_order": [3, 1, 4, 2, ...]
  },
  "analysis_plan": {
    "recommended_model": "string (e.g., quadratic with interactions)",
    "significance_level": "float (default 0.05)",
    "analysis_steps": ["list of recommended analysis procedures"]
  },
  "optimization_result": {
    "optimal_conditions": "dict",
    "predicted_responses": "dict",
    "confidence_intervals": "dict",
    "desirability_score": "float (0-1, for multi-response)"
  },
  "visualization": {
    "pareto_plot": "path (factor importance)",
    "contour_plot": "path (response surface)",
    "optimization_path": "path (for sequential/Bayesian)"
  },
  "recommendations": {
    "next_steps": "string (e.g., 'Run confirmation experiments')",
    "risk_assessment": "string",
    "alternative_designs": "list (if primary design suboptimal)"
  }
}
```

#### 2.4 工具与资源需求

**软件/库需求：**

| 工具类别 | 推荐工具 | 用途 |
|---------|---------|------|
| 实验设计生成 | pyDOE2, Gurobi/CPLEX (D-optimal), OptimalDesign | 生成各类DOE方案 |
| 贝叶斯优化 | BoTorch, GPyTorch, scikit-optimize | GP建模与采集函数优化 |
| 统计分析 | statsmodels, scipy, R (via rpy2) | ANOVA、回归分析 |
| 多目标优化 | pymoo, DEAP, Platypus | Pareto优化 |
| 可视化 | matplotlib, plotly | 响应面、等高线图 |
| 数据管理 | pandas, SQLite | 实验数据管理 |

**知识库需求：**
- 经典DOE参考表（正交表、CCD/BBD标准结构、Plackett-Burman设计表）
- 半导体蚀刻工艺参数典型范围数据库
- 历史DOE案例库（用于初始先验和迁移学习）

---

### 3. 与其他Agent的协作关系

#### 3.1 上游依赖

DOE SubAgent依赖以下Agent提供输入信息：

| 上游Agent | 输入内容 | 协作方式 |
|----------|---------|---------|
| **主Agent（调度器）** | 工艺优化目标、优先级排序、实验预算 | 接收任务分配，反馈执行状态 |
| **特征Agent** | 候选工艺因子列表、参数范围、物理约束 | 获取经过筛选的关键因子候选集 |
| **工艺Agent** | 蚀刻类型、材料体系、设备能力边界 | 获取工艺上下文信息 |
| **知识Agent** | 历史DOE数据、相似工艺参考 | 获取先验知识用于贝叶斯优化 |

> **原始摘录**："In plasma etching, selecting recipes that balance profile control, selectivity, and damage requires navigating nonlinear interactions among RF power, pressure, gas composition, and bias." [^212^]

#### 3.2 下游贡献

DOE SubAgent的输出为以下Agent提供输入：

| 下游Agent | 输出内容 | 协作方式 |
|----------|---------|---------|
| **数据分析Agent** | 设计矩阵、分析计划 | 提供结构化实验数据和分析指导 |
| **预测Agent** | 响应面模型、因子-响应关系 | 提供训练数据格式和模型验证标准 |
| **优化Agent** | 最优工艺窗口、约束条件 | 提供优化的起点和可行域定义 |
| **仿真Agent** | 虚拟DOE方案、模型验证需求 | 协调物理实验与仿真的互补验证 |

#### 3.3 并行协作

DOE SubAgent可与以下Agent并行工作：

| 并行Agent | 协作场景 | 协作方式 |
|----------|---------|---------|
| **仿真Agent** | 物理实验与虚拟DOE同步进行 | 仿真数据补充物理实验，扩大有效样本 |
| **监控Agent** | 实验过程中实时数据反馈 | 根据实时反馈调整序贯实验计划 |
| **知识Agent** | 多任务知识共享 | 利用相似工艺的优化历史加速当前任务 |

---

### 4. 触发条件

DOE SubAgent应在以下场景被触发：

**自动触发条件：**

| 场景 | 触发逻辑 | 优先级 |
|------|---------|--------|
| 新蚀刻工艺开发启动 | 主Agent识别到"全新工艺"需求 | P0（最高） |
| 工艺窗口偏移报警 | 监控Agent检测到工艺漂移超出安全边界 | P1 |
| 多目标权衡需求 | 用户提出同时优化≥3个响应的需求 | P1 |
| 实验预算受限 | 可用实验次数<30次 | P1 |

**人工触发条件：**

| 场景 | 触发方式 |
|------|---------|
| 工程师请求DOE方案 | 通过主Agent提交DOE任务 |
| 需要减少实验次数 | 提出"最小实验量"优化需求 |
| 历史数据复用请求 | 请求基于历史DOE数据重新分析 |

**不触发场景（路由到其他Agent）：**
- 纯数据分析任务（无新实验设计需求）→ 路由到数据分析Agent
- 实时过程控制调整 → 路由到监控Agent
- 物理机理建模需求 → 路由到仿真Agent

---

### 5. 关键证据与引用

#### 5.1 DOE在半导体制造中的核心作用

> "Semiconductor wafer fabrication is one of the most complex and demanding processes in industry. At advanced process nodes below 5 nanometers, even angstrom-level deviations in parameters such as oxide thickness or critical dimension (CD) can lead to yield degradation or device failure." [^214^]

> "DOE is both a fundamental methodology for semiconductor innovation and a forward-looking driver. By combining rigorous statistical methods with artificial intelligence, digital twins, and advanced control technologies, DOE will continue to drive sustainable large-scale production, improve yields, and accelerate technology deployment in future wafer fabs." [^214^]

#### 5.2 小样本DOE策略的有效性

> "Evaluating 11 plasma etch parameters would typically require 2048 runs in a complete factorial design; however, only 12 runs are needed with the Plackett-Burman design, saving time, wafers, and cost while still identifying the dominant drivers." [^214^]

> "Plackett-Burman designs are especially valuable for this purpose, as they estimate main effects with minimal experimental effort." [^214^]

#### 5.3 混合实验设计在蚀刻中的应用

> "A two-phase experimental approach was taken to generate the processes. In phase 1 a fractional factorial screening experiment was used to identify key factors, and in phase 2 a mixture experiment was used for process optimization." [^273^]

#### 5.4 贝叶斯优化的人机协作价值

> "One of the bottlenecks to building semiconductor chips is the increasing cost required to develop chemical plasma processes that form the transistors and memory storage cells. These processes are still developed manually using highly trained engineers searching for a combination of tool parameters that produces an acceptable result on the silicon wafer." [^224^]

> "We find that human engineers excel in the early stages of development, whereas the algorithms are far more cost-efficient near the tight tolerances of the target." [^342^]

#### 5.5 序贯DOE与GP建模的结合

> "Combining sequential DOE with GP modeling has shown clear benefits in advanced semiconductor process development. GP-guided sequential experiments can accelerate convergence toward feasible trade-offs in this multi-objective space." [^212^]

#### 5.6 虚拟DOE与数字孪生

> "SEMulator3D modeling and the execution of a virtual DOE were performed to optimize DED W filling and generate a void-free structure. Si validation using the DOE3 results was completed, and demonstrated that we had solved the void issue." [^225^]

#### 5.7 多目标优化的期望函数方法

> "The desirability function approach, while less sophisticated from a mathematical perspective, remains one of the most extensively utilized methods in industry for optimizing multi-response processes. Its popularity is largely attributed to its simplicity and intuitive framework." [^330^]

#### 5.8 中国国内实践参考

> "正交试验在半导体生产流程中的应用场景：蚀刻工艺（ETCH）优化——蚀刻工艺中涉及多种因子，如气体流量、功率、蚀刻时间等。利用正交试验法，可以系统地研究这些因子对蚀刻速率、表面粗糙度和选择性的影响，从而确定最优的蚀刻条件。" [^知乎^]

> "采用等比数列而非等差数列往往更有效。例如在蚀刻时间优化中，尝试1min、2min、4min的水平设置，比1min、2min、3min能更快定位到最佳时间窗口。" [^297^]

---

### 附录：推荐文献清单

| 编号 | 文献 | 相关性 |
|------|------|--------|
| 1 | Chen & Chen (2025), "Review of Applications of Experimental Designs in Wafer Manufacturing", *Applied System Innovation* [^214^] | 极高 - 半导体DOE综合综述 |
| 2 | Kanarik et al. (2023), "Human-machine collaboration for improving semiconductor process development", *Nature* [^224^] | 极高 - 人机协作贝叶斯优化 |
| 3 | MDPI Overview (2025), "Application of Modern Statistical Techniques in Semiconductor Manufacturing" [^212^] | 极高 - 序贯DOE与GP建模 |
| 4 | Shumate et al. (1996), "Development of a TiW plasma etch process using a mixture experiment", *IEEE Trans. Semicon. Manuf.* [^273^] | 高 - 混合实验设计经典案例 |
| 5 | Lam Research (2022), "Accelerating Semiconductor Process Development Using Virtual DOE" [^225^] | 高 - 虚拟DOE实践 |
| 6 | Derringer & Suich (1980), "Simultaneous Optimization of Several Response Variables", *J. Quality Technology* [^341^] | 高 - 多目标优化经典方法 |
| 7 | Shen et al. (2025), "Atmospheric Plasma Etching-Assisted CMP for 4H-SiC", *Processes* [^216^] | 中 - Taguchi方法应用案例 |
| 8 | Statease, "Mixture Design of Experiments (DOE) for Optimal Plasma Etch" [^301^] | 高 - 混合DOE气体配比优化 |
| 9 | CSDN博客, "贝叶斯优化与深度学习的半导体工艺控制数字孪生框架" [^112^] | 中 - MRBORI方法 |
| 10 | 半导体实战系列, "极限良率背后，是如何优化工艺参数和试验路径的？" [^277^] | 中 - 中文半导体DOE实践 |
