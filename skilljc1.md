已整理成一份面向半导体工程数据分析团队 / 数字算法团队的完整教程，包含你要求的 **三层复用架构、二次开发 SOP、Skill 编写规范、opencode 联动方式、上线治理与培训路径**。

下载完整版 Markdown：

[半导体工程数据分析团队 Skill 教程](sandbox:/mnt/data/semiconductor-skill-agentic-tutorial.md)

下面是教程的核心版本，便于你直接评审和内部转发。

---

# 半导体数据分析团队 Skill 教程

## 从脚本 / API / 应用到 Agentic 化智能分析能力

这份教程面向服务 YAE / FEOL ETCH / Design / Device / PIE / Diff 等部门的工程数据分析团队和数字算法团队。

核心原则只有一句：

> **不要让 Agent 直接接生产库、直接改历史脚本、直接拼 SQL。应该把每个分析能力拆成三层：数据查询 API、数据处理 CLI、绘图与结果输出 CLI；再用 Skill 告诉 Agent 何时使用、如何组合、如何解释、何时停止。**

opencode 的 Skill 本身就是通过 `SKILL.md` 让 Agent 发现可复用指令，并通过原生 `skill` tool 按需加载完整内容；`SKILL.md` 的 `name` 和 `description` 会影响 Agent 是否选择这个能力，所以 Skill 更像“Agent 的作业指导书”，不是普通说明文档。([OpenCode][1])

---

## 1. 目标架构：所有分析能力统一三层化

```text
用户问题
  ↓
Agent / opencode
  ↓
Skill：判断场景、参数、工具、停止规则、输出格式
  ↓
三层复用模块
  ├── 数据查询 API：只读查询、权限、审计、脱敏、标准 schema
  ├── 数据处理 CLI：清洗、聚合、算法、SPC、异常检测、summary
  └── 绘图输出 CLI：Plotly HTML、PNG/SVG、manifest、报告草稿
```

为什么这样拆？

因为半导体生产数据通常受生产服务器、权限、网络、安全、审计限制。数据查询层最接近生产系统，必须服务化、审计化、白名单化；算法处理层更适合 CLI 化，便于版本化、测试、复现；绘图输出层也应 CLI 化，保证相同输入生成一致图表。

FastAPI 适合做查询 API，因为它支持用 Pydantic model 声明 request body，并自动完成 JSON 读取、类型转换、校验和 OpenAPI schema 生成。([FastAPI][2]) Plotly 适合做交互式 HTML 图表输出，因为其官方支持把 figure 保存为 HTML 文件并在浏览器中交互查看。([Plotly][3])

---

## 2. 三层职责边界

### 第一层：数据查询 API

职责：

```text
连接生产 / 准生产数据源
做权限控制、参数校验、审计、限流、脱敏
只读查询
返回标准 schema 的数据文件或 data reference
```

不做：

```text
复杂算法
画图
训练模型
写生产数据
让 Agent 自由提交 SQL
```

推荐 API：

```text
GET  /health
GET  /api/v1/capabilities
GET  /api/v1/{domain}/schema
POST /api/v1/{domain}/query
POST /api/v1/{domain}/profile
GET  /api/v1/jobs/{job_id}
```

Inline 示例：

```text
POST /api/v1/inline/query
POST /api/v1/inline/profile
```

### 第二层：数据处理 CLI

职责：

```text
读取标准数据文件
执行清洗、聚合、统计、算法、SPC、异常检测
输出 stats.parquet、summary.json、manifest.json
```

不做：

```text
连接生产数据库
画最终图
依赖 notebook 状态
只 print 文本而不输出机器可读结果
```

示例：

```bash
fab-analysis inline-spc analyze \
  --input artifacts/raw.parquet \
  --config configs/inline-spc.yaml \
  --output artifacts/stats.parquet \
  --summary artifacts/summary.json \
  --manifest artifacts/analysis-manifest.json
```

### 第三层：绘图与结果输出 CLI

职责：

```text
读取 raw data、stats、summary、manifest
生成 Mean Plot、Std Plot、Scatter Plot、wafer map、correlation plot 等
输出 HTML / PNG / SVG / markdown report / plot-manifest.json
```

不做：

```text
连接数据库
重新定义核心统计方法
修改控制限规则
暴露敏感 lot / wafer / product 信息
```

