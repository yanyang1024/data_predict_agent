---
name: rich-doc-test-adapter
description: use when the user asks to extract verification patterns, test scenarios, native directives, or implementation instructions from pdf/html/word/markdown rich documents and adapt them to a target environment package, with staged extraction, code generation, validation, and human review checkpoints.
---

# 富文本验证模式抽取与测试适配 Skill

## 目标

从 PDF / Word / HTML / Markdown 等富文本材料中提取验证模式和原生指令，结合目标环境包生成适配后的测试代码。核心原则：先抽取中间 JSON，再生成代码，再语法验证，再人工确认逻辑。

## 模块链路

```text
富文本 / PDF 导出
  → extraction rules
  → extracted_patterns.json
  → target env contract
  → generated_tests.py
  → syntax/schema validator
  → review_packet.md
  → 人工确认
```

## 工作流

1. 读取 `AGENTS.md` 和 `references/extraction_rules.md`。
2. 读取文档：`docs/rich_test_spec_export.html`。
3. 读取环境包契约：`env_package/target_env_contract.json`。
4. 先输出 Plan：
   - 可抽取字段；
   - native directive 映射策略；
   - unsupported / uncertain 项；
   - 人工介入点。
5. 用户确认后运行：

```bash
python3 scripts/extract_rich_doc_patterns.py --doc docs/rich_test_spec_export.html --rules references/extraction_rules.md --output output/extracted_patterns.json
python3 scripts/adapt_patterns_to_env.py --patterns output/extracted_patterns.json --env env_package/target_env_contract.json --output output/generated_tests.py --review output/review_packet.md
python3 scripts/validate_generated_tests.py --tests output/generated_tests.py --patterns output/extracted_patterns.json
```

6. 输出说明：
   - 抽取了哪些 pattern；
   - 生成了哪些测试函数；
   - validator 证明了什么；
   - 哪些内容需要人确认。

## Stop Rules

停止并请求人工确认：

- 文档无法可靠提取表格结构；
- 关键列缺失；
- native directive 无法映射到目标环境 API；
- 文档中的阈值、地址、周期来自示例而非正式规范；
- 用户要求跳过 review packet；
- 用户要求把语法验证通过描述为逻辑正确。

## 人工 Review 点

- 测试意图是否被正确抽取；
- 原生指令到目标环境 API 的语义是否一致；
- 周期、阈值、地址、corner 是否来自正式规格；
- 生成测试是否覆盖真实验证目标。
