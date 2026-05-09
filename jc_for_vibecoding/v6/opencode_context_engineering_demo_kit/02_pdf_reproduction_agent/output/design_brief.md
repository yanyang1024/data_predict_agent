# Design Brief

{
  "objective": "Reproduce a small signal anomaly detector for educational agent workflows. The detector scans a single numeric signal and flags points whose normalized score exceeds a threshold.",
  "default_parameters": {
    "window": 4,
    "threshold": 2.5
  },
  "generated_files": [
    "src/adaptive_window.py",
    "tests/test_adaptive_window.py",
    "chip_eval_env.py",
    "data/sample_signal.csv"
  ],
  "human_review_items": [
    "确认 PDF 抽取是否遗漏公式上下文",
    "确认样例 anomaly index 是否符合论文意图",
    "确认算法是否适合真实数据"
  ]
}