示例：

```bash
fab-plot inline-spc render \
  --raw artifacts/raw.parquet \
  --stats artifacts/stats.parquet \
  --summary artifacts/summary.json \
  --plot all \
  --output-dir artifacts/plots \
  --manifest artifacts/plot-manifest.json
```

---

## 3. 二次开发 SOP

### SOP 0：脚本 / 应用盘点

每个旧脚本先填 intake 表，不要直接改代码。

| 项目       | 说明                                                     |
| -------- | ------------------------------------------------------ |
| 能力名称     | inline-spc、etch-chamber-drift、device-wat-correlation   |
| 服务部门     | YAE / FEOL ETCH / Design / Device / PIE / Diff         |
| 当前形态     | Notebook、Python 脚本、Dash、API、定时任务                       |
| 数据源      | Inline、WAT、FDC、MES、Yield、Recipe、Lot History            |
| 查询条件     | product、lot、wafer、step、tool、chamber、recipe、time window |
| 输出       | 图、表、HTML、Excel、PPT、JSON、结论                             |
| 方法       | SPC、聚合、相关性、异常检测、漂移分析、模型推理                              |
| 风险等级     | 是否涉及生产数据、良率、recipe、spec、客户敏感信息                         |
| 是否可 mock | 能否构造脱敏样例数据                                             |
| 是否已有 API | 有 / 无 / 部分有                                            |

适合做 Skill 的能力通常是：高频、输入模式稳定、输出模板稳定、需要多步查询分析绘图、跨部门复用价值高。

---

### SOP 1：定义业务场景和 Skill 边界

模板：

```text
能力名称：
服务部门：
典型问题：
输入条件：
默认时间范围：
核心数据域：
核心方法：
核心图表：
最终输出：
不应处理的任务：
必须人工确认的场景：
```

Inline SPC 示例：

```text
能力名称：fab-inline-spc-analysis
服务部门：YAE / FEOL ETCH / PIE / Device
典型问题：分析最近 30 天 Inline 测量项均值、标准差和原始点分布
输入条件：product_id、lot_id、step_id、equipment_id、measurement_item
默认时间范围：最近 30 天
核心数据域：Inline metrology
核心方法：清洗、分组聚合、均值、标准差、控制限
核心图表：Mean Plot、Std Plot、Raw Scatter Plot
最终输出：HTML 图表、工程观察、风险提示、后续检查建议
不应处理的任务：生产数据库写入、官方 spec 修改、recipe 修改
必须人工确认的场景：控制限规则不明确、查询敏感 lot、跨部门口径冲突
```

---

### SOP 2：定义标准数据契约

所有能力都要先定 contract，再写代码。

Inline 标准 schema 建议：

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

每次 query / analysis / plot 都要产出 manifest：

```json
{
  "run_id": "inline-spc-20260426-001",
  "capability": "fab-inline-spc-analysis",
  "schema_version": "inline_measurement.v1",
  "row_count": 10240,
  "data_window": {
    "start_time": "2026-03-27T00:00:00",
    "end_time": "2026-04-26T00:00:00"
  },
  "filters": {
    "product_ids": ["P1234"],
    "step_ids": ["ETCH_CD"],
    "equipment_ids": ["ETCH01", "ETCH02"]
  },
  "data_artifacts": {
    "raw": "artifacts/raw.parquet",
    "stats": "artifacts/stats.parquet",
    "plots": [
      "artifacts/mean.html",
      "artifacts/std.html",
      "artifacts/scatter.html"
    ]
  },
  "warnings": [
    "target is missing for measurement_item CD_TOP"
  ]
}
```

Agent 的结论必须引用 manifest，而不是凭空总结。

---

### SOP 3：查询层改造成 API

推荐 adapter 模式：

```text
BaseQueryAdapter
├── MockInlineAdapter
├── SqlInlineAdapter
├── LegacyScriptAdapter
├── ExistingApiAdapter
├── DataLakeAdapter
└── McpResourceAdapter
```

每个 adapter 最终都返回标准 schema。

查询 API 验收标准：

