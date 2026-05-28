## 维度：蓝军（Review & 批判）SubAgent

### 1. 技术领域调研

#### 1.1 Red Team/Blue Team方法论

**方法论起源与核心概念**

Red Team/Blue Team（红队/蓝队）方法论起源于军事战争游戏，后在网络安全领域得到系统化发展。NIST将红队定义为"被授权和组织起来以模拟潜在对手攻击能力的一组人员"[^272^]。红队采用攻击者视角，通过创造性思维发现系统漏洞；蓝队则从防御者视角出发，专注于预防、检测和响应威胁[^263^]。

> "Red teams are offensive security professionals who simulate real attackers to test your organization's defenses. They use the same tactics, techniques, and procedures that malicious actors employ to find weaknesses before actual attackers can exploit them." [^263^]

在技术系统评审中，这一方法论已被扩展到AI安全评估领域。NIST AI风险管理框架（AI RMF）在GOVERN 1.7中明确要求建立红队测试机制，将其作为组织治理实践而非一次性技术活动[^314^]。

**AI领域的红蓝对抗应用**

在AI系统安全评估中，红队测试已成为识别未知风险的关键方法。NIST的研究发现，当红队开发针对LLM Agent特定行为模式的新型攻击技术时，任务劫持成功率从11%跃升至81%[^313^]。这表明防御措施如果仅针对已知攻击分类进行校准，很可能严重低估实际攻击面。

> "The headline result is stark: when red teamers developed novel attack techniques tailored to the specific behavioral patterns of LLM-backed agents — rather than relying on known baseline attack patterns — task-hijacking success rates rose from 11% to 81%." [^313^]

微软Azure AI Red Teaming Agent提供了微调的对抗性LLM，专门用于模拟对抗攻击任务，其关键指标是攻击成功率（ASR）[^260^]。腾讯也建立了大模型安全Red Team对抗机制，基于安全专家服务团队主动发现大模型及生态存在的风险[^264^]。

**蓝队角色的价值与职能**

蓝队专注于防御性审查，其核心职能包括：保护组织关键资产、执行风险评估、建立安全基线、持续监控和分析安全事件[^269^]。在半导体工艺评审语境下，蓝队角色对应于"批判性审查者"——不是寻找安全漏洞，而是识别技术方案中的逻辑缺陷、假设偏差和风险盲点。

蓝队的成功衡量指标包括：检测平均时间（MTTD）、响应平均时间（MTTR）、阻止攻击的百分比[^263^]。类比到工艺评审领域，蓝军SubAgent的成功指标应该是：发现的逻辑缺陷数量、识别的风险假设数量、阻止错误方案的能力。

**Purple Team协作模式**

Purple Team（紫队）是红队与蓝队的协作整合，强调知识转移和持续改进[^274^]。在我们的多Agent系统中，蓝军SubAgent与其他Agent的关系类似于Purple Team模式——不是单纯的对抗，而是通过批判性反馈推动整体方案质量提升。

**HAAF框架的启示**

Holographic Agent Assessment Framework（HAAF）提出了"红队探测暴露漏洞表面→蓝队加固设计针对性干预→重新评估验证改进"的迭代循环[^282^]。这一迭代优化工厂模式可以直接应用于蓝军SubAgent的设计：

> "The framework centers on a distribution-aware representative sampling engine... connected through an iterative Trustworthy Optimization Factory: red-team probing exposes vulnerability surfaces, blue-team hardening designs targeted interventions, and re-evaluation verifies improvement, cycling until the deployed system meets deployment-readiness thresholds." [^282^]

#### 1.2 批判性审查在工程中的应用

**Critic-Reviewer设计模式**

在多Agent系统中，"批评者-审查者"（Critic-Reviewer）是一种成熟的设计模式。一个Agent生成初始输出（计划、草案或答案），第二组Agent批判性评估此输出是否符合策略、安全性、合规性、正确性、质量以及与组织目标的一致性[^261^]。

> "批评者-审查者：一个智能体生成初始输出，如计划、草稿或答案。第二组智能体批判性地评估此输出是否符合政策、安全性、合规性、正确性、质量以及与组织目标的一致性。原始创建者或最终智能体根据反馈修订输出。此模式对于代码生成、研究写作、逻辑检查和确保道德一致性特别有效。" [^261^]

OpenCode平台明确支持这种SubAgent设计，提供了code-reviewer模式的配置示例：

