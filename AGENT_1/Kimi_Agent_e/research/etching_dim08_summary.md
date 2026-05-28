## 维度：Summary（信息综合和总结）SubAgent

### 1. 技术领域调研

#### 1.1 多源信息融合方法论

多源信息融合（Multi-Source Information Fusion）是Summary Agent的核心技术基础。该领域起源于Bar-Shalom提出的概率数据互联滤波器，现已发展为涵盖多种方法论的综合技术体系 [^266^]。

**关键融合方法分类：**

| 方法类别 | 代表技术 | 适用场景 | 优缺点 |
|---------|---------|---------|--------|
| 加权融合方法 | 平均加权融合、自适应加权融合 | 导航定位、传感器数据融合 | 简单高效，但对异常值敏感 |
| 最优估计算法 | 卡尔曼滤波(KF)、扩展KF、无迹KF | 线性/非线性系统状态估计 | 数学基础扎实，需建立精确模型 |
| 粒子滤波(PF) | 序贯重要性采样、Bootstrap滤波 | 非线性非高斯系统 | 精度高但计算量大 |
| 联邦滤波(FF) | Carlson联邦滤波 | 容错导航系统 | 设计灵活、容错性好 |
| 因子图方法 | 滑动窗口因子图优化 | 定位、导航 | 精度高但实时性需优化 |
| 人工智能方法 | BP神经网络、RBF神经网络 | 数据驱动场景 | 需大量训练数据，实时性受限 |
| 不确定推理方法 | D-S证据理论、贝叶斯推理、模糊推理 | 无法精确建模的系统 | 灵活性高但存在信息损失 |

> **原始摘录：** "Data fusion was initially introduced in an article titled Extension of the Probabilistic Data Association Filter in Multi-target Tracking published by the American system scientist Bar-Shalom. The article proposed the probabilistic data interconnection filter as the symbol of the formation of multi-source information fusion technology." [^266^]

**对Summary Agent的启示：**
在半导体蚀刻工艺的多智能体系统中，Summary Agent面临的是多源异构信息的融合问题——来自机理仿真、RCP参数、文献检索、数据预测、DOE实验、蓝军（Red Teaming）、TRIZ创新等不同Agent的信息具有不同的置信度、粒度和表达形式。Summary Agent应采用**分层融合架构**：

1. **数据层融合**：对结构化数据（如DOE参数、仿真结果）采用加权融合或统计方法
2. **特征层融合**：对半结构化信息（如文献摘要、TRIZ方案）采用语义对齐和内容选择
3. **决策层融合**：对定性判断（如蓝军评估、创新建议）采用不确定推理或共识构建方法

**MetaCrit框架的冲突解决方法**提供了极具参考价值的五步综合流程 [^299^]：
- Step 1: 收集多数Agent认同的事实（共识识别）
- Step 2: 发现并调和冲突信息（冲突解决）
- Step 3: 收集独特信息（独特价值提取）
- Step 4: 合并所有验证后的信息（综合集成）
- Step 5: 产出简洁、客观的终稿

#### 1.2 自动报告生成技术

自动报告生成是Summary Agent的核心输出能力。调研发现，LLM驱动的报告生成系统通常采用模块化架构 [^260^][^303^][^314^]。

**典型报告生成系统架构：**

```
用户输入/查询
    ↓
[信息收集层] — 多Agent并行收集
    ↓
[数据处理层] — 数据清洗、归一化、对齐
    ↓
[内容生成层] — 分段摘要、综合分析
    ↓
[报告组装层] — 结构化输出、格式编排
    ↓
最终报告（Markdown/HTML/PDF）
```

**NVIDIA报告生成Agent的实现模式** [^314^] 展示了典型的多阶段生成流程：

> **原始摘录：** "The architecture is the simplest so far—a linear workflow that researches the topic, writes the sections, and compiles the whole, finalized report." ... "Orchestrating the section authoring process. Creating author agent for section: Introduction... Autonomous Decision-Making... Integration with Physical World... Agentic AI Trends..."

