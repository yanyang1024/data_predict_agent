# Skill + Tool + Script 路径引用示例

## 推荐目录

```text
project-root/
  AGENTS.md
  opencode.jsonc
  .opencode/
    skills/
      etch-recipe-review/
        SKILL.md
        references/
          terminology.md
        scripts/
          normalize_recipe.py
    tools/
      etch-normalize.ts
  scripts/
    etch/
      validate_recipe.py
```

## `.opencode/skills/etch-recipe-review/SKILL.md`

```markdown
---
name: etch-recipe-review
description: Review semiconductor etch recipe changes and produce a risk checklist
compatibility: opencode
metadata:
  domain: semiconductor-etch
---

## What I do

I help review etch recipe changes and produce risk checklists.

## Path rules

- Treat the git worktree root as the project root.
- Project scripts are referenced relative to the git worktree root.
- Do not assume the shell current directory is this skill directory.
- If you need the terminology reference, read `.opencode/skills/etch-recipe-review/references/terminology.md`.
- If you need to normalize a recipe, prefer the `etch-normalize` custom tool.
- If the custom tool is unavailable, use:
  `python3 .opencode/skills/etch-recipe-review/scripts/normalize_recipe.py <recipe-file>`

## Output

Return:

1. Risk level.
2. Changed parameters.
3. Process-window risk.
4. Required validation.
5. Open questions.
```

## `.opencode/tools/etch-normalize.ts`

```ts
import { tool } from "@opencode-ai/plugin"
import path from "path"

export default tool({
  description: "Normalize an etch recipe file using the project skill script",
  args: {
    recipe: tool.schema.string().describe("Recipe file path relative to the git worktree root"),
  },
  async execute(args, context) {
    const script = path.join(
      context.worktree,
      ".opencode/skills/etch-recipe-review/scripts/normalize_recipe.py",
    )
    const recipe = path.join(context.worktree, args.recipe)
    const result = await Bun.$`python3 ${script} ${recipe}`.text()
    return result.trim()
  },
})
```

## 为什么这样写

- `context.worktree` 是 git worktree 根，适合定位项目文件。
- skill 目录只是说明文件目录，不是 shell 当前目录。
- 把脚本封装成 tool，可以让参数 schema、权限和输出更可控。
- 如果脚本找不到，tool 可以显式报错，而不是让模型反复猜路径。
