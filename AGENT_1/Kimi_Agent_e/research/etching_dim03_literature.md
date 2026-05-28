## 维度：文献SubAgent

---

### 1. 技术领域调研

#### 1.1 半导体蚀刻领域文献资源

半导体蚀刻工艺相关的学术文献主要分布在以下权威数据库和期刊中：

**核心学术数据库：**
- **IEEE Xplore**：涵盖IEEE Transactions on Semiconductor Manufacturing、IEEE Transactions on Plasma Science等期刊，是半导体制造与等离子体刻蚀领域的权威来源 [^23^]
- **Elsevier ScienceDirect**：包含Journal of Vacuum Science & Technology、Journal of Electrochemical Society、Plasma Sources Science and Technology等核心期刊 [^20^][^22^]
- **Springer Link**：包含Neural Computing and Applications等刊载刻蚀工艺优化研究的期刊 [^24^]
- **SPIE Digital Library**：涵盖光刻与刻蚀工艺相关的会议论文与期刊 [^23^]
- **ArXiv**：预印本服务器，收录大量AI/ML在半导体工艺优化中的前沿研究 [^23^]

**关键期刊列表（按相关性排序）：**

| 期刊名称 | 主要覆盖领域 | 代表性内容 |
|---------|------------|-----------|
| Journal of Vacuum Science & Technology A/B | 等离子体刻蚀、RIE、薄膜工艺 | Bosch工艺、DRIE、刻蚀机制研究 [^22^] |
| IEEE Transactions on Semiconductor Manufacturing | 半导体制造过程控制、APC | 虚拟量测、先进过程控制 [^23^] |
| Plasma Sources Science and Technology | 等离子体源设计与诊断 | 等离子体化学反应数据库(QDB) [^20^] |
| Applied Physics Letters | 应用物理快报 | 各向异性刻蚀、选择性刻蚀 [^22^] |
| Journal of Electrochemical Society | 电化学刻蚀 | 湿法刻蚀动力学、KOH刻蚀 [^21^] |
| Journal of the Korean Physical Society | 等离子体工艺参数优化 | DOE/RSM优化刻蚀参数 [^191^] |

**专利资源：**
- **Korea Intellectual Property Rights Information Service (KIPRIS)**：包含3569件以上半导体AI技术相关专利 [^116^]
- **USPTO Patent Full-Text and Image Database (PatFT)**：美国半导体刻蚀专利
- **EPO Espacenet**：欧洲专利局数据库

**原始摘录：**
> "Our research involved searching the SPIE Digital Library, IEEE Xplore, and ArXiv databases, identifying 58 publications in the field of ML-based semiconductor process optimization." [^23^]

> "Particularly, AI technology is actively studied for monitoring manufacturing and etch processes." [^116^]

#### 1.2 文献检索与知识抽取技术

**1.2.1 基于RAG的技术文献问答系统**

检索增强生成（Retrieval-Augmented Generation, RAG）已成为技术文献问答的核心技术架构。其工作流程包括：

1. **文档分块（Chunking）**：将长文档切分为语义连贯的段落 [^17^]
2. **向量化表示**：使用嵌入模型（如SciBERT、Specter2、all-MiniLM-L6-v2）将文本转换为高维向量 [^106^]
3. **相似度检索**：基于余弦相似度在向量数据库中检索最相关片段 [^106^][^80^]
4. **上下文增强生成**：将检索结果作为上下文输入LLM生成回答 [^17^]

**关键发现：**
- 针对科学文献的嵌入模型比较显示：**Specter2**（科学文献调优的Transformer）在科学文档嵌入方面表现最优，但阈值设置敏感；**all-MiniLM-L6-v2**作为通用模型在分离相关/不相关文档方面表现均衡；**TF-IDF**仅适用于高词汇重叠场景 [^106^]

**原始摘录：**
> "A typical RAG system first partitions the document into smaller sections and converts them into vector representations using embedding models. Upon a user query, the system retrieves the most relevant sections based on semantic similarity and passes them as context to an LLM, which then generates a response." [^17^]

> "This mechanism ensures that answers are directly grounded in the provided documents rather than relying solely on the model's pre-trained knowledge, enhancing factual reliability and interpretability." [^17^]

**1.2.2 GraphRAG：基于知识图谱的增强检索**

