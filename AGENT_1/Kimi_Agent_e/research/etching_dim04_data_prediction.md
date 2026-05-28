## 维度：数据（贝叶斯等预测方法）SubAgent

---

## 1. 技术领域调研

### 1.1 贝叶斯优化与高斯过程

#### 1.1.1 贝叶斯优化在半导体工艺优化中的应用

贝叶斯优化（Bayesian Optimization, BO）是一种"智能实验规划"方法，特别适用于半导体工艺开发这种实验成本高、数据稀缺的场景。其核心思想是：利用现有实验数据构建"代理模型"（surrogate model），然后通过"采集函数"（acquisition function）确定最有价值的下一个实验点。[^96^]

**核心组件：**
- **代理模型**：最常用的是高斯过程（Gaussian Process, GP），它不仅提供预测值，还提供预测的不确定性——这一特性至关重要。例如，在5个温度点进行蚀刻速率实验后，GP可以告诉我们："在350°C时，蚀刻速率约为120nm/min，但对这个预测的置信度较低，因为附近没有实验数据点。"[^96^]
- **采集函数**：平衡两种策略——**利用（Exploitation）**：在当前已知最优区域附近精细搜索；**探索（Exploration）**：在高不确定性区域采样以避免错过全局最优。常用的采集函数包括期望改进（Expected Improvement, EI）、上置信界（UCB）和知识梯度（Knowledge Gradient）。[^96^][^125^]

**实际应用场景包括：**
1. **新设备上线（New equipment bring-up）**：将工艺上线过程建模为黑盒优化问题，BO可在5-8次迭代内收敛到合格的工艺窗口，减少60%以上的测试晶圆消耗。[^96^]
2. **配方微调（Recipe fine-tuning）**：从历史数据构建初始代理模型，选择性地在高潜力区域添加实验，避免"盲目参数扫描"。[^96^]
3. **工艺窗口表征（Process window characterization）**：GP的概率特性天然适合分析"安全区域"的大小，可生成参数空间上的"通过概率热图"。[^96^]
4. **多腔室匹配（Multi-chamber matching）**：结合迁移学习，利用A腔室的优化结果加速B腔室的调参。[^96^]

> **原始摘录**："Bayesian optimization models the bring-up process as a black-box optimization problem, converging on a qualified process window within 5-8 iterations (3-5 test wafers per iteration) and reducing test wafer consumption by over 60%." [^96^]

#### 1.1.2 物理信息贝叶斯优化框架（PIBO）

Hu等（2025）提出了物理信息贝叶斯优化（Physics-Informed Bayesian Optimization, PIBO）框架，用于硅等离子体蚀刻中蚀刻速率（ER）和表面粗糙度（Ra）的协同优化。PIBO通过将物理先验知识——特别是源功率（PW）和压力（P）与工艺指标之间的定性关系——整合到高斯过程回归中，克服了传统GP的外推局限性。该框架采用迭代反馈循环：从有限的实验数据开始，推荐新的参数集进行评估；这些结果随后用于优化模型和后续推荐。[^44^]

> **原始摘录**："This study introduces a Physics-Informed Bayesian Optimization (PIBO) framework to efficiently optimize ER and Ra during silicon plasma etching. PIBO overcomes extrapolation limitations of conventional Gaussian Process Regression by integrating physical prior knowledge." [^44^]

#### 1.1.3 高斯过程回归在虚拟量测中的应用

Lynn等（2012）首次将高斯过程回归（GPR）应用于半导体蚀刻数据的虚拟量测，发现GPR模型比所研究的其他建模技术对新数据生成的蚀刻速率估计更加准确。GPR窗口模型产生了最准确的估计值，平均绝对百分比误差（MAPE）约为1.15%。[^56^]

Wan和McLoone（2018）提出了将GPR模型用于虚拟量测（VM）支持的Run-to-Run控制方法。GPR预测的均值作为VM值，预测方差作为置信度度量，用于调整指数加权移动平均（EWMA）R2R控制器的系数。结果表明，该方法比不考虑预测可靠性的实现方案获得了更好的控制性能。[^113^][^114^]

> **原始摘录**："GPR-based windowed models produce the most accurate estimates, achieving mean absolute percentage errors (MAPEs) of approximately 1.15%." [^56^]

#### 1.1.4 异方差高斯过程用于不确定性量化

Kim等（2025）提出了基于异方差高斯过程（heteroscedastic Gaussian process, hetGP）的等离子体蚀刻不确定性量化和设计优化框架。该框架使用hetGP代理模型捕获数据中的复杂不确定性结构，能够分别量化：(a) 晶圆上的空间变异性；(b) 由腔室压力、气体流量和RF功率变化引起的过程相关不确定性。此外，稀疏数据引起的不确定性进一步被量化并纳入基于可靠性的设计优化（RBDO）方案。[^92^]

