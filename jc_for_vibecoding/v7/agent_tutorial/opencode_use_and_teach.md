下面这版可以直接拆成两部分使用：
第一部分适合放在课件最后一页，叫 **OpenCode 快速上手 Take Away**；第二部分是给讲师的 **教学演讲稿**，按 45～60 分钟课程设计。

---

# 一、OpenCode 快速上手 Take Away

## 1. 先建立正确心智模型

OpenCode 不是“更聪明的自动补全”，而是一个 **在本地代码仓库中运行的 coding agent runtime**。

从你给的 Agent 演进材料看，Agent 的核心不是模型本身，而是一个“带状态的决策循环”：目标、状态、动作、观察、策略、运行时。OpenCode 只是把这个抽象落到了软件研发场景里：读文件、搜代码、改代码、跑命令、看测试结果、继续修正。

面向研发人员，可以把 OpenCode 理解成：

> 一个会使用终端、文件系统、搜索、编辑器、测试命令，并且能在会话中持续推进任务的本地 AI 工程助理。

---

## 2. 第一次上手只记住一条主线

**安装 → 连接模型 → 进入项目 → 初始化规则 → 先 Plan → 再 Build → 测试 → Review → Git 提交。**

官方入门文档中，典型流程是进入项目目录后运行 `opencode`，再执行 `/init`，OpenCode 会分析项目并在项目根目录创建 `AGENTS.md`；官方也建议把项目级 `AGENTS.md` 提交到 Git，因为它帮助 OpenCode 理解项目结构和编码规范。([OpenCode][1])

最小命令流可以这样教：

```bash
cd /path/to/project
opencode
```

进入 TUI 后：

```text
/connect   # 配置模型 provider
/init      # 生成或更新 AGENTS.md
```

然后不要急着让它改代码，先切到 Plan：

```text
<TAB>      # 在 Plan / Build 之间切换
```

官方文档也建议复杂功能先用计划模式，因为 Plan 模式不会直接修改代码，而是先建议如何实现。([OpenCode][1])

---

## 3. Plan 和 Build 是第一道安全边界

讲给研发同学时，可以用一句话区分：

> **Plan 是让 Agent 想清楚，Build 是让 Agent 动手。**

OpenCode 内置两个主代理：`Build` 和 `Plan`。`Build` 是默认开发代理，拥有完整工具访问能力；`Plan` 用于分析、审查和制定计划，默认对文件编辑和 bash 命令更谨慎，需要确认。([OpenCode][2])

推荐 SOP：

```text
复杂任务：Plan → 人类确认 → Build
简单任务：Build 直接改，但必须限定范围
高风险任务：Plan + 只读探索 + 手动执行关键命令
```

不要一上来就说：

```text
帮我重构整个项目
```

更好的说法是：

```text
先不要改代码。请阅读 @src/payment 相关文件，
找出 retry 和 idempotency 的实现路径，
给出最小修复方案、影响文件和需要补的测试。
```

---

## 4. AGENTS.md 是项目级“作业指导书”

`AGENTS.md` 不是装饰文件，它是 OpenCode 理解项目的核心上下文之一。

它适合写：

```markdown
# 项目结构
- src/api：HTTP API
- src/domain：领域逻辑
- tests：测试

# 开发约定
- 修改业务逻辑必须补单测
- 不允许直接改 public API，除非用户明确要求
- 优先使用 pnpm test:unit 做定向验证

# 高风险规则
- 不要执行 rm -rf
- 不要执行 pkill -f
- 不要修改 .env / secrets / production config
```

官方文档说明，可以通过 `/init` 创建 `AGENTS.md`，并且该文件会进入模型上下文，用于定制 OpenCode 在项目里的行为；项目级和全局级规则可以分别放在项目根目录和 `~/.config/opencode/AGENTS.md`。([OpenCode][3])

---

## 5. 权限配置要保守，不要默认全放开

