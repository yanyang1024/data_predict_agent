# OpenCode 项目骨架讲解

## 1. AGENTS.md：长期规则

适合写：项目结构、测试命令、禁止动作、代码风格、Stop rules。它不是业务知识库，不要写得太长。

## 2. Skill：任务 SOP

适合写：这类任务什么时候触发、输入输出、流程、工具调用顺序、manifest 检查、人工确认点、报告模板。

## 3. Command：对话入口

适合把高频任务做成 `/dashboard`、`/port-spec`、`/reproduce-paper`、`/safe-change`、`/query-lot`。Command 的正文就是模板 prompt，可以使用 `$ARGUMENTS`。

## 4. Tool：结构化动作

OpenCode custom tool 是 TypeScript / JavaScript 定义的函数，但内部可以调用 Python、Shell 或其他脚本。教学重点是：Tool 不是为了炫技，而是为了把动作参数结构化、白名单化、可审计化。

## 5. Permission：兜底边界

Skill 里写“不要做”只是软约束；`opencode.json` 里的 deny/ask/allow 才是运行时边界。特别是数据、配置、生产脚本，要靠权限、封装脚本和 Data Service 一起控制。