> **原始摘录**："A heteroscedastic Gaussian process (hetGP) surrogate model is employed to capture the complex uncertainty structure in the data, enabling distinct quantification of (a) spatial variability across the wafer and (b) process-related uncertainty arising from variations in chamber pressure, gas flow rate, and RF power." [^92^]

### 1.2 小样本学习方法

#### 1.2.1 少样本测试时优化（Few-Shot TTO）

传统机器学习方法在半导体工艺优化中面临的关键挑战是：它们通常需要为每个新目标反复重新训练模型，这在计算上非常昂贵。Few-Shot Test-Time Optimization（FSTTO）框架通过迭代优化轻量级反向模型（reverse model），实现了无需重新训练的高效少样本优化。[^42^][^141^]

具体而言，Model Feedback Learning（MFL）框架仅需5次迭代即可生成配方，远少于Lam Research方法（至少需要20次迭代）和人类工程师手动方法（通常需要84次迭代）。[^42^]

> **原始摘录**："MFL requires only five iterations to generate recipes, significantly fewer than the Lam Research method, which typically requires at least 20 iterations, and far less than the 84 iterations often needed when performed manually by a senior engineer." [^42^]

#### 1.2.2 元学习贝叶斯优化（MetaBO）

针对半导体制造中实验数据有限的挑战，研究人员提出了将元学习与贝叶斯优化结合的混合方法。MetaBO利用历史任务数据来训练神经采集函数（Neural Acquisition Function, NAF），其中NAF参数通过神经网络进行优化。研究表明，结合粒子群优化（PSO）的混合方法在实际半导体CVD工艺中表现最优。[^99^]

> **原始摘录**："This work proposes hybrid meta-learning and metaheuristic approaches to efficiently determine parameter settings. Meta-learning leverages historical data from similar tasks to train a neural acquisition function within the meta Bayesian optimization (MetaBO) framework." [^99^]

#### 1.2.3 量子机器学习用于小样本建模

Wang等（2025）展示了量子核回归（Quantum Kernel-Aligned Regressor, QKAR）在半导体制造小样本建模中的应用。该方法使用159个GaN HEMT半导体实验样本数据，将经典数据转化为量子态进行机器学习。QKAR技术优于7种不同的经典机器学习算法。[^46^]

> **原始摘录**："These findings demonstrate the potential of QML for effectively handling high-dimensional, small-sample regression tasks in semiconductor domains and point to promising avenues for its deployment in future real-world applications as quantum hardware continues to mature." [^46^]

#### 1.2.4 迁移学习与腔室适配

Kim等（2025）提出了对比熵条件腔室适配（CECCA）框架，用于解决等离子体蚀刻中"腔室到腔室变异"（chamber-to-chamber variations）问题。当训练数据和测试数据来自不同腔室时，传统的深度学习模型性能会显著下降。CECCA通过对抗学习对齐源腔室和目标腔室的潜在表示域，使得模型在两个腔室上保持不变的分类能力。[^158^]

> **原始摘录**："This study proposes a chamber adaptation methodology, the Contrastive Entropy-Conditioned Chamber Adaptation (CECCA) framework, designed to mitigate variations between chambers in real-time EPD for plasma etching processes." [^158^]

### 1.3 虚拟量测与实时预测

#### 1.3.1 虚拟量测概念与价值

虚拟量测（Virtual Metrology, VM）是指通过计算模型估计关键晶圆特性的技术，而非直接物理测量。在先进半导体晶圆厂中，每次物理测量都可能增加成本、时间和污染风险，VM提供了一种非侵入式替代方案。VM通过整合来自原位传感器（如光学发射光谱OES、等离子体阻抗监测PIM）的信息与历史设备和配方数据，以高准确度预测薄膜厚度、蚀刻深度或套刻误差等输出。[^48^]

VM的主要优势包括：[^56^]
- **减少晶圆报废**：通过更快的工艺监测，及时检测处理错误，防止更多晶圆被错误处理
- **改善工艺控制**：VM估计值在每片晶圆处理期间或之后即可获得，克服了物理测量的低频率问题
- **增加吞吐量**：当可靠的VM方案实施时，可以减少实际量测操作的频率

> **原始摘录**："Virtual metrology (VM) refers to the estimation of critical wafer characteristics through computational models, rather than direct physical measurement. By integrating information from in-situ sensors, such as optical emission spectroscopy and chamber monitoring, VM models predict outputs like film thickness, etch depth or overlay errors with high accuracy." [^48^]

#### 1.3.2 OES数据驱动的虚拟量测

光学发射光谱（OES）是VM最重要的数据来源之一。Kim等（2014）使用OES数据进行等离子体蚀刻速率虚拟量测的研究表明，结合工艺配方工具数据和OES原位数据的VM模型，其预测准确度比单独使用任一种数据提高了56%。[^129^]

Ragnoli等的研究在制造晶圆厂中实时实施了基于梯度提升树算法的OES虚拟量测系统，首先通过异常检测算法评估每片晶圆的工艺数据是否适合预测，然后在新量测数据可用时持续重新训练模型。[^130^]

