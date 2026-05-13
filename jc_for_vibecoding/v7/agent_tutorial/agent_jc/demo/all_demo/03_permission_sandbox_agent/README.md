# Demo 03：权限沙箱与受控数据服务 Agent

## 教学定位

这个 demo 用两个轻量场景说明：Agent 不应该直接读敏感数据、直连数据库或改生产配置，而应该被限制在清晰的动作空间内。

```text
用户提出配置变更或 lot history 查询
  -> Agent 读取 policy / schema / Skill
  -> Agent 只能调用受控脚本或数据服务
  -> 脚本把结果写入 output，不暴露 protected 原始数据
  -> 验证脚本检查 policy、schema、protected 文件 hash、字段白名单和审计日志
  -> Agent 汇报可自动验证的部分与人工 review 点
```

场景 A：讲师要求打开 sandbox 里的 `beta_dashboard` flag。Agent 不能修改 `protected/prod_config.json`，只能通过脚本生成可审计 proposal 并应用到 sandbox。

场景 B：讲师要求查询 `LOT-A12` 的 QTime / UT 汇总。Agent 不能读取 `protected/customer_data.csv` 或 `protected/lot_history_raw.csv`，只能通过 `query_lot_history_service.py` 获取聚合摘要和 SVG 图。

## 这个 demo 教什么

1. 先定义 Agent 的动作空间，再让它执行。
2. 用 `opencode.json` 把 protected 文件设为不可读或不可改。
3. 用 policy / schema 约束可变更字段和可查询 lot，而不是让 Agent 自由改 JSON 或自由查表。
4. 用脚本/API 封装高风险动作，输出 proposal、sandbox 结果、数据摘要、图表和审计日志。
5. 用 hash、字段白名单和 manifest 验证敏感文件未被改动、原始字段未泄露。

## Context 构成

| Context | 文件 | 作用 |
|---|---|---|
| 项目规则 | `AGENTS.md` | 说明禁止读取/修改的范围和验证命令 |
| 权限配置 | `opencode.json` | 限制 read/edit/bash/skill 动作 |
| Skill | `.opencode/skills/guarded-change-workflow/SKILL.md` | 固化受控变更流程 |
| Command | `.opencode/commands/safe-change.md`、`.opencode/commands/query-lot.md` | 一句话入口 |
| Tool | `.opencode/tools/config_guard.ts`、`.opencode/tools/data_service.ts` | OpenCode custom tool 示例 |
| Policy | `policy/allowed_flags.json`、`policy/data_access_policy.json` | 白名单化可改 flag 和可查 lot |
| Schema | `schemas/config_patch_schema.json`、`schemas/lot_query_schema.json` | proposal 和数据摘要结构约束 |
| Protected | `protected/prod_config.json`、`protected/customer_data.csv`、`protected/lot_history_raw.csv` | 生产配置、敏感客户数据和原始 lot history |
| Workspace | `workspace/sandbox_config.json` | 可用于演示的 sandbox 输入 |
| Scripts | `scripts/*.py` | 生成、应用、验证受控变更 |

## 从 0 到 1 构建步骤

```text
Step 0：标出 protected 数据和配置，不让 Agent 直接操作
Step 1：把可执行动作收敛为 policy 白名单
Step 2：定义 proposal schema 和审计日志格式
Step 3：写 propose_config_patch.py，只生成受控 proposal
Step 4：写 apply_patch_to_sandbox.py，只应用到 sandbox 输出
Step 5：写 query_lot_history_service.py，只返回聚合字段和图，不返回原始行
Step 6：写 validate_config_patch.py / validate_data_service.py，检查 protected hash、policy、字段白名单和结果
Step 7：写 Skill，规定先取证、再调用受控动作、再验证、最后报告人工确认点
Step 8：写 command/tool/opencode.json，形成可复用入口和权限边界
```

## 运行

```bash
python3 run_demo.py
```

## OpenCode 演示 Prompt

```text
/safe-change 请把 sandbox 中的 beta_dashboard flag 打开，原因是培训演示需要。不要读取 customer_data.csv，不要修改 protected/prod_config.json，只能通过受控脚本生成 proposal 并应用到 sandbox。
```

```text
/query-lot 请查询 LOT-A12 的 QTime / UT 汇总并生成图。不要读取 protected/lot_history_raw.csv，只能通过数据服务脚本返回聚合结果。
```
