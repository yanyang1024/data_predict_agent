# Demo01：Doc Spec 开发规范与跨平台可移植实现

## 教学目标

这个 demo 用一个通用“工单优先级规范”模拟真实业务中的 Doc Spec 开发：同一份规范需要在不同平台实现，并且实现要能被测试验证。

重点不是规则本身，而是让学员理解：

```text
历史规范文档 + 历史平台样例 + 目标平台约束
  → 抽取 spec contract
  → 生成目标平台实现
  → 生成测试
  → 自动验证语法和样例一致性
  → 人确认规范语义和边界情况
```

## 运行

```bash
cd 01_doc_spec_portability
python3 scripts/extract_spec_contract.py --spec docs/ticket_priority_spec.md --output output/spec_contract.json
python3 scripts/port_to_platform_b.py --contract output/spec_contract.json --output output/platform_b
python3 scripts/validate_port.py --impl output/platform_b/rule_engine.js --cases tests/platform_b_cases.json
```

## 教学讲解点

1. `docs/ticket_priority_spec.md` 是业务规范，不是 prompt。
2. `examples/platform_a_python/` 是历史实现样例，帮助 Agent 理解代码风格和边界。
3. `contexts/platform_b_contract.md` 是目标平台约束。
4. `output/spec_contract.json` 是中间表示，便于人 review。
5. 自动测试只能证明样例一致，不证明规范完整。

## OpenCode 对话演示

Plan 阶段：

```text
请使用 doc-spec-portability skill。先不要写代码。
阅读 docs/ticket_priority_spec.md、examples/platform_a_python/ 和 contexts/platform_b_contract.md，说明如何把规范抽取成 contract，并生成平台 B 实现。请列出人工确认点。
```

Build 阶段：

```text
确认执行。请运行 extract_spec_contract.py 和 port_to_platform_b.py，再运行 validate_port.py。最后输出 portability_report.md，并说明哪些只是测试通过，哪些仍需业务 owner 确认。
```