其核心流程为：
1. 初始主题研究（initial topic research）
2. 报告规划（report planner）——确定章节结构
3. 分段撰写（section authoring）——每节独立Agent撰写
4. 整合编译（compiles the whole, finalized report）

**报告生成中的关键技术——Map-Reduce摘要管线** [^315^][^319^]：

Map-Reduce是多文档摘要的标准方法，特别适合Summary Agent处理多源输入：
- **Map阶段**：将每个Agent的输出视为独立"文档"，分别生成摘要
- **Reduce阶段**：合并所有部分摘要，生成连贯的最终报告

> **原始摘录：** "MapReduce is highly parallelizable, which can improve performance for large documents. However, it may lose cross-chunk contextual information, with the final summary missing connections between distant parts of the document." [^319^]

为弥补Map-Reduce的上下文断裂问题，可采用**Refine（渐进细化）方法** [^321^]：
> **原始摘录：** "Progressive summarization constructs a running summary that is updated as each new chunk of the document is processed. This approach, inspired by knowledge accumulation and refinement patterns, offers a scalable solution for summarizing documents too large to fit entirely within the context window."

**多Agent报告生成中的分阶段生成策略** [^303^]：
- Stage 1: Executive Summary（200-300 tokens）
- Stage 2: Detailed Analysis（1000-1500 tokens）
- Stage 3: Conclusions（300-500 tokens）
- 每阶段独立API调用，避免超时

#### 1.3 多Agent协调者设计模式

Summary Agent在多智能体系统中扮演协调者（Coordinator）/整合者（Aggregator）的角色。调研发现，多Agent系统存在几种核心协作模式：

**Google定义的八种多Agent设计模式** [^294^]：

| 模式名称 | 核心特征 | Summary Agent对应关系 |
|---------|---------|---------------------|
| Sequential Pipeline | 顺序流水线，各Agent依次传递输出 | 作为最后节点接收所有上游输出 |
| Coordinator/Dispatcher | 协调者分配任务给专业Agent | Summary Agent是Coordinator的特例 |
| Parallel Fan-out/Gather | 并行分发，汇总收集 | **核心模式**：汇总所有并行Agent输出 |
| Hierarchical Decomposition | 分层分解，高层规划子任务 | 作为高层整合节点 |
| Generator and Critic | 生成者+批评者迭代改进 | 整合批评意见生成最终报告 |
| Iterative Refinement | 生成→批评→精化循环 | 多轮打磨报告质量 |
| Human-in-the-Loop | 人类审批关键决策 | 报告发布前人工审核 |
| Composite Pattern | 组合多种模式 | 实际系统的混合策略 |

> **原始摘录：** "Reliability comes from decentralization and specialization. Multi-Agent Systems (MAS) allow you to build the AI equivalent of a microservices architecture." [^294^]

**Coordinator + Worker模式** [^287^] 是Summary Agent的最佳参考架构：

> **原始摘录：** "Three components: 1. Coordinator — one agent that receives the user's goal, decides which workers to call, dispatches tasks, collects results, and produces the final answer. 2. Workers — specialized agents with focused prompts and their own tools. Each does one thing well. 3. Dispatch logic — Python code that wires the coordinator to the workers and handles parallel execution + errors."

> **原始摘录：** "This pattern wins because: each worker has a tight, focused system prompt (which produces sharper output), workers run in parallel (which cuts wallclock), and the coordinator handles cross-cutting concerns (validation, retries, synthesis) instead of muddling them into worker prompts." [^287^]

**Mixture-of-Agents (MoA)架构** [^327^][^341^] 是Summary Agent的核心参考模型：

MoA采用多层前馈架构，包含**提议者（Proposers）**和**聚合者（Aggregators）**：
- 第一层：多个proposer Agent并行生成多样化候选输出
- 中间层：逐层迭代精化
- 最终层：aggregator LLM综合所有输出为单一高质量响应

