# 从 Agent 技术演进到 OpenCode 工程实践：面向软件研发人员的 Coding Agent 教程

> 目标读者：有日常编码、调试、Code Review、测试经验的软件研发人员。  
> 教程目标：不是把 OpenCode 当成“AI 聊天窗口”介绍，而是把它作为一个可观测、可配置、可治理的 coding agent runtime 来讲清楚：它如何继承 ReAct / SWE-agent 的思想，如何通过 session、agent、tool、permission、snapshot 等模块落地，以及研发团队应该如何安全使用。

---

## 0. 一句话定位

一个成熟的 coding agent 不是“更会写代码的模型”，而是：

> **模型 + 代码仓库上下文 + 工具动作空间 + 权限系统 + 会话状态 + 快照/回滚 + 团队规则 的工作系统。**

OpenCode 可以作为这条演进链在本地开发场景中的一个工程化样本：

```text
ReAct 的思考-行动-观察闭环
  -> Function Calling / Tool Calling 的结构化动作
  -> SWE-agent 的软件工程专用 ACI
  -> OpenCode 的本地 coding agent runtime
```

---

## 1. 技术演进主线：从“会想”到“能安全地改代码”

### 1.1 ReAct：Agent 的最小闭环

ReAct 的价值不是“让模型说出更多推理”，而是建立了一个循环：

```text
观察任务 -> 形成假设 -> 调用动作 -> 接收观察 -> 修正计划 -> 再行动
```

放到研发场景里，就是：

```text
怀疑 bug 在鉴权中间件
-> grep 路由入口
-> read 认证逻辑
-> 跑一条失败测试
-> 发现根因在 token refresh
-> 最小修改
-> 再跑测试验证
```

所以，ReAct 阶段解决的是：**模型不再只做一次性回答，而是可以边查边改、边改边验证。**

### 1.2 Tool Calling：把“我想做”变成“可执行动作”

自然语言的动作无法稳定执行。Coding agent 需要把动作做成结构化接口：

```json
{
  "tool": "grep",
  "input": {
    "pattern": "refreshToken",
    "path": "src"
  }
}
```

这一步对应到 OpenCode，就是 `read`、`grep`、`glob`、`bash`、`edit`、`write`、`apply_patch`、`task`、`skill`、`webfetch` 等工具。模型不再只是“建议你运行测试”，而是可以请求运行某个具体命令、读取某个文件、修改某段代码。

### 1.3 SWE-agent：软件工程需要专门的 ACI

通用工具对 coding agent 不够。软件开发任务天然需要：

- 文件阅读和搜索
- 精确编辑和补丁应用
- 终端命令
- 测试输出
- LSP 语义信息
- 代码库规则
- 会话轨迹和回滚

这就是 SWE-agent 的 Agent-Computer Interface 思想：给 agent 一张适合软件工程的“工作台”，而不是让它只靠聊天窗口猜。

### 1.4 OpenCode：把 coding agent 做成本地运行时

OpenCode 可以这样理解：

```text
OpenCode = 本地 TUI / CLI / Server
         + 多 provider LLM 调用
         + Agent 配置
         + Tool Registry
         + Permission Gate
         + Session Processor
         + Snapshot / Undo
         + AGENTS.md / Skills / Commands / MCP / Plugins
```

它的关键价值不是“生成一段代码”，而是把研发过程中的“查、改、跑、验、审、回滚”串成一个可配置的运行时。

---

## 2. OpenCode 的 Agent 抽象：六个槽位如何落到模块

