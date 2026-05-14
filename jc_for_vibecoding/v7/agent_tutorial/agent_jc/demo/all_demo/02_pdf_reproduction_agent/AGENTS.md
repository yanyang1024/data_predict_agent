# Demo 02 Rules

## 允许修改

- `output/`
- `repro_project/`

## 禁止修改

- `papers/`
- `env_pkg/`
- `references/`
- `data/sample_signal.csv`

## 验证命令

```bash
python3 scripts/extract_pdf_evidence.py --pdf papers/synthetic_agent_eval_paper.pdf --fallback papers/synthetic_agent_eval_paper_text.md --output-dir output
python3 scripts/build_repro_project.py --evidence output/evidence.json --env env_pkg/chip_eval_env.py --output-dir repro_project
python3 scripts/validate_repro_project.py --project-dir repro_project
python3 ../scripts/demo_viewer.py --demo 02_pdf_reproduction_agent --port 8762 --restart
```

## 人工介入点

- 抽取出的实验逻辑是否完整。
- 生成项目是否忠实于论文意图。
- 样例测试通过不代表复现真实论文结论。
- 最终回答要给出 viewer URL，方便讲师浏览 evidence、设计摘要、代码和验证结果。