> **原始摘录：** "The final layer employs a specialized aggregator LLM that synthesizes refined outputs into a single optimized version using a dedicated synthesis prompt. This aggregation combines, reconciles, and enhances the most effective ideas from preceding generations to produce the final output." [^327^]

> **原始摘录：** "The aggregator LLM actively combines beneficial elements from multiple proposals while avoiding conflicting modifications, enabling effective synthesis even when limited to open-source models rather than using simple voting mechanisms." [^327^]

**Aggregator的系统提示模板** [^333^]：
> **原始摘录：** "Your task is to synthesize these responses into a single, high-quality response. It is crucial to critically evaluate the information provided in these responses, recognizing that some of it may be biased or incorrect. Your response should not simply replicate the given answers but should offer a refined, accurate, and comprehensive reply to the instruction."

**冲突证据的多Agent解决方法——Madam-RAG** [^338^]：

> **原始摘录：** "We introduce Madam-RAG, a multi-agent approach for handling conflicting evidence wherein each agent is assigned a separate document and agents debate with each other. The debate is then synthesized into an answer by an aggregator model, leading to improved performance across both standard RAG datasets as well as RamDocs."

#### 1.4 知识综合与多文档摘要技术

**LLM-based多文档摘要方法论** [^261^] 提供了系统的技术路线：

**提示工程方法：**
- 零样本摘要：直接指令生成摘要
- Chain of Thought (CoT)：逐步推理生成
- Chain of Density (CoD)：创建详细、以实体为中心的摘要
- Summary Chain-of-Thought (SumCoT)：引导LLM逐步生成摘要

> **原始摘录：** "SumCoT technique guides LLMs to generate summaries step by step. This approach enables the integration of fine-grained details from source documents into the final summaries, mimicking the human writing process." [^261^]

**生产级摘要系统的构建要点** [^264^]：
1. **Map-Reduce管线**：文档分块→独立摘要→合并终稿
2. **幻觉检测**：分解→验证（decompose-then-verify），将生成摘要拆分为原子声明逐一验证
3. **评估指标**：ROUGE + BERTScore + 事实一致性指标

**多文档摘要中的内容选择策略** [^262^]：
> **原始摘录：** "We explicitly divide the task into three steps—(1) reducing document collections to atomic key points, (2) using determinantal point processes (DPP) to select key points that prioritize diverse content, and (3) rewriting to the final summary."

**Multi2框架的聚合策略** [^300^]：
- **Vote（投票）**：评估所有候选摘要并选择最佳
- **CPS（上下文保持摘要器）**：参考原始文档和候选摘要生成精化摘要
- **CIS（上下文独立摘要器）**：仅基于候选摘要进行参考综合

### 1.5 可视化报告与决策支持技术

可视化报告生成是Summary Agent的关键能力，直接影响决策支持效果。

**大模型驱动的智能分析趋势** [^305^][^306^]：

| 能力维度 | 传统工具 | 大模型融合可视化 | 技术亮点 |
|---------|---------|-----------------|---------|
| 数据查询 | 固定SQL、拖拽筛选 | 自然语言检索、自动提问 | 语义解析、上下文关联 |
| 报表生成 | 手工设计、格式有限 | 智能推荐报表结构、图表类型 | 语义驱动生成、场景自适应 |
| 异常预警 | 静态规则、人工监控 | 自动发现异常、实时预警 | 数据建模、趋势推断 |
| 业务建议 | 无自动说明，靠专家解读 | 自动生成分析报告、业务建议 | 生成式AI、行业知识迁移 |

> **原始摘录：** "AI与大模型的结合为数据可视化带来了新的可能性：实时数据分析——快速处理和分析/提供预测和趋势——高效决策支持；自动报告生成——推荐关键图表/自动生成文本——减少人工干预。" [^305^]

