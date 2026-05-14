# 教学 PPT 文字稿

> 课程：从 Agent 技术演进到 OpenCode 工程实践  
> 面向：传统软件开发人员和数据分析工程师  
> 时长：约 60 分钟  
> 结构：第一部分「软件基础使用」+ 第二部分「实践」

---

# 第一部分：软件基础使用

---

## 第1页 | 封面

**标题**：从 Agent 技术演进到 OpenCode 工程实践  
**副标题**：面向软件研发人员的 Coding Agent 教程

**讲师稿**：  
大家好，今天这节课我们不把 OpenCode 当作一个"AI 写代码工具"来讲，而是把它作为一个可观测、可配置、可治理的本地 coding agent runtime，讲清楚它如何继承 ReAct 和 SWE-agent 的思想，以及研发团队应该如何安全使用它。

---

## 第2页 | 课程目标

**标题**：今天你要带走什么

**要点**：
- 理解 Agent 的本质，不只是"会调用工具的大模型"
- 掌握 OpenCode 的核心模块：session、tool、permission、agent、snapshot
- 学会安全使用 SOP：先 Plan、再 Build、测试验证、Git 提交
- 看懂四个实践 Demo：规则驱动文档、代码迁移、PDF 复现、权限沙箱

**讲师稿**：  
目标读者是有日常编码、调试、Code Review 经验的软件研发人员。我们不是把 OpenCode 当成聊天窗口介绍，而是讲清楚它作为一个 agent runtime 如何落地，以及团队应该如何安全使用。

---

## 第3页 | 一句话定位

**标题**：什么是 OpenCode

**核心定义**：  
> OpenCode 是一个运行在终端、本地项目和 Git 仓库里的 AI coding agent。它可以读代码、搜索代码、编辑文件、执行 shell 命令、跑测试，并通过会话持续推进任务。

**三个关键词**：
1. **本地项目**——不是只在浏览器里和你聊天，而是进入你的真实代码仓库
2. **工具能力**——不只是给建议，而是可以真的读文件、改文件、跑命令
3. **会话推进**——不是一次问答结束，而是可以在一个上下文里持续探索、修改、验证

**讲师稿**：  
正因为它真的能动手，所以我们不能用"随便聊聊"的方式使用它。我们要像管理一个真实开发者一样管理它：给目标、给规则、限制权限、要求测试、保留回滚点。

---

## 第4页 | Agent 技术演进主线

**标题**：从"会想"到"能安全地改代码"

**演进路线**：
```
ReAct（思考-行动-观察闭环）
  → Function Calling / Tool Calling（结构化动作）
    → SWE-agent（软件工程专用 ACI）
      → OpenCode（本地 coding agent runtime）
```

**一个成熟的 coding agent 是**：
> **模型 + 代码仓库上下文 + 工具动作空间 + 权限系统 + 会话状态 + 快照/回滚 + 团队规则 的工作系统。**

**讲师稿**：  
OpenCode 可以作为这条演进链在本地开发场景中的一个工程化样本。它不是"更会写代码的模型"，而是把决策循环、结构化动作、工程专用接口和本地运行时组合在一起的工作系统。

---

## 第5页 | ReAct：Agent 的最小闭环

**标题**：Agent 不是模型，而是决策循环

**核心贡献**：ReAct 的贡献不是"让模型更聪明"，而是建立了循环：
```
推理 → 动作 → 观察 → 再推理
```
或者说：
```
观察任务 → 形成假设 → 调用动作 → 接收观察 → 修正计划 → 再行动
```

**研发场景类比**：
```
怀疑 bug 在鉴权中间件
→ grep 路由入口
→ read 认证逻辑
→ 跑一条失败测试
→ 发现根因在 token refresh
→ 最小修改
→ 再跑测试验证
```

**讲师稿**：  
ReAct 阶段解决的是：模型不再只做一次性回答，而是可以边查边改、边改边验证。这一步特别像一个刚入职的工程师在排障：先想一个假设，再去做个动作，拿到观察，再修正假设。

---

## 第6页 | Tool Calling：结构化动作

**标题**：把"我想做"变成"可执行动作"

**核心**：自然语言的动作无法稳定执行，需要把动作做成结构化接口

```json
{
  "tool": "grep",
  "input": { "pattern": "refreshToken", "path": "src" }
}
```

**OpenCode 对应工具**：
- 观察类：read、grep、glob、lsp、webfetch、websearch
- 修改类：edit、write、apply_patch
- 执行类：bash
- 编排类：task、skill、todo、question
- 研究类：repo_clone、repo_overview

**讲师稿**：  
用一个直观的比方——ReAct 里的 Action 像"跟同事口头说一下要干嘛"；Function Calling 像"提交一张工单"。模型不再只是"建议你运行测试"，而是请求运行某个具体命令、读取某个文件、修改某段代码。没有结构化动作，Agent 只是"会描述自己想做什么"；有了 Function Calling，它才开始"真的能做"。

