# Demo 03 Rules

## 高风险区域

- `protected/prod_config.json`：只读源配置，不能修改。
- `protected/customer_data.csv`：模拟敏感数据，不要读取，不要引用内容。

## 允许动作

- 在 `output/` 中生成 proposal、validation manifest、audit log。
- 在 `workspace/sandbox_config.json` 的副本或 `output/sandbox_config_after.json` 中应用变更。

## 禁止动作

- 不要直接编辑 `protected/`。
- 不要直接编辑 `workspace/sandbox_config.json`，必须通过脚本生成新文件。
- 不要扩大脚本参数白名单。

## 验证命令

```bash
python3 scripts/propose_config_patch.py --flag beta_dashboard --value true --reason "training demo" --output output/proposal_001.json
python3 scripts/apply_patch_to_sandbox.py --proposal output/proposal_001.json --sandbox workspace/sandbox_config.json --output output/sandbox_config_after.json --audit output/audit_log.jsonl
python3 scripts/validate_config_patch.py --proposal output/proposal_001.json --sandbox-output output/sandbox_config_after.json --audit output/audit_log.jsonl
```
