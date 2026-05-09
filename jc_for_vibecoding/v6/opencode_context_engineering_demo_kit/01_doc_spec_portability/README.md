# Demo 01：Doc Spec 开发规范与跨语言迁移 Agent

## 教学定位

这个 demo 用“Python 业务规则模块迁移到 JS/TS 风格模块”的简化场景，讲解基于历史文档和样例的开发：

```text
用户每次给出迁移要求 + 功能文档
  -> Agent 加载迁移规范、历史样例、golden cases
  -> Agent 调用受控脚本生成候选实现
  -> Agent 运行测试验证语法和样例行为
  -> Agent 输出迁移报告和人工 review 点
```

它对应真实业务中的“同一文档在不同平台可移植实现”，但不绑定某个具体平台。

## Context 构成

| Context | 文件 | 作用 |
|---|---|---|
| 功能文档 | `docs/order_discount_spec.md` | 描述规则逻辑，不依赖语言 |
| 迁移规范 | `docs/porting_spec_py_to_js.md` | 说明 Python -> JS/TS 风格的转换注意点 |
| 历史源代码 | `references/source/python_order_rules.py` | 待迁移的 Python 实现 |
| 目标样例 | `references/examples/js_reference_style.mjs` | 目标语言的代码风格参考 |
| 测试项 | `tests/golden_cases.json` | 跨语言行为一致性的 golden cases |
| 脚本 | `scripts/port_py_to_js.py` | 生成候选代码和迁移报告 |
| 验证 | `tests/run_golden_cases.mjs`、`scripts/validate_port.py` | 执行样例行为验证 |

## 从 0 到 1 构建步骤

```text
Step 0：收集语言无关的功能 spec
Step 1：整理源语言实现和目标语言参考样例
Step 2：写迁移注意点和不允许自动决定的点
Step 3：写 golden cases，先定义验收标准
Step 4：写迁移脚本，生成候选代码和 report
Step 5：写 Skill，规定 Agent 必须先读 spec，再生成，再验证
Step 6：写 Command，变成 /port-spec 一句话入口
Step 7：写 Tool，把脚本封装为结构化动作
Step 8：写权限配置，禁止直接改源材料，只允许写 generated/output
```

## 运行

```bash
python3 run_demo.py
```

## OpenCode 演示 Prompt

```text
/port-spec 请把 references/source/python_order_rules.py 按 docs/porting_spec_py_to_js.md 的规范迁移到 generated/pricing.mjs。先输出迁移计划和风险点，再调用脚本生成，并运行 golden tests。
```