---

## 第7页 | SWE-agent：软件工程需要专门的 ACI

**标题**：给模型配一套适合做软件工程的工作台

**核心**：通用工具对 coding agent 不够，软件开发天然需要：
- 文件阅读和搜索
- 精确编辑和补丁应用
- 终端命令和测试输出
- LSP 语义信息
- 代码库规则
- 会话轨迹和回滚

**类比**：就像人类程序员不是赤手空拳写系统，而是要有终端、文件浏览器、编辑器、测试运行器、代码搜索、调试反馈。SWE-agent 就是给 agent 配这些"工位设施"。

**讲师稿**：  
SWE-agent 不是"让模型会写代码"，而是"给模型配了一套适合做软件工程的工作台"。这就是 SWE-agent 的 Agent-Computer Interface 思想——给 agent 一张适合软件工程的"工作台"，而不是让它只靠聊天窗口猜。

---

## 第8页 | OpenCode：将 coding agent 做成本地运行时

**标题**：OpenCode 的模块化架构

**核心公式**：
```
OpenCode = 本地 TUI / CLI / Server
         + 多 provider LLM 调用
         + Agent 配置
         + Tool Registry
         + Permission Gate
         + Session Processor
         + Snapshot / Undo
         + AGENTS.md / Skills / Commands / MCP / Plugins
```

**讲师稿**：  
它的关键价值不是"生成一段代码"，而是把研发过程中的"查、改、跑、验、审、回滚"串成一个可配置的运行时。它不是一个更大的 prompt，而是一套更完整的工作系统。

---

## 第9页 | Agent 六个抽象槽位

**标题**：六部分抽象如何对应 OpenCode 模块

| Agent 抽象 | 研发语义 | OpenCode 对应能力 / 模块 |
|---|---|---|
| Goal 目标 | 这次要修什么、验收标准是什么 | 用户 prompt、自定义 command、AGENTS.md 规则 |
| State 状态 | 当前会话、消息、todo、上下文、快照 | session、message-v2、todo、summary、snapshot |
| Actions 动作空间 | 能读、搜、改、跑、查文档、派生子任务 | tool/registry.ts 和内置工具 |
| Observations 观察 | 命令输出、测试失败、文件内容、LSP 结果 | tool output、truncation、Message parts |
| Policy 策略 | 用哪个 agent、哪个模型、是否能改代码 | Build / Plan / Explore / Scout、自定义 agent |
| Runtime 运行时 | 调度、权限、回滚、压缩、扩展、服务化 | session/processor、permission、snapshot、MCP、plugins、server |

**讲师稿**：  
一个适合教程中的比喻——ReAct 像"会自己排障的实习生"；OpenCode 像"带 IDE、终端、工单、权限审批、代码快照的本地开发工位"。

---

## 第10页 | 最小上手流程

**标题**：第一次使用 OpenCode

**四步流程**：
```bash
cd /path/to/project
opencode           # 第一步：启动
/connect           # 第二步：配置模型 provider
/init              # 第三步：初始化项目规则
```

**讲师稿**：  
`/init` 不是一个形式动作，它生成的是 OpenCode 的项目说明书。对人类新人来说，入职要看 README、CONTRIBUTING、架构文档。对 OpenCode 来说，AGENTS.md 就是这类信息的入口。所以初始化后，我们不要立刻让它开改，而是先看它生成的 AGENTS.md 是否靠谱——有没有正确识别包管理器？有没有写清楚测试命令？有没有遗漏安全规则？

---

## 第11页 | Plan vs Build

**标题**：最重要的操作习惯：先 Plan，再 Build

**一句话区分**：
> **Plan 是让 Agent 想清楚，Build 是让 Agent 动手。**

- **Plan**：受限代理，适合分析、审查、制定计划，不允许直接改代码
- **Build**：默认开发代理，拥有完整工具访问能力，可实际修改文件和执行命令

**界面操作**：Tab 键在 Plan 和 Build 之间切换

**推荐 SOP**：
- 复杂任务：Plan → 人类确认 → Build
- 简单任务：Build 直接改，但必须限定范围
- 高风险任务：Plan + 只读探索 + 手动执行关键命令

---

## 第12页 | Prompt 示例对比

**标题**：好的 Prompt vs 不好的 Prompt

**不好的 Prompt**：
```
帮我重构支付模块。
```
这个提示太大、太模糊，而且一上来就让 Agent 自由发挥。

**更好的 Prompt**：
```
先不要改代码。请阅读支付模块中 retry、charge、idempotency 相关实现，
找出重复扣款可能发生的位置。输出：
1. 相关文件路径
2. 当前调用链
3. 可能根因
4. 最小修复方案
5. 需要补的测试
```

**讲师稿**：  
好的 Prompt 有四个好处：第一，它明确说"先不要改代码"；第二，它限定了搜索范围；第三，它要求输出证据和计划；第四，它把实现和验证拆开。这就是 coding agent 使用中的核心心法——不要让 Agent 一上来写代码，先让它收集证据、收敛假设、提出方案。

