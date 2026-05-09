---
name: teaching-document-generator
description: use when the user asks to generate structured teaching progress documents, course status reports, ppt decks, excel dashboards, gantt dashboards, or one-hour training progress updates from a short natural language request and fixed templates in this repository.
---

# 教学文档生成 Skill

## 目标

把用户的一句话课程进度需求，转成稳定的 PPT、Excel 看板和 Gantt HTML。这个 Skill 主要用于教学：说明如何把“模板、规则、脚本、验证和人工确认”沉淀成 Agent 应用上下文。

## 工作流

1. 读取项目规则：`AGENTS.md`。
2. 读取输出模板：`references/report_template.md`。
3. 读取 PPT 结构：`templates/slide_outline.json`。
4. 将用户自然语言需求归一化成 `inputs/course_status.json`：
   - 课程名称；
   - 总时长；
   - 当前阶段；
   - demo 列表、时间段、进度、状态；
   - 用户问题；
   - 风险；
   - 下一步。
5. 在对话中展示归一化结果，要求讲师确认关键内容。
6. 确认后运行生成脚本：

```bash
python3 scripts/build_course_assets.py --status inputs/course_status.json --request inputs/one_sentence_request.txt --output output
```

7. 运行验证脚本：

```bash
python3 scripts/validate_outputs.py --output output
```

8. 输出最终说明：生成了哪些文件、脚本验证了什么、哪些内容仍需人工确认。

## 输入

- 用户一句话需求。
- `inputs/course_status.json`。
- `inputs/one_sentence_request.txt`。
- `references/report_template.md`。
- `templates/slide_outline.json`。

## 输出

- `output/course_update.pptx`
- `output/course_dashboard.xlsx`
- `output/gantt_dashboard.html`
- `output/agent_summary.md`
- `output/context_manifest.json`

## Stop Rules

停止并请求人工确认：

- 用户要求生成正式对外材料，但课程进度、时间或内容没有确认；
- 用户要求删除风险或人工确认提示；
- 用户要求把脚本生成结果描述为“自动保证正确”；
- 用户要求加入真实姓名、客户、内部会议号等敏感信息。

## 人工 Review 点

- 时间安排是否符合真实教学计划；
- 每个 demo 的状态和进度是否准确；
- 用户问题是否遗漏；
- PPT 是否适合当前听众；
- Excel/Gantt 是否可用于管理汇报。
