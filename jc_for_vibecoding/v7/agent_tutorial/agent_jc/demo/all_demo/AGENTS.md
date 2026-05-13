# OpenCode Context Engineering Demo Kit Rules

## 项目定位

这是一个教学仓库。目标不是展示复杂业务，而是展示如何把业务场景沉淀为可复用的 Agent context：规则、Skill、命令、工具/API、脚本、权限和验证闭环。

## 对 Agent 的长期要求

1. 先阅读当前 demo 的 `README.md`、`AGENTS.md` 和对应 Skill，再执行脚本。
2. 不要把所有文件一次性塞进上下文。优先加载：任务说明 -> Skill -> references 中相关文件 -> 脚本帮助或 README。
3. 修改代码前先给计划，说明：目标、输入、输出、拟调用脚本、验证命令、风险和人工确认点。
4. 只在 `output/`、`generated/`、`repro_project/`、`workspace/` 等允许区域生成结果。
5. 不要编辑 `protected/`、`references/source/`、`docs/locked/` 中的源材料，除非项目 README 明确允许。
6. 每次生成代码或报告后运行项目提供的验证脚本，并在回答里总结验证结果。
7. 如果验证只能证明语法正确，不能证明逻辑正确，必须明确写出需要人工 review 的点。

## 推荐回答结构

```text
1. 我理解的任务
2. 我加载的 context
3. 计划与动作空间
4. 执行结果
5. 验证结果
6. 未覆盖风险 / 需要人工确认
7. 后续如何沉淀成规则、Skill 或脚本
```