Microsoft Research提出的GraphRAG框架通过构建知识图谱显著提升复杂推理任务的问答性能 [^148^][^153^]：

**GraphRAG核心流程：**
1. **实体与关系抽取**：使用LLM从文档中识别实体（概念、对象、事件）及其关系 [^148^]
2. **图谱构建与索引**：构建知识图谱，每个节点关联源内容片段以保持可追溯性 [^148^]
3. **图谱增强检索与生成**：基于语义邻近度和图连通性检索相关子图，引导LLM生成回答 [^148^]

**GraphRAG vs 基线RAG：**
- 基线RAG难以连接分散信息（"connect the dots"）
- GraphRAG通过图遍历实现跨文档信息整合，适用于需要综合多源信息的复杂问题 [^153^]

**在半导体供应链知识管理中的应用：**
> "This study constructs a KG representing the semiconductor manufacturing supply chain and develops a GraphRAG-based question answering (QA) model... This approach improves knowledge retrieval efficiency, mitigates the context-length limitations of a large language model (LLM), and enables interpretable answers by exposing the model's reasoning process." [^110^]

**1.2.3 自然语言处理在科技文献知识抽取中的应用**

NLP技术在材料科学（含半导体工艺）文献中的应用已形成成熟方法论 [^81^][^85^]：

**核心技术栈：**
- **命名实体识别（NER）**：识别材料、工艺参数、设备、性能指标等实体
- **关系抽取（RE）**：抽取实体间的因果关系、条件关系、组成关系
- **联合抽取**：同时进行NER和RE，提升一致性

**关键工具与模型：**

| 工具/模型 | 技术类型 | 适用场景 | 精度水平 |
|----------|---------|---------|---------|
| ChemDataExtractor | 基于规则的NER | 化学式、材料属性 | 高精度（规则覆盖范围内） |
| BERT-PSIE | NER+RC Pipeline | 科学信息精确抽取 | 中等 |
| ChatExtract (GPT-based) | 提示工程 | 零样本/少样本抽取 | 最佳综合表现 |
| LangChain/RAG | 检索增强生成 | 大文档集信息提取 | 40-50% Precision, ~20% Recall |
| MatSciBERT/MatBERT | 领域预训练BERT | 材料科学文本分类、NER | 领域最优 |

**原始摘录：**
> "The use of Natural Language Processing to extract data from publications could greatly benefit the scientific community... Precision was encouraging, with many tools achieving scores of 40-50%, but Recall is identified as a key current issue, with the best tools only achieving 20%." [^90^]

> "We propose a joint extraction method comprising the material entity relationship based on Bi-GRU-GNN-CRF... The knowledge coverage of the material KGs constructed based on proposed method reaches 80%." [^198^]

**1.2.4 知识图谱在半导体/制造领域的应用**

知识图谱在半导体领域已有多个成功应用案例：

1. **晶圆缺陷检测知识图谱**：用于连接不同来源的缺陷数据，实现可追溯性和根因分析 [^109^]
2. **半导体供应链知识图谱**：构建GraphRAG QA系统，通过ontology设计和CoT提示实现复杂查询的准确回答 [^110^]
3. **材料知识图谱（MKG）**：从15万篇同行评审论文摘要中抽取材料-属性-应用三元组，支持材料相似度计算和链接预测 [^145^][^150^]
4. **半导体制造调度决策图**：将历史和当前决策过程转化为多维异构图，通过图神经网络实现深度学习和调度优化 [^19^]

**知识图谱构建流程：**
```
非结构化文本 → 本体设计(Ontology) → NER/RE抽取 → 实体消歧(ER) → 
三元组构建 → 图数据库存储(Neo4j) → 相似度计算/链接预测
```

**原始摘录：**
> "We present a novel NLP pipeline for Knowledge Graph (KG) construction, designed to efficiently extract triples from unstructured scientific texts... utilizing this approach, we constructed a Material Knowledge Graph (MKG) that encapsulates relations between materials and their associated entities derived from the abstracts of 150,000 peer-reviewed papers." [^150^]

#### 1.3 相似场景匹配与推荐方法

**1.3.1 基于案例的推理（Case-Based Reasoning, CBR）**

CBR是制造工艺设计中成熟的相似场景匹配方法，其核心流程为：Retrieve（检索）→ Reuse（复用）→ Revise（修正）→ Retain（保留）[^111^][^114^]。

