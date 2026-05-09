# Demo02 项目规则

1. 富文本 / PDF 信息必须先抽取成 `output/extracted_patterns.json`，不要直接生成最终测试代码。
2. 生成测试代码必须基于 `env_package/target_env_contract.json`。
3. 每次生成后必须运行 `scripts/validate_generated_tests.py`。
4. 语法正确不等于验证逻辑正确，必须输出 `review_packet.md`。
5. 遇到文档歧义、native directive 不可映射、环境包缺失 API 时必须进入人工确认。
