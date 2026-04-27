---
title: "半导体工程数据分析团队 Skill 学习者手册"
subtitle: "从脚本、API、CLI 到 Agentic 分析能力"
author: "工程数据分析团队 / 数字算法团队"
date: "2026-04-27"
lang: zh-CN
---

# 半导体工程数据分析团队 Skill 学习者手册

## 适用对象

这份手册面向已经具备数据处理、Python / SQL / API 基础，并对半导体制造业务有一定了解的数字研发人员。典型读者包括：

- 工程数据分析工程师
- 数字算法工程师
- 数据平台工程师
- 负责 YAE、FEOL ETCH、Design、Device、PIE、Diff 等部门分析需求的应用开发人员
- 正在把已有脚本、Notebook、Dash 应用、API 服务改造成 Agentic 能力的工程师

阅读这份文档后，你应该能够回答四个问题：

1. Skill 在 AI Agent 生态里到底是什么。
2. 为什么半导体工程分析能力要拆成数据查询 API、数据处理 CLI、绘图输出 CLI 三层。
3. 如何把一个历史脚本改造成可复用、可审计、可被 Agent 调用的 Skill。
4. 如何用 opencode 的 Skill、Command、Custom Tool、AGENTS.md、权限配置组织团队能力。

---

## 1. 一句话理解 Skill

在团队内部可以这样定义 Skill：

> Skill 是把某类半导体数据分析任务的业务判断、数据入口、分析流程、工具调用顺序、图表解释方法、输出模板和安全边界，沉淀成 Agent 可按需加载的作业指导书。

Skill 不是一个普通 prompt，也不是一个数据库查询脚本，更不是让 Agent 随意访问生产数据的入口。它更像一个资深工程师写给 Agent 的 SOP：

- 什么时候应该使用这个能力；
- 需要向用户确认哪些参数；
- 应该调用哪个查询 API；
- 应该运行哪个数据处理 CLI；
- 应该生成哪些图；
- 图里哪些现象可以解释，哪些不能过度解释；
- 什么情况必须停止并找人确认。

对半导体数据团队来说，Skill 的价值在于把过去分散在个人经验、项目文档、脚本注释和口头沟通里的分析方法，变成可复用、可审计、可迭代的团队资产。

---

## 2. Agent、Tool、API、CLI、Skill 的关系

很多工程师第一次接触 Agent 时，容易把几个概念混在一起。可以用下面的分层来理解：

```text
用户问题
  ↓
Agent Loop：多轮决策循环，负责计划、调用工具、观察结果、继续迭代
  ↓
Skill：告诉 Agent 某类任务应该怎么做
  ↓
Tool Call：Agent 发起结构化动作，例如调用 API、运行 CLI、读取文件
  ↓
API / CLI / MCP / 文件系统：真实执行层
  ↓
数据、图表、报告、代码变更等结果
```

每层解决的问题不同：

- **Agent Loop** 解决“多步任务怎么持续推进”。
- **Tool Call** 解决“模型怎么用结构化方式发起动作”。
- **API / CLI** 解决“真实系统怎么安全执行动作”。
- **Skill** 解决“在某个专业场景里应该如何组合这些动作”。
- **AGENTS.md** 解决“项目长期规则是什么”。
- **Command** 解决“高频任务如何一键发起”。
- **MCP** 解决“外部资源、文档、工具如何标准化接入”。

一个很重要的判断是：

> Tool 让 Agent 有手；Skill 让 Agent 有工法；权限和审计让 Agent 有边界。

---

## 3. 为什么半导体分析能力必须三层化

半导体数据分析场景通常有几个特点：

1. 数据源复杂：Inline、WAT / PCM、FDC、MES、Yield、Recipe、Lot History、设备日志、CP/FT、客户反馈等。
2. 权限敏感：真实产品、lot、wafer、recipe、设备参数、良率结果、客户信息往往不能随意暴露。
3. 生产服务器受限：Agent 不能直接连生产库，也不能随意执行 SQL 或 shell 命令。
4. 分析方法需要复现：同一个输入应该得到同样的聚合结果、控制限、图表和 manifest。
5. 服务对象多样：YAE、FEOL ETCH、Design、Device、PIE、Diff 等部门关注的问题不同，但底层能力可以复用。

因此，建议所有分析能力统一拆成三层。

```text
第一层：数据查询 API
  负责只读查询、权限、审计、脱敏、标准 schema。

第二层：数据处理 CLI
  负责清洗、聚合、统计、算法、异常检测、summary。

第三层：绘图输出 CLI
  负责 HTML / PNG / SVG / 报告片段等结果输出。
```

这样拆的好处是：

