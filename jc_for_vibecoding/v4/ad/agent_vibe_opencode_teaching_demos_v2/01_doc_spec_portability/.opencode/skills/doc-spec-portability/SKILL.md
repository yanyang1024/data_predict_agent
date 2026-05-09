---
name: doc-spec-portability
description: use when the user asks to implement, port, validate, or standardize code from a document specification, historical examples, or platform contract; especially when the same business spec must produce portable implementations across platforms with tests and human review checkpoints.
---

# Doc Spec 可移植开发 Skill

## 目标

基于历史文档、历史样例和目标平台约束，生成可移植实现。核心原则：先抽取中间 contract，再生成代码，再验证，再人工确认语义。

## 工作流

1. 读取规范文档：`docs/ticket_priority_spec.md`。
2. 读取历史样例：`examples/platform_a_python/`。
3. 读取目标平台契约：`contexts/platform_b_contract.md`。
4. 先输出 Plan：
   - 输入字段；
   - 输出字段；
   - 规则顺序；
   - 目标平台限制；
   - 人工确认点。
5. 用户确认后运行：

```bash
python3 scripts/extract_spec_contract.py --spec docs/ticket_priority_spec.md --output output/spec_contract.json
python3 scripts/port_to_platform_b.py --contract output/spec_contract.json --output output/platform_b
python3 scripts/validate_port.py --impl output/platform_b/rule_engine.js --cases tests/platform_b_cases.json
```

6. 生成讲解摘要：
   - contract 抽取了什么；
   - 代码生成了什么；
   - 测试验证了什么；
   - 业务 owner 还需要确认什么。

## 输出

- `output/spec_contract.json`
- `output/platform_b/rule_engine.js`
- `output/platform_b/rule_engine.test.js`
- `output/portability_report.md`

## Stop Rules

停止并请求人工确认：

- 规范规则顺序不清楚；
- 历史样例与规范冲突；
- 目标平台缺少必要 API；
- 用户要求跳过测试；
- 用户要求把样例测试通过等同于业务签核。

## 人工 Review 点

- 规则优先级是否正确；
- 默认值策略是否正确；
- 平台 B 的边界行为是否和平台 A 一致；
- 测试样例是否覆盖主要业务场景。
