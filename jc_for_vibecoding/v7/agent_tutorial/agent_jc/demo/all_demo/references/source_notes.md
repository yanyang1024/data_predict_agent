# Source Notes

本教学包参考的公开设计原则：

- OpenCode Skills：`.opencode/skills/<name>/SKILL.md`，通过 name/description 发现并按需加载。
- OpenCode Commands：`.opencode/commands/*.md` 用于重复任务入口，支持 `$ARGUMENTS`。
- OpenCode Custom Tools：`.opencode/tools/*.ts` 定义结构化动作，内部可调用 Python 脚本。
- OpenCode Permissions：`opencode.json` 用 allow/ask/deny 控制动作。
- ReAct：Reasoning -> Action -> Observation 的闭环思想。
- SWE-agent：软件工程 Agent 需要专门的 Agent-Computer Interface，能浏览仓库、编辑文件、运行测试。

这些原则被压缩到四个 demo：规则看板、spec 迁移、PDF 复现、权限沙箱。