**智能报告生成的技术栈** [^307^]：
> **原始摘录：** "综合运用了可视化技术、智能报告生成技术、科技资源智能感知技术等关键技术，构建了一套数据交互与知识输出一体化的解决方案。该系统融合了人机协同探索、空间信息融合以及自动报告生成功能。"

**决策支持系统信息呈现原则** [^302^][^308^]：
- 信息必须转化为**可行动的洞察**（actionable information）
- 采用**KPI指标**衡量系统整体性能
- 提供**钻取访问**（drill down）能力，从概览到细节
- 结合**GIS、图形和数字**多种呈现方式
- 保持**交互性**，允许用户探索假设

> **原始摘录：** "The primary goal of the integrated DOM dashboard is to collect data from the different source data streams and convert it, using the decision support system, into actionable information. The conversion of data streams to actionable information involves algorithms to process the data, and presentation of the information in a manner that is intuitive to an operator." [^302^]

---

### 2. SubAgent能力设计建议

#### 2.1 核心能力

基于上述调研，Summary Agent应具备以下**六大核心能力**：

**能力1：多源信息接收与解析**
- 接收来自8个其他Agent的异构输出（文本、表格、结构化数据、图表）
- 自动识别输入格式和置信度标记
- 建立统一的信息表示框架

**能力2：内容选择与重要性评估**
- 基于DPP（Determinantal Point Processes）等方法实现多样化内容选择 [^262^]
- 识别共识性信息与冲突性信息
- 评估各Agent输出的可靠性和相关性权重

**能力3：冲突检测与调和**
- 自动检测多源信息中的矛盾点
- 采用MetaCrit框架的五步综合法 [^299^]：收集共识→调和冲突→提取独特信息→合并→生成终稿
- 对无法调和的冲突进行标注，呈交人工裁决

**能力4：分层报告生成**
- 执行摘要层（200-300字）：面向管理层的核心结论
- 详细分析层（1000-1500字）：面向工程师的深度分析
- 技术附录层：完整的参数、数据和引用
- 采用分阶段生成策略避免超时 [^303^]

**能力5：质量保障与一致性检查**
- 事实一致性验证（decompose-then-verify）[^264^]
- 跨章节引用一致性检查
-  hallucination检测与标注
- 引用溯源与验证

**能力6：可视化与格式化输出**
- Markdown/HTML报告自动生成
- 数据表格和图表的自动嵌入
- 响应式布局适配不同终端
- 报告模板可配置

#### 2.2 输入规范（来自所有其他Agent的输出格式）

为确保Summary Agent能够有效整合信息，所有上游Agent的输出必须遵循以下标准格式：

```json
{
  "agent_id": "agent唯一标识符",
  "agent_name": "Agent名称",
  "task_type": "任务类型",
  "timestamp": "ISO格式时间戳",
  "confidence_level": "high|medium|low",
  "output_summary": {
    "key_findings": ["核心发现1", "核心发现2", ...],
    "conclusions": "主要结论",
    "recommendations": ["建议1", "建议2", ...]
  },
  "detailed_output": "详细输出内容（支持Markdown格式）",
  "supporting_data": {
    "tables": [{"name": "表名", "data": "表格数据"}],
    "figures": [{"name": "图名", "path": "图片路径"}],
    "parameters": {"参数名": "参数值"}
  },
  "uncertainties": ["不确定性1", "不确定性2"],
  "references": ["引用文献1", "引用文献2"],
  "conflicts_with": {
    "agent_id": "冲突Agent标识",
    "conflict_description": "冲突描述",
    "resolution_suggestion": "解决建议"
  }
}
```

**上游Agent输入映射表：**