**相似度计算模型：**
- **最近邻法（Nearest Neighbor）**：结合不同属性类型的相似度计算模型 [^111^]
- **层次分析法（AHP）**：确定属性权重系数，通过矩阵计算实现加权相似度 [^111^]
- **相似度系数公式**：`Ks = a_ml * k_ml + a_mf * k_mf + a_af * k_af`，其中k为匹配比率，a为权重系数 [^114^]

**原始摘录：**
> "A Case-Based Reasoning (CBR) intelligent process design system is developed... The key factor in improving the accuracy of case matching in the CBR system is the similarity calculation of parts... similarity calculation models for different attribute types are presented by combining the nearest neighbor method." [^111^]

**1.3.2 基于图嵌入的相似度计算**

图嵌入技术将工艺过程表示为语义图，通过神经网络学习相似度：
- **sGEM（Siamese Graph Embedding Model）**：学习图嵌入表示，通过余弦相似度比较 [^210^]
- **sGMN（Siamese Graph Matching Network）**：直接学习图对之间的匹配关系 [^210^]
- **GraphSAGE、Node2Vec**：用于图节点嵌入，结合向量语义检索和图拓扑推理 [^88^]

**1.3.3 语义相似度与向量化检索**

语义搜索通过理解查询意图而非简单关键词匹配来检索相关文献：
- **向量搜索**：将文本转换为高维向量（通常768维），通过HNSW、FAISS等近似最近邻算法高效检索 [^80^][^86^]
- **语义搜索**：利用知识图谱和上下文嵌入理解用户意图 [^86^]
- **混合搜索**：结合关键词匹配（BM25）和向量相似度，兼顾精确度和召回率 [^151^]

**关键向量数据库/索引技术：**

| 技术 | 特点 | 适用规模 |
|-----|------|---------|
| HNSW (Hierarchical Navigable Small World) | 分层可导航小世界图，高召回率 | 百万级 |
| FAISS (Facebook AI Similarity Search) | 多种量化算法，GPU加速 | 十亿级 |
| Milvus | 专用向量数据管理系统 | 企业级 |
| Elasticsearch + dense_vector | 与传统搜索引擎集成 | 中小规模 |

**原始摘录：**
> "Vector search finds similar content by converting text into high-dimensional vectors and comparing them... Semantic search, on the other hand, understands the user's intent by leveraging knowledge graphs and contextual embeddings." [^86^]

**1.3.4 工艺参数提取与结构化方法**

从科学文献中提取工艺参数是知识管理的关键环节，已形成多种技术路线：

**技术路线对比：**

| 方法 | 原理 | 优势 | 局限 |
|-----|------|------|------|
| 规则匹配（ChemDataExtractor） | 预定义语法规则 | 高精度（规则覆盖时） | 规则编写耗时，适应性差 |
| BERT-PSIE（NER+RC Pipeline） | BERT命名实体识别+关系分类 | 端到端，无需规则 | 需要标注数据 |
| ChatExtract（Prompt Engineering） | GPT+特定提示模板 | 零样本能力，高Null-Precision | 上下文理解有限 |
| RAG（LangChain） | 检索增强+生成 | 利用大文档集上下文 | Recall约20% |
| LLM微调（如SciBERT） | 领域预训练+微调 | 领域适应性好 | 需计算资源 |

**工艺参数结构化表示：**
基于DOE（实验设计）方法论，刻蚀工艺参数通常表示为多维向量：
- 输入参数：RF功率、偏置电压、气体流量、腔室压力、基底温度、气体配比 [^192^][^207^]
- 输出指标：刻蚀速率、各向异性度、选择性、均匀性 [^192^]

**原始摘录：**
> "Tools based on either ChatExtract or LangChain were delivered the best results... Most tools showed Null-Precision values exceeding 94%." [^90^]

> "Optimization of the etch was done by help of DoE, with four variables: beam current, beam voltage, accelerator voltage, and incident angle... The resulting 19 experiments were done in random order." [^207^]

---

### 2. SubAgent能力设计建议

#### 2.1 核心能力

基于以上调研，文献SubAgent应具备以下核心能力：