| Agent 抽象 | 研发语义 | OpenCode 对应能力 / 模块 |
|---|---|---|
| Goal 目标 | 这次要修什么、验收标准是什么 | 用户 prompt、自定义 command、AGENTS.md 规则 |
| State 状态 | 当前会话、消息、todo、打开过的上下文、快照 | `session/`、`message-v2.ts`、`todo.ts`、`summary.ts`、`snapshot/` |
| Actions 动作空间 | 能读、搜、改、跑、查文档、派生子任务 | `tool/registry.ts` 和内置工具 |
| Observations 观察 | 命令输出、测试失败、文件内容、LSP 结果 | tool output、truncation、Message parts |
| Policy 策略 | 用哪个 agent、哪个模型、是否能改代码 | `agent/`、Build / Plan / Explore / Scout、自定义 agent |
| Runtime 运行时 | 调度、权限、回滚、压缩、扩展、服务化 | `session/processor.ts`、`permission/`、`snapshot/`、MCP、plugins、server |

一个适合教程中的比喻：

> ReAct 像“会自己排障的实习生”；OpenCode 像“带 IDE、终端、工单、权限审批、代码快照的本地开发工位”。

---

## 3. OpenCode 源码模块视角

> 下方模块名以 `anomalyco/opencode` 当前 `dev` 分支结构为参考。版本迭代可能调整目录或文件名，教学时建议以你实际使用版本为准。

### 3.1 `session/`：Agent loop 的主控层

`session/` 可以看作 OpenCode 的会话大脑，包含：

- `processor.ts`：处理 LLM 流式输出、tool call、tool result、权限拦截、doom loop 检测。
- `prompt.ts` / `system.ts`：构建提示词和系统上下文。
- `message-v2.ts`：消息与 part 结构。
- `compaction.ts` / `summary.ts`：长会话压缩与摘要。
- `revert.ts`：会话级 revert / undo。
- `todo.ts`：多步骤任务列表。
- `status.ts` / `run-state.ts`：会话状态。

简化后的执行流：

```text
用户输入
  -> 创建 session message
  -> 构造 system prompt / instructions / agent config
  -> 调用 LLM
  -> LLM 输出文本或 tool call
  -> SessionProcessor 记录 tool call 状态
  -> Permission 判断 allow / ask / deny
  -> Tool 执行并返回 observation
  -> LLM 基于 observation 继续
  -> 生成最终答复
  -> snapshot / summary / todo / status 更新
```

源码细节上，`SessionProcessor` 在 LLM stream 开始前会先捕获 snapshot，避免工具执行过早导致快照捕获太晚。它也内置了 `DOOM_LOOP_THRESHOLD = 3`，当同一工具带相同输入重复调用 3 次时会触发 `doom_loop` 权限询问。

### 3.2 `tool/`：Agent 的“手”和“眼”

`tool/` 目录下可以看到典型 coding agent 工具：

- 观察类：`read`、`grep`、`glob`、`lsp`、`webfetch`、`websearch`
- 修改类：`edit`、`write`、`apply_patch`
- 执行类：`shell` / `bash`
- 编排类：`task`、`skill`、`todo`、`question`
- 研究类：`repo_clone`、`repo_overview`

`tool/registry.ts` 是工具注册中心，负责：

1. 初始化内置工具。
2. 加载 `.opencode/tools/` 或全局目录中的自定义工具。
3. 加载 plugin 提供的工具。
4. 根据 provider、model、feature flag 和 agent 权限过滤工具。
5. 给 `task` 工具注入可用子代理说明，给 `skill` 工具注入可用技能说明。

这说明 OpenCode 的工具系统不是简单的“把 shell 暴露给模型”，而是有工具定义、参数 schema、输出截断、权限检查和上下文注入的一套动作空间。

### 3.3 `permission/`：把自治变成可控

OpenCode 的 permission 不只是“开或关工具”，而是决定某个动作是：

```text
allow -> 直接运行
ask   -> 先问用户
 deny -> 阻止
```

团队落地时，permission 是最重要的安全阀。尤其要控制：

- `bash`
- `edit`
- `write` / `apply_patch`，它们受 `edit` 权限覆盖
- `external_directory`
- `doom_loop`
- `task`
- `webfetch` / `websearch`
- MCP 工具