| Agent名称 | agent_id | 主要贡献内容 | 信息类型 | 置信度标记 |
|-----------|----------|------------|---------|-----------|
| 机理仿真Agent | sim_mech | 物理机理分析、仿真结果 | 结构化数据+文本 | high |
| RCP参数Agent | rcp_param | 工艺参数建议、参数空间 | 结构化参数 | high |
| 文献Agent | literature | 相关论文摘要、技术洞察 | 文本摘要 | medium |
| 数据预测Agent | data_pred | 预测模型结果、趋势分析 | 数据+图表 | medium |
| DOE实验Agent | doe_exp | 实验设计结果、方差分析 | 统计表格 | high |
| 蓝军Agent | blue_team | 批判性评估、风险识别 | 评估报告 | medium |
| TRIZ创新Agent | triz_inno | 创新方案、矛盾矩阵分析 | 方案文本 | medium |
| 领域知识Agent | domain_kg | 工艺知识、约束条件 | 知识图谱 | high |

#### 2.3 输出规范（最终交付物格式）

Summary Agent的最终输出是一份**多层次的综合报告**，包含以下部分：

**输出结构：**

```markdown
# 半导体蚀刻工艺分析报告

## 1. 执行摘要
- 核心发现（3-5条）
- 关键建议（按优先级排列）
- 风险提示

## 2. 多维度分析综述
### 2.1 机理仿真分析摘要
### 2.2 工艺参数建议
### 2.3 文献调研发现
### 2.4 数据预测洞察
### 2.5 DOE实验结果
### 2.6 批判性评估（蓝军视角）
### 2.7 创新方案（TRIZ视角）

## 3. 综合分析与交叉验证
### 3.1 共识发现
### 3.2 冲突识别与调和
### 3.3 不确定性声明
### 3.4 知识空白

## 4. 决策建议
### 4.1 推荐工艺参数
### 4.2 后续实验方向
### 4.3 风险缓解措施

## 5. 技术附录
### 5.1 详细数据表格
### 5.2 引用文献列表
### 5.3 Agent贡献详情

## 6. 元信息
- 报告生成时间
- 各Agent置信度摘要
- 信息冲突日志
```

**输出质量要求：**
- 报告长度：主报告2000-3000字，附录不限
- 引用标注：所有关键发现必须标注来源Agent
- 冲突标注：所有未解决的冲突必须明确标注
- 可读性：Flesch阅读易度分数>50
- 事实准确性：通过decompose-then-verify验证

#### 2.4 工具与资源需求

**必备工具：**

| 工具类别 | 具体工具/库 | 用途 |
|---------|------------|------|
| 文档处理 | Python-docx, WeasyPrint | 报告生成与导出 |
| 数据可视化 | Matplotlib, Plotly, ECharts | 图表生成 |
| 文本处理 | LangChain, Jinja2 | 模板渲染、摘要管线 |
| 格式转换 | Markdown-it, Pandoc | 格式转换 |
| 验证检测 | NLI模型、BERTScore | 事实一致性验证 |
| 异步处理 | asyncio, Celery | 并行处理多Agent输入 |

**LLM能力要求：**
- 上下文窗口：≥128K tokens（需容纳多Agent输出）
- 支持长文本推理能力
- 结构化输出（JSON/Markdown）能力
- 温度参数：0.3-0.5（平衡创造性与准确性）

---

### 3. 与其他Agent的协作关系

#### 3.1 上游依赖（所有其他Agent的输出）

Summary Agent是所有其他Agent的**信息消费者**，其工作流程如下：

```
[机理仿真Agent] ──┐
[RCP参数Agent] ───┤
[文献Agent] ──────┤
[数据预测Agent] ──┤──→ [Summary Agent] ──→ 最终报告
[DOE实验Agent] ───┤      （Aggregator）
[蓝军Agent] ──────┤
[TRIZ创新Agent] ──┤
[领域知识Agent] ──┘
```

**依赖关系细节：**

