---
title: "新人入门教程：半导体工程数据分析与 AI Agent / Skill"
subtitle: "给刚入职同学的业务、数据和智能化基础课"
author: "工程数据分析团队 / 数字算法团队"
date: "2026-04-27"
lang: zh-CN
---

# 新人入门教程：半导体工程数据分析与 AI Agent / Skill

## 你将学到什么

这份教程面向刚入职的新同学。假设你还不熟悉半导体制造业务，也不了解 AI Agent 生态，但你可能有一定编程、数据分析或算法基础。

读完后，你应该能理解：

1. 半导体制造中 wafer、lot、process step、tool、chamber、recipe、Inline、WAT、FDC、Yield 等基本概念。
2. 工程数据分析团队为什么服务 YAE、FEOL ETCH、Design、Device、PIE、Diff 等多个部门。
3. 什么是 AI Agent、Tool、Skill、opencode。
4. 为什么我们把分析能力拆成数据查询 API、数据处理 CLI、绘图输出 CLI 三层。
5. 如何安全地使用一个 Skill，例如 Inline SPC 分析 Skill。

---

# 第一部分：半导体制造基础

## 1. 半导体制造在做什么

半导体制造可以简单理解为：在硅片 wafer 上，通过很多道工艺步骤，制造出大量微小的电路结构。每片 wafer 会经历清洗、氧化、沉积、光刻、刻蚀、离子注入、扩散、化学机械研磨、量测、电性测试等步骤。

真实制造流程非常复杂，一个产品可能经历数百道甚至上千道工艺步骤。每一步都可能影响最终器件性能和良率。

工程数据分析团队的任务，就是把这些复杂过程中的数据组织起来，帮助工程师回答问题：

- 哪个产品或 lot 出现异常？
- 哪个工艺 step 可能贡献了波动？
- 哪台设备或哪个 chamber 与异常相关？
- 某个 Inline 指标的均值或波动是否变差？
- 某个 WAT / PCM 参数是否与良率下降相关？
- 某个设计 split 是否带来参数差异？
- 某次设备 PM 或 recipe 变更后是否出现 drift？

---

## 2. 常见制造对象

### Wafer

Wafer 是硅片。可以把它理解为一个圆形载体，上面会制造很多 die。

### Die

Die 是 wafer 上的单个芯片单元。最终切割后，一个 die 可能成为一个芯片。

### Lot

Lot 是生产批次。一个 lot 通常包含多片 wafer。工程分析经常按 lot 追踪工艺历史、测量结果和良率。

### Product

Product 是产品型号或工艺产品。不同 product 可能有不同工艺流程、不同 spec、不同关注指标。

### Process Step

Process step 是制造流程中的某个工艺步骤，例如某个刻蚀步骤、扩散步骤或量测步骤。

### Tool / Equipment

Tool 或 equipment 是设备。例如某台刻蚀机、量测机、扩散炉。

### Chamber

很多设备内部有多个 chamber。即使是同一台设备，不同 chamber 也可能有不同表现。因此 Etch、Deposition、Diff 等场景常常要看 chamber split。

### Recipe

Recipe 是设备执行工艺时使用的参数配方。Recipe 变更通常是高风险动作，Agent 不能直接建议修改 recipe。

---

## 3. 常见数据类型

### Inline 数据

Inline 是制造过程中间量测数据。它通常用于监控工艺过程是否稳定。例子包括 CD、thickness、overlay、resistance 等。

Inline 数据常见字段：

```text
product_id
lot_id
wafer_id
step_id
equipment_id
chamber_id
measurement_item
measurement_time
measurement_value
target
ucl
lcl
unit
```

Inline 分析常见问题：

- 某个 step 的测量均值是否漂移？
- 某台设备或 chamber 是否偏高或偏低？
- 标准差是否变大？
- 原始点是否出现异常散点？

### WAT / PCM 数据

WAT 或 PCM 是 wafer 级电性测试数据，通常用于观察器件参数表现，例如电阻、电压、电流、阈值、漏电等。

常见问题：

- 某个 device 参数是否偏离目标？
- 某个 design split 是否有显著差异？
- WAT 参数是否与最终良率相关？

### FDC / Sensor 数据

FDC 或 sensor 数据来自设备传感器，例如温度、压力、RF power、gas flow、endpoint 信号等。

常见问题：

- 某个 run 的传感器曲线是否异常？
- 某台设备是否 drift？
- PM 前后 sensor 是否有变化？