- 查询层靠 API 管住生产数据边界；
- 算法层靠 CLI 保证可测试、可复现、可版本化；
- 绘图层靠 CLI 统一样式和输出格式；
- Skill 只负责“如何组合”，不把生产连接串、SQL、复杂算法全部塞进上下文。

---

## 4. 三层通用架构

推荐标准架构如下：

```text
opencode / Agent
  │
  ├── Skill：fab-inline-spc-analysis
  │     ├── 任务触发条件
  │     ├── 参数归一化
  │     ├── 三层工具调用顺序
  │     ├── 工程解释规则
  │     └── 停止规则
  │
  ├── Custom Tool：fab-query
  │     └── 调用数据查询 API
  │
  ├── Custom Tool：fab-analysis
  │     └── 调用数据处理 CLI
  │
  └── Custom Tool：fab-plot
        └── 调用绘图输出 CLI
```

### 4.1 数据查询 API 的定位

数据查询 API 是最接近生产数据的一层，必须严肃设计。

它应该负责：

- 连接生产、准生产、数据湖或脱敏数据源；
- 校验 product、lot、wafer、step、tool、chamber、recipe、time window 等参数；
- 控制最大时间窗口和最大返回行数；
- 只允许白名单表、view、字段；
- 记录审计日志；
- 返回标准 schema 的 parquet / csv / jsonl 或 data reference；
- 生成 query manifest。

它不应该负责：

- 复杂算法；
- 画最终图；
- 写生产数据；
- 接受 Agent 生成的任意 SQL；
- 暴露生产连接串。

FastAPI 是一个常见选择，因为它可以用 Pydantic model 声明 request body，并自动完成 JSON 读取、类型转换、校验和 OpenAPI schema 生成。

### 4.2 数据处理 CLI 的定位

数据处理 CLI 是算法与统计方法的主战场。它应该只依赖输入文件和配置文件，不直接连接数据库。

它应该负责：

- schema 校验；
- 空值过滤、类型转换、异常值标记；
- groupby 聚合；
- rolling window；
- 均值、标准差、控制限；
- drift / excursion / correlation / matching / split comparison；
- 生成 `summary.json`、`stats.parquet`、`analysis-manifest.json`。

它不应该负责：

- 直接访问生产库；
- 画最终图；
- 依赖 Notebook 状态；
- 只输出人类可读文本而没有机器可读文件。

### 4.3 绘图输出 CLI 的定位

绘图 CLI 读取 raw data、stats 和 summary，生成稳定的可交付结果。

它应该负责：

- Mean Plot；
- Std Plot；
- Raw Scatter Plot；
- wafer map；
- chamber split chart；
- correlation heatmap；
- HTML / PNG / SVG / Markdown report fragment；
- `plot-manifest.json`。

Plotly 适合生成交互式 HTML，因为它可以把 figure 保存为 HTML 文件，在浏览器中 hover、zoom、pan，并通过 legend 开关 trace。

它不应该负责：

- 重新查询数据；
- 重新定义核心统计方法；
- 擅自改控制限；
- 暴露敏感标识。

---

## 5. Inline SPC Skill 样例

以 Inline 测量数据分析为例，用户可能这样问：

> 帮我看一下产品 P1234 最近一个月在 ETCH_CD step 上，ETCH01 和 ETCH02 的 Inline CD 测量均值和波动有没有异常。

一个成熟 Skill 不应该让 Agent 直接写 SQL，而应该按以下流程：

```text
1. 归一化用户参数
   product_id = P1234
   step_id = ETCH_CD
   equipment_id = ETCH01, ETCH02
   time_window = 最近 30 天
   measurement_item = CD 或用户指定项

2. 调用 fab-query
   从 inline-query-api 获取标准 schema 数据和 query manifest

3. 检查 query manifest
   row_count 是否为 0
   time_window 是否被截断
   是否有字段缺失或权限限制

4. 调用 fab-analysis inline-spc analyze
   生成 mean、std、control limits、summary

5. 调用 fab-plot inline-spc render
   生成 mean plot、std plot、scatter plot

6. 输出工程报告
   包括图表链接、观察、风险、下一步建议

7. 明确边界
   不直接判断 recipe 是否要改，不直接给生产放行建议
```

### 5.1 推荐 Skill 目录

```text
.opencode/
  skills/
    fab-inline-spc-analysis/
      SKILL.md
      references/
        inline-schema.md
        spc-interpretation.md
      templates/
        engineering-report.md
  commands/
    inline-spc.md
  tools/
    fab-query.ts
    fab-analysis.ts
    fab-plot.ts
```

### 5.2 SKILL.md 的核心内容