```json
{
  "code-reviewer": {
    "description": "审查代码的最佳实践和潜在问题",
    "mode": "subagent",
    "model": "anthropic/claude-sonnet-4-20250514",
    "prompt": "你是一个代码审查员。关注安全性、性能和可维护性。"
  }
}
```
[^294^]

**迭代精炼模式**

Iterative Refinement Pattern（迭代精炼模式）是批判性审查的核心机制：

```
Generator → Critic → Generator (revised) → Critic → ... → Approved Output
```

> "Agents critique and improve each other's work in cycles... The critic agent has specific evaluation criteria: Does the code handle edge cases? Are there security vulnerabilities? Is the logic clear and maintainable? Each critique round makes the output better." [^271^]

**反射模式（Reflection Pattern）**

Reflection模式赋予AI Agent评估和改进自身输出的能力。其实现通常遵循三个阶段：生成（Generate）→ 反思（Reflect）→ 精炼（Refine）[^292^]。

关键实现变体包括：

1. **单次批判（Single-pass critique）**：生成→批判→修订，一次循环。成本低但只有一次修正机会。
2. **迭代精炼（Iterative refinement/Self-Refine）**：多次循环直到批判满意或预算耗尽。每次迭代基于前一轮的具体反馈进行改进[^289^]。
3. **工具辅助验证（Tool-grounded verification）**：结合外部验证工具（如单元测试、搜索、计算）进行事实核查。
4. **多Agent评审委员会（Multi-Agent Review Board）**：部署多个专业批判者（安全、准确性、风格）分别检查不同维度[^290^]。

> "Single-pass critique... Strengths: Low token cost. Weaknesses: One shot at revision. Iterative refinement... Strengths: Genuinely iterative. Weaknesses: On tasks with vague quality criteria, the loop does not converge — it oscillates. Token cost scales linearly with iteration count, and the marginal improvement per iteration drops steeply after iteration 2." [^289^]

**蓝军Agent的批判焦点**

根据现有研究，有效的批判性审查应聚焦以下维度：
- **逻辑一致性**：检查推理链条是否存在断裂或矛盾
- **假设验证**：识别方案中隐含的前提假设，评估其合理性
- **边界情况处理**：评估方案在极端或异常条件下的表现
- **风险评估**：系统性识别潜在失效模式及其影响
- **事实核查**：验证关键声明是否有可靠依据
- **完备性检查**：确认方案是否遗漏关键要素

#### 1.3 FMEA与风险评估方法

**FMEA在半导体蚀刻中的应用**

Failure Mode and Effects Analysis（FMEA，失效模式与影响分析）是半导体制造业核心风险评估工具。在等离子体蚀刻设备中，FMEA用于系统性识别、评估和优先处理潜在失效机制[^267^]。

> "Failure Mode and Effects Analysis (FMEA) is a proactive tool used to identify, assess, and prioritize potential failure mechanisms within plasma etching systems. This structured approach evaluates each subsystem for likely failure modes, the severity of consequences, the likelihood of occurrence, and the ease of detection." [^267^]

FMEA通过三个维度的评分计算风险优先级数（RPN = Severity × Occurrence × Detection）：
- **严重度（S）**：失效后果的严重程度
- **发生度（O）**：失效发生的概率
- **探测度（D）**：现有控制措施探测失效的能力

在蚀刻工艺中的典型应用包括[^267^][^280^]：

| 失效模式 | 严重度 | 发生度 | 探测度 | RPN |
|---------|-------|-------|-------|-----|
| RF发生器漂移 | 高（晶圆报废） | 中 | 低（无早期信号） | 高 |
| 真空泵退化 | 高 | 中 | 中 | 高 |
| 腔室污染 | 高 | 高 | 低 | 高 |
| 配方错误配置 | 高 | 低 | 中 | 中 |
| 喷淋头侵蚀 | 中 | 中 | 低 | 中 |

> "In the context of plasma etching, FMEA can be applied to components such as the RF generator, throttle valve assembly, ESC controller, or endpoint detector. For example, a failure mode such as 'match unit detuning' would be assessed for its potential to cause plasma loss, misprocessing, or chamber arcing." [^267^]

**DMAIC方法论在半导体制造中的应用**

