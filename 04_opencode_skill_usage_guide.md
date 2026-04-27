---
title: "opencode 使用教程：Skill、Command、Tool 与半导体分析工作流"
subtitle: "面向 Skill 使用和 opencode 基础使用"
author: "工程数据分析团队 / 数字算法团队"
date: "2026-04-27"
lang: zh-CN
---

# opencode 使用教程：Skill、Command、Tool 与半导体分析工作流

## 适用对象

这份教程面向需要在 opencode 中使用、维护或开发 Skill 的工程师。读者包括：

- 数据分析工程师
- 数字算法工程师
- API / CLI 开发工程师
- Skill 维护者
- 刚开始使用 opencode 的团队成员

教程重点不是介绍所有 opencode 功能，而是聚焦我们团队的 Agentic 化工作流：

```text
AGENTS.md：项目长期规则
Skill：某类任务怎么做
Command：高频任务入口
Custom Tool：Agent 可调用的 API / CLI 包装
Permission：安全边界
MCP：外部文档和工具接入
Plan / Build Agent：不同工作模式
```

---

## 1. opencode 在团队里的定位

在半导体工程数据分析团队里，opencode 不是单纯的代码补全工具。它更像一个可配置的 Agent 工作台：

- 可以读取项目规则；
- 可以按需加载 Skill；
- 可以调用工具；
- 可以运行命令；
- 可以在权限控制下帮助你分析代码、改造脚本、生成报告、调试 API/CLI。

我们的推荐用法是：

```text
分析类任务：优先 Plan agent
开发类任务：明确需要改代码时使用 Build agent
生产数据相关任务：只通过 approved API / CLI tool
高频任务：通过 /command 发起
专业流程：通过 Skill 编排
```

---

## 2. 推荐项目目录结构

一个标准半导体分析能力项目可以这样组织：

```text
repo/
  AGENTS.md
  opencode.json

  app/
    api/
      inline_query_api/
    adapters/
      mock_inline_adapter.py
      sql_inline_adapter.py
      legacy_script_adapter.py

  packages/
    fab_analysis/
      inline_spc/
      etch_drift/
      yield_correlation/
    fab_plot/
      inline_spc/
      common_style/

  configs/
    inline-spc.yaml

  artifacts/
    .gitkeep

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
      etch-drift.md
    tools/
      fab-query.ts
      fab-analysis.ts
      fab-plot.ts
```

其中：

- `AGENTS.md` 提供项目通用规则；
- `opencode.json` 配置权限、MCP、额外 instructions；
- `.opencode/skills/` 放 Skill；
- `.opencode/commands/` 放快捷命令；
- `.opencode/tools/` 放 Agent 可调用工具；
- `app/api/` 放数据查询 API；
- `packages/fab_analysis/` 放分析 CLI；
- `packages/fab_plot/` 放绘图 CLI。

---

## 3. AGENTS.md：项目长期规则

opencode 支持通过 `AGENTS.md` 给项目提供自定义规则。团队应把项目结构、构建命令、测试命令、安全边界写在这里。

推荐模板：

```md
# AGENTS.md

## Project overview

This repository provides semiconductor engineering data analysis capabilities for YAE, FEOL ETCH, Design, Device, PIE, and Diff teams.

## Architecture

All analysis capabilities must follow the three-layer pattern:

1. Query API for controlled read-only data access.
2. Analysis CLI for deterministic data processing and algorithms.
3. Plot CLI for HTML / PNG / SVG outputs.

## Safety rules

- Do not connect directly to production databases.
- Do not write production data.
- Do not expose product, lot, wafer, recipe, customer, or yield-sensitive data in examples.
- Do not modify spec, target, UCL, LCL, or recipe logic without human approval.

## Build and test

- Run unit tests with `pytest -q`.
- Run API smoke test with `python scripts/smoke_test.py`.
- Use mock adapters for local development.

## Artifact rules

- Query output must include query-manifest.json.
- Analysis output must include summary.json and analysis-manifest.json.
- Plot output must include plot-manifest.json.
```

建议把项目 `AGENTS.md` 提交到 Git，使团队共享同一套规则。

---

