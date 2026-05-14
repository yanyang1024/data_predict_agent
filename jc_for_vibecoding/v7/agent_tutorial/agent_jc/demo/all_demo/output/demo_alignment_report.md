# Demo Alignment Report

Generated at: 2026-05-13T23:57:39.088066+00:00

| Demo | 教学文档要求 | 实现证据 | 状态 |
|---|---|---|---|
| 00 | 一句话进展 -> 规则化 dashboard、状态报告、manifest、viewer | 4 demos, viewer=True | 通过 |
| 01 | Gradio CSV 分析 App -> Flask 项目，保持功能和前端风格 | 4 CSV cases, style=True | 通过 |
| 02 | PDF evidence -> 设计摘要 -> 复现项目 -> 样例测试 | py_compile=True, removed_cache=2 | 通过 |
| 03 | 配置和 lot 查询通过受控脚本/API，不暴露 protected 原始数据 | config=passed, data=passed, protected_ok=True | 通过 |

## 未覆盖风险

- Demo 00：dashboard 内容仍需讲师确认。
- Demo 01：CSV cases 覆盖标准和边界样例，不覆盖生产上传安全、混合编码、超大文件和复杂图表。
- Demo 02：样例测试通过不代表论文科学结论被完整复现。
- Demo 03：字段白名单和 hash 校验通过不代表真实业务口径或审批流程完整。

## 展示入口

- Gallery: `output/demo_gallery.html`
- Demo 00: `http://127.0.0.1:8760/`
- Demo 01: `http://127.0.0.1:8761/`
- Demo 02: `http://127.0.0.1:8762/`
- Demo 03: `http://127.0.0.1:8763/`
