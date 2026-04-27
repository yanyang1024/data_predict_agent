# opencode Skill 编写实战教程

## 从一段简单 Python 数据处理脚本，到 tool、command、Skill

**适用对象**：半导体公司工程数据分析团队、数字算法团队、数字业务工程师、内部培训讲师。  
**训练目标**：用一个最小但完整的数据分析流程，练会如何把 Python 脚本改造成 opencode 可使用的 custom tool、command 和 Skill。  
**样例范围**：只处理本地 CSV，不连接数据库，不调用生产服务，不修改输入数据。  
**样例产物**：`summary.json`、`group_summary.csv`、`trend.html`、`manifest.json`。

---

## 0. 这篇实战文档解决什么问题

很多团队已经有大量 Python 脚本：读 CSV 或数据库结果、清洗数据、分组统计、画图、输出 HTML 或 Excel。把这些脚本“接入 Agent”时，常见错误是让 Agent 直接读脚本、猜参数、跑命令、改代码、甚至临时拼 SQL。

本教程给一个更安全、更可复用的改造路径：

```text
普通 Python 函数
  ↓
可复用 Python 模块
  ↓
稳定 CLI
  ↓
opencode custom tool
  ↓
opencode command
  ↓
opencode skill
  ↓
Agent 按 SOP 使用工具、解释结果、输出报告
```

这个样例很简单，但它完整体现了 Skill 的定位：

> **Skill 不负责替代算法代码；Skill 负责告诉 Agent 什么时候使用某个能力、如何组织输入、如何调用 approved tool、如何读取结果、如何解释产物、什么时候停止。**

---

## 1. 最终样例工程结构

随本文档附带一个完整样例工程：`simple-data-profile-sample`。

```text
sample_project/
├── AGENTS.md
├── README.md
├── opencode.json
├── requirements.txt
├── simple_profile_cli.py
├── data/
│   └── sample_measurements.csv
├── scripts/
│   └── original_simple_script.py
├── src/
│   └── simple_profile/
│       ├── __init__.py
│       └── core.py
├── artifacts/
│   └── simple-profile/
│       ├── summary.json
│       ├── group_summary.csv
│       ├── trend.html
│       └── manifest.json
└── .opencode/
    ├── commands/
    │   └── profile-data.md
    ├── tools/
    │   └── data-profile.ts
    └── skills/
        └── simple-data-quality-analysis/
            ├── SKILL.md
            ├── references/
            │   ├── data-contract.md
            │   └── report-template.md
            └── examples/
                ├── mini-request.md
                └── session-context-walkthrough.md
```

opencode 的 Skill 会从项目或全局目录发现 `SKILL.md`；项目内常用路径是 `.opencode/skills/<name>/SKILL.md`。Skill 的 `name` 和 `description` 会先被 Agent 看到，完整内容则通过原生 `skill` tool 按需加载。因此，`SKILL.md` 不是普通 README，而是 Agent 能力路由和执行 SOP。

---

## 2. 快速跑通样例

进入样例工程：

```bash
cd sample_project
python3 -m pip install -r requirements.txt
```

执行 CLI：

```bash
python3 simple_profile_cli.py \
  --input data/sample_measurements.csv \
  --value-column measurement_value \
  --group-column equipment_id \
  --time-column measurement_time \
  --output-dir artifacts/simple-profile
```

你会看到类似输出：

```json
{
  "capability": "simple-data-quality-analysis",
  "version": "0.1.0",
  "input_path": "data/sample_measurements.csv",
  "output_dir": "artifacts/simple-profile",
  "outputs": {
    "summary": "artifacts/simple-profile/summary.json",
    "group_summary": "artifacts/simple-profile/group_summary.csv",
    "trend_html": "artifacts/simple-profile/trend.html"
  },
  "row_count": 90,
  "valid_value_count": 89,
  "outlier_count": 1,
  "warnings": [
    "value column contains missing or non-numeric values",
    "potential outliers detected by z-score rule"
  ]
}
```

这就是后续 custom tool 要返回给 Agent 的最小信息。注意：不要把整份 CSV 或大图内容塞进上下文。Agent 需要的是 compact manifest、summary 和 artifact 路径。