### 3.4 `agent/`：不同角色的策略封装

OpenCode 内置的 agent 可以分成三类：

- 主 agent：`Build`、`Plan`
- 子 agent：`General`、`Explore`、`Scout`
- 系统隐藏 agent：`Compaction`、`Title`、`Summary`

研发团队可以把它映射成工作角色：

| Agent | 建议角色 | 是否允许改代码 |
|---|---|---|
| Plan | 需求澄清、方案设计、风险分析 | 否 |
| Explore | 只读代码探索、定位入口 | 否 |
| Scout | 查外部依赖、上游实现、文档 | 否 |
| Build | 最小实现、补测试、跑验证 | 是，但需权限控制 |
| Review 自定义 | 安全、正确性、测试覆盖审查 | 否 |

### 3.5 `snapshot/` 与 `/undo`：方便但不能替代 Git

OpenCode 有 snapshot / revert / diff 能力，并提供 `/undo`、`/redo` 等命令。但它应该被视为“会话级便利回滚”，不是团队级版本控制。

正确姿势：

```text
Git checkpoint 是主保险
OpenCode /undo 是辅助保险
```

尤其在多轮修改、子代理、长命令、跨平台文件系统、Windows 保留文件名、snapshot lock 异常等场景下，必须用 Git 自己做明确 checkpoint。

---

## 4. 面向研发人员的 OpenCode 使用 SOP

### Phase 0：进入工作前先建安全边界

```bash
git status --short
git switch -c ai/<ticket-or-task>
# 如果当前已有未提交工作，优先 stash 或 commit
# git stash push -u -m "before opencode <task>"
# 或 git add -A && git commit -m "checkpoint: before opencode <task>"
```

建议规则：

1. 每个独立任务一个分支或 worktree。
2. 不在主分支直接让 agent 改代码。
3. 不把 `/undo` 当唯一回滚机制。
4. 禁止 agent 自动 `git push`、`git reset --hard`、`git clean -fd`。
5. 广义 kill 命令必须人工确认。

### Phase 1：初始化项目规则

在项目根目录启动：

```bash
opencode
/init
```

然后检查生成的 `AGENTS.md`，补充：

- 项目结构
- 包管理器
- 测试命令
- lint / typecheck 命令
- 分支和提交规范
- 禁止事项
- 常见坑
- 关键目录说明

提交它：

```bash
git add AGENTS.md
git commit -m "docs: add opencode project rules"
```

### Phase 2：先 Plan，不要直接 Build

第一次给任务时，要求 OpenCode 只做计划：

```text
请先使用 Plan 模式。不要修改文件，不要运行会改变状态的命令。

任务：修复用户删除 note 后没有 soft delete 的问题。

请输出：
1. 你需要查看的文件列表
2. 可能的调用链
3. 最小实现方案
4. 需要补充的测试
5. 风险点和不确定点
6. 开始改代码前需要我确认的问题
```

适合让 `Explore` 子代理并行做只读探索：

```text
@explore 请只读分析 note 删除链路，找出 API、DB schema、测试入口，不要修改任何文件。
```

### Phase 3：实现前先收敛范围

要求 agent 给出“修改计划 + 文件范围”：

```text
在开始修改前，请列出你计划改动的文件和每个文件的改动目的。
如果需要新文件，请说明为什么不能改已有文件。
不要运行长时间后台服务，不要 kill 进程，不要提交代码。
```

### Phase 4：Build 模式做最小 patch

```text
切换到 Build 模式后，请按刚才确认的方案做最小修改。
要求：
- 优先 edit / patch，不要整体 rewrite 大文件。
- 不要改无关格式。
- 不要自动提交。
- 每完成一个逻辑小步，说明改了什么以及下一步验证什么。
```

### Phase 5：验证必须独立于实现

让 agent 跑最小验证：

```text
请先运行和本次改动最相关的最小测试。
如果失败，先解释失败原因，不要立刻扩大修改面。
然后再运行 lint / typecheck。
```