---

## 第13页 | AGENTS.md：项目作业指导书

**标题**：AGENTS.md 不是装饰文件

**核心**：AGENTS.md 是 OpenCode 理解项目的核心上下文，每次会话都会被加载

**五类信息**：

1. **项目结构**
```markdown
## Project Structure
- src/api: HTTP API
- src/domain: domain logic
- src/infra: database and external services
- tests: unit and integration tests
```

2. **开发命令**
```markdown
## Commands
- Install: pnpm install
- Unit test: pnpm test:unit
- Typecheck: pnpm typecheck
- Lint: pnpm lint
```

3. **代码规范**
```markdown
## Code Style
- Prefer small, focused changes
- Keep public API backward compatible
- Add regression tests for bug fixes
```

4. **安全边界**
```markdown
## Safety
- Do not read or modify .env files
- Do not run rm -rf
- Do not run pkill -f or killall
- Ask before changing database migrations
```

5. **验收标准**
```markdown
## Definition of Done
- Relevant tests pass
- git diff is reviewed
- No unrelated formatting changes
- User-facing behavior is explained
```

**讲师稿**：  
不要把 AGENTS.md 讲成"提示词文件"，要讲成——这是给 Agent 的项目作业指导书。我建议每个团队都把 AGENTS.md 当成工程治理的一部分，而不是个人随意编写的提示词。可以放在项目根目录（项目级）或 `~/.config/opencode/AGENTS.md`（全局级）。

---

## 第14页 | Permission 权限系统

**标题**：别让 Agent 拿到无限 root 权限

**三档权限动作**：
```text
allow：低风险，可自动执行
ask：中风险，需要人类确认
deny：高风险，直接禁止
```

**核心原则**：
> 读操作可以宽一些，写操作要问，删除和杀进程默认拒绝。

**日常建议**：
```
读操作 allow
写操作 ask
删除、杀进程、重置 Git、清理 Docker deny
```

**讲师稿**：  
权限配置不是为了阻碍效率，而是为了让 Agent 在可控范围内提高效率。一个经验判断是：只要这个命令在人类手上敲错都可能造成损失，就不要让 Agent 自动执行。

---

## 第15页 | 推荐安全基线配置

**标题**：opencode.json 安全模板

**讲师稿**：  
下面是一个偏保守的团队模板。第一次落地建议从保守开始，再按团队习惯逐步放宽。注意 OpenCode 的权限匹配是"后匹配规则优先"，所以通配符 `*` 应该放在前面，更具体规则放在后面。

**配置要点**：
- read 匹配 `*.env`、`*.env.*` 设为 deny（`*.env.example` 设为 allow）
- bash 中 `git status/diff/log` 设为 allow，`git push/reset/clean` 设为 deny
- bash 中 `pkill/killall/rm -rf` 设为 deny
- edit/write 设为 ask
- Plan 模式下 edit 设为 deny（禁止 Plan 模式改代码）
- Build 模式下 git push/reset/clean/pkill/killall/rm -rf 设为 deny

---

## 第16页 | 回滚策略

**标题**：Git 是主保险，/undo 是副保险

**核心原则**：
```text
Git checkpoint 是主保险
OpenCode /undo 是辅助保险
```

**每次大改前**：
```bash
git status
git add -A
git commit -m "checkpoint: before opencode task"
# 或
git stash push -u -m "checkpoint before opencode task"
```

**正确姿势**：
- Git checkpoint 是主保险
- OpenCode /undo 是辅助保险
- 尤其在多轮修改、子代理、长命令、跨平台文件系统等场景下，必须用 Git 自己做明确 checkpoint

**讲师稿**：  
OpenCode 的 /undo 是局部撤销工具，不是版本回滚工具。公开 issue 中已经出现过 snapshot cache 的 stale index.lock 导致 undo 异常的问题。Agent 改代码之前，先让 Git 记住当前世界线。

---

## 第17页 | 子代理系统

**标题**：子代理——把不同类型的工作隔离开

**OpenCode 内置代理**：

| Agent | 建议角色 | 是否允许改代码 |
|---|---|---|
| Plan | 需求澄清、方案设计、风险分析 | 否 |
| Explore | 只读代码探索、定位入口 | 否 |
| Scout | 查外部依赖、上游实现、文档 | 否 |
| Build | 最小实现、补测试、跑验证 | 是，但需权限控制 |
| General | 复杂问题、多步骤任务 | 否 |

**使用示例**：
```
@explore 请只读搜索订单删除相关代码路径，不要修改文件。
@scout 请查看当前使用的 ORM 文档，确认 soft delete 查询应该怎么写。
```

**适合子代理的任务**：代码路径探索、依赖文档核对、历史实现对照、风险审查、测试覆盖检查  
**不适合子代理的任务**：让多个 agent 同时乱改同一批文件