OpenCode 的 `permission` 配置决定某个动作是自动执行、询问，还是阻止。官方文档中的动作包括 `allow`、`ask`、`deny` 三种，并支持按工具和输入模式做细粒度规则。([OpenCode][4])

教学时建议给研发同学一个保守模板：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "*": "ask",
    "bash": {
      "git status*": "allow",
      "git diff*": "allow",
      "git log*": "allow",
      "grep *": "allow",
      "rg *": "allow",
      "ls *": "allow",
      "cat *": "allow",
      "npm test*": "ask",
      "pnpm test*": "ask",
      "pytest *": "ask",
      "rm *": "deny",
      "rm -rf *": "deny",
      "pkill *": "deny",
      "killall *": "deny"
    },
    "edit": "ask",
    "write": "ask"
  }
}
```

讲课重点不是让大家记住配置语法，而是记住原则：

> 读操作可以宽一些，写操作要问，删除和杀进程默认拒绝。

---

## 6. 回滚不能只依赖 `/undo`

OpenCode 的 `/undo` 可以撤销最近一条消息以及相关文件修改，`/redo` 可以重做；官方 TUI 文档也说明这些文件更改恢复机制内部依赖 Git，因此项目需要是一个 Git 仓库。([OpenCode][5])

但在团队实践里，**Git checkpoint 才是主保险，`/undo` 只是副保险**。

每次大改前，先做：

```bash
git status
git add -A
git commit -m "checkpoint: before opencode task"
```

或者至少：

```bash
git stash push -u -m "checkpoint before opencode task"
```

原因是公开 issue 中已经有人报告过 snapshot cache 的 stale `index.lock` 会导致 Modified Files、undo/revert 行为异常；该问题通过移除 stale lock 和重置对应 workspace 的 snapshot cache 后恢复。([GitHub][6])

课堂上可以强调：

> Agent 改代码之前，先让 Git 记住当前世界线。

---

## 7. `pkill -f` 是典型高危坑

你提到的 “OpenCode 可能 pkill 乱杀进程” 很适合作为教学案例。

公开 issue 中有用户报告：在 OpenCode TUI 中执行 `pkill -f` 可能导致 tool call 挂起，而通过 `opencode run` 执行时甚至出现命令把 `opencode run` 自身终止的情况；issue 描述中推测 `pkill -f` 可能匹配到了 OpenCode 自身或其子进程。([GitHub][7])

教学建议：

```text
禁止让 Agent 自动执行：
- pkill -f
- killall
- rm -rf
- docker system prune
- git reset --hard
- git clean -fd
```

正确做法是让 Agent 只负责“定位”：

```text
请找出占用 3000 端口的进程，并解释它是什么。
不要 kill 任何进程。
```

然后人类在外部终端确认 PID 后手动处理：

```bash
lsof -i :3000
kill <PID>
```

---

## 8. 最推荐的日常使用 SOP

可以把这段做成课件中的“黄金路径”：

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

一句话总结：

> OpenCode 最适合被当成“初级到中级工程师 + 很快的代码阅读器 + 自动 patch 执行器”，而不是无人驾驶系统。

---

# 二、讲师演讲稿

下面是可直接照着讲的版本。

---

## 开场：为什么今天要讲 OpenCode

各位同学，今天我们不把 OpenCode 当作一个“AI 写代码工具”来讲。

如果只是把它理解成“帮我生成代码”，那它和普通 ChatGPT、Copilot Chat、Cursor Chat 的区别并不明显。真正值得研发人员理解的是：OpenCode 代表的是一类新的研发工具形态，叫 **coding agent**。

它不是一次性回答问题，而是在你的项目目录里持续执行一个循环：

```text
理解目标 → 查看代码 → 执行动作 → 观察结果 → 修正判断 → 继续执行
```

这和我们之前讲的 Agent 演进主线是一致的。Agent 不是模型，而是一个带状态的决策循环；它至少包含目标、状态、动作、观察、策略和运行时。ReAct 讲清楚了“边想边做”的循环，Function Calling 把动作变成结构化接口，SWE-agent 把软件工程环境变成专门的工作台，而 OpenCode 则是把这些能力放到本地代码仓库里的一个 coding agent runtime。

所以今天这节课的目标不是让大家背命令，而是让大家知道：

> 怎么安全、稳定、可回滚地把 OpenCode 放进真实研发流程里。

---

## 第一部分：OpenCode 的一句话定义

我们先给 OpenCode 一个工作定义：

> OpenCode 是一个运行在终端、本地项目和 Git 仓库里的 AI coding agent。它可以读代码、搜索代码、编辑文件、执行 shell 命令、跑测试，并通过会话持续推进任务。

这句话里有三个关键词。

第一个是 **本地项目**。它不是只在浏览器里和你聊天，而是进入你的真实代码仓库。

第二个是 **工具能力**。它不是只给建议，而是可以真的读文件、改文件、跑命令。

第三个是 **会话推进**。它不是一次问答结束，而是可以在一个上下文里持续探索、修改、验证。

也正因为它真的能动手，所以我们不能用“随便聊聊”的方式使用它。我们要像管理一个真实开发者一样管理它：给目标、给规则、限制权限、要求测试、保留回滚点。

---

## 第二部分：先看最小上手流程

我们先从零开始看一遍最小流程。

第一步，进入项目目录：

```bash
cd /path/to/project
```

第二步，启动 OpenCode：

```bash
opencode
```

第三步，配置模型 provider：

```text
/connect
```

第四步，初始化项目规则：

```text
/init
```

官方文档里也是这个流程：进入项目目录，运行 `opencode`，然后执行 `/init`；OpenCode 会分析项目并创建 `AGENTS.md` 文件，官方还建议把这个文件提交到 Git，因为它能帮助 OpenCode 理解项目结构和编码规范。([OpenCode][1])

这里我要停一下，强调一个点：
`/init` 不是一个形式动作，它生成的是 OpenCode 的项目说明书。

对人类新人来说，入职要看 README、CONTRIBUTING、架构文档。对 OpenCode 来说，`AGENTS.md` 就是这类信息的入口。

所以初始化后，我们不要立刻让它开改，而是先看它生成的 `AGENTS.md` 是否靠谱。比如它有没有正确识别包管理器？有没有写清楚测试命令？有没有误判目录结构？有没有遗漏安全规则？

---

## 第三部分：Plan 和 Build 是最重要的操作习惯

接下来讲一个大家最容易忽略、但最重要的习惯：**先 Plan，再 Build。**

OpenCode 有两个内置主代理：`Plan` 和 `Build`。`Build` 是默认开发代理，适合实际修改文件和执行命令；`Plan` 是受限代理，适合分析、审查和制定计划。官方文档说明，Plan 默认对文件编辑和 bash 命令更谨慎，适合在不实际修改代码库的情况下分析代码和建议变更。([OpenCode][2])

在界面里，可以用 Tab 在 Plan 和 Build 之间切换。官方入门文档也建议添加复杂功能时先让 OpenCode 制定计划，再切回构建模式实施。([OpenCode][1])

我们来看两个提示词的差异。

不好的提示词是：

```text
帮我重构支付模块。
```

这个提示太大、太模糊，而且一上来就让 Agent 自由发挥。

更好的提示词是：

```text
先不要改代码。请阅读支付模块中 retry、charge、idempotency 相关实现，
找出重复扣款可能发生的位置。
输出：
1. 相关文件路径
2. 当前调用链
3. 可能根因
4. 最小修复方案
5. 需要补的测试
```

这个提示词有几个好处：

第一，它明确说“先不要改代码”。
第二，它限定了搜索范围。
第三，它要求输出证据和计划。
第四，它把实现和验证拆开。

这就是 coding agent 使用中的核心心法：

> 不要让 Agent 一上来写代码，先让它收集证据、收敛假设、提出方案。

---

## 第四部分：把 OpenCode 当成一个“会用工具的工程师”

我们现在回到 Agent 的原理。

一个 coding agent 的能力不是来自“模型突然特别懂你们项目”，而是来自它能使用工具形成闭环。

它会读文件，看到实现；
它会搜索，找到调用链；
它会编辑，产生 patch；
它会运行测试，看到失败；
它会根据失败继续修改。

这就是 ReAct 里说的：

```text
Reasoning → Action → Observation → Reasoning
```

但在真实研发里，这个循环要受控。
我们不能只关心它会不会写，还要关心它怎么查、怎么改、怎么验证、怎么回滚。

所以，课堂上请大家记住一句话：

> OpenCode 的价值不是替你敲代码，而是把“读代码、改代码、跑测试、看反馈”这条研发闭环自动化了一部分。

---

## 第五部分：AGENTS.md 应该怎么写

接下来我们讲 `AGENTS.md`。

官方文档说，OpenCode 可以通过 `AGENTS.md` 获取自定义指令，这些指令会进入模型上下文，用来针对特定项目定制行为；`/init` 可以创建新的 `AGENTS.md`，项目级规则通常放在项目根目录，全局规则可以放在 `~/.config/opencode/AGENTS.md`。([OpenCode][3])

给研发团队教学时，不要把 `AGENTS.md` 讲成“提示词文件”，要讲成：

> 这是给 Agent 的项目作业指导书。

一个实用的 `AGENTS.md` 至少应该包括五类信息。

第一类，项目结构：

```markdown
## Project Structure
- src/api: HTTP API
- src/domain: domain logic
- src/infra: database and external services
- tests: unit and integration tests
```

第二类，开发命令：

```markdown
## Commands
- Install: pnpm install
- Unit test: pnpm test:unit
- Typecheck: pnpm typecheck
- Lint: pnpm lint
```

第三类，代码规范：

```markdown
## Code Style
- Prefer small, focused changes
- Keep public API backward compatible
- Add regression tests for bug fixes
```

第四类，安全边界：

```markdown
## Safety
- Do not read or modify .env files
- Do not run rm -rf
- Do not run pkill -f or killall
- Ask before changing database migrations
```

第五类，验收标准：

```markdown
## Definition of Done
- Relevant tests pass
- git diff is reviewed
- No unrelated formatting changes
- User-facing behavior is explained
```

我建议每个团队都把 `AGENTS.md` 当成工程治理的一部分，而不是每个人自己随便写。

---

## 第六部分：权限治理，别让 Agent 拿到无限 root 权限

接下来讲安全使用。

OpenCode 的权限配置决定某个动作是自动执行、询问，还是阻止。官方权限文档说明，权限动作包括 `allow`、`ask`、`deny`，并可以按工具和输入模式做细粒度配置。([OpenCode][4])

我们可以把权限理解成三档：

```text
allow：低风险、可自动执行
ask：中风险，需要人类确认
deny：高风险，直接禁止
```

日常建议是：

```text
读操作 allow
写操作 ask
删除、杀进程、重置 Git、清理 Docker deny
```

比如：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "*": "ask",
    "bash": {
      "git status*": "allow",
      "git diff*": "allow",
      "rg *": "allow",
      "ls *": "allow",
      "cat *": "allow",
      "pnpm test*": "ask",
      "npm test*": "ask",
      "pytest *": "ask",
      "rm *": "deny",
      "rm -rf *": "deny",
      "pkill *": "deny",
      "killall *": "deny",
      "git reset --hard*": "deny",
      "git clean *": "deny"
    },
    "edit": "ask",
    "write": "ask"
  }
}
```