### MES / Lot History

MES 和 lot history 记录 lot 经过哪些 step、哪些设备、什么时候加工、有没有 hold、rework、skip、merge 等。

常见问题：

- 异常 lot 是否经过同一台设备？
- 某批 wafer 是否经历过特殊 route？
- 工艺时间或排队时间是否异常？

### Yield 数据

Yield 是良率数据，表示芯片或 wafer 的合格比例。Yield 分析通常是多部门协作的结果。

常见问题：

- 哪些 lot 良率下降？
- 哪些 bin fail 增加？
- 良率变化是否与某些 Inline、WAT、tool、recipe、time window 相关？

---

## 4. 常见部门在看什么

### YAE

YAE 通常关注良率异常、bin fail、lot 异常、产品表现和跨模块数据关联。

典型问题：

- 这个产品最近 yield drop 是否与某个 Inline 指标相关？
- 异常 lot 是否集中在某些 tool 或 step？
- 哪些参数最值得进一步排查？

### FEOL ETCH

FEOL ETCH 关注前段刻蚀工艺稳定性、CD 控制、设备差异、chamber 差异、recipe 和 PM 影响。

典型问题：

- 某台 etch tool 的 CD 是否 drift？
- chamber A 和 chamber B 是否有系统性偏差？
- PM 前后是否发生均值变化或波动增加？

### Design

Design 关注设计结构、split、layout、器件目标与数据表现之间的关系。

典型问题：

- 某个 design split 是否改善参数？
- 某些器件结构是否对工艺波动更敏感？

### Device

Device 关注器件电性参数、WAT/PCM、可靠性和工艺参数对器件表现的影响。

典型问题：

- 参数分布是否偏移？
- 阈值、电流、漏电是否与工艺指标相关？

### PIE

PIE 是工艺整合，通常关注跨模块、跨步骤、跨数据域的关联和根因缩小。

典型问题：

- 哪些 process step 与最终良率或 WAT 参数最相关？
- 多个模块的数据是否共同指向某个工艺窗口问题？

### Diff

Diff 关注扩散、炉管、run-to-run 稳定性、tube / boat / slot 差异、温度和时间相关影响。

典型问题：

- 某个 furnace run 是否异常？
- tube 或 slot 是否带来系统性差异？
- run-to-run 波动是否影响 Inline 或 WAT？

---

# 第二部分：工程数据分析基础

## 1. 什么是 schema

Schema 是数据字段和类型的约定。没有 schema，两个脚本可能用不同名字表示同一个东西，例如：

```text
eqp_id, tool_id, equipment_id
meas_time, measurement_time, timestamp
value, raw_value, measurement_value
```

这会导致复用困难。团队标准要求每个数据域都定义标准 schema。

## 2. 什么是过滤条件

半导体分析常见过滤条件包括：

```text
product_id
lot_id
wafer_id
step_id
equipment_id
chamber_id
recipe_id
measurement_item
time_window
```

如果用户没有明确时间范围，很多 Inline 分析默认最近 30 天，但不同数据域可以有不同默认值。

## 3. 什么是聚合

聚合是把多条原始数据按维度汇总。例如：

```text
按 measurement_time + equipment_id + measurement_item 计算均值
按 lot_id + wafer_id + step_id 计算标准差
按 chamber_id 分组计算中位数
```

常见统计值：

```text
mean：均值
std：标准差
median：中位数
count：样本数
min / max：最小值 / 最大值
p25 / p75：分位数
```

## 4. 什么是 SPC

SPC 是 Statistical Process Control，统计过程控制。它用于观察过程是否稳定。常见图包括均值图、标准差图、控制图、原始点散点图。

在工程分析中，需要特别注意：

- target、UCL、LCL、spec limit 的来源必须清楚；
- 不能随便把临时计算的控制限当成官方 spec；
- 样本量不足时不要给强结论；
- 相关性不等于因果。

## 5. 什么是 manifest

Manifest 是一次运行的记录文件。它告诉我们：这次分析用了哪些数据、什么时间范围、哪些过滤条件、多少行、哪个方法版本、生成了哪些图。

示例：

```json
{
  "run_id": "inline-spc-20260427-001",
  "capability": "fab-inline-spc-analysis",
  "schema_version": "inline_measurement.v1",
  "row_count": 10240,
  "filters": {
    "product_ids": ["P1234"],
    "step_ids": ["ETCH_CD"],
    "equipment_ids": ["ETCH01", "ETCH02"]
  },
  "artifacts": {
    "raw": "artifacts/raw.parquet",
    "stats": "artifacts/stats.parquet",
    "plots": ["artifacts/mean.html", "artifacts/std.html"]
  }
}
```

