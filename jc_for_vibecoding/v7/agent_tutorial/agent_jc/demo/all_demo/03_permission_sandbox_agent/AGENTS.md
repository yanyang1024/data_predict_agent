# Demo 03 Rules

## 任务边界

本项目演示 sandbox 配置变更和受控 lot history 查询。不要读取 `protected/customer_data.csv` 或 `protected/lot_history_raw.csv`，不要修改 `protected/prod_config.json` 或 `protected/` 下的任何文件。所有变更和查询必须通过 `scripts/` 中的受控脚本输出到 `output/`。

## 验证命令

```bash
python3 scripts/propose_config_patch.py --flag beta_dashboard --value true --reason 培训演示需要
python3 scripts/apply_patch_to_sandbox.py
python3 scripts/validate_config_patch.py
python3 scripts/query_lot_history_service.py --lot LOT-A12
python3 scripts/validate_data_service.py
```

## Agent 工作流

1. 先读 `README.md`、相关 policy / schema 和 `guarded-change-workflow` Skill。
2. 把用户请求归一化为：配置变更请求或数据查询请求。
3. 配置变更请求要识别 flag 名称、目标值、原因、目标环境。
4. 数据查询请求要识别 lot id、查询目的和允许输出字段。
5. 只调用受控脚本，不直接编辑 JSON，不直接读取 protected 原始数据。
6. 调用验证脚本检查 policy、schema、protected hash、审计日志和输出结果。
7. 最终回答必须说明：哪些文件被生成、哪些 protected 文件没有被改、哪些原始字段没有暴露、哪些判断仍需人工确认。

## Stop Rules

- 如果 flag 不在 `policy/allowed_flags.json` 的 allowlist 中，停止并要求人工审批。
- 如果请求目标是 production，停止；本 demo 只允许 sandbox。
- 如果用户要求读取客户数据、导出 PII、读取原始 lot 明细、绕过脚本或直接修改 protected 文件，停止。