DMAIC（Define-Measure-Analyze-Improve-Control）方法论结合FMEA已被证明在半导体制造中有效提升良率[^280^]。在蚀刻阶段（wafer cleaning）的FMEA模板中，大部分纠正措施在6周内实施，显著减少了蚀刻步骤后的在线缺陷数量。

> "Following the implementation of the DMAIC methodology... the final probe yield test demonstrated a substantial decrease in die yield loss, nearly reaching 0% post-DMAIC implementation." [^280^]

**半导体制造安全框架**

半导体制造安全框架整合了FMEA和故障树分析（FTA），用于识别制造过程中的潜在故障点[^265^]：

> "The framework incorporates the use of failure modes and effects analysis (FMEA) and fault tree analysis (FTA) for identifying potential failure points in the semiconductor manufacturing process. These tools are employed to assess the likelihood and severity of risks, allowing for the development of mitigation strategies." [^265^]

**HAAF框架的迭代优化模式**

HAAF框架提出的迭代优化工厂模式将红队探测、蓝队加固和重新评估形成闭环[^282^]。这一模式对蓝军SubAgent的设计具有直接指导意义——蓝军不仅是"找问题"的角色，更是推动系统持续改进的驱动力。

---

### 2. SubAgent能力设计建议

#### 2.1 核心能力

基于上述调研，蓝军（Review & 批判）SubAgent应具备以下六大核心能力群：

**能力群1：逻辑一致性检查（Logical Consistency Check）**

| 子能力 | 描述 | 优先级 |
|-------|------|-------|
| 推理链验证 | 检查方案推理链条是否完整、是否存在断裂或跳跃 | P0 |
| 矛盾检测 | 识别方案中自相矛盾的声明或建议 | P0 |
| 因果有效性评估 | 验证因果关系是否成立，是否存在虚假因果 | P1 |
| 量纲/单位一致性 | 检查物理量计算中的量纲一致性 | P1 |

> "The critic is asking 'does this paragraph satisfy the constraints I was given?' That second question is harder to fake, harder to drift on, and crucially uses different reasoning paths than generation itself." [^286^]

**能力群2：假设验证与识别（Assumption Validation）**

| 子能力 | 描述 | 优先级 |
|-------|------|-------|
| 隐式假设挖掘 | 识别方案中未明确声明的前提假设 | P0 |
| 假设合理性评估 | 评估每个假设在蚀刻工艺语境下的合理性 | P0 |
| 边界条件检验 | 验证假设在极端工艺条件下的有效性 | P1 |
| 敏感性分析 | 评估方案输出对假设变化的敏感程度 | P1 |

**能力群3：风险评估（Risk Assessment）**

| 子能力 | 描述 | 优先级 |
|-------|------|-------|
| FMEA式失效分析 | 基于FMEA框架识别潜在失效模式 | P0 |
| 风险优先级排序 | 按S×O×D模型计算RPN并排序 | P0 |
| 连锁失效识别 | 发现单一失效引发的级联效应 | P1 |
| 工艺窗口评估 | 评估方案在安全工艺窗口内的稳健性 | P0 |

> "FMEA enables fabs to prioritize corrective actions and develop targeted maintenance plans. For instance, recurring issues with RF match units or showerhead erosion can be mitigated through predictive replacement schedules rather than reactive fixes." [^267^]

**能力群4：事实核查与幻觉检测（Fact-Checking & Hallucination Detection）**

| 子能力 | 描述 | 优先级 |
|-------|------|-------|
| 物理常数验证 | 验证关键物理常数和材料参数的准确性 | P0 |
| 工艺参数范围核查 | 检查工艺参数是否在物理可行范围内 | P0 |
| 引用文献验证 | 验证引用的标准、文献是否真实存在 | P1 |
| 数值合理性检查 | 检查计算结果的数量级合理性 | P0 |

> "We parse the generated patch into an Abstract Syntax Tree (AST) and cross-reference the extracted symbols against our knowledge base that is derived from a trusted specification. Therefore, we can verify hallucinations of method calls, constants, and type instantiation." [^212^]

**能力群5：完备性与覆盖性检查（Completeness Check）**

| 子能力 | 描述 | 优先级 |
|-------|------|-------|
| 需求覆盖度分析 | 检查方案是否覆盖所有工艺需求 | P0 |
| 约束条件确认 | 确认所有工艺约束是否被满足 | P0 |
| 遗漏要素识别 | 识别方案中可能遗漏的关键因素 | P1 |
| 可执行性评估 | 评估方案在实际产线上的可执行性 | P1 |