**能力1：多源文献检索**
- 支持跨数据库检索（IEEE Xplore、ScienceDirect、Springer、ArXiv等）
- 支持关键词检索、语义检索、引用网络扩展三种模式
- 支持按时间范围、期刊、影响因子过滤

**能力2：知识抽取与结构化**
- 从PDF/文本中提取：工艺参数（输入/输出）、材料信息、设备信息、实验条件
- 使用NER+RE Pipeline识别实体关系
- 输出结构化JSON格式（兼容DOE数据格式）

**能力3：相似场景匹配**
- 基于CBR框架，计算查询场景与文献案例的相似度
- 支持多维度加权相似度：材料类型、工艺方法、设备类型、参数范围
- 返回Top-N最相似案例及相似度分数

**能力4：知识图谱查询**
- 基于领域知识图谱进行语义查询
- 支持路径推理（如：材料A→工艺B→参数C→性能D）
- 支持" connect the dots "类跨文档知识整合

**能力5：文献综合与摘要**
- 生成针对特定工艺问题的文献综述段落
- 对比不同研究的参数设置与结果
- 标识研究空白和潜在解决方案

#### 2.2 输入规范

```json
{
  "query_type": "similar_case_search | knowledge_extraction | literature_synthesis | parameter_lookup",
  "process_description": {
    "etching_type": "dry_etching | wet_etching | plasma_etching | RIE | DRIE | ICP",
    "material_system": "Si | SiO2 | GaN | Al2O3 | etc.",
    "target_structure": "description of target pattern/structure",
    "equipment": "optional equipment information"
  },
  "parameters": {
    "input_params": {
      "rf_power": "value_or_range (W)",
      "bias_voltage": "value_or_range (V)",
      "pressure": "value_or_range (mTorr)",
      "gas_flow": {"gas_name": "flow_rate (sccm)"},
      "temperature": "value_or_range (C)"
    },
    "output_requirements": {
      "etch_rate": "target_or_range (nm/min)",
      "selectivity": "target_or_ratio",
      "anisotropy": "target_or_description",
      "uniformity": "target (%)",
      "roughness": "target (nm)"
    }
  },
  "constraints": {
    "time_range": "optional year range",
    "journals": ["optional preferred journals"],
    "min_similarity_threshold": 0.7
  },
  "context_from_other_agents": {
    "root_cause_analysis": "optional findings from diagnosis agent",
    "equipment_specs": "optional equipment specifications",
    "desired_outcome": "specific optimization goal"
  }
}
```

#### 2.3 输出规范

```json
{
  "status": "success | partial | no_results",
  "results": {
    "similar_cases": [
      {
        "paper_id": "unique_identifier",
        "title": "paper title",
        "authors": ["author list"],
        "journal": "journal name",
        "year": 2024,
        "doi": "doi link",
        "similarity_score": 0.92,
        "matching_dimensions": ["material", "etching_type", "parameter_range"],
        "extracted_knowledge": {
          "input_parameters": {
            "rf_power": "value",
            "pressure": "value",
            "gas_composition": "value"
          },
          "output_results": {
            "etch_rate": "value",
            "selectivity": "value"
          },
          "key_finding": "brief description of main finding"
        },
        "relevance_explanation": "why this case is relevant"
      }
    ],
    "knowledge_graph_insights": {
      "related_entities": ["connected materials/processes/properties"],
      "inferred_relationships": ["potential indirect connections"],
      "graph_paths": ["semantic reasoning paths"]
    },
    "literature_summary": {
      "current_state": "summary of current research status",
      "parameter_trends": "observed trends in parameter optimization",
      "research_gaps": "identified gaps",
      "recommendations": ["actionable recommendations"]
    }
  },
  "metadata": {
    "search_scope": "databases searched",
    "total_papers_screened": 150,
    "total_papers_selected": 12,
    "confidence_level": "high | medium | low"
  }
}
```

#### 2.4 工具与资源需求

**必要工具：**

| 工具类别 | 具体工具/服务 | 用途 |
|---------|-------------|------|
| 文献检索API | arXiv API、CrossRef API、Semantic Scholar API | 批量检索论文元数据 |
| 向量数据库 | Milvus/FAISS/Chroma | 存储论文嵌入向量，支持语义检索 |
| 图数据库 | Neo4j | 存储和查询工艺知识图谱 |
| NLP工具 | SciBERT/MatSciBERT、ChemDataExtractor | 实体识别和关系抽取 |
| LLM接口 | GPT-4/Claude/Llama（本地或API） | 文本理解、摘要生成、知识推理 |
| PDF解析 | GROBID/PyPDF2/pdfplumber | PDF文本和表格提取 |
| 嵌入模型 | Specter2/all-MiniLM-L6-v2 | 论文文本向量化 |