常见验证顺序：

```bash
git diff --stat
git diff
pnpm test <related-test>
pnpm typecheck
pnpm lint
```

### Phase 6：人工 review + checkpoint

让 OpenCode 输出交接摘要：

```text
请总结本次变更：
1. 根因
2. 修改点
3. 新增/修改测试
4. 已运行验证命令和结果
5. 未覆盖风险
6. 建议 code review 重点
```

然后人工检查：

```bash
git diff
git add -p
git commit -m "fix: soft delete notes"
```

---

## 5. 推荐 `opencode.json` 安全基线

> 下面是偏保守的团队模板。第一次落地建议从保守开始，再按团队习惯逐步放宽。

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "*": "ask",

    "read": {
      "*": "allow",
      "*.env": "deny",
      "*.env.*": "deny",
      "*.env.example": "allow"
    },

    "grep": "allow",
    "glob": "allow",
    "list": "allow",

    "edit": "ask",

    "bash": {
      "*": "ask",

      "git status*": "allow",
      "git diff*": "allow",
      "git log*": "allow",
      "git branch*": "allow",

      "rg *": "allow",
      "grep *": "allow",
      "ls *": "allow",
      "cat *": "allow",

      "pnpm test*": "ask",
      "npm test*": "ask",
      "bun test*": "ask",
      "pnpm typecheck*": "ask",
      "pnpm lint*": "ask",

      "git push*": "deny",
      "git reset --hard*": "deny",
      "git clean*": "deny",
      "rm -rf*": "deny",

      "pkill *": "deny",
      "killall *": "deny",
      "taskkill *": "ask",
      "kill *": "ask"
    },

    "external_directory": "ask",
    "doom_loop": "ask",
    "webfetch": "ask",
    "websearch": "ask"
  },

  "agent": {
    "plan": {
      "permission": {
        "edit": "deny",
        "bash": "ask"
      }
    },
    "build": {
      "permission": {
        "edit": "ask",
        "bash": {
          "*": "ask",
          "git status*": "allow",
          "git diff*": "allow",
          "rg *": "allow",
          "pnpm test*": "ask",
          "git push*": "deny",
          "git reset --hard*": "deny",
          "git clean*": "deny",
          "rm -rf*": "deny",
          "pkill *": "deny",
          "killall *": "deny"
        }
      }
    }
  }
}
```

注意：OpenCode 的权限匹配是“后匹配规则优先”，所以通配符 `*` 应该放在前面，更具体规则放在后面。

---

## 6. 推荐 `AGENTS.md` 模板

```markdown
# Project Agent Rules

## Project overview
- This is a <language/framework> project.
- Package manager: pnpm.
- Main app: `apps/web`.
- Shared libraries: `packages/*`.

## Required workflow
1. For non-trivial tasks, start in Plan mode.
2. Before editing, list files you plan to modify and why.
3. Prefer minimal patches. Do not rewrite large files unless explicitly asked.
4. After editing, run the smallest relevant test first.
5. Always summarize changed files, tests run, and remaining risks.

## Commands
- Install: `pnpm install`
- Test: `pnpm test`
- Typecheck: `pnpm typecheck`
- Lint: `pnpm lint`

## Safety rules
- Do not run `git push`.
- Do not run `git reset --hard` or `git clean -fd`.
- Do not run `rm -rf`.
- Do not run broad process-kill commands such as `pkill -f`, `killall`, or `taskkill /IM node.exe`.
- Do not start long-running dev servers inside the agent unless explicitly approved.
- If a command may affect running processes, ask first and explain the exact PID / port / process name.

## Git workflow
- Human owns commits.
- Agent may inspect `git status`, `git diff`, and `git log`.
- Agent must not commit unless explicitly asked.

