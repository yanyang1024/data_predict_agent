# 04. Tools、Skills、Commands、Scripts 与路径坑

> 适用版本：`v1.14.32` / `v1.15.13`。  
> 重点回答：skill 和 tool 脚本代码放哪里、agent 实际使用时如何引用、默认路径原点是什么、`SKILL.md` 与 reference 文档该如何描述 scripts 路径。

## 1. 一句话原则

> **不要让 agent 猜路径；所有可执行脚本都应明确以仓库根或当前会话目录为基准。**

尤其是自定义 tool 调脚本时，不要写：

```ts
await Bun.$`python scripts/foo.py`
```

更推荐写：

```ts
const script = path.join(context.worktree, "scripts/foo.py")
await Bun.$`python3 ${script}`
```

原因是：agent 使用工具时的工作目录、OpenCode 启动目录、git worktree 根、`.opencode/tools` 文件所在目录，不一定是同一个概念。

## 2. 自定义 Tools

### 2.1 放置位置

官方 Custom Tools 文档支持：

```text
项目级：.opencode/tools/
全局级：~/.config/opencode/tools/
```

工具定义必须是 TypeScript 或 JavaScript 文件，但工具内部可以调用任意语言脚本。

示例结构：

```text
project-root/
  opencode.jsonc
  AGENTS.md
  .opencode/
    tools/
      python-add.ts
      add.py
  scripts/
    etch/
      extract_recipe.py
```

### 2.2 文件名与工具名

单个 default export：

```text
.opencode/tools/database.ts -> tool 名为 database
```

多个 export：

```text
.opencode/tools/math.ts 中 export const add -> tool 名为 math_add
.opencode/tools/math.ts 中 export const multiply -> tool 名为 math_multiply
```

避免用内置工具名作为自定义工具名，例如 `bash.ts`，除非你明确要覆盖内置工具。

### 2.3 tool context 中的路径

自定义 tool 的 `execute(args, context)` 可拿到：

```ts
const { agent, sessionID, messageID, directory, worktree } = context
```

推荐约定：

| 字段 | 含义 | 推荐用途 |
|---|---|---|
| `context.worktree` | git worktree 根 | 定位项目脚本、项目配置、仓库内资源 |
| `context.directory` | 当前 session 工作目录 | 尊重用户从子目录启动 OpenCode 的场景 |
| `__dirname` / `import.meta.dir` | tool 文件所在目录 | 定位与 tool 同目录的辅助脚本 |

在项目级 tool 中调用仓库脚本：

```ts
import { tool } from "@opencode-ai/plugin"
import path from "path"

export default tool({
  description: "Run etch recipe extractor on a given input file",
  args: {
    input: tool.schema.string().describe("Input file path relative to the git worktree"),
  },
  async execute(args, context) {
    const script = path.join(context.worktree, "scripts/etch/extract_recipe.py")
    const input = path.join(context.worktree, args.input)
    const result = await Bun.$`python3 ${script} ${input}`.text()
    return result.trim()
  },
})
```

### 2.4 全局 tool 调项目脚本

全局 tool 位于 `~/.config/opencode/tools/`，不能假设自己和项目脚本在同一个目录。因此全局 tool 调项目脚本时更应该用 `context.worktree`：

```ts
const script = path.join(context.worktree, ".opencode/scripts/my-project-script.py")
```

如果脚本是全局工具自带的，则用工具文件自己的目录：

```ts
import path from "path"
import { fileURLToPath } from "url"

const here = path.dirname(fileURLToPath(import.meta.url))
const script = path.join(here, "helper.py")
```

## 3. Skills

### 3.1 放置位置

官方 Skills 文档支持以下路径：

```text
项目 OpenCode：.opencode/skills/<name>/SKILL.md
全局 OpenCode：~/.config/opencode/skills/<name>/SKILL.md
项目 Claude 兼容：.claude/skills/<name>/SKILL.md
全局 Claude 兼容：~/.claude/skills/<name>/SKILL.md
项目 agent 兼容：.agents/skills/<name>/SKILL.md
全局 agent 兼容：~/.agents/skills/<name>/SKILL.md
```

项目级路径发现逻辑是：从当前工作目录向上遍历，直到 git worktree，加载沿途匹配的 skills。

### 3.2 SKILL.md frontmatter

`SKILL.md` 必须从 YAML frontmatter 开始。识别字段：

```yaml
---
name: etch-recipe-review
description: Review semiconductor etch recipe changes and produce risk checklist
license: MIT
compatibility: opencode
metadata:
  domain: semiconductor-etch
---
```

`name` 要满足：

- 1–64 个字符；
- 小写字母、数字、单个 hyphen；
- 不以 `-` 开始或结束；
- 不包含连续 `--`；
- 必须和目录名一致。

### 3.3 skill 里如何描述脚本路径

错误写法：

```markdown
运行 scripts/check.py。
```

问题：agent 不知道是相对当前目录、项目根、skill 目录，还是全局配置目录。

推荐写法：

```markdown
当需要运行检查脚本时，请使用 bash 或项目自定义 tool，并以 git worktree 根作为路径基准：

- 项目脚本：`scripts/etch/check_recipe.py`
- 推荐命令：`python3 scripts/etch/check_recipe.py <recipe-file>`
- 不要从 `.opencode/skills/<name>/` 目录拼相对路径；该目录只是 skill 定义目录，不是执行工作目录。
```