---

## 3. 第一步：从一段普通 Python 脚本开始

假设原始脚本长这样：

```python
from __future__ import annotations

import json
from pathlib import Path
import pandas as pd


def analyze_csv(input_path: str, value_column: str, group_column: str | None = None) -> dict:
    df = pd.read_csv(input_path)
    df = df.dropna(subset=[value_column]).copy()
    df[value_column] = pd.to_numeric(df[value_column], errors="coerce")
    df = df.dropna(subset=[value_column])

    summary = {
        "row_count": int(len(df)),
        "value_column": value_column,
        "mean": float(df[value_column].mean()),
        "std": float(df[value_column].std(ddof=1)),
        "min": float(df[value_column].min()),
        "max": float(df[value_column].max()),
    }

    if group_column:
        grouped = (
            df.groupby(group_column)[value_column]
            .agg(["count", "mean", "std", "min", "max"])
            .reset_index()
        )
        summary["group_summary"] = grouped.to_dict(orient="records")

    return summary
```

这个脚本可以跑，但还不适合 Agent 复用，原因有四个：

1. 参数入口不稳定。Agent 不知道哪些参数必须提供。
2. 输出不稳定。一次返回 dict，一次可能 print 文本，后续很难自动读取。
3. 没有 artifact contract。图、表、summary、manifest 没有固定位置。
4. 没有 stop rule。Agent 可能把它扩展到生产数据或任意文件。

改造目标不是让脚本“更智能”，而是让它**更像一个稳定工程接口**。

---

## 4. 第二步：把脚本拆成 core 模块

先把核心逻辑放到 `src/simple_profile/core.py`，让它成为可测试、可复用的模块。

关键设计：

```python
@dataclass(frozen=True)
class ProfileConfig:
    input_path: Path
    value_column: str
    group_column: str | None = None
    time_column: str | None = None
    output_dir: Path = Path("artifacts/simple-profile")
    z_threshold: float = 3.0
```

然后拆成四个函数：

```text
load_and_clean()
  读取 CSV，检查列，做类型转换。

compute_profile()
  计算 row count、missing count、mean、std、min、max、outlier_count、group summary。

render_trend()
  生成一个简单 Plotly HTML trend plot。

run_profile()
  串联前面步骤，写出 summary、group_summary、trend、manifest。
```

这里的关键不是算法复杂，而是边界清晰：

```text
core.py 负责处理数据和输出结果。
它不关心 opencode，也不关心 Skill。
它不连接数据库，不读生产服务，不改输入文件。
```

这一步对应半导体团队常见三层架构中的第二、第三层：数据处理和结果输出。查询层在本实战里被刻意省略，只使用本地 CSV。

---

## 5. 第三步：把模块包装成 CLI

Agent 不应该 import 你的函数并猜怎么调用。更好的方式是给它一个稳定 CLI。

`simple_profile_cli.py`：

```python
from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.simple_profile.core import ProfileConfig, run_profile


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a simple local data profile and generate summary artifacts.")
    parser.add_argument("--input", required=True, help="Input CSV path")
    parser.add_argument("--value-column", required=True, help="Numeric column to analyze")
    parser.add_argument("--group-column", default=None, help="Optional group column, such as equipment_id")
    parser.add_argument("--time-column", default=None, help="Optional time column for trend plots")
    parser.add_argument("--output-dir", default="artifacts/simple-profile", help="Artifact output directory")
    parser.add_argument("--z-threshold", default=3.0, type=float, help="Outlier threshold in absolute z-score")
    args = parser.parse_args()

    manifest = run_profile(
        ProfileConfig(
            input_path=Path(args.input),
            value_column=args.value_column,
            group_column=args.group_column,
            time_column=args.time_column,
            output_dir=Path(args.output_dir),
            z_threshold=args.z_threshold,
        )
    )
    print(json.dumps(manifest, ensure_ascii=False))


if __name__ == "__main__":
    main()
```

CLI 的好处：

```text
人可以跑。
CI 可以跑。
Agent 可以通过 tool 安全调用。
参数有明确名称。
输出是机器可读 JSON。
artifact 路径固定。
```

