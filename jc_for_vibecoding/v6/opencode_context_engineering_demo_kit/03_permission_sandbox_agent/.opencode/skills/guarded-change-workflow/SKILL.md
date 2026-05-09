---
name: guarded-change-workflow
description: use when the user asks to change important configuration, flags, limits, or data-adjacent settings but direct edits to protected files are not allowed; constrain the agent to approved proposal/apply/validate scripts, sandbox outputs, audit logs, and human approval checkpoints.
compatibility: opencode
metadata:
  language: zh-CN
  demo: context-engineering-03
---

# Guarded Change Workflow Skill

## 目标

把“配置变更”限制在可审计、可验证、可回滚的动作空间里。Agent 不直接操作生产配置，而是生成 proposal，应用到 sandbox，再验证。

## 工作流

1. 读取 `policy/allowed_flags.json` 和 `workspace/sandbox_config.json`。
2. 不要读取 `protected/customer_data.csv`。
3. 生成 proposal：

```bash
python3 scripts/propose_config_patch.py --flag beta_dashboard --value true --reason "training demo" --output output/proposal_001.json
```

4. 应用到 sandbox output：

```bash
python3 scripts/apply_patch_to_sandbox.py --proposal output/proposal_001.json --sandbox workspace/sandbox_config.json --output output/sandbox_config_after.json --audit output/audit_log.jsonl
```

5. 验证：

```bash
python3 scripts/validate_config_patch.py --proposal output/proposal_001.json --sandbox-output output/sandbox_config_after.json --audit output/audit_log.jsonl
```

6. 回答：说明变更没有写入 protected 文件；列出 audit log 和人工审批点。

## Stop Rules

- 用户要求改 production 时，停止。
- 用户要求读取 customer data 时，停止。
- flag 不在白名单时，停止。
- 验证 protected hash 失败时，停止。
- review_required 为 true 时，不能说已经生效，只能说 sandbox proposal 已生成。
