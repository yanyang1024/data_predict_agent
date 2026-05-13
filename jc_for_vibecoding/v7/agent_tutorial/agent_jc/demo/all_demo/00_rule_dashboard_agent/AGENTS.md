# Demo 00 Rules

## 任务边界

本项目只生成教学 dashboard 和进度报告。不要修改 `templates/` 和 `references/` 中的源模板，所有输出写入 `output/`。

## 验证命令

```bash
python3 scripts/generate_dashboard.py --input data/sample_progress.json --output-dir output
python3 scripts/validate_dashboard.py --output-dir output
```

## Agent 工作流

1. 先读 `README.md` 和 `dashboard-generator` Skill。
2. 如果用户输入是自然语言，先提取为结构化 progress JSON；不能确定的字段用模板默认值。
3. 调用脚本生成 dashboard。
4. 运行验证脚本。
5. 最终回答必须说明：哪些内容来自用户、哪些内容来自模板、哪些字段是默认值。