CLI 验收标准：

```text
[ ] 必填参数明确
[ ] 输出 JSON manifest
[ ] 不依赖 notebook 状态
[ ] 不连接数据库
[ ] 不修改输入文件
[ ] 空数据、缺列、类型错误有清楚报错
[ ] 同样输入重复运行结果一致
```

---

## 6. 第四步：把 CLI 包装成 opencode custom tool

opencode custom tool 是 LLM 可以调用的函数。官方文档说明，custom tool 用 TypeScript 或 JavaScript 定义，但 tool definition 可以调用任意语言写的脚本，所以我们用 TS wrapper 调 Python CLI。

`.opencode/tools/data-profile.ts`：

```ts
import { tool } from "@opencode-ai/plugin"
import path from "path"

export default tool({
  description: "Run the approved local simple data profile CLI on a CSV file and return a compact manifest. Use for local training datasets or non-production exported measurement files.",
  args: {
    input_path: tool.schema.string().describe("Path to a local CSV file, relative to the project root when possible"),
    value_column: tool.schema.string().describe("Numeric value column to analyze"),
    group_column: tool.schema.string().optional().describe("Optional group column, such as equipment_id"),
    time_column: tool.schema.string().optional().describe("Optional timestamp column used for trend plot"),
    output_dir: tool.schema.string().optional().describe("Output directory for artifacts"),
    z_threshold: tool.schema.number().optional().describe("Absolute z-score threshold used for outlier flagging"),
  },
  async execute(args, context) {
    const script = path.join(context.worktree, "simple_profile_cli.py")
    const outputDir = args.output_dir ?? "artifacts/simple-profile"
    const zThreshold = args.z_threshold ?? 3.0

    const cmd = [
      "python3",
      script,
      "--input",
      args.input_path,
      "--value-column",
      args.value_column,
      "--output-dir",
      outputDir,
      "--z-threshold",
      String(zThreshold),
    ]

    if (args.group_column) {
      cmd.push("--group-column", args.group_column)
    }
    if (args.time_column) {
      cmd.push("--time-column", args.time_column)
    }

    const result = await Bun.$`${cmd}`.text()
    return result.trim()
  },
})
```

这个 tool 的定位是“安全动作接口”：

```text
Skill 负责说什么时候用 data-profile。
data-profile tool 负责稳定执行 CLI。
CLI 负责真正处理数据和输出 artifact。
```

不要把所有逻辑都写进 tool。tool 越薄，越容易复用和测试。

---

## 7. 第五步：创建 opencode command

Command 是给人的快捷入口。它不是 Skill，也不是 Tool，而是把一个常用 prompt 固化成 `/命令`。

`.opencode/commands/profile-data.md`：

```md
---
description: Run simple local data profiling using the approved skill and tool
agent: plan
---

Use the `simple-data-quality-analysis` skill.

Analyze this local dataset request:

$ARGUMENTS

Rules:
- Use the approved `data-profile` custom tool when execution is needed.
- Do not connect to any database or production service.
- Do not edit the input dataset.
- Return the standard report defined by the skill.
```

使用方式：

```text
/profile-data data/sample_measurements.csv measurement_value equipment_id measurement_time
```

opencode command 的价值是降低使用门槛。培训对象不需要记住完整 prompt，只需要知道 `/profile-data`。

注意：command 只是“入口 prompt”，真正的 SOP 仍然应该写在 Skill 中。

---

## 8. 第六步：写完整 Skill 结构

Skill 目录：

```text
.opencode/skills/simple-data-quality-analysis/
├── SKILL.md
├── references/
│   ├── data-contract.md
│   └── report-template.md
└── examples/
    ├── mini-request.md
    └── session-context-walkthrough.md
```

### 8.1 SKILL.md