```md
---
name: fab-inline-spc-analysis
description: Use for semiconductor inline metrology, process monitoring, SPC trend review, quality-control analysis, and yield-analysis support. Trigger when the user asks to query recent inline measurements by product, lot, process step, equipment, chamber, recipe, or measurement item; generate mean, standard-deviation, or raw scatter plots; or assess process stability and equipment variation for YAE, FEOL ETCH, PIE, Device, Design, or Diff teams.
---

# Fab Inline SPC Analysis

## Workflow

1. Normalize the engineering request.
2. Identify required filters: product, lot, step, equipment, chamber, recipe, item, time window.
3. Use fab-query to call the approved inline query API.
4. Validate query manifest before analysis.
5. Use fab-analysis inline-spc analyze for statistics.
6. Use fab-plot inline-spc render for charts.
7. Return engineering summary with evidence and artifact links.
8. Stop before any production-impacting recommendation.

## Stop rules

Stop and ask for human confirmation before:

- changing SQL whitelist or query scope;
- connecting directly to production database;
- modifying official target / UCL / LCL / spec rules;
- exposing sensitive product, lot, wafer, recipe, customer, or yield information;
- recommending recipe change, lot hold/release, shipment decision, or customer-facing conclusion.
```

---

## 6. 从脚本到 Skill 的二次开发 SOP

### Step 1：脚本盘点

先不要改代码。先回答：

```text
这个脚本服务哪个部门？
典型问题是什么？
输入参数是什么？
数据源是什么？
输出是什么？
哪些逻辑属于查询？
哪些逻辑属于分析？
哪些逻辑属于绘图？
是否涉及生产数据或敏感数据？
是否可以构造 mock 数据？
```

### Step 2：定义标准 schema

例如 Inline 数据标准 schema：

```text
product_id
lot_id
wafer_id
step_id
equipment_id
chamber_id
recipe_id
measurement_item
measurement_time
measurement_value
target
ucl
lcl
unit
source_system
```

不要让每个脚本各自定义字段名，否则 Agent 无法稳定复用。

### Step 3：把查询逻辑改造成 API

API 至少要提供：

```text
GET  /health
GET  /api/v1/capabilities
GET  /api/v1/inline/schema
POST /api/v1/inline/query
POST /api/v1/inline/profile
```

请求体示例：

```json
{
  "product_ids": ["P1234"],
  "step_ids": ["ETCH_CD"],
  "equipment_ids": ["ETCH01", "ETCH02"],
  "measurement_items": ["CD_TOP"],
  "time_window_days": 30,
  "max_rows": 200000
}
```

响应体不要直接塞超大数据。推荐返回 artifact 引用：

```json
{
  "run_id": "inline-query-20260427-001",
  "schema_version": "inline_measurement.v1",
  "row_count": 10240,
  "data_uri": "artifacts/raw.parquet",
  "manifest_uri": "artifacts/query-manifest.json",
  "warnings": []
}
```

### Step 4：把分析逻辑改造成 CLI

CLI 示例：

```bash
fab-analysis inline-spc analyze \
  --input artifacts/raw.parquet \
  --config configs/inline-spc.yaml \
  --output artifacts/stats.parquet \
  --summary artifacts/summary.json \
  --manifest artifacts/analysis-manifest.json
```

分析 CLI 的验收标准：

```text
[ ] 不连接生产数据库
[ ] 输入输出路径显式传入
[ ] 有 schema 校验
[ ] 空数据有明确错误
[ ] 输出 summary.json 和 manifest.json
[ ] 方法版本写入 manifest
[ ] 同样输入重复运行结果一致
[ ] 有 mock / golden case 测试
```

### Step 5：把绘图逻辑改造成 CLI

CLI 示例：

```bash
fab-plot inline-spc render \
  --raw artifacts/raw.parquet \
  --stats artifacts/stats.parquet \
  --summary artifacts/summary.json \
  --plot all \
  --output-dir artifacts/plots \
  --manifest artifacts/plot-manifest.json
```

绘图 CLI 的验收标准：

```text
[ ] 不连接数据库
[ ] 不重新定义统计方法
[ ] 支持 mean / std / scatter / all
[ ] 输出 HTML 和 plot manifest
[ ] 图表标题包含产品、step、设备、时间范围
[ ] hover 信息包含 lot、wafer、time、equipment、item、value、unit
[ ] 图中标明 target / UCL / LCL 的来源
```

### Step 6：写 Custom Tool 封装调用

opencode 的 custom tools 可以用 TypeScript / JavaScript 定义，工具定义本身也可以调用 Python、Shell 或其他语言脚本。

示例：

```ts
import { tool } from "@opencode-ai/plugin"
import path from "path"

export default tool({
  description: "Run approved inline SPC analysis workflow",
  args: {
    product_id: tool.schema.string().describe("Product ID"),
    step_id: tool.schema.string().describe("Process step"),
    equipment_ids: tool.schema.array(tool.schema.string()).describe("Equipment IDs"),
    time_window_days: tool.schema.number().default(30),
  },
  async execute(args, context) {
    const script = path.join(context.worktree, "tools/run-inline-spc.py")
    const result = await Bun.$`python3 ${script} ${JSON.stringify(args)}`.text()
    return result.trim()
  },
})
```

