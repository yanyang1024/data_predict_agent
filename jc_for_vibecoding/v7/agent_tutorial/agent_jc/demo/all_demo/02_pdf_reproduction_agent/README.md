# Demo 02：PDF / 论文信息抽取与复现项目生成 Agent

## 教学定位

这个 demo 演示辅助编程不只是“读 PDF 后给建议”，而是可以把文档信息接入后续执行流程：

```text
PDF / paper
  -> 证据抽取 evidence.json
  -> 设计摘要 design_brief.md
  -> 结合本地环境包生成复现项目
  -> 运行语法和样例测试
  -> 输出 validation manifest 和人工 review 点
```

重点不是复现真实论文，而是教学：如何设计规则提取 PDF 信息，如何用 Skill 串联模块，如何让 Agent 写一部分代码但保留人工验证介入。

## Context 构成

| Context | 文件 | 作用 |
|---|---|---|
| PDF 输入 | `papers/synthetic_agent_eval_paper.pdf` | 模拟论文 |
| PDF fallback text | `papers/synthetic_agent_eval_paper_text.md` | PDF 抽取失败时的稳定输入 |
| 抽取规则 | `references/pdf_extraction_rules.md` | 规定要抽取哪些证据 |
| 环境包 | `env_pkg/chip_eval_env.py` | 本地可用 API，生成项目必须适配 |
| 数据 | `data/sample_signal.csv` | 复现实验输入 |
| 脚本 | `scripts/extract_pdf_evidence.py`、`scripts/build_repro_project.py` | 执行动作 |
| 验证 | `scripts/validate_repro_project.py` | 编译和测试 |

## 从 0 到 1 构建步骤

```text
Step 0：准备一份 synthetic PDF 和 fallback text
Step 1：写 pdf_extraction_rules，定义证据 schema
Step 2：写 extract_pdf_evidence.py，输出 evidence.json
Step 3：写 env_pkg，本地环境包作为可调用依赖
Step 4：写 build_repro_project.py，生成最小复现项目
Step 5：写 validate_repro_project.py，只验证语法和样例行为
Step 6：写 paper-reproducer Skill，串联抽取、设计、生成、验证、人审
Step 7：写 OpenCode tools 和 command
Step 8：在回答中区分“自动验证通过”和“论文逻辑需人工确认”
```

## 运行

```bash
python3 run_demo.py
```

运行后会自动启动或重启本地 viewer 服务，输出类似：

```text
Viewer URL: http://127.0.0.1:8762/
Primary URL: http://127.0.0.1:8762/output/design_brief.md
```

## OpenCode 演示 Prompt

```text
/reproduce-paper 请从 papers/synthetic_agent_eval_paper.pdf 提取实验逻辑，结合 env_pkg/ 中的本地环境库，生成一个最小可运行复现项目。不要声称复现了论文全部结论，只验证语法和示例测试。
```
