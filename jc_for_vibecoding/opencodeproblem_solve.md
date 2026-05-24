下面按你列的 7 个点回答。我的总体判断是：你遇到的很多问题不是“上下文长度不够”导致的，而是 **模型/Provider 的工具调用稳定性、OpenCode 的权限与循环保护、TUI/子代理可见性、Skill/Agent 设计边界** 叠在一起造成的。OpenCode 本身是一个开源 AI coding agent，支持 TUI、Desktop、IDE 扩展；它通过内置工具让模型读写文件、执行 bash、调用 skill、维护 todo、调用子代理等。([OpenCode][1])

## 先给结论

我建议你把 OpenCode 的能力分成四层来治理：

**AGENTS.md**：放项目级长期规则，例如目录结构、测试命令、代码风格、提交前检查。

**Skill**：放可复用 SOP，例如“如何生成 PDF 报告”“如何做代码审查”“如何写迁移脚本”。Skill 本质是被 `skill` 工具按需加载的 Markdown 指令，不是自动执行的插件。OpenCode 会把可用 skill 的名称和描述暴露给模型，模型需要时调用 `skill({ name: "xxx" })` 加载完整内容。([OpenCode][2])

**Agent/Subagent**：放角色、模型、权限、可调用工具和可用 skill 范围。Primary agent 直接和你对话；Subagent 由 primary agent 自动或通过 `@agent-name` 手动调用。([OpenCode][3])

**Custom tool / MCP / 脚本**：放确定性执行逻辑。只靠 Skill 让模型“记住怎么做”，遇到复杂长流程还是会发散；真正稳定的部分应下沉成脚本、custom tool 或 MCP。

你关于“用 sub agent 做多个 skill”的方向是对的，但我会改成：**不要让一个 Skill 再去链式调用很多 Skill；而是让一个 orchestrator primary agent 调用多个职责明确的 subagent，每个 subagent 只白名单少数相关 skills。** 这样比“Skill 调 Skill”稳定得多。

---

## 1. 工具调用报错后重试，尤其 todo / plan 相关

OpenCode 的 `todowrite` 工具用于在复杂任务中创建和更新任务列表，官方说明它是模型组织多步骤任务的工具；但它也是一个真实工具调用，因此会受模型的 JSON/tool-call 质量影响。([OpenCode][4]) 你提到“调用 todo 给任务做计划时报错后重试”，这和社区里已经出现过的现象一致：有人报告 GLM 5.1 在 OpenCode Go 中一旦做 Todos 就卡住，而普通聊天正常，且其他模型如 Kimi、Minimax 没这个问题。([GitHub][5])

更广义地看，OpenCode 的工具调用链路确实可能遇到 malformed tool input、invalid diff、JSON parsing failed 这类问题；有 issue 明确报告在 tool-heavy edit turn 中出现 transient provider/tool-call parsing failures，导致会话 abort 而不是自动修复重试。([GitHub][6]) 另一个 issue 也记录了复杂 bash heredoc / 多行内联脚本触发 JSON 解析错误后，进入很长的 `empty_stream` retry/backoff 状态，重启后恢复。([GitHub][7])

建议分三档处理：

**第一档：确认是不是模型专属问题。** 同一任务分别用你常用模型、OpenCode Zen 里推荐/验证过的模型、以及一个工具调用稳定的模型跑一次。官方推荐新用户使用 OpenCode Zen，因为它是一组经 OpenCode 团队测试和验证的模型。([OpenCode][1]) 如果只在某个模型上出现 todo/tool-call 错误，就不要从 prompt 层硬修；直接把该模型限制在只读分析、摘要、生成方案，不让它做高频工具调用。

**第二档：对 todo 降权。** 如果某模型经常在 `todowrite` 上卡住，可以在对应 agent 里把 todo 设为 `ask` 或 `deny`。这样会牺牲 todo sidebar 的体验，但能减少“计划工具反复失败”的概率。OpenCode 的权限系统支持 `allow`、`ask`、`deny`，并且 `todowrite` 是可配置权限项。([OpenCode][8])

