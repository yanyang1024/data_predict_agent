# Demo 00：基于规则的文档与看板生成 Agent

## 教学定位

这是入门 demo。它用一个通用场景说明：Agent 应用不是每次都重写 prompt，而是把 **模板、规则、脚本、Skill、Command 和验证** 组合起来。

场景：讲师只说一句话描述当前培训进展，Agent 需要按固定模板生成：

- `output/dashboard.html`：1 小时教学进度看板和甘特图；
- `output/status_report.md`：讲师口播版进度摘要；
- `output/dashboard_manifest.json`：可审计 manifest；
- `output/viewer.html`：浏览器演示页，聚合执行状态、产物链接和效果预览；
- `output/service_manifest.json`：本地 viewer 服务信息和可访问 URL；
- 验证结果：`validate_dashboard.py` 检查必要区块和四个 demo 状态。

## 这个 demo 教什么

1. 用 `AGENTS.md` 固化项目规则。
2. 用 Skill 说明“生成 dashboard 应该怎么做”。
3. 用 Command 让用户一句话触发 `/dashboard`。
4. 用 Tool / Script 把渲染动作结构化。
5. 用验证脚本形成闭环，而不是只看页面长得像不像。

## 从 0 到 1 构建步骤

```text
Step 0：写一个 session progress 的模板 JSON
Step 1：写 AGENTS.md，规定输出位置、禁止覆盖模板、必须运行验证
Step 2：写 generate_dashboard.py，把模板渲染成 HTML/Markdown
Step 3：写 validate_dashboard.py，检查输出是否完整
Step 4：写 dashboard-generator Skill，描述流程和人工确认点
Step 5：写 /dashboard command，降低用户入口成本
Step 6：写 dashboard.ts custom tool 示例，把脚本封装为结构化工具
Step 7：写 opencode.json，限制 edit 和 bash 行为
Step 8：调用 demo_viewer.py 自动重启本地服务，输出可直接打开的 URL
```

## 运行

```bash
python3 run_demo.py
```

运行后会自动启动或重启本地 viewer 服务，输出类似：

```text
Viewer URL: http://127.0.0.1:8760/
Primary URL: http://127.0.0.1:8760/output/dashboard.html
```

## OpenCode 演示 Prompt

```text
/dashboard 当前培训总时长 60 分钟。Demo 0 已完成，Demo 1 进行中，Demo 2 和 Demo 3 未开始。用户刚问：如何把一个临时 prompt 沉淀成稳定 Agent 应用？请生成讲师 dashboard。
```