## 4. Skill：专业任务的 SOP

### 4.1 Skill 放在哪里

opencode 会从以下位置发现 Skill：

```text
.opencode/skills/<name>/SKILL.md
~/.config/opencode/skills/<name>/SKILL.md
.claude/skills/<name>/SKILL.md
~/.claude/skills/<name>/SKILL.md
.agents/skills/<name>/SKILL.md
~/.agents/skills/<name>/SKILL.md
```

团队项目内建议优先使用：

```text
.opencode/skills/<name>/SKILL.md
```

个人全局 Skill 可以放到：

```text
~/.config/opencode/skills/<name>/SKILL.md
```

### 4.2 Skill frontmatter

每个 `SKILL.md` 必须以 YAML frontmatter 开头。至少包括：

```md
---
name: fab-inline-spc-analysis
description: Use for semiconductor inline metrology, process monitoring, SPC trend review, quality-control analysis, and yield-analysis support. Trigger when the user asks to query recent inline measurements by product, lot, process step, equipment, chamber, recipe, or measurement item; generate mean, standard-deviation, or raw scatter plots; or assess process stability and equipment variation for YAE, FEOL ETCH, PIE, Device, Design, or Diff teams.
---
```

`description` 非常关键，因为 Agent 会先看到 Skill 名称和描述，再决定是否加载完整 Skill。不要写成：

```md
description: analyze semiconductor data
```

这种描述太泛，容易误触发或不触发。

### 4.3 Skill 正文建议结构

```md
# Fab Inline SPC Analysis

## Purpose

说明这个 Skill 解决什么工程问题。

## Inputs

列出 product、lot、step、equipment、chamber、recipe、measurement item、time window 等参数。

## Workflow

写 query → analysis → plot → report 的顺序。

## Tool strategy

说明用 fab-query、fab-analysis、fab-plot，不直接连生产库。

## Interpretation rules

说明如何解释 mean plot、std plot、scatter plot。

## Output format

规定报告模板。

## Stop rules

列出必须人工确认的场景。
```

### 4.4 Skill 名称规范

建议：

```text
fab-inline-spc-analysis
etch-chamber-drift-analysis
yield-excursion-triage
device-wat-correlation
pie-cross-step-correlation
diff-furnace-run-monitoring
```

避免：

```text
data-helper
analysis-agent
fab-skill
super-tool
```

---

## 5. Command：高频任务入口

opencode 的 custom commands 是放在 `commands/` 目录下的 markdown 文件。团队项目内建议放：

```text
.opencode/commands/<command-name>.md
```

示例：`.opencode/commands/inline-spc.md`

```md
---
description: Run inline SPC analysis through approved query API, analysis CLI, and plot CLI
agent: plan
---

Use the `fab-inline-spc-analysis` skill.

Analyze this request:

$ARGUMENTS

Do not connect directly to production databases.
Do not modify code.
Use approved API/CLI workflow.
Return the standard engineering report.
```

使用方式：

```text
/inline-spc 分析 P1234 最近 30 天 ETCH_CD step 上 ETCH01 和 ETCH02 的 CD_TOP 均值和标准差趋势
```

Command 的价值是把高频任务入口标准化，避免每个用户都用不同说法触发同一流程。

---

## 6. Custom Tool：把 API / CLI 封装给 Agent

opencode custom tool 是 Agent 可以调用的函数。工具定义通常放在：

```text
.opencode/tools/<tool-name>.ts
```

虽然 tool 定义文件是 TypeScript / JavaScript，但里面可以调用 Python、Shell 或其他语言脚本。

### 6.1 fab-query 示例

```ts
import { tool } from "@opencode-ai/plugin"

export default tool({
  description: "Call approved semiconductor data query API and return artifact manifest",
  args: {
    domain: tool.schema.string().describe("Data domain, such as inline, wat, fdc, yield"),
    filters: tool.schema.object({}).describe("Query filters"),
  },
  async execute(args) {
    const response = await fetch(`http://127.0.0.1:8000/api/v1/${args.domain}/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(args.filters),
    })
    if (!response.ok) {
      return `query failed: ${response.status} ${await response.text()}`
    }
    return JSON.stringify(await response.json(), null, 2)
  },
})
```

### 6.2 fab-analysis 示例

```ts
import { tool } from "@opencode-ai/plugin"
import path from "path"