```md
---
name: simple-data-quality-analysis
description: Profile a local CSV dataset for training or non-production data analysis. Use when the user asks to summarize one numeric column, compare groups, detect simple outliers, generate a trend plot, or turn a small Python data-processing script into a reusable opencode tool, command, and skill workflow.
license: internal
compatibility: opencode
metadata:
  owner: data-analysis-enablement
  version: "0.1.0"
---

# Simple Data Quality Analysis

## Purpose

Use this skill to run a small, safe, repeatable local data analysis workflow. The workflow reads a local CSV, analyzes one numeric value column, optionally compares groups, generates a simple trend HTML plot, and returns a concise engineering-style report.

This is a training skill. It intentionally avoids production databases, private APIs, model training, and complex semiconductor domain logic.

## Default workflow

1. Restate the user's analysis goal.
2. Identify the required parameters:
   - input CSV path
   - value column
   - optional group column
   - optional time column
   - optional output directory
3. If parameters are missing, ask one short clarification question.
4. Use the `data-profile` custom tool to run the approved CLI.
5. Inspect the returned manifest and summary paths.
6. If necessary, read only `summary.json` and `group_summary.csv`; do not load the full raw dataset into context.
7. Return the standard report format from `references/report-template.md`.

## Tool policy

Use `data-profile` for execution. Do not run ad-hoc Python through `bash` unless the approved custom tool is unavailable and the user explicitly asks for manual debugging.

Do not use this skill for:
- production database access
- SQL query generation
- recipe/spec/control-limit decisions
- large confidential datasets
- automated file modification

## Output policy

Always mention:
- analyzed file path
- value column
- group column, if provided
- output artifacts
- row count
- missing value count
- outlier count
- top group differences, when group summary exists
- limitations and recommended next checks

## Stop rules

Stop and ask before:
- reading a dataset larger than the local training scope
- using production data
- changing input files
- changing the CLI algorithm
- treating z-score outliers as confirmed process anomalies

## References

Read these only when needed:
- `references/data-contract.md` for required columns and artifact contract.
- `references/report-template.md` for the final response template.
- `examples/session-context-walkthrough.md` to explain how opencode context changes after command and skill loading.
```

### 8.2 reference：数据契约

`references/data-contract.md`：

```md
# Data Contract

## Input

The input is a local CSV file. Minimum required column:

- `measurement_value`: numeric column to analyze, or another numeric column explicitly provided by the user.

Recommended optional columns:

- `measurement_time`: timestamp used for trend plotting.
- `equipment_id`: group column for simple tool/equipment comparison.
- `measurement_item`: measurement item label.
- `lot_id`: lot label for human interpretation only.

## Outputs

The approved CLI writes:

- `summary.json`: compact machine-readable analysis summary.
- `group_summary.csv`: group-level count, mean, std, min, max.
- `trend.html`: interactive Plotly HTML scatter plot.
- `manifest.json`: artifact registry and warnings.

## Interpretation rules

- Missing and non-numeric values are excluded from numeric statistics.
- Outliers are flagged by absolute z-score threshold. This is a screening signal, not a confirmed root cause.
- Group differences should be described as observations unless domain evidence confirms causality.
```

### 8.3 reference：输出模板

`references/report-template.md`：

```md
# Report Template

Use this structure:

## Analysis summary

- Dataset:
- Value column:
- Group column:
- Time column:
- Row count:
- Valid value count:
- Missing value count:
- Outlier count:

## Key observations

1. [Observation with evidence]
2. [Observation with evidence]
3. [Observation with evidence]

## Artifacts

- Summary JSON:
- Group summary CSV:
- Trend HTML:

## Limitations

- This is a local screening analysis.
- Outlier flags require engineering confirmation.
- This workflow does not query production systems or change data.

## Recommended next checks

- [Next check 1]
- [Next check 2]
```

Skill 的好坏主要取决于三个点：

```text
description 是否能正确触发；
workflow 是否让 Agent 少走弯路；
stop rules 是否能阻止危险扩展。
```

---

## 9. 第七步：配置 AGENTS.md 和 opencode.json

### 9.1 AGENTS.md

`AGENTS.md` 是项目规则，适合放所有 session 都应该知道的长期规则。

```md
# Project Instructions

This repository is a training project for opencode skill and tool practice.

## Rules

- Use local sample data only.
- Do not connect to production databases or internal APIs.
- Prefer the `data-profile` custom tool over ad-hoc shell commands.
- Keep outputs in `artifacts/`.
- Treat outlier detection as screening, not root-cause proof.

## Validation

Run the sample CLI with:

```bash
python3 simple_profile_cli.py --input data/sample_measurements.csv --value-column measurement_value --group-column equipment_id --time-column measurement_time --output-dir artifacts/simple-profile
```
```