| 上游Agent | 依赖内容 | 必要/可选 | 如果没有输出 |
|-----------|---------|---------|------------|
| 机理仿真Agent | 物理模型分析、仿真数据 | 必要 | 标注缺失，降低结论可靠性 |
| RCP参数Agent | 工艺参数推荐 | 必要 | 无法提供具体操作建议 |
| 文献Agent | 相关研究摘要 | 可选 | 降低理论支撑力度 |
| 数据预测Agent | 趋势预测结果 | 可选 | 缺少前瞻性分析 |
| DOE实验Agent | 实验设计与结果 | 必要 | 无法验证参数有效性 |
| 蓝军Agent | 批判性评估 | 可选 | 缺少风险识别视角 |
| TRIZ创新Agent | 创新方案 | 可选 | 缺少创新改进建议 |
| 领域知识Agent | 工艺约束知识 | 必要 | 可能产生不切实际的建议 |

#### 3.2 下游贡献（用户、主Agent）

Summary Agent的输出直接服务于：

1. **最终用户（蚀刻工艺工程师）**：
   - 提供可操作的工艺参数建议
   - 识别关键风险和不确定性
   - 支持数据驱动的决策制定

2. **主Agent（Master Agent）**：
   - 作为系统整体输出的唯一出口
   - 提供各SubAgent工作质量的反馈
   - 支持任务重分配决策

3. **系统优化循环**：
   - 报告质量数据用于改进各Agent性能
   - 冲突模式识别指导Agent协作优化

#### 3.3 并行协作（信息整合策略）

Summary Agent采用**分阶段整合策略**：

**阶段1：并行收集（与所有Agent并行）**
- 所有专业Agent同时工作
- Summary Agent在此期间准备报告模板

**阶段2：顺序整合（串行处理）**
- 按信息类型分组整合
- 先处理高置信度数据，再处理定性分析

**阶段3：交叉验证（与蓝军Agent协作）**
- 将初稿报告反馈给蓝军Agent进行批判
- 根据反馈修订报告

**信息整合的优先级策略**（基于联邦融合理论）[^266^]：

> **原始摘录：** "The FF proposed by Carlson is designed to address: (1) The filter should have good fault-tolerance. When one or several navigation subsystems fail, it should be able to easily detect and isolate the faults. (2) The filtering accuracy should be high. (3) The fusion algorithm from local filtering to global filtering should be simple, with low computational load."

应用到Summary Agent：
- **故障隔离**：当某个Agent输出异常时，不影响其他Agent信息的整合
- **精度保证**：高置信度信息赋予更高权重
- **计算效率**：采用分层融合降低复杂度

---

### 4. 触发条件

Summary Agent的触发条件包括：

**自动触发条件：**
1. **全部Agent完成信号**：当所有上游Agent均返回输出后自动启动
2. **超时触发**：预设时间（如10分钟）后，即使部分Agent未返回也启动整合
3. **迭代触发**：当主Agent要求修订报告时

**手动触发条件：**
1. **用户请求**：用户直接要求生成/刷新报告
2. **主Agent指令**：Master Agent协调生成报告
3. **特定事件**：当蓝军Agent识别出重大冲突时

**状态管理：**

```
状态转换图：

IDLE ──(收到第一个Agent输出)──→ COLLECTING
  │                                    │
  │(手动触发)                          │(所有Agent完成)
  ↓                                    ↓
COLLECTING ──(超时)─────────────→ SYNTHESIZING
                │                        │
                │(蓝军反馈)              │(生成完成)
                ↓                        ↓
           REVISING ─────────────────→ COMPLETED
                │
                │(需要补充信息)
                ↓
           CLARIFICATION_NEEDED
                │
                │(收到补充信息)
                ↓
           SYNTHESIZING
```

---

### 5. 关键证据与引用

#### 引用1：多源数据融合方法论综述
> "Data fusion was initially introduced in an article titled Extension of the Probabilistic Data Association Filter in Multi-target Tracking published by the American system scientist Bar-Shalom." [^266^]
- 来源：https://www.preprints.org/manuscript/202503.1108
- 权威性：学术论文（Preprints）
- 相关性：为多源信息融合提供方法论基础