**讲师稿**：  
子代理不是为了炫技，而是为了把不同类型的工作隔离开。多 Agent 的价值是并行取证，不是并行制造冲突。

---

## 第18页 | 日常使用 SOP（黄金路径）

**标题**：推荐日常 SOP

```text
1. git status，确认工作区干净
2. 创建 checkpoint 或新分支
3. opencode 进入项目
4. /init 生成或更新 AGENTS.md
5. Plan 模式：让它读代码、找路径、给方案
6. 人类审计划：范围、风险、测试是否合理
7. Build 模式：只让它做最小修改
8. 跑定向测试，不要一上来跑全量
9. git diff 人工 review
10. 通过后 commit
```

**一句话总结**：
> OpenCode 最适合被当成"初级到中级工程师 + 很快的代码阅读器 + 自动 patch 执行器"，而不是无人驾驶系统。

---

## 第19页 | 验证与 Review

**标题**：验证必须独立于实现

**推荐验证顺序**：
```bash
git diff --stat
git diff
pnpm test <related-test>
pnpm typecheck
pnpm lint
```

**Agent 交接摘要应包含**：
1. 根因
2. 修改点
3. 新增/修改测试
4. 已运行验证命令和结果
5. 未覆盖风险
6. 建议 code review 重点

**讲师稿**：  
让 Agent 跑最小验证，如果失败，先解释失败原因，不要立刻扩大修改面。然后再运行 lint/typecheck。

---

## 第20页 | 常见坑一：pkill 乱杀或挂住

**标题**：常见坑——pkill -f 可能误杀 OpenCode

**现象**：Agent 执行 `pkill -f` 在 TUI 中可能导致 tool call 挂起，在 CLI 中可能导致 `opencode run` 自己被终止。

**根因**：`pkill -f` 按完整命令行匹配，可能匹配到 OpenCode 自身或它的子进程。

**治理方式**：
1. 在 permission 中直接 deny：`"pkill *": "deny"`
2. Agent 可以查进程但不能自动杀进程
3. 正确做法：
```bash
lsof -i :3000   # Agent 负责定位
kill <PID>      # 人类在外部终端执行
```

---

## 第21页 | 更多常见坑

**标题**：后台命令、上下文膨胀、write 覆盖

**坑：长时间后台命令导致 bash tool 挂起或残留进程**
```bash
npm run dev &     # 禁止！
pnpm start &      # 禁止！
```
- 长跑服务放在单独终端或 tmux pane 中
- Agent 只运行短命令：测试、lint、typecheck、grep、git diff
- 如果必须临时启动，要求重定向并写 PID 文件

**坑：MCP / Web 工具过多导致上下文膨胀**
- 默认关闭非必要 MCP
- 文档查找优先用 Scout / webfetch
- 按 agent 配置 MCP 权限

**坑：write 可能覆盖已有文件**
- 优先使用 edit / apply_patch
- 对新文件要求 Agent 先说明文件路径和原因
- prompt 中声明"不要整体重写大文件"

---

## 第22页 | 可直接复用的 Prompt 模板

**标题**：四类 Prompt 模板

**只读探索模板**：
```
请只读探索，不要修改文件，不要运行会改变状态的命令。
目标：<描述任务>
请输出：1. 相关入口文件 2. 调用链 3. 数据结构/API/配置位置
4. 需要验证的假设 5. 建议的最小修改方案
```

**开始实现模板**：
```
请按已确认方案做最小实现。约束：不要提交代码。
不要运行 pkill/killall/taskkill/rm -rf/git reset/git clean。
不要启动长时间后台服务。优先 edit/apply_patch。
修改后先给出 diff 摘要，再运行最小相关测试。
```

**验证模板**：
```
请验证本次改动。步骤：1. git diff --stat 和 git diff
2. 运行最小相关测试 3. 通过后再跑 typecheck/lint
4. 失败先解释，不要扩大修改面
5. 输出已验证项、未验证项和风险
```

**Review 模板**：
```
请以审查者身份审查本次 diff，不要修改文件。
重点看：正确性、边界条件、并发/幂等/事务风险、安全风险、测试覆盖、是否有无关改动
```

---

## 第23页 | 第一部分 Takeaway

**标题**：研发人员应该带走什么

**七个核心点**：
1. Agent 不是模型，而是运行时中的决策循环
2. Coding agent 的关键能力不是"写"，而是"查、改、跑、验、审、回滚"
3. OpenCode 核心学习对象是模块边界：session、tool、permission、agent、snapshot
4. 团队落地先做权限治理，再谈效率提升
5. 永远用 Git 做主版本控制，OpenCode 的 /undo 只是辅助
6. 不要让 agent 执行广义 kill / destructive git / rm -rf 类命令
7. 把 Plan / Explore / Review 变成默认工作流，把 Build 当成受控执行阶段

---

# 第二部分：实践

---

## 第24页 | 实践部分导言

**标题**：四个 Demo，四种业务场景