> **原始摘录**："The virtual metrology model with both process recipe tool data and in-situ data shows higher prediction accuracy by as much as 56% compared with either the process recipe tool data or the in-situ data alone." [^129^]

#### 1.3.3 深度学习虚拟量测

近年来，深度学习方法在VM中得到广泛应用：

- **CNN用于端点检测**：利用OES光谱数据在端点处显示特定波长模式的特性，CNN模型被用于自主端点检测，在图像检测方面表现优异。[^132^]
- **深度卷积自编码器**：利用半监督特征提取的深度学习虚拟量测方法，从OES数据中提取特征进行蚀刻速率估计。[^132^]
- **Time-LLM框架**：利用时间序列大语言模型进行晶圆级蚀刻空间轮廓预测，从多通道过程传感器时间序列预测89个晶圆位置的空间蚀刻深度均匀性分布。[^91^]

#### 1.3.4 贝叶斯神经网络用于不确定性量化和蚀刻深度预测

Kim等（2025）提出了基于贝叶斯神经网络（BNN）的非接触式蚀刻深度预测框架。使用MC Dropout技术，模型在推理时执行50次随机前向传递，生成预测输出的分布。覆盖分析显示：68.25%的验证样本落在±1σ范围内，23.81%落在±2σ范围内，仅7.94%的样本超出2σ不确定性边界。[^95^]

> **原始摘录**："68.25% of the validation samples fall within the ±1σ range, while an additional 23.81% lie within the ±2σ range. Only 7.94% of the samples are outside the 2σ uncertainty bounds, indicating that the model successfully captures the variability of the data in most cases." [^95^]

### 1.4 深度学习在蚀刻剖面预测中的应用

#### 1.4.1 级联循环神经网络（CRNN）

Yao等（2024）提出了级联循环神经网络（CRNN），用于建模和预测蚀刻剖面。蚀刻剖面用极坐标表示，通过循环神经网络建模；相应的蚀刻参数（如压力、功率、温度和电压）通过级联组合层整合到网络中。在10,000个模拟蚀刻剖面数据集上的实验结果表明：与传统蚀刻模拟方法相比，CRNN可实现21,000×的加速，1步预测的平均误差小于0.7nm。[^49^][^50^]

> **原始摘录**："Compared with traditional etching simulation methods, CRNN can speedup 21,000× with an average error of less than 0.7 nm for 1 step prediction." [^49^]

#### 1.4.2 条件卷积循环神经网络（C-ConvRNN）

Gao等（2025）提出了数据驱动的序列建模框架，用于高效准确预测三维等离子体蚀刻剖面。基于物理校准的仿真模型生成了包含2000多个时间分辨垂直剖面序列和1000个深度分辨横向图案片段的综合数据集。在该数据集基础上，开发了条件卷积循环神经网络（Conditional Convolutional Recurrent Neural Network），预测蚀刻轮廓的时间和空间演化，平均结构相似性指数（SSIM）达到0.94以上。[^57^]

> **原始摘录**："The model achieves robust predictive accuracy, with an average Structural Similarity Index Measure above 0.94 across predicted frames, and demonstrates consistent performance for both simple and complex feature arrangements." [^57^]

#### 1.4.3 物理信息神经网络（PINN）

Wang（2024）在MIT的论文中提出了物理信息神经网络（PINN）用于等离子体蚀刻优化。研究表明，使用基于水平集的损失函数的PINN可以改善模型泛化能力。未来工作包括将PINN模型用于贝叶斯框架中，以促进所需蚀刻剖面的配方优化。[^54^]

#### 1.4.4 EPreNet蚀刻剖面预测网络

Lin等（2026）提出了EPreNet蚀刻剖面预测网络，从历史图像序列和工艺参数实现像素级蚀刻剖面预测。与PINN的硬PDE约束不同，EPreNet将工艺条件参数嵌入图像特征以实现条件引导的蚀刻剖面预测。该网络包含：(i) 带有局部窗口注意力机制的空间编码器；(ii) 通过可学习仿射变换注入工艺参数的条件引导特征模块（CFM）；(iii) 结合多层卷积LSTM与因果时间注意力的因果时间模块。[^97^]

### 1.5 时间序列分析与传感器数据处理

#### 1.5.1 设备传感器数据特征

单台蚀刻设备每秒可生成500-2000个传感器读数。一个拥有500台设备的晶圆厂，每秒产生250,000-1,000,000个数据点——远超人工分析能力。传感器数据包括：[^128^]
- **腔室传感器**：多点压力、多区温度、气体流量
- **RF系统**：正向功率、反射功率、DC偏置、匹配网络位置
- **机械系统**：振动、电机电流、位置编码器、真空泵参数
- **工艺指标**：沉积速率、蚀刻速率、均匀性测量

