# PDF 信息抽取规则

从论文或 PDF 中抽取以下证据，不要一开始就生成代码。

## Evidence Schema

```json
{
  "objective": "研究或复现目标",
  "environment_requirements": ["本地依赖或环境包"],
  "algorithm_steps": ["步骤 1", "步骤 2"],
  "default_parameters": {"window": 4, "threshold": 2.5},
  "experiment_logic": ["数据输入", "预期输出"],
  "native_code_instructions": ["需要生成哪些文件"],
  "limitations": ["不能自动证明的结论"]
}
```

## 抽取原则

- 保留原始证据，不要把猜测写成事实。
- 如果 PDF 抽取失败，使用 fallback text，并在 manifest 中记录。
- 算法、参数、数据、预期结果要分开存储，方便后续生成代码和验证。
- 文档没有说明的内容，写入 `human_review_items`。
