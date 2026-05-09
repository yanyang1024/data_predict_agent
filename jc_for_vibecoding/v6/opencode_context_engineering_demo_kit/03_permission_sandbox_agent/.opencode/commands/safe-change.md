---
description: 通过受控 proposal 和 sandbox patch 完成配置变更，不直接操作 protected 文件
agent: plan
---

Use the `guarded-change-workflow` skill.

用户请求：

$ARGUMENTS

要求：
1. 不要读取 `protected/customer_data.csv`。
2. 不要修改 `protected/prod_config.json` 或 `workspace/sandbox_config.json`。
3. 只能调用 `scripts/propose_config_patch.py`、`scripts/apply_patch_to_sandbox.py`、`scripts/validate_config_patch.py`。
4. 最终回答要包含 proposal、sandbox output、audit log、protected integrity 结果和人工审批点。