## Testing policy
- Add or update regression tests when fixing bugs.
- If tests cannot be run, explain why and give the exact command for humans to run.
```

---

## 7. 常见坑与解决方案

### 7.1 坑一：`pkill -f` 可能误杀 OpenCode 或导致工具调用挂住

现象：

```bash
pkill -f vim 2>/dev/null; echo "killed"
```

在 TUI 中可能挂住直到超时；在 CLI 中可能导致 `opencode run` 自己被终止。根因通常是 `pkill -f` 按完整命令行匹配，可能匹配到 OpenCode 自身或它的子进程。

治理方式：

1. **不要让 agent 执行 `pkill -f`。** 在 permission 中直接 `deny`：

```jsonc
"bash": {
  "*": "ask",
  "pkill *": "deny",
  "killall *": "deny",
  "taskkill *": "ask",
  "kill *": "ask"
}
```

2. 需要杀进程时，让人类在 OpenCode 外部终端确认：

```bash
pgrep -af '<process-name-or-port>'
# 确认 PID 后再 kill 指定 PID
kill <PID>
```

3. 优先按端口或 PID 文件管理开发服务，而不是按进程名模糊杀：

```bash
# 示例：先查看占用端口的 PID
lsof -nP -iTCP:3000 -sTCP:LISTEN
# 人工确认后再 kill
kill <PID>
```

4. 在 prompt 中明确禁止：

```text
不要运行 pkill -f、killall、taskkill /IM node.exe 这类广义杀进程命令。
如果你认为需要停止进程，先列出 PID、端口、命令行，并等待我确认。
```

### 7.2 坑二：长时间后台命令导致 bash tool 挂起或残留进程

常见触发：

```bash
npm run dev &
pnpm start &
```

问题在于后台进程可能继承 stdout / stderr / stdin，tool 以为命令还没结束；或者 OpenCode 退出时子进程未被正确清理。

治理方式：

- 长跑服务放在单独终端或 tmux pane 中，由人类控制。
- 让 agent 只运行短命令：测试、lint、typecheck、grep、git diff。
- 如果必须临时启动服务，要求重定向并写 PID 文件，且由人类确认：

```bash
mkdir -p .opencode/runtime .opencode/logs
nohup pnpm dev > .opencode/logs/dev.log 2>&1 < /dev/null & echo $! > .opencode/runtime/dev.pid
```

停止时：

```bash
cat .opencode/runtime/dev.pid
kill <PID>
```

不要让 agent 自动执行上述停止命令，除非 permission 是 `ask` 且你确认 PID。

### 7.3 坑三：`/undo` 或 message revert 不一定等价于 Git 回滚

OpenCode 官方提供 `/undo` 和 `/redo`，但公开 issue 中已经出现过几类 snapshot / revert 问题：

- `git add .` 失败后 snapshot 可能复用旧 tree hash，导致 `/undo` 或 `/redo` 回到很久之前的内容。
- snapshot cache 中残留 `index.lock` 后，某个 workspace 的 Modified Files 和 undo/revert 行为异常。
- TUI 或桌面端 message revert 后文件仍保持修改状态。

治理方式：

1. 每次让 agent 大改前，先建 Git checkpoint：

```bash
git status --short
git switch -c ai/<task>
git add -A
git commit -m "checkpoint: before opencode <task>"
```

如果不想提交：

```bash
git stash push -u -m "before opencode <task>"
```

2. 把 `/undo` 当作便利功能，而不是唯一保险。
3. 每轮后执行：

```bash
git diff --stat
git diff
```

4. 如果 OpenCode 不显示 Modified Files 或 undo 异常：

```text
先退出 OpenCode。
先备份工作区和 ~/.local/share/opencode/snapshot 相关目录。
再检查是否存在 snapshot cache 的 stale index.lock。
确认后再清理对应 workspace 的 snapshot cache。
```

5. Windows 项目中，禁止 agent 创建保留文件名：`nul`、`con`、`aux`、`prn`、`com1`-`com9`、`lpt1`-`lpt9`。

### 7.4 坑四：`write` 可能覆盖已有文件

`write` 的语义是创建新文件或覆盖已有文件，并由 `edit` 权限统一控制。团队更安全的做法是：

- 对大多数任务让 agent 使用 `edit` / `apply_patch`。
- prompt 中声明“不要整体重写大文件”。
- 对新文件创建要求 agent 先说明文件路径和原因。

### 7.5 坑五：MCP / Web 工具过多导致上下文膨胀

MCP 工具会占用上下文。团队落地时不要一次性启用大量 MCP：

- 默认关闭非必要 MCP。
- 按 agent 配置 MCP 权限。
- 文档查找优先用 Scout / webfetch，而不是把所有外部系统工具都塞进主 agent。

### 7.6 坑六：`.gitignore` 会影响 grep / glob / list 的搜索范围

OpenCode 底层搜索工具会受 `.gitignore` 影响。如果你希望 agent 搜索某些被忽略目录，例如生成代码、dist、build、某些 fixtures，可以在项目 `.ignore` 中显式放开：

```gitignore
!dist/
!build/
!fixtures/generated/
```

---

## 8. 可直接复用的 Prompt 模板

### 8.1 只读探索模板

```text
请只读探索，不要修改文件，不要运行会改变状态的命令。