**教学包定位**：不是复现复杂业务，而是展示如何把业务场景沉淀为可复用的 Agent context

**核心教学目标**：
1. 演示 Agent 应用不是单个 prompt，而是对话模式 + 项目规则 + Skill + 工具/API + 脚本 + 权限 + 验证闭环
2. 让学员理解 context 不是越堆越大的提示词，而是可以分层、外部化、可交接的系统
3. 通过 OpenCode 项目结构，展示如何把历史文档、样例、开发规范、测试项、权限边界和验证脚本沉淀下来
4. 训练四个方法论：先设计动作空间再谈自治；先取证验证纠偏再自动完成；先分层 context 再扩展上下文；先工具和安全边界再生产落地
5. 每个 demo 产物通过本地 viewer 服务暴露为浏览器链接，讲师能直观看到执行过程和效果

**四个 Demo 概览**：

| 编号 | 项目 | 教学重点 | 一句话场景 |
|---|---|---|---|
| 00 | 规则驱动 Dashboard | 规则、模板、脚本、工作流入门 | 一句话更新进展，Agent 按模板生成 HTML 看板 |
| 01 | Web App 跨框架迁移 | 历史代码 + 功能 spec + 风格 spec + 样例验证 | Gradio → Flask 迁移，保持功能和界面一致 |
| 02 | PDF 复现项目生成 | PDF 抽取、Skill 串联、环境适配、验证闭环 | 从论文 PDF 抽取实验逻辑，生成可运行复现项目 |
| 03 | 权限沙箱与数据服务 | 权限约束、动作空间设计、受控脚本/API | 配置变更或数据查询，只能通过封装脚本执行 |

---

## 第25页 | Context 分层架构

**标题**：Context 分层速查表

| 层 | 放什么 | 在 OpenCode 中的位置 | 作用 |
|---|---|---|---|
| 对话层 | 用户当前需求、限制、反馈 | 当前聊天 | 说明这一次要做什么 |
| 规则层 | 项目结构、禁止操作、测试命令、编码规范 | AGENTS.md | 每次会话都应该遵守 |
| 流程层 | 某类任务怎么做、何时停止、如何报告 | .opencode/skills/ | 把一次 prompt 变成一类 SOP |
| 入口层 | 高频任务的一句话命令 | .opencode/commands/ | 降低用户发起任务门槛 |
| 动作层 | 可执行能力、受控 API、脚本封装 | .opencode/tools/、scripts/ | 让 Agent 做事，同时限制动作 |
| 证据层 | 历史文档、源实现、样例、schema、验收 cases | references/、docs/、tests/ | 让 Agent 有依据，不凭空生成 |
| 观察层 | 测试结果、lint、manifest、diff、报告 | output/、manifest.json | 让 Agent 能验证和纠偏 |
| 展示层 | 浏览器入口、状态页、产物预览 | output/viewer.html、viewer 服务 | 让讲师和业务方直观看到执行效果 |
| 安全层 | 权限、白名单、字段脱敏、sandbox、stop rules | opencode.json、policy | 缩小动作空间，避免误操作和数据泄露 |

**四个设计原则**：
1. 先设计动作空间，再谈自治
2. 先让 Agent 学会取证、验证和纠偏，再要求它自动完成任务
3. 不要把上下文当成越来越大的 Prompt，要把它当成可分层、可外部化、可交接的系统
4. 生产里的 Agent 稳定性来自运行时、记忆、协议、工具、安全和工作流的组合

---

## 第26页 | OpenCode 项目骨架

**标题**：一个标准 Demo 项目的结构

```text
AGENTS.md                 # 项目长期规则，说明安全边界、目录结构、验证命令
opencode.json             # OpenCode 权限配置示例
.opencode/commands/       # 对话入口，例如 /dashboard、/port-spec
.opencode/skills/         # 可复用 Skill，含 references/templates/checklists
.opencode/tools/          # OpenCode custom tool 示例，封装脚本/API
scripts/                  # 可执行脚本，Agent 应优先调用脚本而不是临时写散乱命令
references/context/       # 历史文档、规范、模板、样例、schema
output/                   # demo 运行后生成的产物、manifest
```

**讲师稿**：  
每个项目都是一个自包含的最小 agent 应用骨架。学员回去做自己的业务 demo 时，可以复用这个结构。我们今天每个 demo 都按同一个问题来看：业务一句话是什么？context 拆成哪些层？Agent 可以做什么，不能做什么？哪些能自动验证，哪些必须人工 review？

---

## 第27页 | Demo 00：规则驱动 Dashboard

**标题**：Demo 00——从一句话到规则化 Dashboard

**一句话场景**：讲师只说当前培训进展，Agent 按模板生成 HTML dashboard、状态报告和 manifest

**教学重点**：规则、模板、脚本、OpenCode 工作流入门

