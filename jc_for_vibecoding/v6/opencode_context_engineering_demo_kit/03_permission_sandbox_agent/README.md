# Demo 03：权限约束与受控动作空间 Agent

## 教学定位

这个 demo 专门讲“先设计动作空间，再谈自治”。场景非常通用：用户想改一个配置，但重要数据和生产配置不能让 Agent 直接读写。

正确做法：

```text
用户一句话变更请求
  -> Agent 读取政策和 sandbox config
  -> Agent 不能直接改 protected/prod_config.json
  -> Agent 只能调用 propose_config_patch.py 生成 proposal
  -> Agent 只能调用 apply_patch_to_sandbox.py 应用到 sandbox
  -> Agent 调用 validate_config_patch.py 检查 protected 文件未变
  -> 输出 audit log 和人工确认点
```

## Context 构成

| Context | 文件 | 作用 |
|---|---|---|
| 保护对象 | `protected/prod_config.json`、`protected/customer_data.csv` | 不允许 Agent 直接修改；customer data 不应读取 |
| 白名单政策 | `policy/allowed_flags.json` | 限制可变更 flag 和目标环境 |
| sandbox | `workspace/sandbox_config.json` | 允许改的模拟配置 |
| 脚本/API | `scripts/propose_config_patch.py`、`scripts/apply_patch_to_sandbox.py` | 封装动作空间 |
| 验证 | `scripts/validate_config_patch.py` | 确认 schema、audit log、protected hash |
| 权限 | `opencode.json` | deny protected edit，bash 仅允许封装脚本 |

## 从 0 到 1 构建步骤

```text
Step 0：列出不能直接操作的数据和配置
Step 1：建立 protected/ 和 workspace/ 分区
Step 2：定义 allowed_flags 白名单和 patch schema
Step 3：写 propose 脚本，只生成 proposal，不修改配置
Step 4：写 apply 脚本，只能应用到 sandbox
Step 5：写 validate 脚本，验证 protected 文件 hash 未变化
Step 6：写 Skill，明确 Stop rules 和人工审批点
Step 7：写 Command 和 Tool，把用户入口和动作参数结构化
Step 8：写 opencode.json，用权限兜底
```

## 运行

```bash
python3 run_demo.py
```

## OpenCode 演示 Prompt

```text
/safe-change 请把 sandbox 中的 beta_dashboard flag 打开，原因是培训演示需要。不要读取 customer_data.csv，不要修改 protected/prod_config.json，只能通过受控脚本生成 proposal 并应用到 sandbox。
```