export default tool({
  description: "Run approved fab analysis CLI on an input artifact",
  args: {
    workflow: tool.schema.string().describe("Analysis workflow, such as inline-spc"),
    input: tool.schema.string().describe("Input data path"),
    config: tool.schema.string().describe("Config file path"),
    output_dir: tool.schema.string().describe("Output directory"),
  },
  async execute(args, context) {
    const script = path.join(context.worktree, "tools/run-fab-analysis.py")
    const result = await Bun.$`python3 ${script} ${JSON.stringify(args)}`.text()
    return result.trim()
  },
})
```

### 6.3 Tool 设计原则

```text
一个 tool 只做一个清晰动作。
参数必须结构化。
description 要写清楚什么时候用。
不要暴露生产连接串。
不要让 tool 接收任意 SQL。
返回 manifest 和 artifact 路径，而不是超大数据正文。
失败时返回可读错误。
```

---

## 7. Permission：权限控制

opencode 支持在配置里控制工具行为，例如 allow、ask、deny。团队推荐默认偏保守。

示例 `opencode.json`：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "read": "allow",
    "grep": "allow",
    "glob": "allow",
    "edit": "ask",
    "bash": "ask",
    "webfetch": "allow",
    "skill": {
      "fab-*": "allow",
      "experimental-*": "ask",
      "production-*": "deny"
    }
  },
  "agent": {
    "plan": {
      "permission": {
        "edit": "deny",
        "bash": "ask"
      }
    },
    "build": {
      "permission": {
        "edit": "ask",
        "bash": "ask"
      }
    }
  }
}
```

建议：

- 分析类任务用 Plan agent；
- 需要改代码时才用 Build agent；
- 生产数据查询只能走 approved API tool；
- 高风险 Skill 设置 ask 或 deny；
- bash 默认 ask；
- edit 默认 ask；
- production write 类工具直接 deny。

---

## 8. Plan Agent 与 Build Agent

opencode 内置 primary agents。团队使用时建议这样区分：

### Plan Agent

适合：

```text
需求分析
影响面分析
代码阅读
Skill 流程检查
API/CLI 设计建议
报告生成
```

不适合：

```text
直接改代码
批量重构
运行高风险命令
```

### Build Agent

适合：

```text
创建 API adapter
实现 CLI
修改测试
更新 Skill 文件
修复 bug
```

使用 Build 前建议先让 Plan 产出计划。

### Subagent

Subagent 适合做局部探索，例如：

```text
只读探索某个 repository 中 Inline schema 使用情况
检查某个 CLI 的测试覆盖
搜索 recipe_id 在代码中的来源
```

Subagent 不适合拿来做生产决策。

---

## 9. MCP：外部工具和文档接入

opencode 支持配置 MCP servers。MCP 工具会和内置工具一起提供给 LLM。

推荐使用 MCP 的场景：

```text
Jira / issue：需求和缺陷
Confluence / 文档库：业务规则和 SOP
数据目录：字段解释和数据 owner
监控系统：只读查看运行状态
GitHub / GitLab：PR、issue、代码检索
```

不推荐直接用 MCP 暴露生产数据库的任意查询能力。生产数据查询应该优先走 approved Query API。

示例：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "docs": {
      "type": "remote",
      "url": "https://docs.example.com/mcp",
      "enabled": true
    },
    "jira": {
      "type": "remote",
      "url": "https://jira.example.com/mcp",
      "enabled": true
    }
  }
}
```

注意：MCP 工具会增加上下文，工具太多会让 Agent 选择困难，也可能消耗过多 token。因此不要把所有 MCP 都默认开启。

---

## 10. 从 0 到 1 创建一个 Inline SPC Skill

### Step 1：创建目录

```bash
mkdir -p .opencode/skills/fab-inline-spc-analysis
mkdir -p .opencode/commands
mkdir -p .opencode/tools
```

### Step 2：写 SKILL.md

```bash
cat > .opencode/skills/fab-inline-spc-analysis/SKILL.md <<'MD'
---
name: fab-inline-spc-analysis
description: Use for semiconductor inline metrology, process monitoring, SPC trend review, quality-control analysis, and yield-analysis support. Trigger when the user asks to query recent inline measurements by product, lot, process step, equipment, chamber, recipe, or measurement item; generate mean, standard-deviation, or raw scatter plots; or assess process stability and equipment variation for YAE, FEOL ETCH, PIE, Device, Design, or Diff teams.
---