**Context 分层**：
- **规则层**：AGENTS.md 规定输出位置、禁止改模板、必须运行验证
- **流程层**：Skill 规定字段怎么抽取、加载什么 context、调用什么脚本、怎么验证
- **入口层**：Command `/dashboard` 提供对话入口
- **动作层**：脚本负责渲染 HTML
- **观察层**：验证脚本检查必要区块，manifest 记录输入、输出、生成时间和验证提示

**讲师稿**：  
如果每次让模型临时写 HTML，字段、样式、状态口径都会漂移。我们的做法是把字段抽取规则、模板、脚本和验证固定下来，用户的一句话才会变成稳定产物。注意 Skill 不是业务知识大全，它是这个任务的 SOP——加载什么 context、调用什么脚本、怎么验证、什么时候停止。

---

## 第28页 | Demo 00：演示流程

**标题**：Demo 00——现场演示

**现场 Prompt**：
```
/dashboard 当前培训总时长 60 分钟。Demo 0 已完成，Demo 1 进行中，
Demo 2 和 Demo 3 未开始。用户刚问：如何把一个临时 prompt 沉淀成
稳定 Agent 应用？请生成讲师 dashboard。
```

**现场命令**：
```bash
cd 00_rule_dashboard_agent
python3 run_demo.py
```

**浏览器打开**：`http://127.0.0.1:8760/`

**查看产物**：
- output/ 中的 HTML dashboard
- output/dashboard_manifest.json（记录输入、输出、时间、验证提示）
- viewer 页面展示执行状态、执行过程、产物链接和效果预览

**展示要点**：
- viewer 页面展示执行状态、执行过程、产物链接和效果预览
- 状态报告说明哪些内容来自模板，哪些需要讲师确认
- manifest 是可交接的观察结果，不只是"页面生成成功"

**人工 review 点**：
- 用户自然语言里缺失的字段是否用了默认值
- Dashboard 内容是否代表真实教学状态

**Takeaway**：规则驱动文档生成的重点，不是让模型写得更花，而是把模板、字段、脚本和验证固化下来。

---

## 第29页 | Demo 01：Web App 跨框架迁移

**标题**：Demo 01——Gradio → Flask 迁移

**一句话场景**：把 Gradio CSV 分析与绘图 Web App 迁移为 Flask 项目，保持功能和前端界面风格一致

**教学重点**：基于历史代码、功能文档和前端风格规范的开发

**对应真实业务**：已有内部 Gradio/Streamlit 工具或老框架页面，需要迁移到统一的 Flask/FastAPI/企业 Web 平台

**讲师稿**：  
这个 demo 不是单纯翻译语法，而是要同时看原始实现、功能 spec、迁移规范、前端风格规范和样例验收。

---

## 第30页 | Demo 01：架构与演示

**标题**：Demo 01——Context 分层与现场演示

**Context 分层**：
- **证据层（用户需求）**：user_migration_request.md
- **证据层（功能规格）**：csv_analysis_app_spec.md
- **证据层（迁移规范）**：gradio_to_flask_migration_spec.md
- **证据层（前端风格）**：frontend_style_spec.md
- **证据层（历史代码）**：references/source/gradio_csv_analyzer.py
- **证据层（参考实现）**：references/examples/flask_reference_style.py
- **观察层（验收）**：analysis_cases.json + 多组 CSV（标准、无数值列、缺失值、空数据）
- **入口层**：Command `/port-spec`

**现场 Prompt**：
```
/port-spec 请把 references/source/gradio_csv_analyzer.py 迁移为 Flask 项目，
输出到 generated/flask_app/。要求保持 docs/csv_analysis_app_spec.md 中的
CSV 分析和绘图功能，并遵循 docs/frontend_style_spec.md 的前端风格。
先输出迁移计划和风险点，再调用脚本生成，并运行标准路径和边界 CSV 验证。
```

**现场命令**：
```bash
cd 01_doc_spec_portability
python3 run_demo.py
```

**浏览器打开**：`http://127.0.0.1:8761/`

**当前验证覆盖**：CSV 行列统计、数值列识别、数值摘要、推荐绘图列、无数值列、缺失值统计、空数据错误路径、静态风格检查

**人工 review 点**：
- 生产上传安全、MIME 校验、病毒扫描
- 部署方式和运行环境
- 复杂图表、混合编码、超大文件处理

**Takeaway**：Web App 迁移不是"换一个框架语法"，而是"源实现 + 功能 spec + 迁移规范 + 前端风格 spec + 样例验证"的组合。自动验证通过只说明样例和边界行为、静态结构符合预期，不说明生产问题都已解决。

---

## 第31页 | Demo 02：PDF 抽取与复现项目

**标题**：Demo 02——从 PDF 到可运行复现项目

**一句话场景**：从 synthetic paper PDF 抽取实验逻辑，结合本地环境包生成最小可运行复现项目

**教学重点**：PDF/论文信息抽取、Skill 串联、环境包适配、验证闭环

**核心流程**：
```
PDF → 抽取 evidence → 设计摘要 → 生成代码 → 验证
```

