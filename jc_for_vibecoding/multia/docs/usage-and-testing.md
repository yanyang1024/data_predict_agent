# 半导体蚀刻多智能体系统 — 使用与测试文档

> **适用版本**: OpenCode 1.15.10+
> **最后更新**: 2026年6月

---

## 目录

1. [快速配置指南](#1-快速配置指南)
2. [调试方法](#2-调试方法)
3. [逐 Subagent 测试方案](#3-逐-subagent-测试方案)
   - 3.1 etch-orchestrator
   - 3.2 etch-mechanism
   - 3.3 etch-literature
   - 3.4 etch-data
   - 3.5 etch-doe
   - 3.6 etch-blue-team
   - 3.7 etch-triz
   - 3.8 etch-summary
4. [集成测试](#4-集成测试)
5. [常见问题排查](#5-常见问题排查)

---

## 1. 快速配置指南

### 1.1 环境要求

| 要求 | 说明 |
|------|------|
| OpenCode 版本 | ≥ 1.15.10（Tool + Subagent 完整支持） |
| 插件依赖 | `@opencode-ai/plugin`（TS Tool 开发所需） |
| 网络要求 | 文献 API(32300) 和数据 API(5314/5315) 需可访问 |
| Node/Bun | 运行 TS Tool 所需运行时 |

### 1.2 目录验证

确认以下文件和目录全部到位：

```bash
# 验证 Subagent 文件（应看到 8 个 .md）
ls -la .opencode/agent/

# 验证 Tool 文件（应看到 7 个 .ts）
ls -la .opencode/tools/

# 验证 Skill 文件
ls -la .opencode/skill/

# 验证主配置
cat opencode.json
```

### 1.3 配置检查清单

- [ ] `.opencode/agent/etch-orchestrator.md` 存在
- [ ] `.opencode/agent/etch-mechanism.md` 存在
- [ ] `.opencode/agent/etch-literature.md` 存在
- [ ] `.opencode/agent/etch-data.md` 存在
- [ ] `.opencode/agent/etch-doe.md` 存在
- [ ] `.opencode/agent/etch-blue-team.md` 存在
- [ ] `.opencode/agent/etch-triz.md` 存在
- [ ] `.opencode/agent/etch-summary.md` 存在
- [ ] `.opencode/tools/literature-api.ts` 存在
- [ ] `.opencode/tools/data-load.ts` 存在
- [ ] `.opencode/tools/data-analyze.ts` 存在
- [ ] `.opencode/tools/data-optimize.ts` 存在
- [ ] `.opencode/tools/data-predict.ts` 存在
- [ ] `.opencode/tools/mechanism-placeholder.ts` 存在
- [ ] `.opencode/tools/triz-reference.ts` 存在
- [ ] `.opencode/skill/etch-engineer.md` 存在
- [ ] `opencode.json` JSON 语法正确

### 1.4 加载 Skill

在 OpenCode 对话中使用 Skill 工具加载蚀刻多智能体技能：

```
skill → 选择 etch-engineer
```

加载后可以看到可用 Subagent 列表。主入口为 `@etch-orchestrator`。

### 1.5 子智能体调用方式

| 方式 | 命令示例 | 适用场景 |
|------|---------|---------|
| 完整流程 | `@etch-orchestrator <蚀刻问题>` | 需要全部分析维度的综合问题 |
| 单独调用 | `@etch-literature <问题>` | 只咨询某个专家 |
| 跳过部分 | `@etch-orchestrator 只看机理和数据，不需要文献` | 指定部分专家 |

---

## 2. 调试方法

### 2.1 检查 Subagent 注册

在对话中输入 `@etch-` 看 Tab 补全是否出列表。

> 注意：所有 Subagent 在 `opencode.json` 中设为 `hidden: true`，因此不会出现在 `@` 补全菜单中。但 `@etch-orchestrator` 仍可直接输入使用。如需显示，修改 `opencode.json` 中 `hidden` 为 `false`。

### 2.2 检查 Tool 是否加载

在主对话中直接要求调用某个工具：

```
请调用 literature-api 工具检索"SiO2刻蚀"
```

如果工具加载成功，OpenCode 会触发工具调用并返回结果。如果返回 "unknown tool" 错误：

```bash
# 检查文件是否存在且命名正确
ls -la .opencode/tools/literature-api.ts
```

### 2.3 API 连通性测试

#### 文献 API (10.18.220.244:32300)

```bash
# 测试创建对话
curl -X POST http://10.18.220.244:32300/create_conversation \
  -H "Content-Type: application/json" \
  -d '{"knowledge_base_name":"半导体蚀刻","query":"test"}'
```

**预期成功输出**:
```json
{"conversation_id": "xxx"}
```

**预期失败输出**:
```
curl: (7) Failed to connect to 10.18.220.244 port 32300: Connection refused
```

#### 数据 API (10.20.52.249:5314)

```bash
# 测试数据加载
curl -X POST http://10.20.52.249:5314/data/load \
  -H "Content-Type: application/json" \
  -d '{"layer_type":"LCH"}'
```

#### 数据优化 API (10.20.52.249:5315)

```bash
# 测试优化
curl -X POST http://10.20.52.249:5315/data/optimize \
  -H "Content-Type: application/json" \
  -d '{"layer_type":"LCH","constraints":{"biasCD":{"max":10}}}'
```

### 2.4 查看 Subagent 运行时行为

- 观察 OpenCode 的 tool call 日志（对话框内可以看到 Tool 调用记录）
- 观察 `task()` 调用的返回结果
- 检查 Subagent 的 `maxSteps` 是否有耗尽

---

## 3. 逐 Subagent 测试方案

---

### 3.1 etch-orchestrator（主控编排）

| 属性 | 值 |
|------|-----|
| 实现形态 | Independent（纯编排指令） |
| 依赖 tools | 无 |
| 依赖 APIs | 无 |
| 依赖其他 agent | 全部 7 个 Subagent |

#### TC-ORC-01: 完整全流程

**目的**: 验证 Orchestrator 能按 Supervisor 模式正确完成"并行分析→按需串行→综合汇总"的全流程

**测试 Prompt**:
```
@etch-orchestrator 当前蚀刻工艺Bias CD偏大，层类型LCH，
刻蚀气体C4F8/CF4/Ar，源功率600W，偏压功率150W，气压30mTorr。
请分析原因并给出优化建议
```

**预期行为**:
1. Orchestrator 并行调用 mechanism + literature + data
2. 等待全部返回后，检查结果
3. data 有优化结果 → 调 blue-team 审查
4. 最终调 summary 整合

**验证步骤**:
- [ ] Mechanism 被调用（输出定性分析）
- [ ] Literature 被调用（输出文献检索结果，或 API unavailable 提示）
- [ ] Data 被调用（输出加载+分析+优化结果，或 API unavailable 提示）
- [ ] Summary 被调用（输出综合决策报告）
- [ ] Blue-team 被调用（如果 data 有推荐结果）
- [ ] 最终输出包含完整的 5 个部分（问题摘要/各专家结论/共识分歧/行动方案/风险评估）

---

#### TC-ORC-02: 指定跳过部分 Subagent

**目的**: 验证 Orchestrator 能根据用户指令跳过特定专家

**测试 Prompt**:
```
@etch-orchestrator 我只想看机理分析和数据优化，不需要文献和TRIZ。
层类型MCH，偏压功率偏高导致损伤
```

**预期行为**:
- 只调用 mechanism + data + blue-team（data 有结果时）
- 跳过 literature 和 triz
- Summary 只整合实际调用的 agent 输出

**验证步骤**:
- [ ] Literature 未被调用
- [ ] TRIZ 未被调用
- [ ] 输出中不包含文献/TRIZ 相关章节

---

#### TC-ORC-03: 全部 API 不可用

**目的**: 验证系统在无外部 API 时的降级能力

**测试条件**: 预先确认 literature API 和 data API 不可用

**测试 Prompt**:
```
@etch-orchestrator 请分析 LCH 层的 Bias CD 问题
```

**预期行为**:
- Mechanism 正常输出（本地理论分析）
- Literature 返回 API unavailable 提示
- Data 返回 API unavailable 提示
- Summary 在报告中标注"文献和数据分析当前不可用"
- 最终输出仍然有可用的定性分析和建议

**验证步骤**:
- [ ] 即使 API 不可用，系统仍有完整输出结构
- [ ] 报告中标注了信息来源的局限性

---

#### TC-ORC-04: 单个 Subagent 超时/失败

**目的**: 验证一个 Subagent 失败不影响其他并行的 Subagent

由于 OpenCode `task()` 超时机制由平台控制，本测试验证调用模式正确性：

- 确认 Orchestrator 使用 `await Promise.all()` 并行启动三个分析 agent
- 确认单个 agent 失败时，其他 agent 的结果仍被保留
- 确认 Summary 会标注"某个专家未能返回结果"

---

### 3.2 etch-mechanism（机理模型）

| 属性 | 值 |
|------|-----|
| 实现形态 | Independent（理论驱动，无仿真后端） |
| 依赖 tools | 无（mechanism-placeholder.ts 为可选补充） |
| 依赖 APIs | 无 |
| 依赖其他 agent | 无 |

#### TC-MEC-01: 标准 RCP 参数输入

**目的**: 验证机理模型能正确输出定性分析

**测试 Prompt**:
```
@etch-mechanism 请分析以下RCP参数：
CF4: 100sccm, CHF3: 20sccm, Ar: 200sccm,
源功率: 500W, 偏压功率: 100W, 气压: 30mTorr, 温度: 20°C
```

**预期输出结构**:
```
## Qualitative Analysis

### Expected Parameter Effects
| Parameter | Value | Expected Impact | Confidence |
|-----------|-------|-----------------|------------|
| CF4       | 100   | ...             | ...        |

### Process Window Analysis
- ...
### Potential Root Causes
- ...

### ⚠️ Disclaimer
...
```

**验证步骤**:
- [ ] 输出包含参数影响表（每个参数对应一行）
- [ ] 输出包含工艺窗口分析
- [ ] 输出包含免责声明
- [ ] 分析在物理上合理（例如高功率 → 选择比下降）

---

#### TC-MEC-02: 带问题描述的输入

**目的**: 验证机理模型能根据具体问题提供根因推断

**测试 Prompt**:
```
@etch-mechanism 当前刻蚀速率太慢，Bias CD偏大。
RCP参数：C4F8: 80sccm, CF4: 120sccm, Ar: 150sccm,
源功率: 400W, 偏压功率: 80W, 气压: 50mTorr
请分析原因
```

**预期输出**:
- 针对"刻蚀速率慢"的根因推断（如功率偏低、气压偏高）
- 针对"Bias CD偏大"的根因推断（如聚合物过多、离子方向性不足）
- 每项根因都基于物理/化学原理

**验证步骤**:
- [ ] 输出了刻蚀速率慢的可能原因
- [ ] 输出了 Bias CD 偏大的可能原因
- [ ] 各原因与输入参数直接关联

---

#### TC-MEC-03: 异常参数输入

**目的**: 验证错误处理

**测试 Prompt**:
```
@etch-mechanism 分析参数：abc: 123, xyz: 456
```

**预期行为**: 输出仍然包含基本结构，但会提示参数名非标准，置信度降低

---

### 3.3 etch-literature（文献检索）

| 属性 | 值 |
|------|-----|
| 实现形态 | API 实装 |
| 依赖 tools | `literature-api.ts` |
| 依赖 APIs | `10.18.220.244:32300` |
| 依赖其他 agent | 无 |

#### TC-LIT-01: API 正常 — 完整流程

**目的**: 验证文献检索的完整工作流：create_conversation → chat_query → wait → get_message_info

**测试条件**: API 10.18.220.244:32300 可访问

**测试 Prompt**:
```
@etch-literature 请检索高选择比SiO2刻蚀的相关文献和方法
```

**预期行为**:
1. 调用 `literature-api` 工具，传入 query
2. 工具内部完成完整 API 工作流
3. 返回回答内容 + 引用文档列表

**验证步骤**:
- [ ] literature-api 工具被调用
- [ ] 返回结果包含 answer 字段
- [ ] 返回结果包含 references 数组
- [ ] 每个 reference 包含 document、snippet、link
- [ ] Subagent 对检索结果做了跨场景类比分析

---

#### TC-LIT-02: API 不可用 — Fallback 测试

**目的**: 验证 API 不可用时的降级行为

**测试条件**: API 10.18.220.244:32300 不可访问

**测试 Prompt**:
```
@etch-literature 请检索高选择比SiO2刻蚀的相关文献
```

**预期行为**:
1. `literature-api` 工具返回 `status: "unavailable"`
2. Subagent 检测到 API 不可用，明确告知用户
3. Subagent 基于自身知识提供基本分析

**验证步骤**:
- [ ] 输出包含"API当前不可用"的提示
- [ ] 不抛出未处理的错误
- [ ] 用户得到有意义的回应（不是空输出）

---

#### TC-LIT-03: 复杂蚀刻问题

**目的**: 验证对复杂多维度问题的处理能力

**测试 Prompt**:
```
@etch-literature 在SiO2刻蚀中，如何在保持高选择比的同时提高刻蚀速率？
类似场景的文献中常用的方法有哪些？
```

**预期输出**:
- 搜索到相关文献（或 API 不可用提示）
- 分析了文献中提到的平衡选择比和刻蚀速率的方法
- 标注了引用来源
- 包含了数据污染评估

**验证步骤**:
- [ ] 输出包含具体的方法论建议
- [ ] 引用格式正确（文档名 + 片段 + 链接）
- [ ] 数据污染评估部分存在

---

### 3.4 etch-data（数据挖掘）

| 属性 | 值 |
|------|-----|
| 实现形态 | API 实装 |
| 依赖 tools | `data-load.ts`, `data-analyze.ts`, `data-optimize.ts`, `data-predict.ts` |
| 依赖 APIs | `10.20.52.249:5314`, `10.20.52.249:5315` |
| 依赖其他 agent | 无 |

#### 3.4.1 data-load 测试

##### TC-DAT-LD-01: 正常加载

**测试 Prompt**:
```
@etch-data 请加载 LCH 层的历史数据
```

**预期行为**:
1. 调用 `data-load` 工具
2. 返回数据质量报告

**验证步骤**:
- [ ] 输出包含 sampleCount（样本数）
- [ ] 输出包含 featureCount（特征数）
- [ ] 输出包含 pcaDimensions（PCA 维数）
- [ ] 输出包含 excludedFeatures（排除特征列表）
- [ ] 有数据质量 summary

---

##### TC-DAT-LD-02: 无效 layerType

**测试 Prompt**:
```
请调用 data-load 工具，layerType 设为 "INVALID"
```

**预期行为**: 工具返回 error 状态，Subagent 能正确处理

---

#### 3.4.2 data-analyze 测试

##### TC-DAT-AN-01: 模型对比

**测试 Prompt**:
```
@etch-data 请分析 LCH 层的数据，评估各模型的R²表现
```

**预期行为**:
1. 先调 data-load 了解数据
2. 调 data-analyze 对比模型

**验证步骤**:
- [ ] 输出了 6 种模型的 R² 对比
- [ ] 标注了最优模型
- [ ] 给出了模型可信度评估（高/中/低）
- [ ] R² > 0.8 标注为"高"可信度

---

#### 3.4.3 data-optimize 测试

##### TC-DAT-OP-01: 有可行解

**测试 Prompt**:
```
@etch-data 请对LCH层进行多目标优化，约束条件：
Bias CD < 10nm, Bottom CD 90-110nm, Max CD < 120nm
```

**预期行为**:
1. 调 data-load 了解数据
2. 调 data-analyze 评估模型
3. 调 data-optimize 做优化
4. 返回推荐参数 + 历史对比

**验证步骤**:
- [ ] 输出推荐参数组合
- [ ] 每个参数标注 BETTER/WORSE/PASS/FAIL 对比历史
- [ ] 输出 Top N 候选方案
- [ ] 标注是否找到可行解

---

##### TC-DAT-OP-02: 无可行解

通过设置极其严格的约束来触发：

**测试条件**: 设置不可能满足的约束（如 Bias CD < 0.1nm）

**预期行为**: 工具返回 `hasFeasibleSolution: false`，并返回违反约束最少的方案

**验证步骤**:
- [ ] 明确提示"无完全可行解"
- [ ] 给出违反约束最少的候选方案
- [ ] 列出违反的具体约束

---

##### TC-DAT-OP-03: 约束 JSON 格式错误

**测试 Prompt**:
```
@etch-data 请做优化，约束条件：abc
```

**预期行为**: `data-optimize` 工具返回 JSON 解析错误，Subagent 提示用户修正

---

#### 3.4.4 data-predict 测试

##### TC-DAT-PR-01: 有效部分参数

**测试 Prompt**:
```
@etch-data 请预测：如果 C4F8 流量设为 80sccm，源功率设为 600W，
其他参数保持默认，LCH 层的结果会怎样？
```

**预期行为**:
1. 调 data-predict 工具
2. 返回预测的完整参数组合和性能指标

**验证步骤**:
- [ ] 输出预测的完整参数
- [ ] 输出预测的性能指标
- [ ] 输出置信度

---

##### TC-DAT-PR-02: 空参数

**测试 Prompt**: 尝试调用 data-predict 但不提供参数

**预期行为**: 工具返回"请至少指定一个参数"错误

---

#### 3.4.5 data API 不可用时整体测试

##### TC-DAT-ALL-01: API Unavailable

**测试条件**: API 10.20.52.249:5314/5315 不可访问

**测试 Prompt**:
```
@etch-data 请分析 LCH 层数据并给出优化建议
```

**预期行为**: 每个 tool 调用都返回 `status: "unavailable"`，Subagent 明确告知用户

**验证步骤**:
- [ ] 输出包含"数据API当前不可用"提示
- [ ] 不抛出未处理错误
- [ ] 给出后续操作建议

---

### 3.5 etch-doe（实验设计）

| 属性 | 值 |
|------|-----|
| 实现形态 | Skill 封装 |
| 依赖 tools | `skill`（内置工具，加载 DOE Skill） |
| 依赖 APIs | 无 |
| 依赖其他 agent | 无 |

#### TC-DOE-01: Skill 加载

**目的**: 验证 DOE Subagent 能成功加载 Skill

**测试 Prompt**:
```
@etch-doe 我需要设计一个实验来优化蚀刻速率
```

**预期行为**:
1. Subagent 激活
2. 开始引导对话，询问实验目标、因子、水平
3. 输出设计推荐

**验证步骤**:
- [ ] Subagent 开始引导对话
- [ ] 询问了实验目标
- [ ] 询问了可控因子和范围
- [ ] 询问了响应变量
- [ ] 推荐了合适的设计类型

---

#### TC-DOE-02: 完整实验流程

**目的**: 验证从问题到报告的完整流程

**测试 Prompt**:
```
@etch-doe 我想做一个3因子2水平的全因子实验，
因子A是气压(20-80mTorr)，B是源功率(300-700W)，C是C4F8流量(50-150sccm)，
响应变量是刻蚀速率和选择比，最多做12次实验
```

**预期对话流程**:
1. Subagent 确认因子和水平
2. 推荐设计类型（此处应为 Full Factorial 或 Fractional Factorial）
3. 生成编码矩阵（±1），随机化运行顺序
4. 用户输入实验结果后 → 进行统计分析
5. 输出 HTML 报告

**验证步骤**:
- [ ] 推荐了正确的设计类型
- [ ] 生成了编码矩阵
- [ ] 说明了因子名到 RCP 参数的映射
- [ ] 统计分析包含主效应、交互效应、ANOVA

---

#### TC-DOE-03: 用户提供不完整信息

**目的**: 验证 Subagent 能主动追问缺失信息

**测试 Prompt**:
```
@etch-doe 我要做个实验
```

**预期行为**: Subagent 开始引导对话，逐步询问：
1. 实验目标是什么？
2. 有几个因子？分别是什么？
3. 水平范围是多少？
4. 响应变量是什么？
5. 能做多少次实验？

**验证步骤**:
- [ ] 输出了一系列追问问题
- [ ] 不因信息不足而报错或卡住

---

### 3.6 etch-blue-team（蓝军审查）

| 属性 | 值 |
|------|-----|
| 实现形态 | Independent（纯 LLM 对抗性评估） |
| 依赖 tools | 无 |
| 依赖 APIs | 无 |
| 依赖其他 agent | 无 |

#### TC-BLU-01: 审查标准输出

**目的**: 验证蓝军按正确格式输出审查报告

**测试 Prompt**:
```
@etch-blue-team 请审查以下机理模型的分析结果：

问题：Bias CD偏大
分析：偏压功率与气压比例不合适，建议将气压从30mTorr降至20mTorr
以改善离子方向性；同时将C4F8流量从80降至60sccm以减少聚合物沉积。

请问这份分析有什么潜在问题？
```

**预期输出结构**:
```
## Blue Team Review

### Summary Assessment
...

### Critical Risks
...

### Moderate Concerns
...

### Minor Observations
...

### Recommendations
...
```

**验证步骤**:
- [ ] 输出了 Summary Assessment
- [ ] 输出了至少一个 Critical Risk 或 Moderate Concern
- [ ] 每个问题都标注了严重程度
- [ ] 给出了具体建议

---

#### TC-BLU-02: 审查有明显缺陷的分析

**目的**: 验证蓝军能识别逻辑问题和假设漏洞

**测试 Prompt**:
```
@etch-blue-team 请审查以下数据优化建议：

推荐参数：源功率800W，偏压功率200W，气压10mTorr
预期效果：刻蚀速率提升50%，选择比不变
数据来源：基于LCH层历史数据的NSGA-II优化，R²=0.95

这份建议有什么问题？
```

**预期行为**: 蓝军应能识别：
- 800W 功率是否超出硬件限制（设备能力假设）
- R²=0.95 可能是过拟合信号
- "选择比不变"的结论需要更多验证
- 样本代表性（训练数据是否覆盖了10mTorr条件）

**验证步骤**:
- [ ] 识别了潜在的硬件限制问题
- [ ] 对高 R² 提出过拟合风险
- [ ] 质疑了数据的样本代表性

---

#### TC-BLU-03: 审查空输入

**目的**: 验证对模糊/信息不足输入的合理处理

**测试 Prompt**:
```
@etch-blue-team 请审查以下结论：建议优化工艺参数
```

**预期行为**: 蓝军应指出信息不足，要求提供更多上下文

---

### 3.7 etch-triz（TRIZ 创新方法）

| 属性 | 值 |
|------|-----|
| 实现形态 | Independent + 本地 Tool |
| 依赖 tools | `triz-reference.ts` |
| 依赖 APIs | 无 |
| 依赖其他 agent | 无 |

#### TC-TRIZ-01: 标准矛盾输入

**目的**: 验证 TRIZ 对经典工艺矛盾的正确处理

**测试 Prompt**:
```
@etch-triz 在SiO2刻蚀中，我需要提高刻蚀速率，
但这会导致选择比下降。请用TRIZ方法解决这个矛盾
```

**预期行为**:
1. 识别矛盾：提高速率(生产率/速度) ↔ 选择比下降(有害副作用/物质损失)
2. 调用 `triz-reference` 查询矛盾矩阵
3. 返回推荐的发明原理
4. 将原理映射到蚀刻场景

**验证步骤**:
- [ ] tris-reference 工具被调用
- [ ] 输出了 TRIZ 参数抽象（改善/恶化参数）
- [ ] 输出了推荐的发明原理列表
- [ ] 每个原理都有蚀刻场景的应用建议

---

#### TC-TRIZ-02: 复杂矛盾描述

**目的**: 验证对自然语言描述的自动抽象能力

**测试 Prompt**:
```
@etch-triz 我遇到的问题是：增加偏压功率能改善刻蚀轮廓的方向性，
但会加重对衬底表面的离子损伤。怎么解决这个两难问题？
```

**预期行为**:
- 正确抽象为：改善形状 ↔ 增加有害副作用
- 或：提高功率 ↔ 增加损伤
- 查询矛盾矩阵
- 得到推荐原理并映射

**验证步骤**:
- [ ] 正确识别矛盾的双方
- [ ] TRIZ 抽象合理
- [ ] 蚀刻应用建议具体可行

---

#### TC-TRIZ-03: triz-reference 工具单独测试

**目的**: 验证工具内部矛盾矩阵查询正确性

**测试 Prompt**:
```
请调用 triz-reference 工具，矛盾描述为"刻蚀速率 vs 选择比"
```

**预期行为**: 返回的矛盾抽象应为改善生产率(39) ↔ 恶化有害副作用(31) 或其他合理映射

**验证步骤**:
- [ ] 返回了 contradiction 映射结果
- [ ] 返回了对应的发明原理 ID 和名称
- [ ] 返回了蚀刻应用建议

---

#### TC-TRIZ-04: 非典型蚀刻问题

**目的**: 验证对非标准问题的处理能力

**测试 Prompt**:
```
@etch-triz 我们的刻蚀机台产能不够，
但加快刻蚀速率会影响均匀性，怎么办？
```

**预期行为**: 正确抽象为生产率 vs 均匀性的矛盾

---

### 3.8 etch-summary（综合总结）

| 属性 | 值 |
|------|-----|
| 实现形态 | Independent（信息整合） |
| 依赖 tools | 无 |
| 依赖 APIs | 无 |
| 依赖其他 agent | 需要其他 agent 的输出作为上下文 |

#### TC-SUM-01: 整合单次分析结果

**目的**: 验证 Summary 能结构化整合单来源信息

**测试 Prompt**:
```
@etch-summary 请整合以下机理模型的分析结果：

机理模型分析：
Bias CD偏大可能原因：
1. 偏压功率与气压比例不合适（当前偏压150W/气压30mTorr）
2. 聚合物沉积不足（C4F8流量80sccm偏低）
建议：将气压降至20mTorr，C4F8增至100sccm
```

**预期输出结构**:
```
## Etch Process Optimization Decision Report

### Problem Summary
...

### Key Findings
...

### Recommended Action Plan
...

### Next Steps
...
```

**验证步骤**:
- [ ] 输出包含完整报告头部（Problem Summary / Key Findings / Action Plan）
- [ ] 信息被结构化重述而非原文照搬
- [ ] 给出了明确的行动建议

---

#### TC-SUM-02: 整合多来源含冲突观点

**目的**: 验证 Summary 能处理和标注不同 agent 间的意见分歧

**测试 Prompt**:
```
@etch-summary 请整合以下两个专家的分析：

机理模型：增加偏压功率到200W可改善轮廓，但会增加离子损伤风险
数据优化：推荐偏压功率220W，R²=0.92，置信度高

蓝军审查：数据优化可能存在过拟合，建议先在中等功率(180W)验证
```

**预期行为**:
- 识别出机理和数据在偏压功率方向上的共识（增加）
- 识别出蓝军对过拟合风险的质疑
- 在报告中同时列出共识和分歧
- 给出权衡后的行动建议

**验证步骤**:
- [ ] 输出了 Consensus Points 部分
- [ ] 输出了 Points of Contention 部分
- [ ] 每个分歧都有 Resolution Path
- [ ] 行动建议考虑了多方意见

---

#### TC-SUM-03: 报告格式完整性

**目的**: 验证报告包含所有必要字段

**测试 Prompt**:
```
@etch-summary 请整合以下信息：

机理模型：气压偏高可能导致各向同性刻蚀
数据优化：推荐气压25mTorr（历史最优），BETTER
蓝军：25mTorr在历史数据中表现好，但需确认设备状态是否一致
TRIZ：建议用脉冲刻蚀技术（周期性动作原理）来改善
```

**预期输出字段检查清单**:
- [ ] Problem Summary
- [ ] Key Findings (含 Consensus Points 和 Points of Contention)
- [ ] Risks & Mitigations
- [ ] Recommended Action Plan（分 Immediate / Short-term / Long-term）
- [ ] Next Steps

---

## 4. 集成测试

### 4.1 全链路端到端测试

**测试 Prompt**:
```
@etch-orchestrator 当前工艺：LCH层刻蚀，Bias CD偏大（目标<10nm，当前12nm），
刻蚀气体C4F8/CF4/Ar = 80/100/200sccm，源功率600W，偏压功率150W，气压30mTorr。
请分析原因、检索类似案例、做数据优化，给出综合建议
```

**检查清单**:
- [ ] **Phase 1 并行**:
  - [ ] Mechanism 被调用并输出定性分析
  - [ ] Literature 被调用（或提示 API 不可用）
  - [ ] Data 被调用（load + analyze + optimize）
- [ ] **Phase 2 按需**:
  - [ ] Data 有结果 → Blue-team 被调用
  - [ ] 用户未要求跳过其他 agent
- [ ] **Phase 3 整合**:
  - [ ] Summary 被调用
  - [ ] 输出了完整的结构化报告
- [ ] 全部步骤在合理时间内完成

---

### 4.2 降级与容错测试

**测试 4.2.1: 网络断开**
1. 断开网络
2. 执行 `@etch-orchestrator` 完整问题
3. 验证：
   - [ ] Literature 工具返回 `unavailable` → Subagent 降级
   - [ ] Data 工具返回 `unavailable` → Subagent 降级
   - [ ] Mechanism 正常运行（无需网络）
   - [ ] Summary 标注了信息来源受限

**测试 4.2.2: 单个 Subagent 文件缺失**
1. 临时移走一个 `.md` 文件（如 `etch-mechanism.md`）
2. 执行 `@etch-orchestrator` 问题
3. 验证：Orchestrator 是否能检测到缺失并继续

---

### 4.3 权限隔离测试

**测试 4.3.1: 非 Orchestrator 不能调 Task**

在非 orchestrator Subagent 的权限配置中，`task` 工具为不可用状态（未在 tools 中声明）。验证：

- [ ] `etch-blue-team` 尝试 `task()` 时应该失败
- [ ] `etch-mechanism` 不能创建其他 subagent

**测试 4.3.2: 蓝军只读验证**

- [ ] 确认 `etch-blue-team` 的 `edit: deny`, `write: deny`, `bash: deny`
- [ ] 尝试要求蓝军修改文件 → 应被拒绝

---

### 4.4 稳定性测试

**测试 4.4.1: 重复调用**

```
连续 3 次执行相同的 @etch-orchestrator 问题
```

- [ ] 每次都有完整输出
- [ ] 不累积上下文导致输出退化
- [ ] 不出现工具调用错误

**测试 4.4.2: 长对话会话**

```
在同一个对话中连续提出 5 个不同的蚀刻问题
```

- [ ] 每个问题独立处理
- [ ] 没有跨对话的上下文污染

---

## 5. 常见问题排查

### 问题 1: Subagent 未注册 / 找不到

```
@etch-orchestrator 报错 "unknown agent"
```

**排查步骤**:
1. 检查文件名：`.opencode/agent/etch-orchestrator.md` 拼写正确？
2. 检查 opencode.json 中是否有对应 agent 配置
3. 重启 OpenCode 使配置文件生效

### 问题 2: Tool 找不到

```
"unknown tool: literature-api"
```

**排查步骤**:
1. 确认文件在 `.opencode/tools/` 下
2. 确认文件名与工具名一致（`literature-api.ts` → 工具名 `literature-api`）
3. 检查 TS 语法是否正确（可以在外面先 `bun run` 或 `tsc` 验证）

### 问题 3: API 调用失败 — 返回 unavailable

```
"知识库API当前不可用"
```

**排查步骤**:
1. 用 curl 直接测试 API 是否可达（见 2.3 节）
2. 检查网络是否能通目标 IP 和端口
3. 如果是暂时断开，告知用户稍后重试

### 问题 4: Orchestrator 只调了部分 Subagent

**可能原因**:
- 用户指令中要求跳过某些 agent
- 被跳过的 agent 的 `permission.task` 配置不对
- 被跳过的 agent 对应的 `.md` 文件不存在

**排查**: 检查 Orchestrator 的 `permission.task` 是否包含所有 `etch-*` agent 的 allow 规则

### 问题 5: Summary 输出不完整

**可能原因**:
- 输入的 agent 输出内容太少
- Summary 的 maxSteps 不够

**排查**: 检查 Summary 的 `maxSteps` 配置，适当增加

### 问题 6: TRIZ 工具输出异常

**可能原因**:
- 矛盾描述解析错误
- 矛盾矩阵中没有对应条目（fallback 到通用原理）

**排查**: 检查 `triz-reference.ts` 中的 `PRINCIPLES` 和 `MATRIX` 数据完整性

### 问题 7: DOE Skill 加载失败

**可能原因**: DOE Skill 文件路径不对

**排查**: 检查 `etch-doe` 中调用 skill 的路径是否正确

---

## 附录：测试速查表

| Test ID | Subagent | 测试点 | 耗时 | 依赖 |
|---------|----------|--------|------|------|
| TC-ORC-01 | orchestrator | 全流程 | 3-5min | 全部 agent |
| TC-ORC-02 | orchestrator | 跳过指定 | 2min | 全部 agent |
| TC-ORC-03 | orchestrator | API 降级 | 2min | - |
| TC-MEC-01~03 | mechanism | 定性分析 | 3min | - |
| TC-LIT-01~03 | literature | API 流程 | 5min | API:32300 |
| TC-DAT-LD-01~02 | data-load | 数据加载 | 3min | API:5314 |
| TC-DAT-AN-01 | data-analyze | 模型对比 | 3min | API:5314 |
| TC-DAT-OP-01~03 | data-optimize | 多目标优化 | 5min | API:5314 |
| TC-DAT-PR-01~02 | data-predict | 参数预测 | 3min | API:5314 |
| TC-DAT-ALL-01 | data | API 降级 | 2min | - |
| TC-DOE-01~03 | doe | 实验设计 | 5min | Skill |
| TC-BLU-01~03 | blue-team | 审查评估 | 3min | - |
| TC-TRIZ-01~04 | triz | 创新方法 | 5min | - |
| TC-SUM-01~03 | summary | 信息整合 | 3min | - |
| 集成 4.1 | 全链路 | 端到端 | 5min | 全部 |
| 集成 4.2 | 降级 | 容错 | 3min | - |
| 集成 4.3 | 权限 | 隔离 | 2min | 全部 |
| 集成 4.4 | 稳定性 | 重复调用 | 3min | 全部 |

---

> **测试指引**: 建议按 Subagent 序号 ①→⑧ 逐个测试，再跑集成测试。每个 Subagent 内部按 TC 编号顺序执行。API 不可用的测试可以留到网络恢复或模拟环境下执行。