如果 skill 自带 reference 文档或脚本，推荐目录：

```text
.opencode/skills/etch-recipe-review/
  SKILL.md
  references/
    terminology.md
    process-window.md
  scripts/
    normalize_recipe.py
```

在 `SKILL.md` 里写：

```markdown
相关 reference 文件位于本 skill 目录下：

- `references/terminology.md`
- `references/process-window.md`

如果需要读取这些文件，先用 read 工具读取 `.opencode/skills/etch-recipe-review/references/terminology.md`。

如果需要执行 skill 自带脚本，不要假设当前目录在 skill 目录；请使用项目根相对路径：
`python3 .opencode/skills/etch-recipe-review/scripts/normalize_recipe.py <file>`。
```

更稳妥的方式是：把脚本封装成 custom tool，而不是让 skill 直接让 agent 拼 shell 命令。

## 4. Commands

### 4.1 放置位置

```text
项目级：.opencode/commands/<name>.md
全局级：~/.config/opencode/commands/<name>.md
```

`.opencode/commands/test.md` 会产生 `/test` 命令。

### 4.2 command 模板能力

Commands 支持：

```text
$ARGUMENTS     全部参数
$1, $2, $3     位置参数
!`command`     执行 shell 命令并把输出注入 prompt
@file/path     把文件内容注入 prompt
```

示例：

```markdown
---
description: Review etch recipe change
agent: plan
model: anthropic/claude-sonnet-4-20250514
---

Review recipe file @$1 and compare it with @$2.

Constraints:
- Do not edit files.
- Focus on chamber matching, gas flow, RF power, pressure and endpoint changes.
- Output risk level and validation checklist.
```

调用：

```text
/review-etch-recipe recipes/new.yaml recipes/base.yaml
```

### 4.3 `!` Shell 注入的风险

`!` 会运行命令并把输出注入 prompt。不要在 command 中写会改变状态的命令，例如：

```markdown
!`npm install`
!`git reset --hard`
!`rm -rf dist`
```

更推荐只用只读命令：

```markdown
!`git diff --stat`
!`git diff -- src/etch`
!`git log --oneline -10`
```

## 5. Rules / AGENTS.md 与外部文件引用

OpenCode 不会自动解析 `AGENTS.md` 里的任意文件引用。也就是说，下面这句话不一定会让 OpenCode 自动读取文件：

```markdown
请参考 docs/dev.md。
```

更稳妥做法：

### 方式一：用 `instructions`

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "instructions": [
    "docs/dev.md",
    "docs/testing.md",
    ".cursor/rules/*.md"
  ]
}
```

### 方式二：在 AGENTS.md 里显式教 agent 读取

```markdown
## External File Loading

当你看到 `@rules/<name>.md` 这样的引用时，请先判断该文件是否与当前任务相关；如果相关，用 read 工具读取该文件，不要凭记忆回答。
```

## 6. 路径基准常见坑

| 场景 | 常见误判 | 推荐做法 |
|---|---|---|
| 从 VSCode 终端进入项目子目录启动 opencode | 以为当前目录就是项目根 | tool 用 `context.worktree`；命令里写清楚“相对项目根” |
| monorepo | agent 在 package 子目录找不到根 scripts | 在 AGENTS.md 写明 repo root、package root、命令在哪跑 |
| skill 自带脚本 | 以为 shell 当前目录是 skill 目录 | 用项目根相对路径 `.opencode/skills/<name>/scripts/foo.py` 或封装 tool |
| 全局 tool 调项目脚本 | 以为全局 tool 目录和项目有关 | 用 `context.worktree` 找项目脚本 |
| 自定义 command 用 `@file` | 文件相对路径不明确 | 明确写相对项目根，如 `@src/foo.ts` |
| bash 工具找不到脚本 | 脚本没有执行权限或 shebang | 用 `python3 script.py` / `bash script.sh`，不要依赖可执行位 |
| Windows/WSL 混用 | 路径分隔符、盘符、大小写问题 | 优先在 WSL 内跑 Linux 路径；避免 `/mnt/c` 上大仓库 |
| `.gitignore` 排除生成目录 | grep/glob 搜不到 | 用 `.ignore` 显式放开必要目录 |

## 7. 推荐项目目录规范

```text
project-root/
  AGENTS.md
  opencode.jsonc
  .ignore
  .opencode/
    agents/
      review.md
    commands/
      review-diff.md
      plan-change.md
    skills/
      etch-recipe-review/
        SKILL.md
        references/
        scripts/
    tools/
      etch-recipe.ts
  scripts/
    etch/
      extract_recipe.py
      validate_recipe.py
  docs/
    opencode/
      development-standards.md
      testing-policy.md
```

## 8. 推荐在 AGENTS.md 中加入的路径规则

```markdown
## Path rules

- Treat the git worktree root as the default project root.
- When referencing project files, use paths relative to the git worktree root.
- Do not assume the current shell directory is the same as `.opencode/tools` or `.opencode/skills`.
- For custom tools, use `context.worktree` to locate project scripts.
- If a script is under `scripts/`, invoke it with an explicit interpreter, e.g. `python3 scripts/etch/validate_recipe.py`.
- If a command fails because a file is not found, run `pwd`, `git rev-parse --show-toplevel`, and `ls` before retrying.
```