**讲师稿**：  
很多人会把这类任务理解成"让 AI 读 PDF，然后给我建议"。但这里我们要演示的是更工程化的流程——先抽取 evidence，再生成设计摘要，再生成代码，再验证。PDF 抽取规则规定要提取哪些字段，这样 Agent 不是读完后凭印象写代码，而是先生成结构化证据。

---

## 第32页 | Demo 02：架构与演示

**标题**：Demo 02——Context 分层与现场演示

**Context 分层**：
- **证据层**：pdf_extraction_rules.md（目标、环境要求、算法步骤、参数、实验逻辑、限制）
- **证据层**：papers/synthetic_paper_text.md
- **证据层**：env_pkg 本地环境库
- **流程层**：Skill 规定抽取 → 设计 → 生成 → 验证流程
- **入口层**：Command `/reproduce-paper`

**现场 Prompt**：
```
/reproduce-paper 请从 papers/synthetic_agent_eval_paper.pdf 提取实验逻辑，
结合 env_pkg/ 中的本地环境库，生成一个最小可运行复现项目。
不要声称复现了论文全部结论，只验证语法和示例测试。
```

**现场命令**：
```bash
cd 02_pdf_reproduction_agent
python3 run_demo.py
```

**浏览器打开**：`http://127.0.0.1:8762/`

**查看产物**：evidence.json、design_brief.md、repro_project/src/、repro_project/tests/、validation_manifest.json

**重要声明边界**：
- 验证脚本通过 → 生成项目语法正确、样例测试通过
- 不能说论文已被完整复现
- 不能说算法科学结论成立
- 公式语义、实验口径、真实数据适配仍需人审

**人工 review 点**：
- PDF 抽取是否遗漏公式上下文
- 样例 anomaly index 是否符合论文意图
- 算法是否适合真实数据

**Takeaway**：辅助编程不只是"读资料给建议"，也可以完成一部分执行动作；但执行动作必须被 evidence 和验证约束。

---

## 第33页 | Demo 03：权限沙箱与受控数据服务

**标题**：Demo 03——权限、动作空间与 Data Service

**两个场景**：
- **场景A（配置变更）**：用户要求打开 sandbox 的 beta_dashboard flag，但不能改 production 配置
- **场景B（数据查询）**：查询 lot history 的 QTime / UT 汇总，但不读取 protected 原始数据

**教学重点**：权限约束、动作空间设计、受控脚本/API、保护数据和配置

**讲师稿**：  
Skill 里的"不要做"只是软约束，opencode.json 和脚本/API 才是运行时边界。这个配置禁止编辑 protected/，禁止读取敏感原始数据。

---

## 第34页 | Demo 03：架构与演示

**标题**：Demo 03——Context 分层与现场演示

**Context 分层**：
- **安全层**：opencode.json 禁止编辑 protected/、禁止读取敏感原始数据
- **安全层**：data_access_policy.json、allowed_flags.json
- **安全层**：config_patch_schema.json、lot_query_schema.json
- **动作层**：propose_config_patch.py（只能通过受控脚本生成 proposal）
- **动作层**：query_lot_history_service.py（模拟 Data Service，只返回聚合结果）
- **观察层**：validate_data_service.py（检查字段白名单、lot 白名单、审计日志、protected hash）

**场景A Prompt**：
```
/safe-change 请把 sandbox 中的 beta_dashboard flag 打开，原因是培训演示需要。
不要读取 customer_data.csv，不要修改 protected/prod_config.json，
只能通过受控脚本生成 proposal 并应用到 sandbox。
```

**场景B Prompt**：
```
/query-lot 请查询 LOT-A12 的 QTime / UT 汇总并生成图。
不要读取 protected/lot_history_raw.csv，只能通过数据服务脚本返回聚合结果。
```

**现场命令**：
```bash
cd 03_permission_sandbox_agent
python3 run_demo.py
```

**浏览器打开**：`http://127.0.0.1:8763/`

**验证结果**：Config patch validation passed. / Data service validation passed.

**验证脚本检查项**：字段白名单、lot 白名单、审计日志、protected 文件 hash（未改动）

**人工 review 点**：
- QTime / UT 口径是否符合业务定义
- 真实落地时脚本应替换成带鉴权、审计、限流和脱敏的 HTTP Data Service

**Takeaway**：生产里的 Agent 不是权限全开的自动化脚本，而是被封装在受控动作空间里的协作者。

---

## 第35页 | 四个 Demo 横向对比

**标题**：四个 Demo 核心对比

| Demo | 一句话场景 | 关键约束 | 自动验证了什么 | 没验证什么（需人工 review） |
|---|---|---|---|---|
| 00 | 一句话生成 Dashboard | 模板 + 字段固化 | HTML 结构 + 内容合规 | 内容是否代表真实状态 |
| 01 | Gradio → Flask 迁移 | 功能 spec + 风格 spec | 样例 CSV 行为和静态结构 | 生产上传安全、部署、超大数据 |
| 02 | PDF → 复现项目 | evidence + 设计摘要 | 语法正确 + 样例测试通过 | 论文完整复现、科学结论 |
| 03 | 配置变更 / 数据查询 | 脚本封装 + Data Service | 字段白名单 + 审计 + 无泄露 | QTime 口径业务正确性 |