Skill 和 AGENTS.md 的边界：

```text
AGENTS.md：项目通用规则，所有任务都加载。
Skill：某类任务的方法论，相关时才加载。
references：更细资料，需要时才读。
tool：可执行动作接口。
command：给人的快捷入口。
```

### 9.2 opencode.json

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "skill": "allow",
    "read": "allow",
    "glob": "allow",
    "grep": "allow",
    "bash": "ask",
    "edit": "deny"
  },
  "agent": {
    "plan": {
      "permission": {
        "edit": "deny",
        "bash": "ask",
        "skill": "allow"
      }
    }
  }
}
```

培训时建议默认使用 `plan` agent，因为它适合分析、规划和报告，不适合自动改文件。对于数据分析类 Skill，默认 `edit: deny` 更安全。

---

## 10. opencode 加载 Skill 时，session 上下文如何变化

这是培训中最重要的一段。很多人以为 Skill 一启动就把所有内容塞进模型上下文。正确理解应该是：**先暴露轻量描述，相关时再加载完整 Skill，必要时再读取 references 或运行工具。**

下面用一次对话样例说明。

### 阶段 A：session 刚开始

用户还没发分析请求时，Agent 的上下文大概包含：

```text
系统指令 / 模型运行时指令
+ 当前会话历史
+ 项目 AGENTS.md 规则
+ 可用工具列表
+ skill tool 的描述
+ available_skills 的 name 和 description
```

此时并不会把完整 `SKILL.md`、`references/data-contract.md`、`report-template.md` 全部塞进去。它只看到类似：

```xml
<available_skills>
  <skill>
    <name>simple-data-quality-analysis</name>
    <description>Profile a local CSV dataset for training or non-production data analysis...</description>
  </skill>
</available_skills>
```

这就是为什么 `description` 要写清楚：它决定 Agent 会不会想起这个 Skill。

### 阶段 B：用户输入 command

用户输入：

```text
/profile-data data/sample_measurements.csv measurement_value equipment_id measurement_time
```

opencode 把 command 展开成 prompt：

```text
Use the `simple-data-quality-analysis` skill.

Analyze this local dataset request:

data/sample_measurements.csv measurement_value equipment_id measurement_time

Rules:
- Use the approved `data-profile` custom tool when execution is needed.
- Do not connect to any database or production service.
- Do not edit the input dataset.
- Return the standard report defined by the skill.
```

此时上下文新增的是 command 模板展开后的内容，不是 Skill 全文。

### 阶段 C：Agent 决定加载 Skill

Agent 根据 command 和 available skills 调用：

```json
skill({ "name": "simple-data-quality-analysis" })
```

工具返回完整 `SKILL.md` 后，session 上下文新增：

```text
+ simple-data-quality-analysis/SKILL.md 全文
```

Agent 现在才知道完整 workflow、tool policy、output policy、stop rules、references 导航。

### 阶段 D：Agent 调用 custom tool

Agent 根据 Skill 选择 approved tool：

```json
{
  "tool": "data-profile",
  "arguments": {
    "input_path": "data/sample_measurements.csv",
    "value_column": "measurement_value",
    "group_column": "equipment_id",
    "time_column": "measurement_time",
    "output_dir": "artifacts/simple-profile"
  }
}
```

Tool 返回 compact manifest：

```json
{
  "capability": "simple-data-quality-analysis",
  "outputs": {
    "summary": "artifacts/simple-profile/summary.json",
    "group_summary": "artifacts/simple-profile/group_summary.csv",
    "trend_html": "artifacts/simple-profile/trend.html"
  },
  "row_count": 90,
  "valid_value_count": 89,
  "outlier_count": 1,
  "warnings": [
    "value column contains missing or non-numeric values",
    "potential outliers detected by z-score rule"
  ]
}
```

上下文新增的是这个 compact tool result，而不是完整 CSV，也不是完整 HTML。

### 阶段 E：Agent 按需读取 reference 或 artifact

如果 Agent 不确定输出格式，它可以读：

```text
.opencode/skills/simple-data-quality-analysis/references/report-template.md
```

如果需要更具体的数据，它可以读：

```text
artifacts/simple-profile/summary.json
artifacts/simple-profile/group_summary.csv
```

但它不应该读完整 `data/sample_measurements.csv`，除非用户明确要求人工检查原始数据。

### 阶段 F：Agent 输出报告

最终输出应该像这样：

```text
## Analysis summary

