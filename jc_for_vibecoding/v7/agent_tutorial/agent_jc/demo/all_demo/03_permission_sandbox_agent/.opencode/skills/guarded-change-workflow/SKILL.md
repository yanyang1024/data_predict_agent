---
name: guarded-change-workflow
description: use when the user asks to change protected configuration safely or query lot history through a controlled data service; narrow the action space with policy allowlists, generate auditable outputs, avoid direct protected data access, and validate protected files and output fields.
compatibility: opencode
metadata:
  language: zh-CN
  demo: context-engineering-03
---

# Guarded Change Workflow Skill

## 目标

把配置变更和数据查询从“Agent 直接改文件 / 直连数据库 / 读原始数据”变成“Agent 调用受控脚本或数据服务、生成审计产物、验证和交接”的流程。

## Context 加载顺序

1. 读项目 `AGENTS.md`。
2. 如果是配置变更，读 `policy/allowed_flags.json` 和 `schemas/config_patch_schema.json`。
3. 如果是 lot 查询，读 `policy/data_access_policy.json` 和 `schemas/lot_query_schema.json`。
4. 如需讲解动作空间设计，读 `references/动作空间设计.md`。
5. 调用脚本，不直接编辑 protected 或 workspace JSON，不直接读取原始 lot history。

## 工作流

### 配置变更

1. 归一化用户请求：flag、value、reason、target environment。
2. 检查目标是否为 sandbox；production 一律停止。
3. 调用：

```bash
python3 scripts/propose_config_patch.py --flag beta_dashboard --value true --reason 培训演示需要
```

4. 调用：

```bash
python3 scripts/apply_patch_to_sandbox.py
```

5. 验证：

```bash
python3 scripts/validate_config_patch.py
```

6. 输出回答：生成文件、被拒绝的动作、验证结果、人工确认点。

### 受控数据查询

1. 归一化用户请求：lot id、查询目的、是否需要图表。
2. 检查 lot 是否在 `policy/data_access_policy.json` 允许范围内。
3. 调用：

```bash
python3 scripts/query_lot_history_service.py --lot LOT-A12
```

4. 验证：

```bash
python3 scripts/validate_data_service.py
```

5. 输出回答：只汇报聚合字段、QTime / UT 口径、图表路径、原始字段隐藏情况和人工确认点。

## Stop Rules

- 不读取 `protected/customer_data.csv` 或 `protected/lot_history_raw.csv`，不把客户数据或原始行放进 proposal / summary / report。
- 不修改 `protected/prod_config.json`。
- 不绕过 policy、schema、脚本或数据服务直接改 JSON / 查表。
- 如果 reason 为空、flag 不在白名单、lot 不在白名单、目标不是 sandbox，停止。
- 验证只能证明本 demo 的结构、安全约束和样例聚合口径，不证明变更或数据结论在真实生产中一定合规。
