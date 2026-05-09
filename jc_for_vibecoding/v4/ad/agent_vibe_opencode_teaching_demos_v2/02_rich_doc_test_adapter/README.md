# Demo02：从富文本 / PDF 信息抽取到测试实现适配

## 教学目标

这个 demo 模拟从 PDF、网页或富文本导出的说明文档中抽取验证模式和原生代码指令，再结合目标环境包生成适配后的测试代码。

重点教学内容：

1. 如何设计信息抽取规则，而不是让模型“随便读文档”。
2. 如何用 Skill 串联多个模块：抽取 → 归一化 → 适配 → 语法验证 → Review Packet。
3. AI 不只是能读文档和给参考，也能调用脚本完成一部分执行动作。
4. 自动验证通常只能验证语法、schema、文件存在性；逻辑正确必须和人协同验证。

## 运行

```bash
cd 02_rich_doc_test_adapter
python3 scripts/extract_rich_doc_patterns.py --doc docs/rich_test_spec_export.html --rules references/extraction_rules.md --output output/extracted_patterns.json
python3 scripts/adapt_patterns_to_env.py --patterns output/extracted_patterns.json --env env_package/target_env_contract.json --output output/generated_tests.py --review output/review_packet.md
python3 scripts/validate_generated_tests.py --tests output/generated_tests.py --patterns output/extracted_patterns.json
```

## OpenCode 对话演示

Plan 阶段：

```text
请使用 rich-doc-test-adapter skill。先不要生成代码。
阅读 docs/rich_test_spec_export.html、references/extraction_rules.md 和 env_package/target_env_contract.json，说明应抽取哪些验证模式、哪些 native directive、哪些内容需要人工确认。
```

Build 阶段：

```text
确认执行。请运行抽取、适配和验证脚本。最后解释：语法验证通过意味着什么，不意味着什么。
```
