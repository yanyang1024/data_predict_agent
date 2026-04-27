---
title: "半导体数据分析团队 Skill 培训演讲稿"
subtitle: "面向培训者的授课脚本、演示流程与练习设计"
author: "工程数据分析团队 / 数字算法团队"
date: "2026-04-27"
lang: zh-CN
---

# 半导体数据分析团队 Skill 培训演讲稿

## 使用说明

这份文档不是普通教程，而是给培训者使用的授课脚本。你可以把它拆成 PPT，也可以按文档顺序进行 2.5 至 3 小时的工作坊。

培训对象是半导体公司工程数据分析团队和数字算法团队，包括服务 YAE、FEOL ETCH、Design、Device、PIE、Diff 等部门的数据工程师、算法工程师和应用开发工程师。学员通常懂 Python、SQL、数据处理和部分半导体业务，但对 AI Agent、Skill、opencode、MCP、上下文工程的生态了解有限。

培训目标：

1. 让学员理解 Skill 不是 prompt，而是 Agent 的作业指导书。
2. 让学员理解为什么生产数据相关能力要拆成数据查询 API、数据处理 CLI、绘图输出 CLI 三层。
3. 让学员能判断一个历史脚本是否适合改造成 Skill。
4. 让学员能读懂并初步编写 `SKILL.md`、opencode command 和 custom tool。
5. 让学员建立安全意识：Agent 不能直接连生产库、不能直接改 spec / recipe / 控制限。

---

## 培训结构总览

建议总时长：150 至 180 分钟。

```text
模块 0：开场与目标                10 分钟
模块 1：Agent 和 Skill 基础        25 分钟
模块 2：半导体分析三层架构         30 分钟
模块 3：Inline SPC Skill 案例      35 分钟
模块 4：从历史脚本到 Skill 的 SOP  35 分钟
模块 5：opencode 实操              25 分钟
模块 6：练习、评审与答疑           25 分钟
```

如果时间只有 90 分钟，建议压缩为：

```text
概念 20 分钟
三层架构 25 分钟
Inline 案例 25 分钟
opencode 演示 15 分钟
答疑 5 分钟
```

---

# 模块 0：开场与目标

## 讲师目标

让大家意识到这次培训不是“学习一个新 prompt 技巧”，而是学习“如何把团队已有数据分析能力 Agentic 化”。

## 推荐开场白

各位今天的培训主题是 Skill。我们不会把 Skill 当成一个孤立的新名词来讲，而是放在我们团队的真实工作里讲：我们已经有不少脚本、API、Dash 应用、Notebook 和算法服务，这些能力过去主要靠人来记住怎么用。现在我们要做的是，把这些能力变成 Agent 可以稳定调用、工程师可以复用、管理上可以审计的智能分析能力。

我们服务的部门很多，YAE 关注良率异常，FEOL ETCH 关注设备和 chamber 差异，Device 和 Design 关注参数分布和设计 split，PIE 关注跨工艺步骤关联，Diff 关注炉管和 run-to-run 稳定性。这些场景不一样，但底层能力是可以复用的：查数据、做分析、出图和解释。

今天我们要建立一个统一方法：所有应用能力都拆成三层，数据查询做 API，数据处理做 CLI，绘图输出做 CLI，然后用 Skill 把这三层编排起来。

## 板书或投影片

```text
旧模式：人记住脚本怎么跑
  人 → 脚本 / Notebook / API / Dash → 图表 / 结论

新模式：Agent 按 Skill 调用标准能力
  人 → Agent → Skill → Query API → Analysis CLI → Plot CLI → 报告
```

## 互动问题

问学员：你们手上有没有这样一种脚本，别人也想用，但每次都要问你参数怎么填、数据从哪里取、图怎么看？

引导答案：这种脚本就是 Skill 化的候选对象。

---

# 模块 1：Agent 和 Skill 基础

## 讲师目标