```text
[ ] 提供 /health
[ ] 提供 /schema
[ ] 提供 mock adapter
[ ] 提供真实或 legacy adapter
[ ] 有 schema 校验
[ ] 有 row limit 和 time window limit
[ ] 有参数化查询或白名单查询
[ ] 有审计日志
[ ] 有脱敏策略
[ ] 有样例请求和响应
[ ] 有单元测试和 smoke test
```

安全规则：

```text
禁止 Agent 直接连生产库
禁止 Agent 提交任意 SQL
只允许白名单表 / view / 字段
默认最近 30 天或业务批准窗口
默认 max_rows
所有请求进入 audit log
生产连接串不写入 Skill、AGENTS.md、命令模板
```

---

### SOP 4：数据处理层改造成 CLI

Analysis CLI 验收标准：

```text
[ ] 输入只依赖数据文件和配置
[ ] 不连接生产数据库
[ ] 输出 summary.json
[ ] 输出 manifest.json
[ ] 有 schema 校验
[ ] 空数据、缺字段、类型错误有明确报错
[ ] 有 mock / golden data 测试
[ ] 同样输入重复运行结果一致
[ ] 方法版本写入 manifest
[ ] 控制限、异常检测、筛选规则配置化
```

建议沉淀通用模块：

```text
fab_analysis.common.schema
fab_analysis.common.cleaning
fab_analysis.common.grouping
fab_analysis.common.spc
fab_analysis.common.correlation
fab_analysis.common.drift
fab_analysis.common.summary
```

不同业务域只写 domain-specific method，不重复写底层清洗和聚合。

---

### SOP 5：绘图输出层改造成 CLI

Plot CLI 验收标准：

```text
[ ] 不连接数据库
[ ] 不重新计算核心分析结果
[ ] 支持 all / mean / std / scatter 等图表选择
[ ] 输出 HTML 和 manifest
[ ] 空数据时明确报错
[ ] 图表标题、单位、时间范围、筛选条件完整
[ ] 图中标明 target / UCL / LCL / spec 的来源
[ ] 支持敏感标识脱敏
```

统一绘图规范：

```text
target：实线
UCL / LCL：虚线
spec：点划线
颜色：equipment / chamber
符号：measurement_item / wafer group
hover：lot、wafer、time、equipment、step、item、value、unit、sample_count
```

---

### SOP 6：接入 Agent 工具

Agent 不直接运行任意命令，而是调用安全封装工具。

推荐工具：

```text
fab-query
  调用查询 API，返回 data_url 和 manifest

fab-analysis
  调用 analysis CLI，返回 stats_url、summary_url、manifest

fab-plot
  调用 plot CLI，返回 plot artifact 和 manifest

fab-report
  串联 query → analysis → plot
```

opencode 的 custom tools 是 LLM 可以调用的函数，工具定义可以放在 `.opencode/tools/` 或全局工具目录中；定义文件使用 TypeScript / JavaScript，但可以调用任何语言写的脚本，因此很适合用 TS tool 包装 Python API/CLI。([OpenCode][4])

---

### SOP 7：编写 Skill

Skill 必须写清楚：

```text
触发场景
输入参数
默认值
三层模块调用顺序
查询 API 选择规则
处理 CLI 选择规则
绘图 CLI 选择规则
图表解释方法
输出报告模板
停止规则
安全规则
常见失败处理
```

Inline SPC 示例 frontmatter：

```md
---
name: fab-inline-spc-analysis
description: Use for semiconductor inline metrology, process monitoring, SPC trend review, quality-control analysis, and yield-analysis support. Trigger when the user asks to query recent inline measurements by product, lot, process step, equipment, chamber, recipe, or measurement item; generate mean, standard-deviation, or raw scatter plots; or assess process stability and equipment variation for YAE, FEOL ETCH, PIE, Device, Design, or Diff teams.
license: internal
compatibility: opencode
metadata:
  owner: engineering-data-analysis
  version: "0.1.0"
---
```

Skill 的核心 workflow：

```text
1. 重述工程问题
2. 识别部门上下文：YAE / FEOL ETCH / Design / Device / PIE / Diff
3. 归一化查询条件
4. 调用 fab-query
5. 检查 row_count、time window、schema_version、warnings
6. 调用 fab-analysis
7. 检查 summary 和 risk flags
8. 调用 fab-plot
9. 输出图表链接和工程解释
10. 给出下一步检查建议，不直接给生产决策
```

停止规则：