#### 1.5.2 LSTM用于时序预测

LSTM网络被广泛应用于半导体设备传感器数据的时序模式识别。在多任务学习框架中，LSTM编码器处理原始时序数据并提取相关的时间特征，同时支持异常检测和剩余使用寿命（RUL）预测两个任务。[^134^][^144^]

#### 1.5.3 故障检测与分类（FDC）

FDC系统运行连续的四步循环：数据采集、异常检测、分类和触发响应。[^94^] 现代FDC方法包括：
- **实时监测**：偏差发生时立即标记
- **多变量分析**：同时评估多个参数
- **细微模式检测**：ML模型标记在任何单个图表上看起来正常但组合成故障前特征的漂移[^94^]

> **原始摘录**："FDC systems run a continuous four-step loop: collect data, detect anomalies, classify them, and trigger response." [^94^]

### 1.6 主动学习在工艺优化中的应用

主动学习（Active Learning）是一种通过与环境交互来选择最有价值的样本进行标注和学习的方法。贝叶斯优化本质上是一种主动学习方法，其目标是以最少的数据量识别目标属性的最优值。[^171^]

Bayesian优化通过采集函数智能地在探索不确定区域和利用有希望的区域之间进行权衡，从而以比其他优化方法更少的数据收敛到最优解。[^171^]

在多步前瞻贝叶斯优化中，研究者采用强化学习方法（如PPO）来定位下一个最优采样点，同时考虑多个未来的采样-评估试验，将其应用于批量到批量（B2B）优化问题。[^168^]

> **原始摘录**："Bayesian optimization (BO) represents a specific type of SML within a narrower category of models known as active learning. The objective is to identify an optimal value for the target properties with a minimum amount of data." [^171^]

---

## 2. SubAgent能力设计建议

### 2.1 核心能力

基于上述调研，数据预测SubAgent应具备以下核心能力：

#### 2.1.1 概率预测能力

| 能力ID | 能力名称 | 描述 | 优先级 |
|--------|----------|------|--------|
| PRED-001 | 高斯过程回归（GPR）预测 | 基于工艺参数（功率、压力、气体流量、温度等）预测蚀刻结果（蚀刻速率、深度、CD、粗糙度等），并提供预测不确定性 | 高 |
| PRED-002 | 贝叶斯神经网络（BNN）预测 | 使用MC Dropout等技术进行不确定性量化，区分偶然不确定性和认知不确定性 | 高 |
| PRED-003 | 异方差高斯过程（hetGP）预测 | 处理复杂的不确定性结构，分别量化空间变异性和过程相关不确定性 | 中 |
| PRED-004 | 虚拟量测（VM）集成 | 结合OES、PIM等多源传感器数据，实现原位实时蚀刻结果预测 | 高 |

#### 2.1.2 贝叶斯优化能力

| 能力ID | 能力名称 | 描述 | 优先级 |
|--------|----------|------|--------|
| BO-001 | 工艺参数优化 | 使用BO寻找最优工艺参数组合（功率、压力、气体流量比等），最大化/最小化目标指标（蚀刻速率、均匀性、选择比等） | 高 |
| BO-002 | 多目标协同优化 | 同时优化多个冲突目标（如蚀刻速率vs表面粗糙度），提供Pareto前沿 | 高 |
| BO-003 | 采集函数选择 | 支持EI、UCB、KG等多种采集函数，根据场景自适应选择 | 中 |
| BO-004 | 物理信息BO（PIBO） | 整合物理先验知识（如功率与蚀刻速率的关系）到优化过程中 | 中 |
| BO-005 | 小样本/少样本优化 | 在实验数据极少（<20次）的情况下仍能有效优化 | 高 |

#### 2.1.3 深度学习能力

| 能力ID | 能力名称 | 描述 | 优先级 |
|--------|----------|------|--------|
| DL-001 | 蚀刻剖面预测 | 使用CRNN、C-ConvRNN等模型预测完整蚀刻剖面（而非仅标量指标） | 高 |
| DL-002 | 时序传感器分析 | 使用LSTM/Transformer处理OES、PIM等时序传感器数据 | 高 |
| DL-003 | 端到端特征学习 | 自动从原始传感器数据中学习特征，减少人工特征工程 | 中 |

#### 2.1.4 迁移与元学习能力

| 能力ID | 能力名称 | 描述 | 优先级 |
|--------|----------|------|--------|
| TL-001 | 跨腔室迁移学习 | 将在一个腔室上训练的模型迁移到另一个腔室，减少重复实验 | 高 |
| TL-002 | 跨工序元学习 | 利用历史相似任务的优化经验加速新任务的优化 | 中 |
| TL-003 | 域自适应 | 处理由于腔室差异、配方变化引起的数据分布偏移 | 中 |

#### 2.1.5 辅助能力