```json
{
  "$schema": "https://opencode.ai/config.json",
  "agent": {
    "stable-build": {
      "description": "Stable build agent for tool-heavy implementation without todo loops",
      "mode": "primary",
      "temperature": 0.1,
      "permission": {
        "todowrite": "deny",
        "question": "ask",
        "edit": "ask",
        "bash": {
          "*": "ask",
          "git status*": "allow",
          "git diff*": "allow",
          "rg *": "allow",
          "grep *": "allow"
        }
      }
    }
  }
}
```

**第三档：不要让模型用复杂 bash 一口气写大脚本。** 你可以在 AGENTS.md 或 agent prompt 里明确要求：大脚本必须先用 `write`/`edit`/`apply_patch` 创建真实文件，再用短命令执行；禁止把几十行 Python/Node 代码塞进一个多行 heredoc 的 bash 调用。这个建议不是因为 heredoc 本身不能用，而是因为多层转义、换行、嵌套引号很容易放大 tool-call JSON 出错概率。

---

## 2. 会话调用一些工具后自己停止，需要你说“继续”

这里要区分三种“停止”。

第一种是 **模型自己判断任务完成或先输出阶段性总结**。OpenCode 的 agent loop 默认会持续迭代，直到模型选择停止或用户打断；如果配置了 `steps`，达到上限后会强制转为文本响应并总结已做工作和剩余任务。([OpenCode][3]) 所以如果你自定义 agent 里设了较低 `steps`，它很容易“做到一半就总结”，你再打“继续”它才接着做。

第二种是 **工具/Provider 报错导致本轮终止**。这类表现通常是工具调用失败、JSON 解析失败、provider empty stream、rate limit 或网络错误；打“继续”只是给了模型一个新回合，未必是真正恢复同一个执行栈。官方 troubleshooting 建议遇到问题先看日志，日志位置在 macOS/Linux 的 `~/.local/share/opencode/log/`，Windows 在 `%USERPROFILE%\.local\share\opencode\log`，也可以用 `opencode --log-level DEBUG` 获取更详细日志。([OpenCode][9])

第三种是 **子代理或问题工具在等输入，但父会话看起来像停了**。有 issue 报告 subagent 工作流里父会话会长时间显示 loading，实际可能是子代理在等用户回答，或某个 `webfetch` / `bash` 卡住；当时唯一可行的方式是切到子会话检查。([GitHub][10]) 官方文档也说明 subagent 会创建 child sessions，需要用 `session_child_first`、左右切换、`session_parent` 在父子会话间导航。([OpenCode][3])

我的建议：

在长任务里，给 agent 加一个“停止契约”：

```md
When the task is not finished:
- Do not end with a generic summary.
- Either continue with the next concrete tool call, or stop with a section named BLOCKED.
- BLOCKED must include the exact reason, the last successful file/path/command, and the next user decision needed.
- Do not ask "Should I continue?" unless a permission, destructive operation, or product decision is required.
```

同时，把大任务拆成“计划 → 执行一个小阶段 → 验证 → 汇报”。这比让它一次性跑完整项目更稳。OpenCode 官方也建议新增功能时先用 Plan mode 制定计划，再切回 Build mode 执行。([OpenCode][1])

---

## 3. 很卡、反复执行同一个操作，但实际没完成

你描述的“反复说要写脚本，但脚本没写出来”，我会优先怀疑四类原因：

**一是模型在说计划，没有真正调用写文件工具。** 这时需要强制“完成定义”从语言变成可验证状态。例如要求它每创建脚本后必须执行：

```bash
ls -l path/to/script
sed -n '1,80p' path/to/script
git diff -- path/to/script
```

并在没有这些验证前不得声称“脚本已创建”。

**二是工具调用参数为空或畸形。** 有 issue 报告 GPT-5.4 在 OpenCode 里反复调用空的 `apply_patch {}`，导致 `Tool execution aborted` 反复出现，目标文件从未修改；同一任务用 GPT-5.3 Codex 未复现。([GitHub][11]) 这很像你说的“上下文还没超限，但它一直没做成”：问题不在上下文，而在模型输出的 tool-call payload 或 OpenCode 解析/执行层。

