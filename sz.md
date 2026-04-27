已补充一份 **实战型文档**，并附带一个可直接参考的 demo 工程。

下载：

[实战文档 DOCX](sandbox:/mnt/data/semiconductor_skill_practical/docs/05_practical_opencode_skill_workshop.docx)
[实战文档 Markdown](sandbox:/mnt/data/semiconductor_skill_practical/docs/05_practical_opencode_skill_workshop.md)
[完整实战包 ZIP：文档 + demo_project](sandbox:/mnt/data/semiconductor_skill_practical_workshop.zip)

这份文档按“从简单到复杂”的路线写：

```text
普通 Python 函数
→ 可复用 CLI
→ opencode custom tool
→ opencode command
→ opencode skill
→ 半导体 Inline Display 三层业务改造
```

其中 demo 工程包含：

```text
demo_project/
├── data/sample_measurements.csv
├── tools_src/quick_stats.py
├── .opencode/
│   ├── tools/
│   │   ├── quick-stats.ts
│   │   ├── fab-query.ts
│   │   ├── fab-analysis.ts
│   │   └── fab-plot.ts
│   ├── commands/
│   │   ├── quick-stats.md
│   │   └── inline-display.md
│   └── skills/
│       ├── simple-data-profile/SKILL.md
│       └── inline-display/SKILL.md
├── inline_display/
│   ├── api/main.py
│   ├── cli/inline_analyze.py
│   ├── cli/inline_plot.py
│   ├── data/inline_records.json
│   └── artifacts/
└── opencode.json
```

我也做了基本验证：

```text
quick_stats.py 已用 sample_measurements.csv 跑通
inline_analyze.py 已生成 stats.csv 和 summary.json
inline_plot.py 已生成 inline_display.html
DOCX 已渲染为 29 页并抽查页面无明显排版问题
```

文档里用到的 opencode 说明基于官方文档：custom tools 可以放在 `.opencode/tools/`，工具定义用 TypeScript / JavaScript，但可以调用 Python 等任意语言脚本；commands 可以放在 `.opencode/commands/`，支持 frontmatter 和 `$ARGUMENTS` / `$1` 等参数；skills 通过 `.opencode/skills/<name>/SKILL.md` 发现，并由 `name` / `description` 决定触发和加载。([OpenCode][1])

Inline Display 的三层示例也按你之前的要求设计：查询层用 FastAPI mock API，处理层和绘图层用 CLI；FastAPI 的请求体建模参考了官方 Pydantic `BaseModel` 模式，Plotly HTML 输出参考了官方交互式 HTML 导出能力。([fastapi.tiangolo.com][2])

[1]: https://opencode.ai/docs/custom-tools/ "Custom Tools | OpenCode"
[2]: https://fastapi.tiangolo.com/tutorial/body/ "Request Body - FastAPI"