让学员理解 Agent、Tool、Skill、MCP、AGENTS.md、Command 的区别。

## 讲稿

先把几个容易混的概念拆开。

Agent 不是一个单次回答的大模型。Agent 更像一个带状态的决策循环：它接收目标，观察环境，决定下一步动作，调用工具，拿到结果，再继续判断下一步。

Tool 是 Agent 可以执行的动作，例如读取文件、调用 API、运行 CLI、搜索文档、画图。Tool 解决的是“能做什么”。

Skill 解决的是“某类任务应该怎么做”。比如 Inline SPC Skill 会告诉 Agent：先归一化 product、lot、step、equipment、measurement item；再调用 approved query API；再运行 analysis CLI；再运行 plot CLI；最后按照固定报告模板输出，不要直接给生产放行建议。

AGENTS.md 是项目长期规则，例如项目结构、构建命令、测试命令、禁止操作。

Command 是高频任务入口，例如 `/inline-spc`。它帮助用户用统一方式发起任务。

MCP 是外部资源和工具接入协议，适合接 Jira、Confluence、数据目录、监控系统等。但生产数据查询最好仍然走团队批准的 Query API。

## 投影片建议

```text
Tool：你能做什么
Skill：你应该怎么做
AGENTS.md：这个项目长期规则是什么
Command：常用任务怎么一键发起
MCP：外部系统怎么接入
Permission：什么动作需要允许、询问或拒绝
```

## 讲师强调

Skill 不是把脚本原文粘给模型。Skill 应该尽量短，像控制面；复杂逻辑应该沉到 API、CLI、工具和 references 里。

## 快速练习

给学员 3 个例子，让他们判断是 Tool、Skill 还是 Command。

例 1：`fab-query`，调用 Inline Query API。

答案：Tool。

例 2：`fab-inline-spc-analysis`，规定 Inline SPC 的分析流程和停止规则。

答案：Skill。

例 3：`/inline-spc P1234 ETCH_CD ETCH01`。

答案：Command。

---

# 模块 2：半导体分析三层架构

## 讲师目标

让学员理解三层拆分是为了复用、安全、审计和可复现。

## 讲稿

我们团队的核心架构建议是：所有分析能力都拆成三层。

第一层是数据查询 API。它只做受控、只读、可审计的数据访问。Agent 不能直接连生产库，也不能自己拼 SQL。查询 API 要做参数校验、权限判断、白名单字段、最大时间窗口、最大行数、脱敏和审计。

第二层是数据处理 CLI。它只读取输入数据文件和配置文件，执行清洗、聚合、SPC、异常检测、相关性、drift 分析等方法。CLI 的优势是可版本化、可测试、可复现。

第三层是绘图输出 CLI。它读取 raw data、stats 和 summary，生成 HTML、PNG、SVG 或报告片段。绘图 CLI 不应该重新查询数据，也不应该重新定义统计方法。

为什么不直接把所有东西写成一个 API？因为数据处理和绘图经常需要版本化和本地复现，CLI 更容易测试和编排。为什么查询一定要 API？因为查询最接近生产数据，必须由服务层管住权限和审计。

## 投影片建议

```text
Query API
  只读、权限、审计、脱敏、schema、row limit

Analysis CLI
  清洗、聚合、SPC、算法、summary、manifest

Plot CLI
  HTML / PNG / SVG、统一样式、plot manifest

Skill
  负责任务判断、三层编排、工程解释、安全停止
```

## 现场类比

可以把三层比成工厂流程：

- Query API 像物料领用：必须按权限、按单据、可追踪。
- Analysis CLI 像工艺处理：方法要稳定，参数要记录。
- Plot CLI 像出货包装：格式统一，标签完整。
- Skill 像作业指导书：告诉人和 Agent 这批任务怎么走流程。

## 互动问题

问：为什么不允许 Agent 直接连生产库？

引导答案：权限、审计、误查询、敏感数据、SQL 注入、性能影响、不可追溯。