**能力群6：批判性反馈生成（Critical Feedback Generation）**

| 子能力 | 描述 | 优先级 |
|-------|------|-------|
| 结构化评审报告 | 生成包含问题-证据-建议的评审报告 | P0 |
| 风险等级标注 | 对每个发现的问题标注风险等级 | P0 |
| 改进建议提供 | 提供具体可行的改进建议 | P0 |
| 共识/分歧追踪 | 记录与其他Agent的分歧点及理由 | P1 |

> "Structured critique should produce a verdict of PASS or FAIL, a list of issues with severity levels and locations, concrete fix suggestions for each issue, and clarification questions when needed." [^288^]

#### 2.2 输入规范

蓝军SubAgent的输入应包括以下内容：

**必需输入（Required Inputs）**：

1. **待评审方案（Proposal）**：上游Agent（如工艺参数优化Agent、流程设计Agent）生成的完整方案
   - 格式：结构化文本 + 参数表格 + 推理过程
   - 包含：方案目标、推荐参数、推理依据、预期结果

2. **评审上下文（Review Context）**：
   - 原始工艺需求与约束条件
   - 晶圆规格（材料类型、关键尺寸要求、膜厚等）
   - 设备限制（设备型号、能力范围）

3. **评审指令（Review Directive）**：
   - 评审重点（如侧重逻辑检查、风险评估或完备性）
   - 评审深度（快速审查/详细审查）
   - 特殊关注事项

**可选输入（Optional Inputs）**：

4. **上游Agent推理链（Reasoning Chain）**：生成方案的完整推理过程，用于逻辑一致性检查
5. **历史评审记录（Historical Reviews）**：类似方案的过往评审结果，用于模式识别
6. **知识库查询结果（KB Query Results）**：与方案相关的工艺知识库条目

#### 2.3 输出规范

蓝军SubAgent的输出应采用结构化评审报告格式：

```json
{
  "review_id": "REV_001",
  "review_status": "NEEDS_REVISION", // APPROVED / NEEDS_REVISION / REJECTED
  "overall_assessment": {
    "score": 72, // 0-100
    "summary": "方案整体合理，但存在3个高风险问题需要修正",
    "confidence": "HIGH"
  },
  "findings": [
    {
      "finding_id": "F001",
      "category": "ASSUMPTION_VIOLATION",
      "severity": "HIGH", // CRITICAL / HIGH / MEDIUM / LOW
      "location": "Section 3.2 - Parameter Recommendation",
      "description": "推荐RF功率500W超出了设备的安全操作范围（上限400W）",
      "evidence": "设备规格书显示RF发生器最大额定功率为400W",
      "recommendation": "将RF功率调整至350-400W范围内，或更换设备型号",
      "rationale": "超过额定功率可能导致设备损坏和安全事故"
    }
  ],
  "risk_assessment": {
    "fmea_items": [
      {
        "failure_mode": "RF功率过高导致设备损坏",
        "severity": 9,
        "occurrence": 6,
        "detection": 4,
        "rpn": 216
      }
    ],
    "overall_risk_level": "HIGH"
  },
  "assumptions_checked": [
    {
      "assumption": "蚀刻选择比保持恒定",
      "valid": false,
      "reason": "选择比随RF功率变化而显著变化"
    }
  ],
  "metadata": {
    "reviewer_agent": "blue_team_critic",
    "review_time": "2025-01-15T10:30:00Z",
    "iterations": 2
  }
}
```

**输出字段说明**：

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| review_status | Enum | 是 | 整体评审结论 |
| overall_assessment.score | Integer | 是 | 综合评分（0-100） |
| findings | Array | 是 | 发现的问题列表 |
| findings[].category | Enum | 是 | 问题类别：LOGIC_ERROR/ASSUMPTION_VIOLATION/RISK/INCOMPLETENESS/FACTUAL_ERROR |
| findings[].severity | Enum | 是 | 严重级别 |
| risk_assessment | Object | 否 | FMEA风险评估结果 |
| assumptions_checked | Array | 是 | 假设验证结果 |

#### 2.4 工具与资源需求

**内部工具**：

1. **知识库查询工具**：访问半导体工艺知识库，验证参数范围和物理约束
2. **计算器**：执行数值验证和量纲检查
3. **FMEA模板引擎**：生成标准化的风险评估表格
4. **历史案例检索器**：查询类似方案的评审历史