新人需要养成习惯：任何报告结论都应该能追溯到 manifest。

---

# 第三部分：AI Agent 和 Skill 基础

## 1. 大模型是什么

大模型可以理解为一个能理解和生成文本、代码、结构化数据的智能系统。它擅长总结、解释、生成代码、写文档、规划步骤，但它本身不知道你公司的生产系统，也不能天然访问数据库。

## 2. Agent 是什么

Agent 是一个带状态的工作循环。它不是一次性回答，而是多步推进：

```text
接收目标
  ↓
理解当前上下文
  ↓
决定下一步动作
  ↓
调用工具
  ↓
观察结果
  ↓
继续判断
  ↓
完成或停止
```

## 3. Tool 是什么

Tool 是 Agent 能执行的动作。例如：

```text
读取文件
搜索代码
调用 API
运行 CLI
生成图表
访问文档
```

对于生产数据，Tool 必须受控。Agent 不应该直接拿到生产库密码，也不应该随意执行 SQL。

## 4. Skill 是什么

Skill 是给 Agent 的任务说明书。它告诉 Agent：在某类任务里应该怎么做。

例如 Inline SPC Skill 会告诉 Agent：

- 什么时候使用这个 Skill；
- 如何理解用户的 product、lot、step、equipment；
- 调用哪个 query API；
- 运行哪个 analysis CLI；
- 生成哪些 plot；
- 如何解释 Mean Plot、Std Plot、Scatter Plot；
- 什么情况必须停止。

## 5. opencode 是什么

opencode 是我们用来运行 coding / analysis Agent 的工具环境之一。它支持：

- `AGENTS.md`：项目规则；
- `.opencode/skills/`：Skill；
- `.opencode/commands/`：自定义命令；
- `.opencode/tools/`：自定义工具；
- `opencode.json`：权限和配置；
- Plan / Build agent：不同权限的工作模式。

新人只需要先记住：

```text
AGENTS.md 放长期规则
SKILL.md 放某类任务怎么做
commands 放高频入口
tools 放可执行动作
opencode.json 放权限
```

---

# 第四部分：为什么我们采用三层能力架构

一个历史脚本通常会把三件事混在一起：

```text
查数据
处理数据
画图
```

这在个人使用时很方便，但不适合 Agent 复用。因为 Agent 如果直接运行这种脚本，可能不知道：

- 数据从哪里来；
- SQL 是否安全；
- 字段是什么意思；
- 控制限怎么算；
- 图表是否可以公开；
- 输出结论是否过度。

所以我们把它拆成三层：

```text
Query API：查数据
Analysis CLI：处理数据
Plot CLI：画图和输出结果
```

Skill 负责把三层串起来。

---

# 第五部分：Inline SPC 新手示例

## 1. 用户问题

```text
请看一下 P1234 最近 30 天 ETCH_CD step 上 ETCH01 和 ETCH02 的 CD_TOP 测量有没有异常。
```

## 2. Agent 应该怎么理解

```text
数据域：Inline metrology
产品：P1234
步骤：ETCH_CD
设备：ETCH01, ETCH02
测量项：CD_TOP
时间：最近 30 天
目标：看均值、波动和原始点分布
```

## 3. 调用数据查询 API

Agent 通过工具调用 approved API，不直接连生产库。

```json
{
  "product_ids": ["P1234"],
  "step_ids": ["ETCH_CD"],
  "equipment_ids": ["ETCH01", "ETCH02"],
  "measurement_items": ["CD_TOP"],
  "time_window_days": 30
}
```

## 4. 调用分析 CLI

分析 CLI 读取 raw data，计算：

```text
mean by time / equipment / item
std by time / equipment / item
sample_count
target / UCL / LCL
warning flags
```

## 5. 调用绘图 CLI

绘图 CLI 输出：

```text
mean.html
std.html
scatter.html
plot-manifest.json
```

## 6. Agent 输出报告

安全的报告表达：

```text
数据显示，ETCH02 在 CD_TOP 均值上相对 ETCH01 持续偏高，但当前样本范围内尚不能单独判断 recipe 或 chamber 根因。建议进一步检查 chamber split、PM 记录、recipe version、metrology tool matching，并由工艺 owner 确认是否需要扩大分析窗口。
```

