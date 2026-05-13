---
description: 按迁移规范和 golden tests 完成跨语言/平台候选实现
agent: plan
---

Use the `spec-porting` skill.

用户请求：

$ARGUMENTS

要求：
1. 先阅读 `docs/order_discount_spec.md`、`docs/porting_spec_py_to_js.md`、`references/source/python_order_rules.py`、`tests/golden_cases.json`。
2. 先给迁移计划、动作空间和人工确认点。
3. 调用 `scripts/port_py_to_js.py` 生成候选实现，不要直接修改源文件。
4. 调用 `scripts/validate_port.py` 跑 golden tests。
5. 最终回答区分：已自动验证的行为、未覆盖风险、人工 review 项。