**知识资源需求：**
- 半导体蚀刻领域本体（Ontology）：定义材料、工艺、设备、参数、性能指标等概念体系
- 领域知识图谱：预构建的刻蚀工艺知识图谱（含三元组数据）
- 论文语料库：定期更新的刻蚀相关论文全文/摘要集合
- 历史案例库：结构化存储的历史工艺案例（参数+结果）

**原始摘录：**
> "The lead agent maintains overall research state through a memory system that persists context when conversations exceed 200,000 tokens, preventing loss of research plans and findings. Subagents function as intelligent filters, iteratively using search tools to gather relevant information before condensing findings for the lead agent's synthesis." [^152^]

---

### 3. 与其他Agent的协作关系

#### 3.1 上游依赖

| 上游Agent | 提供内容 | 使用方式 |
|----------|---------|---------|
| 诊断SubAgent | 问题诊断结果、疑似根因 | 作为检索关键词的语义扩展输入 |
| 主Agent（调度器） | 任务指令、查询问题 | 解析任务类型，确定检索策略 |

文献SubAgent需要从上游获取的具体信息：
- 工艺问题的自然语言描述（用于语义检索）
- 已识别的根因类别（用于缩小检索范围）
- 当前工艺参数（用于相似度计算）
- 目标性能指标（用于匹配优化方向）

#### 3.2 下游贡献

| 下游Agent | 接收内容 | 价值 |
|----------|---------|------|
| 参数优化SubAgent | 文献中的最优参数组合、参数-性能映射关系 | 提供先验知识，缩小搜索空间 |
| 根因分析SubAgent | 类似案例的根因-解决方案对 | 验证或补充诊断假设 |
| 预测SubAgent | 历史参数-结果数据集 | 作为训练数据或特征工程参考 |
| 主Agent（汇总） | 结构化文献综述、Top-N案例推荐 | 支撑最终决策建议 |

#### 3.3 并行协作

文献SubAgent可以与以下Agent并行工作：
- **设备SubAgent**：文献SubAgent检索类似设备的工艺文献，设备SubAgent查询设备规格手册
- **参数优化SubAgent**：文献SubAgent提供文献先验，参数优化SubAgent基于仿真/实验优化
- **知识图谱SubAgent**（如有）：协同进行知识图谱查询和推理

**协作模式参考（Anthropic SubAgent设计）：**

```
主Agent（调度器）
    ↓ 任务分解
    ├─→ 文献SubAgent：检索类似案例和参数
    ├─→ 诊断SubAgent：分析当前问题根因
    ├─→ 设备SubAgent：查询设备能力和限制
    └─→ 参数优化SubAgent：优化工艺参数
         ↓ 并行执行
    ← ← ← ← 聚合结果
    ↓
主Agent综合 → 返回用户
```

**设计原则（参考Anthropic SubAgent模式）：**
- **上下文隔离**：文献SubAgent的工作细节不污染主Agent上下文 [^149^]
- **结果压缩**：文献SubAgent仅返回最相关的发现，而非完整中间过程 [^149^]
- **无状态设计**：每次调用独立，通过输入参数传递全部必要上下文

**原始摘录：**
> "Subagents function as intelligent filters, iteratively using search tools to gather relevant information before condensing findings for the lead agent's synthesis. This distributed approach enables the system to process far more information than single-agent systems." [^120^]

---

### 4. 触发条件

文献SubAgent应在以下场景被触发：

| 触发场景 | 触发条件 | 预期输出 |
|---------|---------|---------|
| 新问题诊断 | 收到新蚀刻工艺问题时 | 检索类似问题的文献案例 |
| 参数优化建议 | 需要参考已有文献的优化方案 | 最优参数组合推荐 |
| 根因验证 | 需要验证某根因假设是否有文献支持 | 支持/反驳的文献证据 |
| 知识空白识别 | 当前知识库无法回答 | 扩展检索范围后的综合报告 |
| 工艺迁移 | 从已知材料/工艺迁移到新场景 | 迁移案例和经验总结 |