这里请大家注意，权限配置不是为了阻碍效率，而是为了让 Agent 在可控范围内提高效率。

一个经验判断是：

> 只要这个命令在人类手上敲错都可能造成损失，就不要让 Agent 自动执行。

---

## 第七部分：现场演示 SOP

现在我们进入实际演示流程。假设我们要修一个 bug：

> 用户删除订单后，订单列表中仍然偶尔显示已删除订单。

我们不直接让它修，而是按 SOP 走。

第一步，看 Git 状态：

```bash
git status
```

确认没有未提交的重要改动。

第二步，创建 checkpoint：

```bash
git add -A
git commit -m "checkpoint: before opencode order delete fix"
```

第三步，进入 OpenCode。

第四步，切到 Plan 模式，输入：

```text
先不要改代码。
请分析订单删除后列表仍显示已删除订单的问题。
请完成：
1. 找出订单删除接口
2. 找出订单列表查询逻辑
3. 找出 deleted / status 字段的使用方式
4. 给出最小修复方案
5. 说明需要补哪些测试
```

然后我们等待它输出计划。

这里讲师可以停下来问学员：

> 这个计划有没有证据？有没有列出文件？有没有把实现和测试分开？有没有改太多东西？

如果计划合理，再切到 Build：

```text
<TAB>
```

