---
name: paper-reproducer
description: use when the user asks to extract implementation, experiment, verification, or reproduction logic from a PDF or paper and create a minimal local project using approved environment packages; extract evidence first, generate code second, validate syntax/sample tests, and require human review for scientific correctness.
compatibility: opencode
metadata:
  language: zh-CN
  demo: context-engineering-02
---

# Paper Reproducer Skill

## 目标

把 PDF / 论文阅读变成可执行的复现项目生成流程，同时保留人类在中间方案和最终逻辑正确性上的介入。

## 流程

1. 证据抽取：读取 `references/pdf_extraction_rules.md`，调用：

```bash
python3 scripts/extract_pdf_evidence.py --pdf papers/synthetic_agent_eval_paper.pdf --fallback papers/synthetic_agent_eval_paper_text.md --output-dir output
```

2. 设计摘要：检查 `output/evidence.json`，确认算法、参数、环境包和预期测试。
3. 生成项目：

```bash
python3 scripts/build_repro_project.py --evidence output/evidence.json --env env_pkg/chip_eval_env.py --output-dir repro_project
```

4. 验证：

```bash
python3 scripts/validate_repro_project.py --project-dir repro_project
```

5. 输出：说明哪些结果已由脚本验证，哪些仍需人工确认。

## Stop Rules

- PDF 抽取结果缺少算法或参数时，不要生成代码，先请求人工补充。
- 不要修改 `papers/`、`env_pkg/`、`references/`。
- 语法测试通过不代表论文结论正确。
- 任何“复现成功”的说法都必须限定为“demo 样例测试通过”。