**触发条件判断逻辑：**
```
IF 任务类型 == "etching_problem_solving" AND
   (query_contains("similar case") OR 
    query_contains("文献") OR 
    query_contains("paper") OR
    query_contains("reference") OR
    diagnosis_uncertainty > threshold)
THEN 触发文献SubAgent
```

---

### 5. 关键证据与引用

#### 5.1 文献检索数据库与资源

[^18^] Xiong, W. et al. (2021). "Wafer Reflectance Prediction for Complex Etching Process Based on K-Means Clustering and Neural Network," *IEEE Trans. on Semiconductor Manufacturing*, vol. 34, no. 2, pp. 207-216.

[^20^] Tennyson, J. et al. (2017). "QDB: a new database of plasma chemistries and reactions," *Plasma Sources Science and Technology*, 26, 055014. DOI: 10.1088/1361-6595/aa6669

[^21^] Kendall, D.L. (1990). "A new theory for the anisotropic etching of silicon and some underdeveloped chemical micromachining concepts," *Journal of Vacuum Science and Technology* 8(4): 3598-3605.

[^22^] Selective Plasma Etching of Polymeric Substrates, *PMC*, DOI references including Coburn & Winters (1979), Oehrlein (1986).

[^23^] "Exploring Machine Learning for Semiconductor Process Optimization: A Systematic Review," *IEEE Access*, 2024. DOI: 10.1109/ACCESS.2024.3428217 — 系统综述了SPIE、IEEE Xplore、ArXiv三大数据库的58篇ML半导体工艺优化论文。

[^24^] Chen, W.C. et al. (2013). "Parameter optimization of etching process for a LGP stamper," *Neural Computing and Applications*, 23, 1539-1550.

#### 5.2 RAG与文献问答

[^16^] "Federated Retrieval-Augmented Generation: A Systematic Mapping Study," arXiv:2505.18906, 2025.

[^17^] "Transforming Science with Large Language Models: A Survey on AI-assisted Scientific Discovery," arXiv:2502.05151v1, 2025. — 详细描述RAG在科学文献QA中的应用机制。

[^80^] "VectorSearch: Enhancing Document Retrieval with Semantic Embeddings," arXiv:2409.17383v1, 2024.

[^106^] Automated Literature Review Generation with Embedding-Based Paper Filtering, arXiv:2509.15292, 2025. — 比较TF-IDF、all-MiniLM-L6-v2、Specter2三种嵌入模型性能。

#### 5.3 NLP与知识抽取

[^81^] "Natural Language Processing for Materials Procedures Extraction," arXiv:2302.05597. — 综述NLP在材料科学信息提取中的应用。

[^82^] Ning, W. et al. (2025). "Optimizing Data Extraction from Materials Science Literature," *Digital Discovery*, RSC. — 对比5种AI工具（ChemDataExtractor、BERT-PSIE、ChatExtract、LangChain、Kimi）的提取性能。

[^83^] "Accelerated materials language processing enabled by GPT," arXiv:2308.09354v1. — GPT用于材料语言处理（NER、文本分类、QA）。

[^84^] "SciQu: Accelerating Materials Properties Prediction with Automated Literature Mining," arXiv:2407.08270, 2024. — 自动化文献挖掘与材料性质预测。

[^85^] "Natural Language Processing for Knowledge Discovery and Information Extraction from Energetics Corpora," arXiv:2402.06964v1, 2024.

[^89^] "Natural language processing-guided meta-analysis and structure factor database extraction from glass literature," *Journal of Non-Crystalline Solids: X*, 2022.

[^90^] Ning, W. et al. "Optimizing data extraction from materials science literature," *Digital Discovery*, RSC, 2025. — 关键发现：Precision 40-50%, Recall ~20%, Null-Precision >94%。

#### 5.4 知识图谱

[^19^] "Optimisation method for semiconductor wafer manufacturing system scheduling: Reinforcement learning with decision graph guiding," *Journal of Manufacturing Systems*, 2025. — 半导体制造决策图引导的强化学习。

[^88^] "Graph-Vector Fusion for Academic Literature Retrieval," arXiv:2604.16416. — 图向量融合用于学术文献检索。