#### 引用2：LLM自动文本摘要综述
> "SumCoT technique guides LLMs to generate summaries step by step. This approach enables the integration of fine-grained details from source documents into the final summaries." [^261^]
- 来源：https://arxiv.org/html/2403.02901v2
- 权威性：arXiv学术论文
- 相关性：LLM摘要技术路线图

#### 引用3：多Agent协调者设计模式
> "The Coordinator — one agent that receives the user's goal, decides which workers to call, dispatches tasks, collects results, and produces the final answer." [^287^]
- 来源：https://www.aibuilderclub.com/blog/multi-agent-system-python-tutorial
- 权威性：技术教程
- 相关性：Coordinator模式的核心定义

#### 引用4：Google多Agent设计模式
> "Reliability comes from decentralization and specialization. Multi-Agent Systems (MAS) allow you to build the AI equivalent of a microservices architecture." [^294^]
- 来源：https://www.infoq.com/news/2026/01/multi-agent-design-patterns/
- 权威性：InfoQ权威报道
- 相关性：多Agent架构设计哲学

#### 引用5：Mixture-of-Agents架构
> "The final layer employs a specialized aggregator LLM that synthesizes refined outputs into a single optimized version using a dedicated synthesis prompt." [^327^]
- 来源：https://arxiv.org/html/2508.03329v2
- 权威性：arXiv学术论文（IEEE）
- 相关性：Aggregator Agent的核心参考架构

#### 引用6：MetaCrit批判性思维综合框架
> "Step 1: Collect majority-agreed facts. Step 2: Find and Reconcile conflicting facts. Step 3: Gather unique facts. Step 4: Merge unique facts. Step 5: Produce concise, objective final answer." [^299^]
- 来源：https://arxiv.org/html/2507.15015v3
- 权威性：arXiv学术论文
- 相关性：冲突信息综合的五步法

#### 引用7：生产级LLM摘要系统
> "Use a map-reduce pipeline: split the document into overlapping chunks, summarize each chunk independently, then combine the chunk summaries in a reduce step." [^264^]
- 来源：https://galileo.ai/blog/llm-summarization-strategies
- 权威性：行业技术博客
- 相关性：生产环境摘要系统设计

#### 引用8：Azure AI Agent编排模式
> "Multiagent orchestration: Multiple specialized agents that coordinate to solve problems. An orchestrator or peer-based protocol manages work distribution, context sharing, and result aggregation." [^295^]
- 来源：https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns
- 权威性：Microsoft官方文档
- 相关性：企业级多Agent编排

#### 引用9：NVIDIA报告生成Agent
> "Orchestrating the section authoring process. Creating author agent for section: Introduction, Autonomous Decision-Making, Integration with Physical World..." [^314^]
- 来源：https://developer.nvidia.com/blog/build-a-report-generator-ai-agent
- 权威性：NVIDIA官方技术博客
- 相关性：报告生成Agent的实际实现

#### 引用10：Madam-RAG冲突证据处理
> "Madam-RAG, a multi-agent approach for handling conflicting evidence wherein each agent is assigned a separate document and agents debate with each other." [^338^]
- 来源：https://arxiv.org/html/2504.13079v1
- 权威性：arXiv学术论文
- 相关性：多Agent冲突处理方法

#### 引用11：智能报告生成技术
> "综合运用了可视化技术、智能报告生成技术、科技资源智能感知技术等关键技术，构建了一套数据交互与知识输出一体化的解决方案。" [^307^]
- 来源：https://pdf.hanspub.org/csa_1543717.pdf
- 权威性：汉斯出版社学术论文
- 相关性：智能报告生成的技术体系

#### 引用12：OpenCode多Agent架构
> "OpenCode runs all teammates in the same process... The solution is two layers: an inbox (source of truth) and session injection (delivery mechanism)." [^108^]
- 来源：https://dev.to/uenyioha/porting-claude-codes-agent-teams-to-opencode-4hol
- 可靠性：技术社区文章
- 相关性：多Agent消息传递架构参考