### Step 7：写 Skill

Skill 要写：

```text
什么时候触发
需要哪些输入
默认参数是什么
调用哪些工具
如何检查 manifest
如何解释图表
输出模板是什么
哪些情况必须停止
```

### Step 8：加 Command

Command 让团队成员用统一入口发起任务：

```md
---
description: Run inline SPC analysis through approved query API, analysis CLI, and plot CLI
agent: plan
---

Use the `fab-inline-spc-analysis` skill.

Analyze this request:

$ARGUMENTS

Do not connect directly to production databases. Do not modify code. Return the standard engineering report.
```

### Step 9：评审和回归

上线前检查：

```text
[ ] API 有 mock adapter
[ ] API 有真实 adapter 或 legacy adapter
[ ] CLI 有 golden data 测试
[ ] 图表输出经过人工确认
[ ] Skill description 能正确触发
[ ] Skill 有 stop rules
[ ] opencode 权限配置合理
[ ] 无密钥、连接串、真实敏感数据进入 Skill
[ ] 关键输出都有 manifest
```

---

## 7. Skill 输出报告模板

建议所有半导体分析 Skill 使用类似模板：

```text
# 工程分析报告

## 1. 问题重述
用工程语言重述用户的问题、对象、时间窗口、筛选条件。

## 2. 数据范围
说明数据源、schema version、row count、时间范围、过滤条件、权限限制。

## 3. 生成结果
列出 Mean Plot、Std Plot、Scatter Plot 或其他图表链接。

## 4. 关键观察
只写有数据支持的观察。
不要把相关性写成因果。

## 5. 风险与不确定性
说明缺失数据、样本量不足、时间窗口被截断、target / spec 缺失等问题。

## 6. 建议下一步
建议工程师查看哪些 step、equipment、chamber、recipe、lot、wafer 或补充哪些数据。

## 7. 需要人工确认的问题
列出不能由 Agent 自动决定的问题。
```

---

## 8. 常见错误

### 错误 1：让 Agent 直接拼 SQL

风险：权限不可控、审计困难、容易误查敏感数据。

正确做法：查询层 API 化，SQL 放在受控 adapter 里。

### 错误 2：把所有逻辑都塞进 Skill

风险：上下文过大、不可测试、不可复现。

正确做法：Skill 写 SOP，算法写 CLI，查询写 API。

### 错误 3：图表 CLI 重新计算统计结果

风险：图表和 summary 不一致。

正确做法：分析 CLI 产出 stats，绘图 CLI 只读取 stats。

### 错误 4：没有 manifest

风险：报告无法追溯，不知道用了哪批数据和哪个方法版本。

正确做法：query / analysis / plot 三层都要产出 manifest。

### 错误 5：Skill 没有停止规则

风险：Agent 可能给出越权建议，例如 recipe 修改、生产放行、客户结论。

正确做法：在 Skill 里明确 stop rules，并在 opencode permission 中兜底。

---

## 9. 学习路径

### 第一周：理解概念

- 理解 Agent Loop、Tool Call、Skill、AGENTS.md、Command、MCP 的区别。
- 阅读一个已有 Skill，例如 `fab-inline-spc-analysis`。
- 用 mock 数据跑一遍 query → analysis → plot。

### 第二周：改造一个小脚本

- 找一个只读、低风险、输入输出明确的脚本。
- 拆成 query adapter、analysis CLI、plot CLI。
- 生成标准 manifest。

### 第三周：写第一个 Skill

- 写 `SKILL.md`。
- 写 opencode command。
- 写 custom tool 包装 CLI。
- 让同事用 3 个真实问题测试。

### 第四周：评审和上线

- 修正触发条件。
- 增加 stop rules。
- 增加 golden case。
- 提交团队 Skill Registry。

---

## 10. 参考资料

- OpenCode Agent Skills: https://opencode.ai/docs/skills
- OpenCode Custom Tools: https://opencode.ai/docs/custom-tools/
- OpenCode Commands: https://opencode.ai/docs/commands/
- OpenCode Agents: https://opencode.ai/docs/agents/
- OpenCode Rules / AGENTS.md: https://opencode.ai/docs/rules/
- OpenCode MCP Servers: https://opencode.ai/docs/mcp-servers
- FastAPI Request Body and Pydantic Models: https://fastapi.tiangolo.com/tutorial/body/
- Plotly Interactive HTML Export: https://plotly.com/python/interactive-html-export/