然后说：

```text
按刚才计划做最小修改。
不要重构无关代码。
修改后运行最小相关测试。
```

修改完成后，我们不直接相信它，而是看 diff：

```bash
git diff
```

然后跑测试：

```bash
pnpm test:unit -- order
```

最后再 commit：

```bash
git add -A
git commit -m "fix: filter deleted orders from list query"
```

这就是一个完整的 OpenCode 安全使用闭环。

---

## 第八部分：常见坑 1 —— pkill 乱杀或挂住

现在讲第一个坑：`pkill`。

很多 Agent 在遇到端口占用、测试卡住、服务没退出时，会倾向于执行类似：

```bash
pkill -f node
pkill -f vite
pkill -f pytest
```

这很危险。

公开 issue 中已经有人报告过，`pkill -f` 在 OpenCode TUI 中可能导致工具调用挂起，而在 `opencode run` 中可能导致 OpenCode 自己被终止；issue 中推测原因是 `pkill -f` 可能匹配到了 OpenCode 自身或子进程。([GitHub][7])

所以我们要给学员一个明确规则：

> Agent 可以查进程，但不能自动杀进程。

好的提示词是：

```text
请检查哪个进程占用了 3000 端口。
只输出 PID、命令名和建议，不要 kill 任何进程。
```