---

# 模块 3：Inline SPC Skill 案例

## 讲师目标

用一个具体例子把前面概念串起来。

## 案例描述

Inline SPC 分析用于查询最近 30 天 Inline 测量数据，支持按 product、lot、step、equipment、chamber、recipe、measurement item 筛选。它生成三种图：Mean Plot、Std Plot、Raw Scatter Plot。工程师用它查看测量均值趋势、波动变化、设备间差异和潜在漂移。

## 讲稿

假设用户问：

> 帮我看一下 P1234 最近一个月在 ETCH_CD step 上 ETCH01 和 ETCH02 的 CD_TOP 是否有异常。

Agent 如果没有 Skill，可能会做三件危险的事：随手写 SQL、随手读大表、随手解释异常。Skill 的作用就是把它拉回受控流程。

正确流程是：

```text
1. 解析问题
   product = P1234
   step = ETCH_CD
   equipment = ETCH01, ETCH02
   item = CD_TOP
   window = 30 days

2. 调用 fab-query
   获取 raw.parquet 和 query-manifest.json

3. 检查 manifest
   row_count、time range、schema_version、warnings

4. 调用 fab-analysis inline-spc analyze
   生成 stats.parquet、summary.json、analysis-manifest.json

5. 调用 fab-plot inline-spc render
   生成 mean.html、std.html、scatter.html

6. 输出报告
   问题重述、数据范围、图表、观察、风险、下一步建议
```

## Demo 脚本

如果有 mock 服务，可以现场演示：

```bash
curl http://127.0.0.1:8000/health

python scripts/run_mock_request.py

fab-analysis inline-spc analyze \
  --input artifacts/raw.parquet \
  --config configs/inline-spc.yaml \
  --output artifacts/stats.parquet \
  --summary artifacts/summary.json \
  --manifest artifacts/analysis-manifest.json

fab-plot inline-spc render \
  --raw artifacts/raw.parquet \
  --stats artifacts/stats.parquet \
  --summary artifacts/summary.json \
  --plot all \
  --output-dir artifacts/plots \
  --manifest artifacts/plot-manifest.json
```

如果用 opencode，可以演示：

```text
/inline-spc 分析 P1234 最近 30 天 ETCH_CD step 上 ETCH01 和 ETCH02 的 CD_TOP 均值和标准差趋势
```

## 讲师强调

报告里不能写“建议马上调整 recipe”。更安全的说法是：

> 数据显示 ETCH02 在 CD_TOP 上相对 ETCH01 有持续偏高趋势，建议工程师进一步检查对应 chamber、recipe version、PM 记录和 metrology matching。是否需要 recipe 调整应由工艺 owner 基于更多证据确认。

---

# 模块 4：从历史脚本到 Skill 的 SOP

## 讲师目标

让学员能把自己的脚本按步骤改造，而不是直接把脚本扔给 Agent。

## 讲稿

我们把二次开发 SOP 分成九步。

### 第一步：脚本盘点

先回答这些问题：