| 能力ID | 能力名称 | 描述 | 优先级 |
|--------|----------|------|--------|
| AUX-001 | 不确定性量化与报告 | 为所有预测提供置信区间，标记高不确定性区域 | 高 |
| AUX-002 | 异常检测 | 识别工艺数据中的异常点和离群值 | 中 |
| AUX-003 | 特征重要性分析 | 识别对预测结果影响最大的工艺参数 | 中 |
| AUX-004 | 模型可解释性 | 提供SHAP等可解释性分析，帮助工程师理解预测结果 | 中 |

### 2.2 输入规范

#### 2.2.1 数据来源

数据预测SubAgent接收以下类型的输入数据：

**1. 工艺配方参数（Process Recipe Parameters）**
```json
{
  "recipe_id": "recipe_001",
  "parameters": {
    "source_power_w": 500,
    "bias_power_w": 150,
    "pressure_mtorr": 20,
    "gas_flows": {
      "SF6_sccm": 120,
      "O2_sccm": 75,
      "Ar_sccm": 50
    },
    "temperature_c": 60,
    "etch_time_s": 120
  }
}
```

**2. 传感器时序数据（Sensor Time-Series Data）**
```json
{
  "wafer_id": "wafer_001",
  "sensor_data": {
    "OES": {
      "wavelengths_nm": [426, 440, 685, 703, 750, 777],
      "intensities": [[...], [...], ...],
      "sampling_rate_hz": 10
    },
    "PIM": {
      "voltage_v": [...],
      "current_a": [...],
      "power_w": [...],
      "impedance_ohm": [...]
    }
  }
}
```

**3. 历史工艺结果（Historical Process Results）**
```json
{
  "metrology_data": {
    "etch_rate_nm_min": 109.9,
    "etch_depth_nm": 2255.5,
    "mask_remaining_nm": 358.9,
    "top_cd_nm": 198.8,
    "bottom_cd_nm": 188.8,
    "delta_cd_nm": 10.0,
    "bow_cd_nm": 198.5,
    "surface_roughness_nm": 2.5
  }
}
```

**4. 优化目标与约束（Optimization Objectives and Constraints）**
```json
{
  "optimization_task": {
    "objectives": [
      {"metric": "etch_rate", "target": "maximize", "weight": 0.5},
      {"metric": "uniformity", "target": "minimize", "weight": 0.3},
      {"metric": "roughness", "target": "minimize", "weight": 0.2}
    ],
    "constraints": {
      "etch_depth_nm": {"min": 2250, "max": 2750},
      "cd_nm": {"min": 190, "max": 210}
    },
    "budget": {"max_experiments": 20}
  }
}
```

#### 2.2.2 数据预处理要求

- 缺失值处理：支持插值、前向填充、删除等策略
- 数据标准化：Min-Max归一化或Z-score标准化
- 异常值检测：基于统计方法或隔离森林
- 降维处理：PCA、t-SNE等用于高维OES数据
- 时间对齐：确保多源传感器数据的时间同步

### 2.3 输出规范

#### 2.3.1 预测结果输出

```json
{
  "prediction_id": "pred_001",
  "timestamp": "2025-01-15T10:30:00Z",
  "predictions": {
    "etch_rate_nm_min": {
      "mean": 109.9,
      "std": 3.2,
      "ci_95": [103.6, 116.2],
      "uncertainty_type": "epistemic"
    },
    "etch_depth_nm": {
      "mean": 2255.5,
      "std": 12.3,
      "ci_95": [2231.4, 2279.6]
    }
  },
  "model_info": {
    "model_type": "GPR",
    "kernel": "RBF",
    "training_samples": 15,
    "last_updated": "2025-01-15T09:00:00Z"
  },
  "confidence_assessment": "high",
  "recommendation": "Consider adding experiments near current optimal region to reduce uncertainty."
}
```

#### 2.3.2 优化结果输出

```json
{
  "optimization_id": "opt_001",
  "status": "completed",
  "iterations": 8,
  "recommended_parameters": {
    "source_power_w": 520,
    "bias_power_w": 145,
    "pressure_mtorr": 18,
    "gas_flows": {
      "SF6_sccm": 115,
      "O2_sccm": 80,
      "Ar_sccm": 48
    }
  },
  "expected_outcomes": {
    "etch_rate_nm_min": {"mean": 115.0, "ci_95": [109.0, 121.0]},
    "uniformity_pct": {"mean": 1.5, "ci_95": [1.2, 1.8]}
  },
  "pareto_front": [...],
  "acquisition_history": [...],
  "next_best_experiment": {
    "parameters": {...},
    "expected_improvement": 0.05
  }
}
```

#### 2.3.3 模型诊断输出

```json
{
  "diagnostics": {
    "model_fit": {
      "r2_score": 0.92,
      "rmse": 2.5,
      "mape": 1.15
    },
    "uncertainty_calibration": {
      "ci_95_coverage": 0.95,
      "ci_68_coverage": 0.68
    },
    "feature_importance": [
      {"feature": "source_power", "importance": 0.35},
      {"feature": "pressure", "importance": 0.25},
      {"feature": "gas_ratio", "importance": 0.20}
    ],
    "anomalies_detected": [],
    "model_drift_warning": false
  }
}
```