人类确认后，再在外部终端执行：

```bash
lsof -i :3000
kill <PID>
```

不要让 Agent 直接执行：

```bash
pkill -f node
```

这一点在团队里要写进 `AGENTS.md` 和 `opencode.json`。

---

## 第九部分：常见坑 2 —— 回滚不要只靠 `/undo`

第二个坑是回滚。

OpenCode 提供 `/undo` 和 `/redo`。官方 TUI 文档说明，`/undo` 会撤销对话中的最后一条消息并还原相关文件更改，`/redo` 可以重做；这些文件更改恢复内部使用 Git，因此项目需要是 Git 仓库。([OpenCode][5])

听起来很安全，但真实团队里不要只依赖它。

原因是 OpenCode 的内部快照机制也可能遇到状态问题。公开 issue 中有人报告 stale snapshot `index.lock` 导致 Modified Files、undo/revert 不能正常工作；删除 stale lock 并重置对应 workspace 的 snapshot cache 后才恢复。([GitHub][6])

所以我们要建立一个原则：

> `/undo` 是局部撤销工具，Git checkpoint 才是版本回滚工具。

每次大改前都要做：

```bash
git status
git add -A
git commit -m "checkpoint: before opencode task"
```

或者：

```bash
git stash push -u -m "checkpoint before opencode task"
```

这不是保守，这是工程纪律。

---

## 第十部分：常见坑 3 —— 上下文太大，Agent 开始跑偏

第三个坑是上下文过大。

当我们让 Agent 一次性看太多文件、改太多模块、跑太多任务，它很容易开始混淆目标。这个问题不是 OpenCode 独有，而是所有 coding agent 都会遇到。

解决方法不是“换更大的模型”，而是拆任务。

比如不要说：

```text
帮我优化整个订单系统。
```

应该拆成：

