---
description: 通过受控 proposal 和 sandbox 输出完成低风险配置变更
agent: plan
---

Use the `guarded-change-workflow` skill.

用户请求：

$ARGUMENTS

要求：
1. 先识别 flag、目标值、原因和目标环境；不确定时停止确认。
2. 不要读取 `protected/customer_data.csv`。
3. 不要修改 `protected/prod_config.json` 或任何 `protected/` 文件。
4. 只能调用 `scripts/propose_config_patch.py` 生成 proposal，再调用 `scripts/apply_patch_to_sandbox.py` 应用到 sandbox 输出。
5. 最后调用 `scripts/validate_config_patch.py`，并报告验证结果、审计文件和人工确认点。
6. 如果用户同时要求查询 lot history，引导使用 `/query-lot` 或 `scripts/query_lot_history_service.py`，不要读取 protected 原始数据。