[^109^] "The Complete Guide to Using Knowledge Graphs For Wafer Defect Detection in 2025," yieldWerx.

[^110^] "Design and Implementation of a Semiconductor Supply Chain Knowledge Graph for GraphRAG-Based QA," University of Hawaii, 2025. — GraphRAG在半导体供应链QA中的应用，BERTScore和F1-score优于VectorRAG基线。

[^145^] "Construction and Application of Materials Knowledge Graph in Multidisciplinary Materials Science via Large Language Model," NeurIPS 2024. — 从15万篇论文构建材料知识图谱。

[^148^] "GraphRAG for Complex Question Answering over Academic Articles," arXiv:2509.16780. — GraphRAG在学术文献QA中的方法论。

[^150^] Same as [^145^], NeurIPS 2024 Conference Proceedings.

[^153^] Microsoft Research, "GraphRAG" official documentation. — GraphRAG与基线RAG的对比分析。

[^198^] Wei, X. et al. (2022). "基于自然语言处理的材料领域知识图谱构建方法," *上海大学学报(自然科学版)*, 28(3): 386-398. — Bi-GRU-GNN-CRF联合抽取，知识覆盖率80%。

#### 5.5 自动文献综述生成

[^108^] "HiReview: Hierarchical Taxonomy-Driven Automatic Literature Review Generation," arXiv:2410.03761v1, 2024.

[^113^] "AI-Assisted Tools for Scientific Review Writing," *PMC/NIH*, 2025. — RAG+模块化LLM Agent自动生成科学综述。

#### 5.6 相似度计算与CBR

[^111^] Liu, J. et al. "Research on the Application of CBR Technology in Intelligent Process Design System," Henan Polytechnic University. — CBR在工艺设计中的相似度计算。

[^114^] "Improved Methods for Production Manufacturing Processes in Environmentally Benign Manufacturing," Semantic Scholar. — CBR相似度系数公式。

[^210^] "Using Graph Embedding Techniques in Process-Oriented Case-Based Reasoning," *Algorithms*, 2022, 15(2), 27. — sGEM和sGMN图嵌入学习工艺相似度。

#### 5.7 多Agent架构设计

[^120^] Anthropic, "How we built our multi-agent research system," 2025. — Orchestrator-Worker模式，LeadAgent+SubAgent+CitationAgent三层架构。

[^149^] "Anthropic Subagent: The Multi-Agent Architecture Revolution," 2026. — SubAgent核心设计原则：任务分解、并行执行、上下文隔离、结果压缩。

[^151^] "Queryome: A Multi-Agent System for Scientific Literature Analysis," bioRxiv, 2025. — PI+Planner+Critic+Synthesizer层级架构，子Agent并行处理不同子问题。

[^152^] ZenML, "Anthropic: Building a Multi-Agent Research System for Complex Information Tasks." — 引用系统和并行工具调用设计。

#### 5.8 半导体工艺优化方法

[^116^] "Text mining method to identify artificial intelligence technologies for the semiconductor industry in Korea," *World Patent Information*, 2025. — 从3569件专利中识别刻蚀工艺监控AI技术趋势。

[^154^] Kim, B. & May, G.S. (1994). "An optimal model for plasma etching," *IEEE Transactions on Semiconductor Manufacturing*, Vol.7, No.1. — 神经网络用于等离子体刻蚀的经典论文。

[^156^] Xiao, T. (2022). "Recurrent Neural-Network-Based Model Predictive Control for Plasma Etching Processes," UCLA. — RNN-MPC用于等离子体刻蚀过程优化。

[^191^] Lee, Y. et al. (2020). "Optimization of the etching process parameters in plasma etching of Al2O3 using a design of experiment," *Journal of the Korean Physical Society*, 77(3):219-224. — DOE优化Al2O3等离子体刻蚀参数。

[^192^] "Modeling and Optimization of High Aspect Ratio Plasma Etching for Semiconductor Devices," Be-Cu Etch, 2025. — HAR等离子体刻蚀参数影响表（RF功率、偏置电压、气体流量、压力、温度）。

[^207^] Rasmussen, K.H. (2014). "Advanced dry etching studies for micro- and nano-systems," PhD Thesis, DTU. — DOE设计磁 stack刻蚀参数（4变量，19次实验）。