- Dataset: data/sample_measurements.csv
- Value column: measurement_value
- Group column: equipment_id
- Time column: measurement_time
- Row count: 90
- Valid value count: 89
- Missing value count: 1
- Outlier count: 1

## Key observations

1. 数据集中有 1 条缺失或非数值 measurement_value，已从数值统计中排除。
2. z-score 规则发现 1 个潜在离群点，需要工程确认，不可直接判断为制程异常。
3. 已按 equipment_id 输出 group_summary.csv，可进一步比较不同设备的均值和波动。

## Artifacts

- Summary JSON: artifacts/simple-profile/summary.json
- Group summary CSV: artifacts/simple-profile/group_summary.csv
- Trend HTML: artifacts/simple-profile/trend.html

## Limitations

这是本地训练数据分析，不连接生产系统，不代表正式 SPC 结论。
```

这就是 Skill 加载带来的上下文变化：

```text
初始：只知道有这个 Skill
Command 后：知道用户要用这个 Skill
Skill tool 后：拿到完整 SOP
Custom tool 后：拿到 compact 结果
Reference/artifact 后：补充必要细节
Final 后：输出标准报告
```

---

## 11. 为什么这个例子符合 Skill 的定位

这个例子只有一列数值、一个分组列和一个趋势图，看起来很简单，但它符合 Skill 最核心的要求：

```text
有明确触发场景：本地 CSV 数据 profile。
有稳定输入：input path、value column、group column、time column。
有 approved tool：data-profile。
有确定产物：summary、group summary、trend HTML、manifest。
有输出模板：report-template.md。
有解释边界：outlier 是筛查信号，不是根因。
有 stop rules：不查生产库、不改输入、不擅自扩大范围。
```

这比“写一个万能数据分析 Skill”更适合作为培训样例。

---

## 12. 课堂练习

### 练习 1：改输出目录

运行：

```bash
python3 simple_profile_cli.py \
  --input data/sample_measurements.csv \
  --value-column measurement_value \
  --group-column equipment_id \
  --time-column measurement_time \
  --output-dir artifacts/practice-01
```

检查：

```text
artifacts/practice-01/summary.json
artifacts/practice-01/group_summary.csv
artifacts/practice-01/trend.html
artifacts/practice-01/manifest.json
```

### 练习 2：改 Skill description

把 description 改得更窄：

```text
Use only for local CSV measurement_value profiling in training projects.
```

讨论：

```text
变窄后误触发减少，但泛化能力下降。
```

### 练习 3：增加一个 reference

新增：

```text
.opencode/skills/simple-data-quality-analysis/references/outlier-rules.md
```

内容写清楚：

```text
z-score outlier is a screening method, not a process-control rule.
```

然后在 `SKILL.md` 的 References 里加上它。

### 练习 4：把 group column 从 equipment_id 改成 product_id

运行：

```bash
python3 simple_profile_cli.py \
  --input data/sample_measurements.csv \
  --value-column measurement_value \
  --group-column product_id \
  --time-column measurement_time \
  --output-dir artifacts/by-product
```

观察 group summary 变化。

### 练习 5：设计一个半导体版本 Skill

把这个训练 Skill 改造成：

```text
inline-csv-screening-analysis
```

要求：

```text
输入：导出的 inline CSV
输出：mean/std/scatter 三类基础观察
stop rule：不得声称正式 SPC 结论
reference：inline 字段说明、图表解释模板
```

---

## 13. 从训练样例迁移到真实半导体分析能力

训练样例只做本地 CSV。真实团队能力通常应该升级成三层：

```text
数据查询 API
  负责权限、审计、参数校验、生产数据访问。