### 2.4 工具与资源需求

#### 2.4.1 核心Python库

| 库名称 | 用途 | 版本要求 |
|--------|------|----------|
| `scikit-learn` | 基础机器学习模型、预处理 | >=1.3 |
| `GPy` / `GPyTorch` | 高斯过程回归和贝叶斯优化 | >=1.10 |
| `Botorch` | 大规模贝叶斯优化 | >=0.9 |
| `PyTorch` / `TensorFlow` | 深度学习模型 | >=2.0 |
| `Pyro` / `NumPyro` | 概率编程、贝叶斯神经网络 | >=1.8 |
| `XGBoost` | 梯度提升、特征重要性分析 | >=2.0 |
| `Optuna` / `Ax` | 超参数优化框架 | >=3.0 |
| `SHAP` | 模型可解释性 | >=0.42 |
| `SciPy` | 科学计算、优化 | >=1.11 |
| `Pandas` / `NumPy` | 数据处理 | >=2.0 |

#### 2.4.2 计算资源需求

- **GPU**：深度学习模型训练和推理需要GPU加速（推荐NVIDIA GPU，VRAM >= 8GB）
- **内存**：对于GP模型，内存需求随样本数呈O(n²)增长，建议>=16GB RAM
- **存储**：模型持久化和历史数据存储

#### 2.4.3 模型持久化

- 训练好的模型应支持序列化和反序列化
- 模型版本管理，支持回滚到历史版本
- 增量更新能力，支持在线学习

---

## 3. 与其他Agent的协作关系

### 3.1 上游依赖

```
┌─────────────────────────────────────────────────────────────┐
│                    主Agent（Master Agent）                    │
│                     任务分发与协调                             │
└─────────────┬───────────────────────────────┬───────────────┘
              │                               │
    ┌─────────▼─────────┐          ┌─────────▼─────────┐
    │  工艺知识Agent      │          │  数据采集Agent      │
    │  (Process KB)      │          │  (Data Collection) │
    └─────────┬─────────┘          └─────────┬─────────┘
              │                               │
              │  ①工艺约束/先验知识            │  ②传感器数据/工艺参数
              │  （功率-蚀刻速率关系等）         │  （OES/PIM/Recipe）
              │                               │
              └──────────────┬────────────────┘
                             │
                    ┌─────────▼─────────┐
                    │  数据预测Agent       │
                    │ (Bayesian/ML)      │
                    │  ← 当前Agent        │
                    └─────────┬─────────┘
```

**上游依赖详情：**

| 上游Agent | 提供内容 | 使用方式 |
|-----------|----------|----------|
| 工艺知识Agent | 物理约束、先验知识（如功率与蚀刻速率的定性关系） | 整合到PIBO的GP先验中 |
| 工艺知识Agent | 工艺窗口约束（参数安全范围） | 作为优化的边界条件 |
| 数据采集Agent | 实时传感器数据（OES、PIM等） | 用于虚拟量测和特征提取 |
| 数据采集Agent | 工艺配方参数 | 作为模型的输入特征 |
| 数据采集Agent | 历史量测数据（蚀刻速率、CD等） | 作为模型的训练标签 |

### 3.2 下游贡献

```
                    ┌─────────────────────────┐
                    │      数据预测Agent       │
                    │    (Bayesian/ML)        │
                    └────────────┬────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
    ┌─────────▼─────────┐ ┌──────▼──────┐  ┌───────▼───────┐
    │  工艺优化Agent      │ │  监控Agent   │  │  仿真Agent     │
    │  (Optimization)   │ │ (Monitoring) │  │ (Simulation)  │
    └───────────────────┘ └─────────────┘  └───────────────┘
           ③优化建议              ④预测结果           ⑤代理模型
        （推荐下一组实验参数）    （实时蚀刻结果预测）   （GP代理模型）
```

**下游贡献详情：**

| 下游Agent | 提供内容 | 价值 |
|-----------|----------|------|
| 工艺优化Agent | 预测结果和不确定性估计 | 帮助确定下一步实验方向 |
| 工艺优化Agent | 采集函数推荐的下一组实验参数 | 直接指导实验设计 |
| 监控Agent | 虚拟量测预测值 | 替代低频率的物理量测，实现实时监控 |
| 监控Agent | 异常检测结果 | 标记超出正常范围的预测 |
| 仿真Agent | GP代理模型 | 作为物理仿真的快速替代模型 |
| 报告Agent | 预测报告、不确定性分析 | 为决策提供数据支持 |

### 3.3 并行协作