**三是 OpenCode 的循环保护触发。** 官方权限里有 `doom_loop`，当同一个工具调用以相同输入重复 3 次时触发；默认 `doom_loop` 和 `external_directory` 是 `ask`。([OpenCode][8]) 我不建议把 `doom_loop` 直接设成 `allow`，因为这可能让自动恢复继续消耗 token。更稳妥是保留 `ask`，一旦提示，就中断、查看 `/details`、检查日志，然后换模型或改 prompt。

**四是它把大量代码塞进一个 bash/heredoc，导致 JSON/转义失败。** 上面提到的 malformed tool-call / empty_stream issue 就是类似风险。([GitHub][7]) 最稳的做法是让它“先写文件，再运行文件”，而不是“在 bash 里临时拼一大段脚本”。

我建议你在项目的 `AGENTS.md` 加这段：

```md
For any generated script or file:
1. Create or modify the actual file with write/edit/apply_patch.
2. Verify the file exists with ls or equivalent.
3. Read back the first 40-80 lines before claiming success.
4. Run the smallest relevant smoke test.
5. If the same tool fails twice with the same input, stop and report BLOCKED instead of retrying.
```

这个规则通常能显著降低“它一直说要写，但没写”的幻觉式执行。

---

## 4. Skill 触发机制：一句话能触发多个 skill 吗？一个会话能触发多个 skill 吗？

OpenCode 的 Skill 机制不是一个确定性的“关键词触发器”，更像是 **LLM 可见的按需工具**。OpenCode 会扫描项目和全局目录中的 `SKILL.md`，只把 skill 的名称和 description 暴露在 `skill` 工具描述里；模型判断需要时，再调用 `skill({ name: "git-release" })` 加载完整内容。([OpenCode][2])

所以答案是：

**一句话理论上可能涉及多个 skill，但不要依赖它自动稳定触发多个。** `skill` 工具一次调用加载一个 skill；模型可以在一个任务里先后调用多个 skill，但这取决于模型判断、工具调用能力、权限设置和 skill 描述是否清晰。官方文档没有承诺“一句话自动多 skill 路由”。

**一个会话里当然可以加载多个 skill。** 只要权限允许，agent 可以在后续回合继续调用 `skill` 工具加载其他 skill。OpenCode 还支持用 `permission.skill` 做全局或 per-agent 的 allow/deny/ask 控制。([OpenCode][2])

**Skill 的 description 非常关键。** 官方要求 description 为 1–1024 字符，并建议写得足够具体，方便 agent 正确选择。([OpenCode][2]) 不要写“帮助开发”“处理文档”这种泛描述；应该写“当需要把研究报告 Markdown 转成带中文字体、引用和图表的 PDF 时使用”。

推荐结构：

```md
---
name: academic-report-to-pdf
description: Convert academic Markdown reports into publication-quality PDF with Chinese font support, citations, figures, and reproducible build commands. Use only when the user asks to export a report to PDF.
---

## When to use
Use this skill when the user has a Markdown academic report and wants a PDF.

## When not to use
Do not use this skill for slide generation, code review, or general writing.

## Required workflow
...
```

如果你发现“一个任务可能需要 3 个 skill”，不要指望模型自动串起来。更稳的是创建一个 **workflow skill**，例如 `academic-report-workflow`，里面明确写：

```md
1. If the input is a paper PDF, load/use academic-paper-reading.
2. If a Markdown report is requested, follow academic-report-writing.
3. If PDF export is requested, follow academic-report-to-pdf.
4. If slides are requested, follow academic-report-to-slides.
```

但更推荐下一节的 subagent 方案。

---

## 5. Skill 链式调用时间长、反馈逻辑紊乱；是否用 subagent 做多个 skill？

你的想法是对的，但需要加一层“编排设计”。

不要这样设计：

```text
用户 → build agent → skill A → skill B → skill C → 工具调用 → 长时间执行
```

这会让上下文、目标、状态、权限、完成定义混在一起，很容易出现逻辑紊乱。

更稳的设计是：

```text
用户
  ↓
orchestrator primary agent
  ↓ task
research subagent  ── 只允许 research-* skills，禁止 edit
writer subagent    ── 只允许 writing-* skills
coder subagent     ── 只允许 coding-* skills，允许 edit/bash
reviewer subagent  ── 只允许 review-* skills，禁止 edit
```