**外部资源**：

1. **工艺参数数据库**：包含设备规格、材料特性、工艺窗口数据
2. **物理模型验证器**：用于验证物理计算的正确性
3. **行业标准库**：SEMI标准、JEDEC规范等

> "The framework incorporates the use of failure modes and effects analysis (FMEA) and fault tree analysis (FTA) for identifying potential failure points in the semiconductor manufacturing process." [^265^]

**模型配置建议**：

参考OpenCode的SubAgent配置模式，蓝军SubAgent应采用低temperature设置以确保批判的严谨性和一致性[^296^]：

```yaml
---
description: 蓝军批判性审查Agent - 负责审查蚀刻工艺方案的逻辑一致性、假设有效性和风险水平
mode: subagent
model: anthropic/claude-sonnet-4-20250514  # 或等效的高性能推理模型
temperature: 0.1  # 低temperature确保批判的严谨性和一致性
tools:
  write: false    # 蓝军只审查不修改
  edit: false
  kb_query: true  # 可查询知识库
  calculator: true # 数值验证工具
---
```

---

### 3. 与其他Agent的协作关系

#### 3.1 上游依赖

蓝军SubAgent依赖于以下Agent的输出作为审查对象：

| 上游Agent | 输入内容 | 审查重点 |
|----------|---------|---------|
| 工艺参数优化Agent | 优化的蚀刻参数组合 | 参数合理性、物理约束符合性、风险评估 |
| 流程设计Agent | 蚀刻工艺流程方案 | 逻辑一致性、步骤完备性、因果关系有效性 |
| 设备匹配Agent | 设备配置建议 | 设备能力匹配性、安全操作范围符合性 |
| 质量预测Agent | 预期质量指标 | 预测假设验证、指标可达性评估 |

**依赖模式**：
- 每个上游Agent完成方案生成后，自动触发蓝军SubAgent进行审查
- 蓝军接收方案 + 推理链 + 原始需求，执行多维度审查
- 审查结论决定方案是直接通过还是需要修订

#### 3.2 下游贡献

蓝军SubAgent的评审结果将传递至以下Agent或流程：

| 下游接收方 | 贡献内容 | 作用 |
|----------|---------|------|
| 方案修订循环 | 结构化评审报告 + 改进建议 | 驱动方案的迭代优化 |
| 主Agent（协调器） | 审查状态 + 关键风险警报 | 支持全局决策 |
| 知识库 | 审查发现 + 纠正记录 | 积累组织经验 |
| 人类操作员 | 高风险问题报告 | 需要人工干预时通知 |

**贡献模式**：
- 评审结果（APPROVED/NEEDS_REVISION/REJECTED）直接决定方案流向
- 高风险问题（CRITICAL/HIGH）自动上报主Agent
- 审查发现纳入知识库用于持续学习

#### 3.3 并行协作

**多Agent辩论与共识机制**

蓝军SubAgent可参与多Agent辩论架构，与其他专业Agent形成协作审查网络：

> "Multi-Agent Debate (MAD) is a collaborative framework in which multiple agents iteratively refine solutions through the generation of reasoning and alternating critique cycles." [^213^]

HCP-MAD框架提出的三阶段渐进推理机制为蓝军协作提供了参考[^213^]：
1. **异构共识验证（HCV）**：快速共识验证，使用两个异构Agent进行早期终止
2. **异构对偶辩论（HPAD）**：成对Agent相互批判，自适应终止
3. **升级集体投票（ECT）**： enlist额外Agent聚合多元视角

**辩论树架构**

在辩论树框架中，蓝军Agent可扮演以下角色之一[^278^]：
- **质疑者（Challenger）**：主动提出质疑，挑战方案的合理性
- **验证者（Verifier）**：验证关键声明的事实依据
- **风险评估者（Risk Assessor）**：系统评估方案的潜在风险

**迭代协作流程**

```
[方案Agent] → 生成初始方案
    ↓
[蓝军SubAgent] → 执行批判性审查
    ↓
[修订Agent] → 根据反馈修订方案（如需要）
    ↓
[蓝军SubAgent] → 重新审查修订版本
    ↓
[共识达成] → 批准或升级至人类审核
```

