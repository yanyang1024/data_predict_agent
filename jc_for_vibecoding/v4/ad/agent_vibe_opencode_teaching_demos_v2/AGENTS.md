# OpenCode 教学 Demo 总规则

你正在协助讲师从 0 到 1 构建教学型 Agent 应用。请遵守以下规则：

## 工作方式

1. 复杂任务先用 plan 思维：先阅读 README、AGENTS.md、Skill、references、scripts，再提出最小执行计划。
2. 不要一次性改很多文件。每次只修改一个 demo、一个脚本或一个 Skill 模块。
3. 修改后必须运行对应 validator 或 `python3 run_all_demos.py` 的相关部分。
4. 输出解释时要区分：
   - Agent 可以自动完成的动作；
   - 脚本可以验证的语法 / schema / 文件存在性；
   - 必须由人确认的业务逻辑和最终结论。

## 安全边界

1. 不要连接生产数据库、内部系统或外部真实服务。
2. 不要读取或修改 `protected/` 下的真实敏感配置。Demo 中的 protected 文件均为 mock/sample。
3. 不要把生成代码标记为已完成业务 signoff。
4. 任何“逻辑正确”“规范完整”“可以上线”的结论都必须明确需要人工 review。

## 教学目标

请始终围绕“如何沉淀上下文”讲解，而不是围绕具体业务实现复杂度讲解。重点说明：

- AGENTS.md：项目长期规则和边界。
- Command：高频任务入口。
- Skill：任务流程、输入输出、工具顺序、停止规则。
- references：业务知识、模板、术语、契约、检查表。
- scripts/tools/API：可执行能力和受控动作。
- validators：语法、schema、文件、参数边界的自动检查。
- Human review：中间方案和最终逻辑正确性的人工确认。
