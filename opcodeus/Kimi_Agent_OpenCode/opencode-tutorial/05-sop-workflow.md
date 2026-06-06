# 5. 面向研发人员的 OpenCode 使用 SOP

---

## 5.1 Phase 0：进入工作前先建安全边界

```bash
git status --short
git switch -c ai/<ticket-or-task>
# 如果当前已有未提交工作，优先 stash 或 commit
# git stash push -u -m "before opencode <task>"
# 或 git add -A && git commit -m "checkpoint: before opencode <task>"
```

### 安全基线规则

1. 每个独立任务一个分支或 worktree。
2. 不在主分支直接让 agent 改代码。
3. 不把 `/undo` 当唯一回滚机制。
4. 禁止 agent 自动 `git push`、`git reset --hard`、`git clean -fd`。
5. 广义 kill 命令必须人工确认。

---

## 5.2 Phase 1：初始化项目规则

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

---

## 5.3 Phase 2：先 Plan，不要直接 Build

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

---

## 5.4 Phase 3：实现前先收敛范围

要求 agent 给出"修改计划 + 文件范围"：

```text
在开始修改前，请列出你计划改动的文件和每个文件的改动目的。
如果需要新文件，请说明为什么不能改已有文件。
不要运行长时间后台服务，不要 kill 进程，不要提交代码。
```

---

## 5.5 Phase 4：Build 模式做最小 patch

```text
切换到 Build 模式后，请按刚才确认的方案做最小修改。
要求：
- 优先 edit / patch，不要整体 rewrite 大文件。
- 不要改无关格式。
- 不要自动提交。
- 每完成一个逻辑小步，说明改了什么以及下一步验证什么。
```

---

## 5.6 Phase 5：验证必须独立于实现

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

---

## 5.7 Phase 6：人工 review + checkpoint

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

## 5.8 推荐 `opencode.json` 安全基线

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

> **注意**：OpenCode 的权限匹配是**"后匹配规则优先"**，所以通配符 `*` 应该放在前面，更具体规则放在后面。

---

## 5.9 推荐 `AGENTS.md` 模板

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

## Path and script execution
- Working directory is the project root.
- Before executing scripts, run `pwd` to confirm current directory.
- Use absolute paths or paths relative to project root.
- Do not assume the current directory is the project root after `cd` commands.
- Custom tools are in `./.opencode/tools/`.
- Prefer calling skills via `@skillname` rather than direct bash execution.
```

---

## 5.10 团队落地 checklist

- [ ] 确定团队统一的模型和 provider（建议写入项目 `.opencode/config.json`）
- [ ] 为每位成员配置 API Key（环境变量或 `~/.opencode/config.json`）
- [ ] 创建项目 `AGENTS.md`，包含项目结构、命令、安全规则
- [ ] 配置保守的 `opencode.json` 权限基线
- [ ] 建立 Git checkpoint 工作流（分支 + stash/commit）
- [ ] 定义 Plan → Explore → Build → Review 的标准 workflow
- [ ] 在 CI 中集成验证步骤（test、lint、typecheck）
- [ ] 定期检查 OpenCode 版本更新，同步配置变更
