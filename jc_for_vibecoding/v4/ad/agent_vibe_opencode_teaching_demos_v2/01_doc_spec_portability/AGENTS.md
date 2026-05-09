# Demo01 项目规则

1. 先抽取 `spec_contract.json`，再生成平台代码。不要直接从 Markdown 文档生成最终实现。
2. 平台 B 代码必须通过 `scripts/validate_port.py`。
3. 不要修改 `docs/ticket_priority_spec.md`，除非用户明确要求改规范。
4. 任何规范歧义都应写入 `output/portability_report.md`。
5. 自动测试只覆盖样例，不代表业务逻辑完整签核。