# Fab Inline SPC Analysis

## Workflow

1. Normalize product, lot, step, equipment, chamber, recipe, measurement item, and time window.
2. Use approved fab-query tool. Never connect directly to production databases.
3. Validate query manifest before analysis.
4. Use fab-analysis with workflow `inline-spc`.
5. Use fab-plot with workflow `inline-spc`.
6. Return standard engineering report with artifact links.
7. Stop before any production-impacting recommendation.

## Output format

Return:

1. Problem restatement
2. Data scope
3. Generated artifacts
4. Key observations
5. Risks and uncertainty
6. Recommended next checks
7. Required human confirmations

## Stop rules

Stop and ask before:

- expanding query scope to sensitive data;
- changing target, spec, UCL, or LCL logic;
- recommending recipe change or lot hold/release;
- exposing sensitive product, lot, wafer, recipe, customer, or yield information.
MD
```

### Step 3：写 command

```bash
cat > .opencode/commands/inline-spc.md <<'MD'
---
description: Run approved inline SPC analysis
agent: plan
---

Use the `fab-inline-spc-analysis` skill.

Analyze this request:

$ARGUMENTS

Use approved API/CLI workflow only. Do not connect directly to production databases. Return the standard engineering report.
MD
```

### Step 4：写 tool

先写一个 mock tool，后续再接真实 API / CLI。

```ts
import { tool } from "@opencode-ai/plugin"

export default tool({
  description: "Mock inline SPC workflow for local testing",
  args: {
    product_id: tool.schema.string(),
    step_id: tool.schema.string(),
    equipment_ids: tool.schema.array(tool.schema.string()),
    measurement_item: tool.schema.string(),
    time_window_days: tool.schema.number().default(30),
  },
  async execute(args) {
    return JSON.stringify({
      run_id: "mock-inline-spc-001",
      query_manifest: "artifacts/query-manifest.json",
      analysis_manifest: "artifacts/analysis-manifest.json",
      plot_manifest: "artifacts/plot-manifest.json",
      plots: ["artifacts/mean.html", "artifacts/std.html", "artifacts/scatter.html"],
      summary: "Mock workflow completed. Replace this tool with approved API/CLI adapters."
    }, null, 2)
  },
})
```

### Step 5：配置权限

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "skill": {
      "fab-inline-spc-analysis": "allow",
      "experimental-*": "ask"
    },
    "edit": "ask",
    "bash": "ask"
  },
  "agent": {
    "plan": {
      "permission": {
        "edit": "deny"
      }
    }
  }
}
```

### Step 6：试用

在 opencode 中输入：

```text
/inline-spc 分析 P1234 最近 30 天 ETCH_CD step 上 ETCH01 和 ETCH02 的 CD_TOP 均值和标准差趋势
```

观察 Agent 是否：

```text
正确加载 Skill
正确识别参数
不直接连库
使用 approved tool
检查 manifest
输出标准报告
遇到高风险场景会停止
```

---

## 11. 常见操作手册

### 11.1 Skill 没有被发现

检查：

```text
[ ] 文件名是否是 SKILL.md，且全大写
[ ] 路径是否是 .opencode/skills/<name>/SKILL.md
[ ] frontmatter 是否包含 name 和 description
[ ] name 是否和目录名一致
[ ] name 是否只用小写字母、数字和单个连字符
[ ] opencode.json 是否把该 skill deny 了
[ ] 是否有重名 Skill
```

### 11.2 Command 没有出现

检查：

```text
[ ] 文件是否在 .opencode/commands/
[ ] 文件后缀是否是 .md
[ ] frontmatter 是否正确闭合
[ ] command 名是否和文件名一致
```

### 11.3 Tool 调用失败