> "HCP-MAD employs a three-stage progressive reasoning mechanism to develop adaptive solutions across varying task complexities... simple tasks can be effectively resolved via lightweight pair-agent debates, while complex tasks require expanded collaboration." [^213^]

---

### 4. 触发条件

蓝军SubAgent的触发条件设计：

**自动触发条件**：

| 条件 | 描述 | 优先级 |
|------|------|-------|
| 方案生成完成 | 任一上游Agent完成方案生成后自动触发审查 | 默认 |
| 高风险操作检测 | 方案中包含超出安全范围的参数建议时 | 立即 |
| 方案修订提交 | 修订后的方案重新提交审查 | 高 |
| 多Agent意见分歧 | 不同Agent对方案产生分歧时启动辩论模式 | 中 |

**手动触发条件**：

| 条件 | 描述 | 场景 |
|------|------|------|
| 人类操作员请求审查 | 操作员手动请求对特定方案进行审查 | 怀疑方案质量时 |
| 定期审查任务 | 按预定周期审查已批准方案的有效性 | 工艺变更后 |

**审查深度决策逻辑**：

```
if (方案复杂度 == 高 或 风险等级 == 高):
    审查深度 = "详细审查"（全维度）
elif (方案复杂度 == 中):
    审查深度 = "标准审查"（核心维度）
else:
    审查深度 = "快速审查"（关键风险检查）
```

**终止条件**：

1. 审查通过（APPROVED）：未发现严重问题或所有问题已解决
2. 最大迭代次数达到：默认最多3轮审查-修订循环
3. 人类干预：高风险问题需要人类决策
4. 质量阈值满足：综合评分达到预设阈值（如≥80分）

> "A key innovation involves prompting LLMs in a way that structures their reasoning process by decomposing complex fact-checking tasks into smaller, verifiable steps. The underlying idea is that human fact-checkers often break down a claim into sub-claims or evidence checks." [^216^]

---

### 5. 关键证据与引用

#### 5.1 Red Team/Blue Team方法论核心来源

| 引用编号 | 来源 | 核心发现 |
|----------|------|---------|
| [^263^] | Wiz Academy | 红队/蓝队角色定义、核心差异对比表 |
| [^269^] | PurpleSec | 蓝队风险评估方法论、成本效益分析 |
| [^272^] | Coursera/NIST | NIST对红队的官方定义 |
| [^274^] | Iterasec | Purple Team协作改进模式 |
| [^260^] | Microsoft Azure | AI Red Teaming Agent的ASR指标 |
| [^264^] | 腾讯云安全 | 大模型安全Red Team对抗机制实践 |

#### 5.2 批判性审查Agent设计模式来源

| 引用编号 | 来源 | 核心发现 |
|----------|------|---------|
| [^261^] | 博客园 | 多Agent协作模式概述，Critic-Reviewer模式定义 |
| [^271^] | Panaversity | 迭代精炼模式的Generator→Critic循环 |
| [^294^] | OpenCode/CSDN | OpenCode SubAgent配置模式（code-reviewer示例） |
| [^296^] | OpenCode官方 | Agent配置JSON/Markdown格式规范 |
| [^295^] | 腾讯云 | AI Agent反思模式（双Agent协作实现） |
| [^278^] | CSDN | Multi-Agent辩论树架构（Paper Agent/Moderator Agent） |

#### 5.3 反射与自批判模式来源

| 引用编号 | 来源 | 核心发现 |
|----------|------|---------|
| [^284^] | LearnAgenticPatterns | Reflection Pattern三段式：Generate→Evaluate→Revise |
| [^286^] | Antigravity Lab | 四种Self-Critique架构及生产实践建议 |
| [^288^] | Arun Baby | Draft-Critique-Revise-Freeze模式及停止条件 |
| [^289^] | Oxagen | 三种反射架构的性能分析与token成本分析 |
| [^290^] | Zylos Research | 多Agent辩论、工具辅助验证等实现模式 |
| [^292^] | Tungsten Automation | 企业级Reflection Pattern实现及Self-RAG |

#### 5.4 多Agent辩论与共识来源

| 引用编号 | 来源 | 核心发现 |
|----------|------|---------|
| [^213^] | arXiv (HCP-MAD) | 异构共识渐进推理的三阶段机制 |
| [^215^] | arXiv | HCP-MAD的实验验证：准确率提升与token成本降低 |
| [^282^] | arXiv (HAAF) | 红队探测→蓝队加固→重新评估的迭代循环 |
| [^283^] | arXiv (BlueCodeAgent) | 蓝队Agent的自动红队测试赋能机制 |