```text
第一步：只分析订单查询慢的原因，不改代码。
第二步：只针对订单列表接口提出优化方案。
第三步：只修改 query 层，补 benchmark 或测试。
第四步：review diff，确认没有改变业务语义。
```

也就是说：

> 长任务靠拆分，不靠硬塞上下文。

这和你原始材料里提到的 memory、compact、handoff 是同一个思想：长程任务的关键不是把所有东西都放进上下文，而是把中间结论整理成可交接、可验证的状态。

---

## 第十一部分：什么时候适合用子代理

OpenCode 内置了主代理和子代理。官方文档中，主代理包括 Build 和 Plan；子代理包括 General、Explore 和 Scout。Explore 是只读代码库探索代理，Scout 适合外部文档和依赖研究，General 可用于复杂问题和多步骤任务。([OpenCode][2])

课堂上可以这样讲：

> 子代理不是为了炫技，而是为了把不同类型的工作隔离开。

例如：

```text
@explore 请只读搜索订单删除相关代码路径，不要修改文件。
```

或者：

```text
@scout 请查看当前使用的 ORM 文档，确认 soft delete 查询应该怎么写。
```

适合子代理的任务包括：

```text
代码路径探索
依赖文档核对
历史实现对照
风险审查
测试覆盖检查
```

不适合子代理的任务是：

```text
让多个 agent 同时乱改同一批文件
```

多 Agent 的价值是并行取证，不是并行制造冲突。

---

## 第十二部分：给学员的最终口诀

最后我们把今天内容压成一句口诀：

> **先规则，后任务；先计划，后修改；先小改，后测试；先 checkpoint，后放手。**

展开就是：

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

这就是 OpenCode 对研发团队最现实的价值：
它可以显著加快代码阅读、方案探索、样板修改、测试修复这些工作，但前提是我们用工程化方式约束它。

今天大家回去之后，不要一上来让它改核心业务代码。建议先从三个低风险场景开始：

```text
1. 让它解释陌生模块
2. 让它补充单元测试
3. 让它修一个范围明确的小 bug
```

等你熟悉了 Plan、Build、AGENTS.md、权限、Git checkpoint 这一整套流程，再把它用于更复杂的研发任务。

---

# 三、可放到课件最后一页的精简版

```text
OpenCode 快速上手 Take Away

1. OpenCode 是 coding agent runtime，不是自动补全。
2. Agent 的本质是：目标 + 状态 + 动作 + 观察 + 策略 + 运行时。
3. 第一次使用：opencode → /connect → /init → commit AGENTS.md。
4. 复杂任务必须先 Plan，再 Build。
5. AGENTS.md 是项目级作业指导书，要写结构、命令、规范、安全边界。
6. permission 要保守：读操作 allow，写操作 ask，删除/杀进程 deny。
7. 大改前必须 Git checkpoint，不要只依赖 /undo。
8. 禁止 Agent 自动执行 pkill -f、rm -rf、git reset --hard。
9. 让 Agent 先找证据，再写 patch，再跑测试。
10. OpenCode 的最佳定位：快速代码阅读器 + 自动 patch 执行器 + 测试反馈循环助手。
```

[1]: https://opencode.ai/docs/zh-cn "简介 | OpenCode"
[2]: https://dev.opencode.ai/docs/zh-cn/agents/ "代理 | OpenCode"
[3]: https://opencode.ai/docs/zh-cn/rules/ "规则 | OpenCode"
[4]: https://opencode.ai/docs/permissions/ "Permissions | OpenCode"
[5]: https://opencode.ai/docs/zh-cn/tui/ "TUI | OpenCode"
[6]: https://github.com/anomalyco/opencode/issues/22275 "bug: stale snapshot index.lock breaks Modified Files and undo for one workspace · Issue #22275 · anomalyco/opencode · GitHub"
[7]: https://github.com/anomalyco/opencode/issues/25664 "pkill -f command causes tool call hang in opencode TUI · Issue #25664 · anomalyco/opencode · GitHub"