```text
连接生产数据库前必须停止
修改 SQL 绕过权限前必须停止
修改官方 SPC / spec / target / UCL / LCL 方法前必须停止
输出真实客户、产品、lot、wafer 敏感信息前必须停止
建议 recipe 修改、生产 hold/release、客户结论前必须停止
```

---

### SOP 8：opencode 落地结构

```text
.opencode/
├── skills/
│   └── fab-inline-spc-analysis/
│       └── SKILL.md
├── commands/
│   └── inline-spc.md
└── tools/
    ├── fab-query.ts
    ├── fab-analysis.ts
    └── fab-plot.ts
```

opencode 支持 custom commands，把重复任务包装成 `/command`；命令可以通过 markdown 文件放在 `.opencode/commands/`，正文就是发送给模型的模板，`$ARGUMENTS` 可承接用户输入。([OpenCode][5])

示例 command：

```md
---
description: Run inline SPC analysis through approved query API, analysis CLI, and plot CLI
agent: plan
---

Use the `fab-inline-spc-analysis` skill.

Analyze this request:

$ARGUMENTS

Do not modify code. Do not connect directly to production databases. Use the approved API/CLI workflow and return the standard engineering report.
```

opencode 也区分 Build 和 Plan agent：Build 是默认开发 agent，拥有完整工具；Plan 是受限 agent，默认文件编辑和 bash 命令需要确认，适合分析代码、提出计划、避免实际修改。这个团队教程里建议：分析报告类任务默认用 Plan，代码改造类任务再切 Build。([OpenCode][6])

---

## 4. 面向不同部门的 Skill 复用方式

### YAE：良率异常初筛

```text
Skill：yield-excursion-triage
Query API：inline-query-api + yield-query-api
Analysis CLI：inline-spc + yield-correlation
Plot CLI：trend-control + pareto + scatter-correlation
```

输出：

```text
异常 lot 范围
Inline 指标变化
tool / chamber 差异
与 yield drop 的时间关系
建议下一步查哪些 step / equipment / recipe
```

### FEOL ETCH：Chamber drift 分析

```text
Skill：etch-chamber-drift-analysis
Query API：inline-query-api + equipment-sensor-query-api
Analysis CLI：chamber-drift + tool-matching + rolling-spc
Plot CLI：chamber-split-trend + mean/std/scatter
```

输出：

```text
chamber 间差异
rolling mean / rolling std
漂移开始时间
是否集中在某个 recipe / product / lot
建议检查 PM、recipe、sensor、metrology tool matching
```

### Design / Device：WAT/PCM 参数分布与 split 对比

```text
Skill：device-split-correlation
Query API：wat-query-api + split-info-api + design-metadata-api
Analysis CLI：distribution-compare + correlation
Plot CLI：box-violin + histogram + scatter-matrix
```

输出：

```text
split 间分布差异
统计显著性和工程差异
wafer / lot / site pattern
需要 Design 或 Device 确认的问题
```

### PIE：跨工艺步骤关联

```text
Skill：pie-cross-step-correlation
Query API：inline-query-api + lot-history-api + yield-query-api
Analysis CLI：cross-step-correlation + feature-ranking
Plot CLI：correlation-heatmap + scatter-by-step + trend-overlay
```

输出：

```text
相关步骤和测量项排序
lot / time 对齐方式
相关性是否可能来自批次效应
建议后续 DOE 或工程验证方向
```

### Diff：Furnace run 稳定性监控

```text
Skill：diff-furnace-run-monitoring
Query API：equipment-run-query-api + inline-query-api
Analysis CLI：run-stability + recipe-drift
Plot CLI：run-chart + control-chart + equipment-split
```

输出：

```text
run-to-run 波动
recipe / tube / boat / slot 差异
与 Inline 或 WAT 结果对应关系
建议设备或工艺排查项
```

---

## 5. MCP 的位置

MCP 可以用于接 Jira、Confluence、文档库、监控系统、数据目录等外部资源，但不建议把生产数据查询直接随意暴露成大量 MCP 工具。opencode 支持本地和远程 MCP server，加入后 MCP tools 会和内置工具一起提供给 LLM；但文档也提醒 MCP server 会增加上下文，工具太多会快速消耗上下文，所以应谨慎启用。([OpenCode][7])