OpenCode 的文档明确支持 primary agents 与 subagents：primary 是你直接交互的主助手，subagents 是专门助手，可由 primary 自动调用，也可用 `@` 手动调用；还可以用 `permission.task` 控制某个 agent 能调用哪些 subagents。([OpenCode][3])

一个可用的 orchestrator 配置示例：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "agent": {
    "orchestrator": {
      "description": "Plans multi-step work and delegates to approved specialist subagents",
      "mode": "primary",
      "temperature": 0.1,
      "steps": 40,
      "permission": {
        "edit": "deny",
        "bash": "ask",
        "skill": {
          "*": "deny",
          "workflow-*": "allow"
        },
        "task": {
          "*": "deny",
          "researcher": "allow",
          "implementer": "allow",
          "reviewer": "allow"
        },
        "question": "ask",
        "doom_loop": "ask"
      }
    },
    "researcher": {
      "description": "Read-only research subagent for docs, dependencies, and codebase exploration",
      "mode": "subagent",
      "temperature": 0.1,
      "permission": {
        "edit": "deny",
        "bash": "ask",
        "skill": {
          "*": "deny",
          "research-*": "allow"
        }
      }
    },
    "implementer": {
      "description": "Implementation subagent for making scoped code changes and running tests",
      "mode": "subagent",
      "temperature": 0.1,
      "permission": {
        "edit": "ask",
        "bash": "ask",
        "skill": {
          "*": "deny",
          "coding-*": "allow",
          "test-*": "allow"
        }
      }
    },
    "reviewer": {
      "description": "Read-only code review subagent that checks diffs, risks, and missing tests",
      "mode": "subagent",
      "temperature": 0.1,
      "permission": {
        "edit": "deny",
        "bash": {
          "*": "ask",
          "git diff*": "allow",
          "git status*": "allow"
        },
        "skill": {
          "*": "deny",
          "review-*": "allow"
        }
      }
    }
  }
}
```

关键点是：

**每个 subagent 的 skill 白名单要窄。** OpenCode 支持用 pattern 控制 skill 权限，例如 `internal-*` deny、`documents-*` allow；被 deny 的 skill 会从 agent 可见范围里隐藏或拒绝访问。([OpenCode][2])

**orchestrator 不直接做大修改。** 它只拆任务、调用 subagent、汇总结果。这样即使 implementer 卡了，你也能定位到是哪个子任务的问题。

**subagent 最好少问问题。** 如果 subagent 有 `question` 权限，很容易出现“子代理在等用户输入，但父会话看起来卡住”的体验；这个问题已有 issue 记录。([GitHub][10]) 对多数 subagent，我会让它们遇到不确定时输出 `BLOCKED`，而不是向用户发交互式问题。

**不要盲目并行。** 官方 general subagent 可用于并行工作，但并行越多，TUI 状态可见性和日志排查越难。OpenCode 文档也说明需要在 child sessions 间导航。([OpenCode][3]) 我的经验性建议是：先把单个 subagent 跑稳，再做并行；每个子代理输出统一格式：

```md
## Result
## Files changed
## Commands run
## Tests
## Risks
## Next recommended action
```

---

## 6. 图片渲染：想图文并茂，但对话里不能直接渲染图

这基本是 TUI 形态的天然限制。OpenCode TUI 是终端界面，官方文档强调它可以在终端里对话、引用文件、执行 bash、导出 Markdown；它也支持把图片拖进终端作为输入，让模型扫描图片并加入 prompt。([OpenCode][12]) 但“模型生成图片后直接在 TUI 对话中 inline 渲染”不是一个可以稳定依赖的能力。

近期也有 TUI Markdown 渲染相关问题和修复：有人报告长 Markdown 内容在 TUI 中渲染乱码/样式错误；changelog 里则记录了后续版本恢复 Markdown rendering、修复表格渲染、改进 H1 等。([GitHub][13]) 这说明 TUI 渲染层在演进，但你要的“图文并茂 inline 输出”仍不应作为主路径。

推荐三种方案：

**方案 A：生成 HTML 报告。** 让 OpenCode 生成 `report.html`、`assets/*.png`、`assets/*.svg`，最后用浏览器打开。对“图文并茂”最稳定。

```text
请生成 report.html 和 assets/ 目录：
- 所有图表保存为 SVG 或 PNG
- HTML 内用相对路径引用图片
- 最后运行 python -m http.server 或给出 open report.html 的命令
```

**方案 B：生成 Markdown + 图片文件。** TUI 里显示 Markdown 链接，图片去路径查看。适合你已经接受“图在路径里看”的模式。可以配合 `/export` 导出当前对话为 Markdown，官方 TUI 支持 `/export`。([OpenCode][12])

**方案 C：用 Mermaid / ASCII / SVG 源码作为可读中间态。** 如果只是架构图、流程图，要求它输出 Mermaid 代码块，同时保存 `diagram.svg`。TUI 看代码，浏览器看最终图。

我不建议把“终端里直接渲染图片”作为强需求。即使某些终端支持 Kitty/WezTerm 图片协议，OpenCode TUI 是否完整透传和布局适配也不一定稳定。对交付物来说，HTML/PDF/Markdown 文件更可控。

---

## 7. 其他常见使用问题与解决方式

### A. 版本和缓存问题

先升级。OpenCode changelog 最近仍在密集修复 tool、TUI、Desktop、session、plugin、Markdown、reasoning、provider 相关问题，例如 v1.15.9 改进 skill invocation 错误提示，v1.15.7 让 tool schema failures 以友好工具错误呈现，v1.14.51 修复 interrupted assistant messages 导致会话卡住等。([OpenCode][14])

如果遇到 provider package、API call、奇怪启动/工具错误，官方 troubleshooting 建议清理 `~/.cache/opencode`，重启后重新安装 provider package。([OpenCode][9])

```bash
opencode upgrade
rm -rf ~/.cache/opencode
opencode --log-level DEBUG
```

Windows 用户优先用 WSL。官方明确建议 Windows 上为了更好性能和完整兼容性使用 WSL；troubleshooting 也提到 Windows 上慢、文件访问或终端问题时尝试 WSL。([OpenCode][1])

### B. 插件导致的卡顿或异常

OpenCode Desktop 官方排障里说，很多 Desktop 问题来自插件异常、缓存损坏或服务器设置错误；建议先完全退出重启，必要时临时禁用插件，把 `plugin` 设为空数组，或移走插件目录。([OpenCode][9]) 即使你主要用 TUI，如果装了工作区/全局插件，也建议在复现问题时先做一次“无插件复现”。

```json
{
  "$schema": "https://opencode.ai/config.json",
  "plugin": []
}
```

### C. 权限配置过松或过紧

默认大多数权限是 `allow`，`doom_loop` 和 `external_directory` 默认为 `ask`，`.env` 文件默认被 read 拒绝。([OpenCode][8]) 我建议日常开发不要全局 YOLO，而是：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "read": {
      "*": "allow",
      "*.env": "deny",
      "*.env.*": "deny",
      "*.env.example": "allow"
    },
    "grep": "allow",
    "glob": "allow",
    "edit": "ask",
    "bash": {
      "*": "ask",
      "git status*": "allow",
      "git diff*": "allow",
      "git log*": "allow",
      "rg *": "allow",
      "grep *": "allow",
      "npm test*": "ask",
      "pnpm test*": "ask",
      "rm *": "deny",
      "git push*": "deny"
    },
    "external_directory": "ask",
    "doom_loop": "ask",
    "question": "ask"
  }
}
```

这样读代码很顺，写文件和危险命令仍要确认。

### D. 忽略文件导致它“找不到代码”

OpenCode 的 `grep`、`glob` 底层使用 ripgrep，默认遵守 `.gitignore`，所以 `.gitignore` 里的 `dist/`、`build/`、`node_modules/` 等不会被搜索。官方建议如果确实要包含通常被忽略的目录，可以在项目根目录创建 `.ignore` 进行显式允许。([OpenCode][4])

```gitignore
!dist/
!build/
!node_modules/some-package/
```

### E. 改坏代码后的恢复

强烈建议每次大任务前先保证工作区干净。OpenCode 的 `/undo` 和 `/redo` 可以撤销/恢复消息及文件修改，但官方说明它内部依赖 Git 管理文件变更，所以项目需要是 Git 仓库。([OpenCode][12])

推荐习惯：

```bash
git status
git add -A && git commit -m "checkpoint before opencode task"
```

然后再让 OpenCode 改。失败时先 `/undo`，再缩小任务范围重试。

### F. Web 搜索和文档检索

OpenCode 有 `webfetch` 和 `websearch`。`webfetch` 适合读取指定 URL；`websearch` 适合发现信息，但官方说明它只在使用 OpenCode provider 时可用，或设置 `OPENCODE_ENABLE_EXA`。([OpenCode][4])

```bash
OPENCODE_ENABLE_EXA=1 opencode
```

如果你经常让它查新文档，建议给一个 `docs-researcher` subagent，只允许 `webfetch/websearch/read/grep`，禁止 edit。这样不会因为查文档把代码也改了。

---

## 我给你的最终推荐工作流

对于你这种已经深度使用 OpenCode、并开始做 Skill/Agent 体系的人，我会采用下面的工程化方案。

第一，建立一个“稳定默认 agent”，禁用 todo 或降为 ask，保留 `doom_loop: ask`，低温度，限制危险 bash。它用于日常 coding。

第二，把 skill 分成小而明确的 SOP，description 写清“何时用、何时不用”。不要把所有 skill 全局放开给所有 agent。

第三，创建 orchestrator primary agent，但让它少改文件，多做拆解和委派。每个 subagent 只允许相关 skill，权限最小化。

第四，所有长流程都要求“可验证完成定义”：文件存在、diff 可见、测试命令已跑、失败时输出 BLOCKED，而不是泛泛说“我会继续”。

第五，图文输出不要追求 TUI inline 渲染。让它生成 HTML/Markdown/PDF + assets，TUI 只负责路径、摘要和命令。

第六，遇到“重复同一个操作”时不要继续硬等：打开 `/details`，看是不是空 `apply_patch`、todo loop、bash JSON parse、subagent 等输入；然后中断、换模型或降权相关工具。上下文没超限并不代表 agent loop 一定健康。

最值得先落地的，是这三件事：**为不同模型设置不同 agent 权限；给每个 subagent 做 skill 白名单；在 AGENTS.md 加“生成文件必须读回验证”的完成规则。**

[1]: https://opencode.ai/docs/ "Intro | AI coding agent built for the terminal"
[2]: https://opencode.ai/docs/skills/ "Agent Skills | OpenCode"
[3]: https://opencode.ai/docs/agents/ "Agents | OpenCode"
[4]: https://opencode.ai/docs/tools "Tools | OpenCode"
[5]: https://github.com/anomalyco/opencode/issues/24178 "GLM 5.1 Opencode Go Stuck on Todos · Issue #24178 · anomalyco/opencode · GitHub"
[6]: https://github.com/anomalyco/opencode/issues/15906 "retry invalid tool-call diff / malformed tool input instead of aborting · Issue #15906 · anomalyco/opencode · GitHub"
[7]: https://github.com/anomalyco/opencode/issues/25566 "Validate provider-bound payloads before streaming to avoid empty_stream after malformed tool calls · Issue #25566 · anomalyco/opencode · GitHub"
[8]: https://opencode.ai/docs/permissions/ "Permissions | OpenCode"
[9]: https://opencode.ai/docs/troubleshooting/ "Troubleshooting | OpenCode"
[10]: https://github.com/anomalyco/opencode/issues/10802 "TUI: Parent session appears stuck \"loading\" when subagent is blocked (waiting user input / hanging tool call); lack of visibility and recovery UX · Issue #10802 · anomalyco/opencode · GitHub"
[11]: https://github.com/anomalyco/opencode/issues/20227 "[Bug] GPT-5.4 repeatedly sends empty apply_patch tool calls (`{}`), causing `Tool execution aborted`, while GPT-5.3 Codex does not · Issue #20227 · anomalyco/opencode · GitHub"
[12]: https://opencode.ai/docs/tui/ "TUI | OpenCode"
[13]: https://github.com/anomalyco/opencode/issues/24120 "TUI markdown render error · Issue #24120 · anomalyco/opencode · GitHub"
[14]: https://opencode.ai/changelog "OpenCode | Changelog"