```
┌─────────────────────────────────────────────────────────────────┐
│                        主Agent                                   │
└──────┬───────────┬───────────┬───────────┬───────────┬─────────┘
       │           │           │           │           │
┌──────▼──────┐ ┌──▼──────┐ ┌──▼──────┐ ┌──▼──────┐ ┌──▼──────┐
│ 数据预测Agent │ │仿真Agent│ │知识Agent│ │监控Agent│ │优化Agent│
│ (预测+优化)  │ │(物理仿真)│ │(工艺知识)│ │(实时监测)│ │(参数优化)│
└──────┬──────┘ └──┬──────┘ └──┬──────┘ └──┬──────┘ └──┬──────┘
       │           │           │           │           │
       └───────────┴─────┬─────┴───────────┴───────────┘
                         │
                    ┌────▼────┐
                    │ 结果融合  │
                    │ (主Agent) │
                    └─────────┘
```

**并行协作模式：**

1. **预测-仿真并行**：数据预测Agent（GP代理模型）与仿真Agent（物理模型）同时运行，相互验证结果。GP代理提供快速预测，物理仿真提供精确但缓慢的结果。[^58^]
2. **多模型集成预测**：可与其他ML模型Agent并行运行，采用集成学习策略提高预测鲁棒性。[^48^]
3. **实时协作**：与监控Agent并行工作，数据预测Agent提供VM预测值，监控Agent进行FDC异常检测。

---

## 4. 触发条件

### 4.1 自动触发条件

| 触发条件ID | 条件描述 | 响应动作 |
|------------|----------|----------|
| AUTO-001 | 收到新的工艺实验数据（>1条新记录） | 自动重新训练/更新GP模型 |
| AUTO-002 | 模型不确定性超过阈值（如平均σ > 10%目标值） | 触发采集函数计算，推荐下一组实验 |
| AUTO-003 | 收到实时传感器数据流（OES/PIM） | 执行虚拟量测预测 |
| AUTO-004 | 检测到数据漂移（新数据分布与训练数据显著不同） | 触发模型适配/迁移学习 |
| AUTO-005 | 新配方开发请求（无历史数据） | 启动小样本BO优化流程 |

### 4.2 手动触发条件

| 触发条件ID | 条件描述 | 响应动作 |
|------------|----------|----------|
| MANU-001 | 工程师请求工艺参数优化建议 | 执行贝叶斯优化，推荐最优参数 |
| MANU-002 | 工程师请求蚀刻结果预测 | 基于当前参数执行预测 |
| MANU-003 | 工程师请求不确定性分析 | 生成预测置信区间和校准报告 |
| MANU-004 | 工程师请求跨腔室迁移 | 执行域自适应/迁移学习 |
| MANU-005 | 工程师请求特征重要性分析 | 执行SHAP分析，生成参数重要性排序 |

### 4.3 周期性触发

| 触发条件ID | 条件描述 | 响应动作 |
|------------|----------|----------|
| PERI-001 | 每日模型健康检查 | 评估模型性能、校准度、漂移情况 |
| PERI-002 | 每周模型重新训练 | 使用最新数据重新训练模型 |
| PERI-003 | 每月特征重要性重评估 | 更新参数重要性排序 |

---

## 5. 关键证据与引用

### 5.1 贝叶斯优化与高斯过程

1. **Hu et al. (2025)** - Physics-Informed Bayesian Optimization Framework for Etching Rate and Surface Roughness Co-Optimization. SISPAD 2025. [^44^]
   - PIBO框架整合物理先验知识，有效优化ER和Ra

2. **Kanarik et al. (2023)** - Human-machine collaborative etching process optimization based on Bayesian optimization. (通过[^42^]引用)
   - BO结合人工协作优化蚀刻剖面，减少实验成本50%

3. **Wan & McLoone (2018)** - Gaussian Process Regression for Virtual Metrology-Enabled Run-to-Run Control. IEEE Trans. Semiconductor Manufacturing, 31(1), 12-21. [^113^][^114^]
   - GPR用于VM-R2R控制，利用预测方差调整控制器系数

4. **Kim et al. (2025)** - Uncertainty quantification and parameter optimization of plasma etching process using heteroscedastic Gaussian process. arXiv:2511.04990. [^92^]
   - hetGP分别量化空间变异性和过程相关不确定性

### 5.2 小样本学习

5. **Berkeley (2025)** - Few-Shot Test-Time Optimization Without Retraining for Semiconductor Recipe Generation. arXiv:2505.16060. [^42^]
   - MFL仅需5次迭代生成配方，优于BO（20次）和人工（84次）

6. **Wang et al. (2025)** - Quantum Kernel Learning for Small Dataset Modeling in Semiconductor Fabrication. Advanced Science. [^46^]
   - 量子核回归优于7种经典ML算法

7. **Info. Sciences (2025)** - Optimizing semiconductor process recipe settings using hybrid meta-learning and metaheuristic approaches. [^99^]
   - MetaBO+PSO在半导体CVD工艺中表现最优

### 5.3 虚拟量测与实时预测