#### 5.5 FMEA与半导体工艺评审来源

| 引用编号 | 来源 | 核心发现 |
|----------|------|---------|
| [^265^] | HAL科学文献 | 半导体制造安全框架：FMEA+FTA整合 |
| [^267^] | IJRPR期刊 | 等离子体蚀刻设备FMEA应用、RPN计算、Pareto分析 |
| [^277^] | FasterCapital | FMEA在半导体QC中的角色、SPC/AOI/Cleanroom标准 |
| [^280^] | Springer (DMAIC) | DMAIC+FMEA在蚀刻阶段的实际应用与良率改善 |
| [^321^] | Eureka/PatSnap | SEMI/IEC/JEDEC等半导体工业标准体系 |

#### 5.6 AI幻觉检测与事实核查来源

| 引用编号 | 来源 | 核心发现 |
|----------|------|---------|
| [^212^] | arXiv (Hallucination Inspector) | 基于AST的API幻觉检测、两层分类体系 |
| [^214^] | arXiv | Hallucination Inspector在Android API迁移中的评估 |
| [^216^] | arXiv (Hallucination to Truth综述) | 事实核查框架全景：MiniCheck/CliniFact/HiSS等 |

#### 5.7 NIST与AI红队框架来源

| 引用编号 | 来源 | 核心发现 |
|----------|------|---------|
| [^312^] | Logicalis | NIST AI RMF的红队测试要求、三大测试领域 |
| [^313^] | Cloud Security Alliance | NIST AI Agent安全红队指南（AgentDojo框架） |
| [^314^] | Let's Ask Claire | NIST AI RMF GOVERN 1.7/MITRE ATLAS合规框架 |
| [^315^] | SentinelOne | AI红队核心组件：攻击面映射、多学科团队 |
| [^318^] | Techno Guide | NIST红队报告的五大关键发现 |
| [^322^] | IJAIBDCMS (COMPASS-RT) | 六柱AI红队框架：范围→威胁建模→混合测试→基准验证→治理→持续验证 |

#### 5.8 关键原始摘录汇总

**关于蓝队角色的本质**：
> "Blue teams are defensive security specialists who protect your organization's systems, detect threats, and respond to incidents." [^263^]

**关于批判的价值**：
> "This pattern for code generation, research writing, logic checking and ensuring ethical consistency is particularly effective. This approach's advantages include enhanced robustness, improved quality, and reduced likelihood of hallucinations or errors." [^261^]

**关于迭代优化的必要性**：
> "The Trustworthy Optimization Factory: red-team probing exposes vulnerability surfaces, blue-team hardening designs targeted interventions, and re-evaluation verifies improvement, cycling until the deployed system meets deployment-readiness thresholds." [^282^]

**关于FMEA的实践价值**：
> "FMEA enables fabs to prioritize corrective actions and develop targeted maintenance plans. Incorporating these tools into fab-wide reliability programs enhances decision-making and ensures systematic reduction in tool variability and unplanned downtime." [^267^]

**关于结构化批判的要求**：
> "Structured critique should produce a verdict of PASS or FAIL, a list of issues with severity levels and locations, concrete fix suggestions for each issue, and clarification questions when needed." [^288^]

---

### 附录：蓝军SubAgent设计速查表

| 设计要素 | 建议 |
|---------|------|
| **角色定位** | 防御性审查者、质量守门人 |
| **核心使命** | 识别方案中的逻辑缺陷、假设偏差、风险盲点 |
| **工作模式** | Critic-Reviewer模式：审查→反馈→不直接修改 |
| **协作模式** | Purple Team式协作：批判是为了改进而非否定 |
| **审查维度** | 逻辑一致性、假设有效性、风险评估、事实核查、完备性 |
| **评估框架** | FMEA（S×O×D=RPN）+ 结构化评分 |
| **迭代机制** | 最多3轮审查-修订循环，质量阈值触发终止 |
| **输出格式** | JSON结构化评审报告（状态+评分+发现+建议） |
| **触发条件** | 方案生成后自动触发、高风险操作立即触发 |
| **模型配置** | 高性能推理模型 + temperature=0.1 + 只读工具权限 |
| **特殊要求** | 不生成方案只审查方案、提供证据支持的反馈 |