推荐策略：

```text
生产数据查询：优先 Query API
算法处理：优先 CLI
绘图输出：优先 CLI
文档 / Jira / 监控 / 数据目录：可以用 MCP
Skill：负责告诉 Agent 什么时候用哪个
```

---

## 6. 上线治理

### 能力分级

| 等级 | 描述                   | 可用范围           |
| -- | -------------------- | -------------- |
| L0 | 个人脚本                 | 个人使用，不接 Agent  |
| L1 | 三层拆分完成               | 团队内部试用         |
| L2 | API / CLI / Skill 完成 | 小范围 Agent 使用   |
| L3 | 有权限、审计、测试、文档         | 跨部门正式使用        |
| L4 | 平台级能力                | 多个 Skill 和应用复用 |

### 风险分级

| 风险       | 示例                         | Agent 权限    |
| -------- | -------------------------- | ----------- |
| Low      | mock 数据、公开样例               | allow       |
| Medium   | 内部历史数据只读分析                 | allow 或 ask |
| High     | 真实 lot/product、良率、控制限、spec | ask         |
| Critical | 生产写操作、recipe 修改、生产放行       | deny 或人工审批  |

### Skill Registry

```yaml
skills:
  - name: fab-inline-spc-analysis
    owner: engineering-data-analysis
    departments: [YAE, FEOL ETCH, PIE, Device]
    query_api: inline-query-api
    analysis_cli: fab-analysis inline-spc
    plot_cli: fab-plot inline-spc
    risk: medium
    status: production
    version: 0.1.0
```

---

## 7. 最终检查清单

当团队成员说“我把这个脚本做成 Skill 了”，至少检查：

```text
[ ] 原始脚本已经拆成 query / analysis / plot 三层
[ ] query 层是 API，不是 Agent 直接连库
[ ] analysis 层是 CLI，不依赖数据库和 notebook 状态
[ ] plot 层是 CLI，不重新定义统计方法
[ ] 有 mock 数据
[ ] 有 schema contract
[ ] 有 manifest
[ ] 有 API / CLI 测试
[ ] 有 opencode custom tool 或 command
[ ] 有 SKILL.md
[ ] Skill description 能准确触发
[ ] Skill 有输出模板
[ ] Skill 有 stop rules
[ ] Skill 不包含密钥、生产连接串、敏感数据
[ ] Agent 输出会引用证据和 artifact
[ ] 高风险结论会要求人工确认
```

---

## 8. 推荐推广路线

```text
第 1 阶段：选 Inline SPC 做标杆能力
  inline-query-api
  fab-analysis inline-spc
  fab-plot inline-spc
  fab-inline-spc-analysis Skill

第 2 阶段：抽通用模块
  schema validation
  artifact manifest
  data redaction
  SPC utilities
  plot style
  CLI base framework

第 3 阶段：迁移高频场景
  etch-chamber-drift-analysis
  yield-excursion-triage
  device-wat-correlation
  pie-cross-step-correlation
  diff-furnace-run-monitoring

第 4 阶段：建立 Skill Review Board
  数据工程 owner
  算法 owner
  业务部门代表
  IT / 平台 owner
  数据安全 owner
  Agent 平台 owner

第 5 阶段：平台化
  能力注册中心
  API/CLI 模板生成器
  Skill 模板生成器
  mock data generator
  golden case regression
  artifact registry
  permission policy
```

---

最终要传达给团队的是：

> **Skill 不是把脚本交给大模型运行，而是把团队多年积累的数据访问规范、算法方法、绘图标准、工程判断和安全边界，沉淀成 Agent 可复用、可审计、可迭代的工作方法。**

[1]: https://opencode.ai/docs/skills "Agent Skills | OpenCode"
[2]: https://fastapi.tiangolo.com/tutorial/body/ "Request Body - FastAPI"
[3]: https://plotly.com/python/interactive-html-export/ "
     Interactive html export in Python
"
[4]: https://opencode.ai/docs/custom-tools/ "Custom Tools | OpenCode"
[5]: https://opencode.ai/docs/commands/ "Commands | OpenCode"
[6]: https://opencode.ai/docs/agents/ "Agents | OpenCode"
[7]: https://opencode.ai/docs/mcp-servers/ "MCP servers | OpenCode"