```text
服务哪个部门？
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

### 第二步：定义数据 contract

不要直接复用旧脚本里的字段名。先定义标准 schema。Inline 例子包括：

```text
product_id, lot_id, wafer_id, step_id, equipment_id, chamber_id,
recipe_id, measurement_item, measurement_time, measurement_value,
target, ucl, lcl, unit, source_system
```

### 第三步：查询逻辑 API 化

把动态 SQL、get_df、数据库连接、权限校验都收进 API adapter。API 返回 data URI 和 manifest，不要把大量数据直接放进 Agent 上下文。

### 第四步：分析逻辑 CLI 化

把清洗、聚合、统计和算法做成 CLI。输入是文件，输出是文件。不要依赖 Notebook 里的全局变量。

### 第五步：绘图逻辑 CLI 化

Plot CLI 只读 raw、stats、summary，不重新定义统计逻辑。

### 第六步：写 Custom Tool

把 API 和 CLI 包装成 Agent 可调用的工具。工具参数要结构化，description 要清楚。

### 第七步：写 Skill

Skill 写触发条件、参数归一化、工具顺序、manifest 检查、图表解释、报告模板和停止规则。

### 第八步：写 Command

把高频入口做成 `/inline-spc`、`/etch-drift`、`/yield-triage` 等命令。

### 第九步：评审上线

做 mock、golden case、权限检查、安全检查和 Skill review。

## 分组练习

把学员分成 3 到 5 人一组，每组选择一个真实或模拟脚本，完成下面表格：

```text
脚本名称：
服务部门：
典型用户问题：
查询条件：
标准 schema：
Query API endpoint：
Analysis CLI 命令：
Plot CLI 命令：
Skill 名称：
Command 名称：
Stop rules：
```

## 讲师点评重点

点评时不要只看技术是否可行，要看边界是否清楚：

- 是否禁止 Agent 直接连库；
- 是否有标准 schema；
- 是否有 manifest；
- 是否能 mock；
- 是否有 stop rules；
- 是否避免把业务结论说过头。

---

# 模块 5：opencode 实操

## 讲师目标

让学员知道在 opencode 里 Skill 放在哪里、Command 怎么写、Tool 怎么接、权限怎么配。

## 讲稿

opencode 里 Skill 通常放在：

```text
.opencode/skills/<name>/SKILL.md
```

也可以放到全局：

```text
~/.config/opencode/skills/<name>/SKILL.md
```

每个 Skill 的 `SKILL.md` 必须有 frontmatter，至少包括 `name` 和 `description`。description 非常重要，因为 Agent 是先看到 name 和 description，再决定是否加载完整 Skill。

Command 放在：

```text
.opencode/commands/<command>.md
```

Custom Tool 放在：

```text
.opencode/tools/<tool>.ts
```

项目长期规则放在：

```text
AGENTS.md
```

权限放在：

```text
opencode.json
```

## Demo 文件结构

```text
repo/
  AGENTS.md
  opencode.json
  .opencode/
    skills/
      fab-inline-spc-analysis/
        SKILL.md
    commands/
      inline-spc.md
    tools/
      fab-query.ts
      fab-analysis.ts
      fab-plot.ts
```

## 讲师演示 1：Skill

打开 `SKILL.md`，讲解：

```md
---
name: fab-inline-spc-analysis
description: Use for semiconductor inline metrology, process monitoring, SPC trend review...
---
```

强调：description 要写触发条件，不要写成“help analyze data”。

## 讲师演示 2：Command

打开 `.opencode/commands/inline-spc.md`：

```md
---
description: Run approved inline SPC analysis
agent: plan
---

Use the `fab-inline-spc-analysis` skill.

Analyze this request:

$ARGUMENTS

Do not connect directly to production databases.
```

强调：分析类任务默认用 plan agent。

## 讲师演示 3：Permission

打开 `opencode.json`：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "edit": "ask",
    "bash": "ask",
    "skill": {
      "fab-*": "allow",
      "production-*": "deny",
      "experimental-*": "ask"
    }
  },
  "agent": {
    "plan": {
      "permission": {
        "edit": "deny",
        "bash": "ask"
      }
    }
  }
}
```

强调：不要只靠 Skill 文字提醒，权限也要兜底。

---

# 模块 6：练习、评审与答疑

## 练习 1：判断是否适合 Skill 化

给出四个候选脚本：

1. 每天自动汇总 Inline CD 趋势并输出图表。
2. 临时一次性数据修复脚本，会写生产表。
3. FEOL ETCH chamber drift 分析脚本。
4. 某工程师个人探索 Notebook，没有固定输入输出。

建议答案：1 和 3 适合优先 Skill 化；2 不适合直接 Agent 化；4 需要先规范化。

## 练习 2：写一个 description

差例子：

```md
description: analyze semiconductor data
```

