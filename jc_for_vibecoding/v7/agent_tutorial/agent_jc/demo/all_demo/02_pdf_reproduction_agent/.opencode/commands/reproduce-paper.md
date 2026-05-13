---
description: 从 PDF / 论文提取实验逻辑并生成最小可运行复现项目
agent: plan
---

Use the `paper-reproducer` skill.

用户请求：

$ARGUMENTS

要求：
1. 先读 `references/pdf_extraction_rules.md` 和项目 `AGENTS.md`。
2. 先抽取 evidence，不要直接写代码。
3. 调用抽取脚本生成 `output/evidence.json`。
4. 基于 evidence 和 `env_pkg/chip_eval_env.py` 生成 `repro_project/`。
5. 调用验证脚本。
6. 最终回答必须区分：PDF 证据、生成动作、自动验证、人类 review 点。