---

## 第36页 | 四种方法论总结

**标题**：从 Demo 中提炼的四个方法论

**第一，先设计动作空间，再谈自治。**
没有工具约束、权限边界和验证回路，Agent 只是放大不稳定性。

**第二，先让 Agent 学会取证、验证和纠偏，再要求它自动完成任务。**
Demo 01 和 Demo 02 都是在先定义证据和验收标准，再生成代码。

**第三，不要把 context 当成越来越大的 prompt，要把它当成可分层、可外部化、可交接的系统。**
AGENTS.md、Skill、Command、Tool、references、output manifest 各有位置。

**第四，真正让 Agent 在生产里站住脚的，不是某一个神奇 prompt，而是运行时、记忆、协议、工具、安全和工作流一起配合。**

---

## 第37页 | 最终 Takeaway 与起步建议

**标题**：最终口诀与起步建议

**最终口诀**：
> **先规则，后任务；先计划，后修改；先小改，后测试；先 checkpoint，后放手。**

**展开**：
```text
1. AGENTS.md 写清楚项目规则
2. opencode.json 收紧危险权限
3. 复杂任务先用 Plan
4. 修改前先做 Git checkpoint
5. 让 Agent 做最小 patch
6. 让测试和 git diff 说话
7. 高危命令由人类手动执行
8. 不把 /undo 当唯一回滚方案
```

**推荐三个低风险起步场景**：
1. 让 Agent 解释陌生模块
2. 让 Agent 补充单元测试
3. 让 Agent 修一个范围明确的小 bug

**讲师稿**：  
不要一上来让它改核心业务代码。先从低风险场景开始，等你熟悉了 Plan、Build、AGENTS.md、权限、Git checkpoint 这一整套流程，再把它用于更复杂的研发任务。

---

## 第38页 | 结尾页

**标题**：谢谢 / Q&A

**回到定义**：
> 一个成熟的 coding agent 不是"更会写代码的模型"，而是：
> **模型 + 代码仓库上下文 + 工具动作空间 + 权限系统 + 会话状态 + 快照/回滚 + 团队规则 的工作系统。**

**讲师稿**：  
今天大家回去之后，建议从这三个问题开始做自己的业务 demo：
1. 用户的一句话需求是什么？
2. Agent 能做哪些动作，不能做哪些动作？
3. 证据、模板、schema、样例和测试分别放在哪里？
4. 最终输出如何验证，哪些地方必须人工 review？

---

# 附录：快速索引

## 四个 Demo 的 Viewer URL

| Demo | URL |
|---|---|
| 00 规则看板 | http://127.0.0.1:8760/ |
| 01 Gradio → Flask | http://127.0.0.1:8761/ |
| 02 PDF 复现 | http://127.0.0.1:8762/ |
| 03 权限沙箱 | http://127.0.0.1:8763/ |

## 四个 Demo 的运行命令

```bash
# 全部运行
cd agent_jc/demo/all_demo && python3 run_all_demos.py

# 单个运行
cd agent_jc/demo/all_demo/00_rule_dashboard_agent && python3 run_demo.py
cd agent_jc/demo/all_demo/01_doc_spec_portability && python3 run_demo.py
cd agent_jc/demo/all_demo/02_pdf_reproduction_agent && python3 run_demo.py
cd agent_jc/demo/all_demo/03_permission_sandbox_agent && python3 run_demo.py
```

## 第一部分核心概念速查

| 概念 | 一句话 |
|---|---|
| Agent | 带状态的决策循环（目标+状态+动作+观察+策略+运行时） |
| ReAct | 推理→动作→观察的闭环 |
| Tool Calling | 用 JSON Schema 定义结构化动作接口 |
| SWE-agent | 为软件工程设计专门的 Agent-Computer Interface |
| OpenCode | 本地 coding agent runtime |
| Plan | 想清楚——分析、方案、风险 |
| Build | 动手——实现、测试、验证 |
| AGENTS.md | 给 Agent 的项目作业指导书 |
| Permission | allow / ask / deny 三档权限控制 |
| /undo | 会话级便利回滚，不能替代 Git |

## 可复用 Prompt 速查

| 场景 | 一句话模板 |
|---|---|
| 只读探索 | "请只读探索，不要修改文件。请分析...输出相关文件、调用链、方案。" |
| 开始实现 | "按已确认方案做最小实现。优先 edit，不要 rewrite，不要提交。" |
| 验证 | "先看 diff，再跑最小测试，失败先解释，不要扩大修改面。" |
| Review | "以审查者身份审查本次 diff，看正确性、边界、安全、测试覆盖。" |