目标：<描述任务>

请输出：
1. 相关入口文件
2. 调用链
3. 数据结构 / API / 配置位置
4. 需要验证的假设
5. 建议的最小修改方案
```

### 8.2 开始实现模板

```text
请按已确认方案做最小实现。

约束：
- 不要提交代码。
- 不要运行 pkill/killall/taskkill/rm -rf/git reset/git clean。
- 不要启动长时间后台服务。
- 优先 edit/apply_patch，不要整体 rewrite 大文件。
- 修改完成后先给出 diff 摘要，再运行最小相关测试。
```

### 8.3 验证模板

```text
请验证本次改动。

步骤：
1. 先看 git diff --stat 和 git diff。
2. 运行最小相关测试。
3. 如果最小测试通过，再运行 typecheck/lint。
4. 如果失败，先解释失败，不要扩大修改面。
5. 最后输出已验证项、未验证项和风险。
```

### 8.4 Review 模板

```text
请以代码审查者身份审查本次 diff，不要修改文件。
重点看：
1. 正确性
2. 边界条件
3. 并发/幂等/事务风险
4. 安全风险
5. 测试覆盖
6. 是否有无关改动
```

---

## 9. 教程结尾建议：研发人员应该带走什么

1. **Agent 不是模型，而是运行时中的决策循环。**
2. **Coding agent 的关键能力不是“写”，而是“查、改、跑、验、审、回滚”。**
3. **OpenCode 的核心学习对象是模块边界：session、tool、permission、agent、snapshot。**
4. **团队落地先做权限治理，再谈效率提升。**
5. **永远用 Git 做主版本控制，OpenCode 的 `/undo` 只是辅助。**
6. **不要让 agent 执行广义 kill / destructive git / rm -rf 类命令。**
7. **把 Plan / Explore / Review 变成默认工作流，把 Build 当成受控执行阶段。**

---

## 10. 参考资料

- 用户提供的 Agent 演进 Markdown 素材。
- OpenCode 官方文档：Introduction, Agents, Tools, Permissions, Rules, Commands, Custom Tools, MCP Servers.
- anomalyco/opencode GitHub 仓库：`session/`, `tool/`, `permission/`, `agent/`, `snapshot/` 相关源码目录。
- GitHub issues: `pkill -f command causes tool call hang in opencode TUI #25664`, `Snapshot .nothrow causes silent data loss #10589`, `stale snapshot index.lock breaks Modified Files and undo #22275`, `Reverting a message does not revert changed files #20638`, `running scripts continue after interrupt #3057`, `LSP processes remain orphaned #18632`.