数据处理 CLI
  负责清洗、聚合、统计、算法、summary、manifest。

绘图输出 CLI
  负责 HTML、PNG、报告草稿和 plot manifest。
```

对应到 Skill：

```text
Skill 不直接拼 SQL。
Skill 不直接改算法。
Skill 不直接画临时图。
Skill 负责组合 approved API/CLI/tool，并解释结果。
```

如果从本样例扩展到 Inline SPC：

```text
simple_profile_cli.py
  → fab-analysis inline-spc analyze

data-profile custom tool
  → inline-spc-analysis custom tool

simple-data-quality-analysis Skill
  → fab-inline-spc-analysis Skill

summary.json / group_summary.csv / trend.html
  → raw.parquet / stats.parquet / mean.html / std.html / scatter.html / manifest.json
```

迁移时保留的设计原则：

```text
输入契约稳定。
输出 artifact 稳定。
Tool 返回 compact manifest。
Skill 只加载必要 reference。
生产查询只能走 API。
高风险结论必须人工确认。
```

---

## 14. 实战检查清单

当一个同学说“我已经把脚本做成 Skill 了”，检查这些项：

```text
[ ] 原始脚本已经拆出 core 函数
[ ] 有 CLI，参数明确
[ ] CLI 输出 JSON manifest
[ ] 有固定 artifact 路径
[ ] 有 opencode custom tool
[ ] custom tool 返回 compact result
[ ] 有 opencode command
[ ] 有 SKILL.md
[ ] Skill description 写清触发场景
[ ] Skill workflow 指定 tool 使用顺序
[ ] Skill output policy 指定报告格式
[ ] Skill stop rules 明确禁止生产/危险操作
[ ] references 拆出数据契约和输出模板
[ ] examples 提供请求样例和 session context walkthrough
[ ] AGENTS.md 放项目通用规则
[ ] opencode.json 配置权限
[ ] 不包含密钥、生产连接串、真实敏感数据
```

---

## 15. 常见问题

### Q1：为什么不直接让 Agent 用 bash 跑 Python？

因为自由 bash 太宽。custom tool 可以把参数、路径、输出和安全边界固定下来。Skill 再指导 Agent 何时调用这个 tool。

### Q2：command 和 skill 有什么区别？

Command 是用户入口，负责把 `/profile-data ...` 展开成 prompt。Skill 是方法论，负责规定 workflow、tool policy、output policy、stop rule。

### Q3：Skill 是否应该包含完整 Python 代码？

不建议。代码应该在 `src/`、CLI 或 tool 中。Skill 只写如何使用它们。复杂细节放 references，稳定执行逻辑放脚本。

### Q4：什么时候读 reference？

当 Agent 已经加载 Skill，但还需要数据契约、报告模板、解释规则时再读。不要在 `SKILL.md` 里堆所有细节。

### Q5：为什么 tool result 只返回 manifest？

因为 Agent Loop 的上下文很宝贵。返回 manifest 可以让 Agent 知道 artifact 在哪里、数据规模如何、有哪些 warning。需要细节时再读小文件。

---

## 16. 参考资料

- OpenCode Agent Skills: https://opencode.ai/docs/skills
- OpenCode Custom Tools: https://opencode.ai/docs/custom-tools
- OpenCode Commands: https://opencode.ai/docs/commands
- OpenCode Rules / AGENTS.md: https://opencode.ai/docs/rules
- OpenCode Agents: https://opencode.ai/docs/agents
- OpenCode Permissions: https://opencode.ai/docs/permissions

---

## 17. 讲师收尾话术

今天这个样例非常小，但它是一个完整模式。以后你们手上的半导体分析脚本，无论是 Inline、WAT、FDC、Yield、Chamber drift，还是 split correlation，都不要先问“怎么让大模型跑脚本”，而要先问：

```text
这个脚本的输入契约是什么？
输出 artifact 是什么？
哪些动作应该封装成 CLI 或 API？
Agent 只需要看到哪些 compact 信息？
Skill 应该写哪些 workflow 和 stop rules？
```

把这几个问题回答清楚，脚本就不再只是个人工具，而会变成团队可复用、可审计、可培训、可 Agentic 化的能力。