8. **Lynn et al. (2012)** - Virtual Metrology for Plasma Etch Processes. PhD Thesis, NUI Maynooth. [^56^]
   - 首次将GPR应用于半导体蚀刻数据VM，MAPE约1.15%

9. **Kim et al. (2014)** - In-situ virtual metrology for the silicon-dioxide etch rate by using OES data. J. Korean Physical Society, 65(1), 168. [^129^]
   - 结合OES和工艺数据，准确度提高56%

10. **Kim et al. (2025)** - In-situ and Non-contact Etch Depth Prediction using BNN with MC Dropout. [^95^]
    - 68.25%验证样本落在±1σ范围内

### 5.4 深度学习蚀刻预测

11. **Yao et al. (2024)** - Etching process prediction based on cascade recurrent neural network. Engineering Applications of AI. [^49^][^50^]
    - CRNN比传统仿真加速21,000×，1步预测误差<0.7nm

12. **Gao et al. (2025)** - Sequence modeling for predicting three-dimensional plasma etching profiles with deep learning. J. Vacuum Science & Technology A, 43(4). [^57^]
    - 条件卷积循环神经网络，平均SSIM > 0.94

13. **Lin et al. (2026)** - EPreNet: A Condition-Guided Network Accelerates Etching Profile Prediction. Micromachines, 17(5), 546. [^97^]
    - 从18,360张图像的918个工艺条件中学习

### 5.5 时间序列与传感器数据

14. **Wang et al. (2026)** - Wafer-Level Etch Spatial Profiling for Process Monitoring from Time-Series with Time-LLM. arXiv:2603.23576. [^91^]
    - Time-LLM预测89个晶圆位置的空间蚀刻深度分布

15. **Lynn et al. (2012)** - Real-time virtual metrology and control for plasma etch. Journal of Process Control, 22(4), 666-676. [^130^][^173^]
    - 实时VM结合预测函数控制，蚀刻速率控制精度在1%以内

### 5.6 主动学习与迁移学习

16. **Kim et al. (2025)** - Adaptive learning strategies for addressing chamber variations in real-time EPD. Journal of Intelligent Manufacturing. [^158^]
    - CECCA框架解决腔室变异问题

17. **Lee & Kim (2023)** - Multitask learning for virtual metrology in semiconductor manufacturing systems. Computers & Industrial Engineering. [^121^]
    - 多任务学习处理多腔室VM，每个腔室作为单独任务

### 5.7 多Agent架构设计参考

18. **OpenCode SubAgent Pattern** - mode="subagent", stateless, tools: [write, edit, bash] [^107^][^4^]
    - SubAgent保持无状态，主Agent集中调度

19. **Anthropic Multi-Agent Research System** - orchestrator-worker pattern [^120^]
    - Lead Agent协调SubAgent并行探索不同方向

20. **LangChain Multi-Agent Architecture** - Subagents pattern for centralized orchestration [^11^]
    - 主管Agent协调专业化SubAgent，子Agent保持无状态

---

## 附录A：技术选型决策矩阵

| 技术 | 小样本适配 | 不确定性量化 | 计算效率 | 可解释性 | 推荐场景 |
|------|-----------|------------|----------|----------|----------|
| GPR/BO | ★★★★★ | ★★★★★ | ★★★☆☆ | ★★★★☆ | <50样本，需UQ |
| BNN | ★★★★☆ | ★★★★★ | ★★☆☆☆ | ★★☆☆☆ | 需深度不确定性 |
| hetGP | ★★★★☆ | ★★★★★ | ★★☆☆☆ | ★★★☆☆ | 复杂异方差噪声 |
| CRNN/LSTM | ★★☆☆☆ | ★★☆☆☆ | ★★★★☆ | ★★☆☆☆ | 大量时序数据 |
| PINN | ★★★☆☆ | ★★☆☆☆ | ★★★☆☆ | ★★★★☆ | 有PDE先验知识 |
| 迁移学习 | ★★★★★ | ★★★☆☆ | ★★★★☆ | ★★★☆☆ | 跨腔室/跨工序 |

## 附录B：实现优先级路线图

| 阶段 | 功能模块 | 时间估算 | 关键交付物 |
|------|----------|----------|------------|
| Phase 1 (MVP) | GPR虚拟量测 + BO参数优化 | 2-3周 | 可工作的预测和优化管线 |
| Phase 2 | BNN不确定性量化 + 异方差GP | 2周 | 完整的不确定性量化能力 |
| Phase 3 | 深度学习剖面预测（CRNN） | 3周 | 蚀刻剖面预测功能 |
| Phase 4 | 迁移学习 + 元学习 | 2周 | 跨腔室适配能力 |
| Phase 5 | 集成学习与模型融合 | 1周 | 多模型集成预测 |

---

*文档生成时间：2025年*
*版本：v1.0*
*基于18+次独立搜索（中英文）的调研结果*