不安全的表达：

```text
ETCH02 异常，建议马上修改 recipe。
```

---

# 第六部分：新人 30 天学习计划

## 第 1 周：理解业务和数据

目标：能看懂一个简单 Inline 分析需求。

学习任务：

- 认识 wafer、lot、step、tool、chamber、recipe；
- 看懂 Inline 数据字段；
- 看懂 Mean Plot、Std Plot、Scatter Plot；
- 听一次 YAE 或 PIE 的真实需求讨论。

练习：

```text
找一个历史 Inline 报告，标出 product、lot、step、equipment、measurement item、time window、主要观察。
```

## 第 2 周：理解三层架构

目标：知道脚本为什么要拆成 API / CLI / CLI。

学习任务：

- 运行 mock query API；
- 运行一个 analysis CLI；
- 打开 plot HTML；
- 阅读 manifest。

练习：

```text
解释 raw.parquet、stats.parquet、summary.json、plot-manifest.json 各自作用。
```

## 第 3 周：理解 Agent 和 Skill

目标：能读懂一个 `SKILL.md`。

学习任务：

- 阅读 `fab-inline-spc-analysis/SKILL.md`；
- 找出 description、workflow、output format、stop rules；
- 用 opencode command 发起一次 mock 分析。

练习：

```text
把一个自然语言需求改写成标准参数。
```

## 第 4 周：参与一个小改造

目标：参与把一个低风险脚本改造成 Skill。

学习任务：

- 帮忙整理 schema；
- 写一组 mock 数据；
- 写一个 golden case；
- 给 Skill 加一个 stop rule；
- 参与 code review。

练习：

```text
为一个小脚本填写脚本盘点表。
```

---

# 第七部分：新人安全守则

请牢记这些规则：

```text
1. 不要把生产数据库密码写进 Skill、AGENTS.md、prompt 或代码样例。
2. 不要让 Agent 直接连生产库。
3. 不要让 Agent 自动修改 recipe、spec、target、UCL、LCL。
4. 不要把真实客户、产品、lot、wafer 敏感信息放进公开示例。
5. 不要把相关性写成因果。
6. 不要在样本量不足时给确定性结论。
7. 不要跳过 manifest。
8. 不要用个人 Notebook 输出作为团队正式结果。
9. 高风险结论必须找业务 owner、工艺 owner 或数据 owner 确认。
```

---

# 第八部分：常用词汇表

## Agent

可以多步执行任务的 AI 工作循环。

## Skill

给 Agent 的专业任务 SOP。

## Tool

Agent 可以调用的动作，例如 API 或 CLI。

## CLI

Command Line Interface，命令行工具。

## API

Application Programming Interface，应用接口。

## MCP

一种把外部工具、资源和提示模板接入 Agent 的协议。

## Inline

制造过程中的中间量测数据。

## WAT / PCM

晶圆级电性测试数据。

## FDC

设备传感器和过程监控数据。

## SPC

统计过程控制。

## UCL / LCL

Upper Control Limit / Lower Control Limit，上下控制限。

## Target

目标值。

## Spec

规格限。注意 spec 和 control limit 不是一回事。

## Lot

生产批次。

## Wafer

晶圆。

## Chamber

设备腔体。

## Recipe

设备工艺配方。

## Manifest

一次分析运行的追溯记录。

---

# 第九部分：新人可以问的好问题

当你不确定时，建议这样问：

```text
这个数据源的 owner 是谁？
这个字段的标准含义是什么？
这个 target / UCL / LCL 是官方值还是临时计算值？
这个结论可以对外发送吗？
这个 lot / product 是否敏感？
这个 CLI 是否有 golden case？
这个 Skill 的 stop rules 是否覆盖了当前场景？
这个图表里的异常是设备差异、产品差异、lot 差异还是样本量问题？
```

这些问题比盲目给结论更专业。

---

# 第十部分：参考资料

- OpenCode Agent Skills: https://opencode.ai/docs/skills
- OpenCode Commands: https://opencode.ai/docs/commands/
- OpenCode Custom Tools: https://opencode.ai/docs/custom-tools/
- OpenCode Agents: https://opencode.ai/docs/agents/
- OpenCode Rules / AGENTS.md: https://opencode.ai/docs/rules/
- FastAPI Request Body and Pydantic Models: https://fastapi.tiangolo.com/tutorial/body/
- Plotly Interactive HTML Export: https://plotly.com/python/interactive-html-export/
