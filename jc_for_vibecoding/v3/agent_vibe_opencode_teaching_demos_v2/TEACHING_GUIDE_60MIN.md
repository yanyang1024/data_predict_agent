# 1 小时讲师脚本

## 0. 开场：为什么需要教学型 demo

这次不把 Agent 当作“更强的自动补全”，而是把它作为工程协作者：它能读文件、生成代码、运行脚本、整理报告，但必须被规则、工具和权限约束。

板书：

```text
一次性 prompt：解决一个问题
Skill：解决一类问题
Tool：把可执行动作封装起来
Permission：规定哪些动作能做、哪些必须问、哪些禁止
Human Review：确认业务语义和最终决策
```

## 1. Demo 00 讲法：基于规则的文档生成

先展示用户一句话，然后展示项目结构：

```text
AGENTS.md                       项目长期规则
.opencode/commands/teach-status.md 高频入口
.opencode/skills/rule-based-doc-generator/SKILL.md 作业指导书
scripts/generate_training_artifacts.py 确定性执行动作
configs/course_template.yaml     模板和输出规则
output/                          PPT、Excel、甘特图、dashboard
```

强调：Agent 不是直接随意生成 PPT，而是按模板提取信息、按固定 schema 生成输出，并把缺失信息写进 review checklist。

## 2. Demo 01 讲法：Doc Spec 可移植开发

三步：

```text
Spec -> Normalized Rules -> Platform Implementations -> Golden Case Validation
```

强调：同一份 spec 支持多个平台，不应让 Agent 每次重新解释文档。要抽取成中间规则，再由平台适配层生成目标实现。

## 3. Demo 02 讲法：富文本规则提取与 Skill 串联

四步：

```text
PDF/Markdown Manual -> Extracted Rules -> Environment Adapter -> Syntax Validation -> Human Logic Review
```

强调：语法正确不代表逻辑正确。工具可以验证格式、schema、语法；业务语义和结果合理性需要人介入。

## 4. Demo 03 讲法：权限约束执行

对比两种做法：

```text
危险做法：Agent 直接读 protected_data 或改 config
安全做法：Agent 只能调用 approved_query.py 和 propose_config_change.py
```

强调：不要只靠口头提醒或 prompt 约束。要用 opencode.json、封装 CLI、只读导出、manifest、proposal patch 共同兜底。