检查：

```text
[ ] .opencode/tools/<name>.ts 是否存在
[ ] tool description 是否清楚
[ ] args schema 是否正确
[ ] 被调用脚本路径是否基于 context.worktree
[ ] API 服务是否启动
[ ] CLI 是否可执行
[ ] 权限是否被 deny 或 ask 未批准
[ ] 返回值是否过大
```

### 11.4 Agent 开始乱跑

处理：

```text
1. 停止当前任务。
2. 检查 Skill 是否缺少 workflow 或 stop rules。
3. 检查 command 是否太泛。
4. 检查 tool description 是否不明确。
5. 把高风险工具改成 ask 或 deny。
6. 把复杂业务规则拆进 references。
```

---

## 12. 半导体分析 Skill 开发规范

### 12.1 必须包含

```text
[ ] 明确的 name 和 description
[ ] 业务目的
[ ] 输入参数
[ ] 默认时间范围
[ ] 三层调用顺序
[ ] manifest 检查规则
[ ] 输出模板
[ ] 图表解释规则
[ ] stop rules
[ ] 安全与敏感数据规则
```

### 12.2 不允许包含

```text
[ ] 生产数据库连接串
[ ] 密钥或 token
[ ] 真实敏感 product / lot / wafer / customer 示例
[ ] 任意 SQL 模板
[ ] 直接修改 recipe / spec 的指令
[ ] 绕过权限的提示
```

### 12.3 推荐 Skill 类型

```text
fab-inline-spc-analysis
etch-chamber-drift-analysis
yield-excursion-triage
device-wat-correlation
pie-cross-step-correlation
diff-furnace-run-monitoring
fdc-run-anomaly-review
metrology-tool-matching
```

---

## 13. 团队日常使用建议

### 分析一个业务问题

```text
1. 用 /inline-spc、/etch-drift 等 command 发起。
2. 优先使用 Plan agent。
3. 检查 Agent 是否使用了正确 Skill。
4. 检查数据范围和 manifest。
5. 阅读图表和 summary。
6. 对高风险结论找 owner 确认。
```

### 改造一个脚本

```text
1. 用 Plan agent 让它阅读脚本并拆分 query / analysis / plot。
2. 人工确认拆分方案。
3. 用 Build agent 实现 API adapter 或 CLI。
4. 添加 mock 和 golden tests。
5. 写 Skill 和 command。
6. 做 Skill review。
```

### 审查一个 Skill

```text
1. description 是否精确。
2. workflow 是否能执行。
3. 工具顺序是否合理。
4. 是否禁止直接连库。
5. 是否有 manifest 规则。
6. 是否有 stop rules。
7. 输出是否适合工程师使用。
```

---

## 14. 最小可用配置模板

### opencode.json

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "read": "allow",
    "grep": "allow",
    "glob": "allow",
    "edit": "ask",
    "bash": "ask",
    "skill": {
      "fab-*": "allow",
      "experimental-*": "ask",
      "production-*": "deny"
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

### Skill review checklist

```text
[ ] name 符合规范
[ ] description 明确触发条件
[ ] workflow 有顺序
[ ] query 通过 API
[ ] analysis 通过 CLI
[ ] plot 通过 CLI
[ ] 输出报告模板清楚
[ ] stop rules 完整
[ ] 无敏感信息
[ ] mock case 可跑
```

---

## 15. 参考资料

- OpenCode Agent Skills: https://opencode.ai/docs/skills
- OpenCode Custom Tools: https://opencode.ai/docs/custom-tools/
- OpenCode Commands: https://opencode.ai/docs/commands/
- OpenCode Agents: https://opencode.ai/docs/agents/
- OpenCode Permissions: https://opencode.ai/docs/permissions
- OpenCode Tools: https://opencode.ai/docs/tools/
- OpenCode Rules / AGENTS.md: https://opencode.ai/docs/rules/
- OpenCode MCP Servers: https://opencode.ai/docs/mcp-servers
- FastAPI Request Body and Pydantic Models: https://fastapi.tiangolo.com/tutorial/body/
- Plotly Interactive HTML Export: https://plotly.com/python/interactive-html-export/