好例子：

```md
description: Use for FEOL ETCH chamber drift analysis when the user asks to compare inline metrology, equipment, chamber, recipe, or lot trends over a time window; generate chamber split trend plots and engineering summaries for process stability review.
```

## 练习 3：找 stop rules

让学员给 `etch-chamber-drift-analysis` 写 stop rules。

参考答案：

```text
停止并人工确认：
- 用户要求修改 recipe；
- 用户要求决定 lot hold/release；
- 用户要求扩大查询到敏感产品或客户 lot；
- PM 记录和测量趋势冲突；
- spec / target / control limit 来源不明确；
- 数据样本量不足但用户要求给确定性结论。
```

---

## 常见问题回答脚本

### Q1：Skill 和 prompt 模板有什么区别？

Prompt 模板通常只是一段输入文本。Skill 是可被 Agent 按需发现和加载的能力说明，里面包含触发条件、流程、工具策略、输出格式和停止规则。Skill 通常还会和 references、templates、scripts、custom tools、commands、权限配置一起工作。

### Q2：为什么数据处理和绘图不直接做 API？

可以做，但团队标准建议数据处理和绘图优先 CLI 化。CLI 更适合离线复现、版本控制、测试、批处理和 Agent 编排。查询层最接近生产数据，必须 API 化。

### Q3：Agent 能不能自己判断异常？

可以做初步工程观察，但不能替代工艺 owner 或设备 owner 做生产决策。Skill 输出应使用“数据显示”“建议进一步检查”，避免直接给 recipe 修改、lot 放行、客户结论。

### Q4：MCP 能不能直接接数据库？

技术上可以，但生产数据场景不推荐默认这么做。更安全的做法是把数据库访问收进 Query API，由 API 做权限、审计、脱敏和限流。MCP 更适合接文档、Jira、监控、数据目录等辅助资源。

### Q5：一个 Skill 应该写多长？

`SKILL.md` 应该像控制面，不要写成知识库。详细 schema、业务解释、图表规范可以放到 references；复杂逻辑放 API / CLI / scripts / tools。

---

## 培训结束总结

推荐收尾话术：

今天我们不是学习了一个 AI 小技巧，而是建立了一套团队级智能化改造方法。以后我们不再把脚本直接交给 Agent，而是先拆成 Query API、Analysis CLI、Plot CLI，再用 Skill 编排它们。这样做的目标不是让 Agent 变得“更自由”，而是让 Agent 在受控边界里更稳定、更可复用、更可审计地完成半导体工程分析任务。

你们回去之后，先不要改最大、最复杂的系统。请从一个高频、只读、低风险、输入输出明确的分析脚本开始，把它做成团队第一个可复用 Skill。等这个模式跑通，再迁移 Etch drift、Yield excursion、Device correlation、PIE cross-step、Diff furnace monitoring 等能力。

---

## 讲师课后材料清单

建议培训后发给学员：

```text
1. Skill 学习者手册
2. 新人入门教程
3. opencode 使用教程
4. Inline SPC Skill 样例仓库
5. 脚本盘点表模板
6. Skill Review Checklist
7. Query API / Analysis CLI / Plot CLI 脚手架
```

---

## 参考资料

- OpenCode Agent Skills: https://opencode.ai/docs/skills
- OpenCode Custom Tools: https://opencode.ai/docs/custom-tools/
- OpenCode Commands: https://opencode.ai/docs/commands/
- OpenCode Agents: https://opencode.ai/docs/agents/
- OpenCode Permissions: https://opencode.ai/docs/permissions
- OpenCode Rules / AGENTS.md: https://opencode.ai/docs/rules/
- OpenCode MCP Servers: https://opencode.ai/docs/mcp-servers
- FastAPI Request Body and Pydantic Models: https://fastapi.tiangolo.com/tutorial/body/
- Plotly Interactive HTML Export: https://plotly.com/python/interactive-html-export/
