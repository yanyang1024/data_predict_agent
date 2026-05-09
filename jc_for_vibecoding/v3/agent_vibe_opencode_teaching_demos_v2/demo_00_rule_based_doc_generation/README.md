# Demo 00 - 基于规则的文档生成

## 教学目标

用一个通用场景作为实践开场：用户只说一句话，Agent 按规则生成：

- PPT：教学进度汇报；
- Excel：进度看板与甘特图数据；
- PNG：甘特图；
- HTML：轻量 dashboard；
- Markdown：讲师简报和人工 review checklist。

这个 demo 用于讲解 OpenCode 从 0 到 1 的工作流：

```text
用户一句话
  -> OpenCode Command
  -> Skill 加载规则
  -> 脚本按模板执行
  -> 输出 PPT/Excel/图表/dashboard
  -> 人工确认缺失信息和最终表达
```

## 运行

```bash
python3 scripts/generate_training_artifacts.py \
  --request sample_request.txt \
  --progress data/course_progress.json \
  --template configs/course_template.yaml \
  --output-dir output
```

## 讲师提示

讲解时不要强调脚本多复杂，而要强调：

1. 生成类任务也需要 schema 和模板；
2. Agent 可以组织内容，但稳定输出依赖脚本和模板；
3. PPT/Excel/图表是执行结果，不是自由聊天结果；
4. 最终发布前仍需要人检查语气、事实、时间和听众。