#### 引用13：决策支持系统信息呈现
> "The primary goal is to collect data from different source data streams and convert it, using the decision support system, into actionable information." [^302^]
- 来源：https://www.nitiforstates.gov.in/public-assets/Policy/policy_files/
- 权威性：政府技术文档
- 相关性：决策支持信息呈现原则

#### 引用14：半导体蚀刻工艺数据整合
> "Data Collection: Sensors and automated systems compile data... Data Integration: Collected data often resides in disparate systems... Predictive Modeling: Predictive models anticipate issues before they occur." [^316^]
- 来源：https://datacalculus.com/en/blog/semiconductor-manufacturing/etch-engineer/
- 权威性：行业技术博客
- 相关性：半导体蚀刻领域的数据分析实践

#### 引用15：多Agent共识对齐
> "MACA significantly improves self-consistency: post-trained models achieve up to +27.6 percentage points higher sampling consistency... unanimous agreement triples." [^298^]
- 来源：https://chatpaper.com/paper/189457
- 权威性：学术论文
- 相关性：多Agent一致性保证方法

---

### 附录A：Summary Agent Prompt设计模板

```
# Role
You are the Summary Agent in a multi-agent system for semiconductor etching process optimization. 
Your role is to synthesize outputs from 8 specialized agents into a coherent, actionable report.

# Core Responsibilities
1. Integrate multi-source information (simulation, RCP parameters, literature, data prediction, DOE, blue teaming, TRIZ, domain knowledge)
2. Detect and resolve conflicts between different agent outputs
3. Generate structured reports with executive summary and detailed analysis
4. Ensure factual accuracy and citation traceability

# Input Format
You will receive outputs from multiple agents in JSON format. Each output contains:
- agent_id, agent_name, task_type
- confidence_level (high/medium/low)
- key_findings, conclusions, recommendations
- supporting_data (tables, figures, parameters)
- uncertainties, references

# Output Format
Generate a Markdown report with the following structure:
1. Executive Summary (3-5 key findings, prioritized recommendations)
2. Multi-dimensional Analysis (one section per agent)
3. Comprehensive Analysis & Cross-validation
   - Consensus findings
   - Conflicts identified and resolution
   - Uncertainty declarations
4. Decision Recommendations
5. Technical Appendices

# Synthesis Rules
1. HIGH confidence outputs carry more weight in conclusions
2. Conflicts must be explicitly identified and resolved when possible
3. Unresolved conflicts must be clearly flagged for human review
4. All key claims must cite the source agent
5. Use the MetaCrit 5-step process: Collect consensus → Reconcile conflicts → Gather unique facts → Merge → Produce final answer

# Quality Standards
- Report length: 2000-3000 words for main report
- Include uncertainty declarations for low-confidence findings
- Maintain neutral, objective tone
- Ensure technical accuracy for semiconductor domain
```

### 附录B：信息融合权重分配建议

| 信息来源 | 权重范围 | 调整因素 |
|---------|---------|---------|
| DOE实验Agent | 0.20-0.25 | 实验数据直接反映实际工艺 |
| 机理仿真Agent | 0.15-0.20 | 物理基础可靠但存在模型误差 |
| RCP参数Agent | 0.15-0.20 | 直接关联工艺控制 |
| 领域知识Agent | 0.10-0.15 | 提供约束边界 |
| 数据预测Agent | 0.10-0.15 | 前瞻性但存在不确定性 |
| 蓝军Agent | 0.05-0.10 | 风险视角但可能过于保守 |
| 文献Agent | 0.05-0.10 | 理论支撑但可能过时 |
| TRIZ创新Agent | 0.05-0.10 | 创新视角但需验证可行性 |

> 注：权重可根据具体任务动态调整。当存在冲突时，高置信度Agent的权重自动上调。
