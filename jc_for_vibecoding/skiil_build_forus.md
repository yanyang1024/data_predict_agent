下面是一份面向工程团队的教程：**如何从一次和 Agent 的成功对话中，沉淀成可复用 Skill，让之后相同代码迁移/开发场景可以更快、更稳地完成**。示例以 **opencode** 为 Agent 应用，重点放在“代码迁移 + 开发任务”的落地。

---

# 从一次 Agent 对话沉淀可复用 Skill：opencode 实战教程

## 1. 核心结论

不要把一次成功对话原封不动保存成“历史记录”。更好的做法是把它拆成四类可复用资产：

| 资产      | 放什么                                   | 在 opencode 中的承载方式                         |
| ------- | ------------------------------------- | ----------------------------------------- |
| 项目长期上下文 | 项目结构、构建命令、测试命令、架构约定、目录职责              | `AGENTS.md`                               |
| 可复用工作流  | “遇到某类任务时应该怎么做”的步骤、检查点、失败处理、输出格式       | `.opencode/skills/<skill-name>/SKILL.md`  |
| 一键触发入口  | 高频任务的固定 prompt，例如 `/migrate-code xxx` | `.opencode/commands/*.md`                 |
| 专用角色    | 只读审查员、安全审计员、迁移规划员等                    | `.opencode/agents/*.md` 或 `opencode.json` |

opencode 本身支持这些组合：它是一个开源 AI coding agent，可运行在终端、桌面应用或 IDE 中；它支持 `AGENTS.md` 项目规则、Agent Skills、custom commands、custom agents 和权限配置。([OpenCode][1])

一个有参考价值的研究结论是：arXiv 上一篇关于 `AGENTS.md` 的预印本实验了 10 个仓库和 124 个 PR，报告称有 `AGENTS.md` 时，AI coding agent 的中位运行时间降低约 28.64%，输出 token 降低约 16.58%，同时任务完成行为大体可比。这个结果不是“所有仓库必然如此”的定律，但支持一个实践判断：**把仓库级规则外化给 Agent，通常比每次重新解释更高效**。([arXiv][2])

---

## 2. 先分清：AGENTS.md、Skill、Command、Agent 各自解决什么

### 2.1 `AGENTS.md`：项目级长期规则

`AGENTS.md` 适合放“每次进入这个仓库都应该知道”的东西，例如：

```md
# Project Rules

## Build / Test
- Install dependencies with `pnpm install`.
- Run unit tests with `pnpm test`.
- Run focused package tests with `pnpm --filter <package> test`.

## Architecture
- `packages/legacy-*` contains old services.
- `packages/*-service` contains new TypeScript services.
- Shared DTOs live in `packages/contracts`.

## Coding Conventions
- Prefer explicit return types for exported functions.
- Do not introduce new runtime dependencies without explaining why.
```

opencode 的 `/init` 会扫描仓库中的重要文件，必要时询问少量问题，并创建或更新 `AGENTS.md`；官方文档也建议把项目的 `AGENTS.md` 提交到 Git，以便团队共享。([OpenCode][1])

**判断标准：**
只要它是“这个仓库所有任务都需要知道的背景”，就放进 `AGENTS.md`，不要放进某个具体 Skill。

---

### 2.2 Skill：按需加载的可复用任务工作流

Skill 适合放“某一类任务的标准操作流程”。例如：

* 旧服务迁移到新框架。
* 从 REST API 迁移到 gRPC。
* 给已有模块补测试。
* 做一次安全修复。
* 做一次数据库 schema 迁移。

opencode 的 Agent Skills 使用 `SKILL.md` 定义可复用行为；Agent 会先看到可用 skill 的名称和描述，然后在需要时通过原生 `skill` tool 加载完整内容。skill 可以放在项目级 `.opencode/skills/<name>/SKILL.md`，也可以放在全局配置目录，且 opencode 还支持 `.claude/skills` 和 `.agents/skills` 兼容路径。([OpenCode][3])

**判断标准：**
只要它是“跨多次需求可重复执行的一套流程”，就应该沉淀为 Skill。

---

### 2.3 Command：把高频入口变成 slash command

Command 适合做“固定 prompt 入口”。例如：

```bash
/migrate-code source=packages/legacy-payment target=packages/payment-service
```

opencode custom commands 可以通过 `.opencode/commands/*.md` 或配置文件定义；命令文件的文件名会变成 slash command 名称，frontmatter 可以指定描述、agent、model，正文会作为 prompt 模板，且支持 `$ARGUMENTS`、位置参数、shell 输出和文件引用。([OpenCode][4])

**判断标准：**
如果团队成员经常不知道该如何正确开口，就给他一个命令入口。

---

### 2.4 Agent：给不同阶段配置不同能力和权限

Agent 适合区分“规划、实现、审查”的角色。例如：

* `plan`：只读规划，不允许改文件。
* `build`：允许编辑和运行测试。
* `migration-reviewer`：只读审查迁移质量，不直接改代码。

opencode 内置 `Build` 和 `Plan` 两个 primary agents；`Build` 默认用于需要文件操作和命令执行的开发工作，`Plan` 更适合在不修改代码的情况下分析代码、提出方案或创建计划。opencode 也支持通过 JSON 或 Markdown 定义自定义 agent，并配置 prompt、model、temperature 和权限。([OpenCode][5])

**判断标准：**
如果某个步骤需要不同权限、安全边界或审查视角，就做成专用 Agent。

---

## 3. 从一次对话中沉淀 Skill 的完整流程

推荐使用下面的六步法。

---

## Step 1：保留一次完整的成功样例

一次成功对话通常包含这些信息：

1. 用户原始需求。
2. Agent 做计划时问过的问题。
3. Agent 读取了哪些文件。
4. Agent 采用了哪些迁移策略。
5. Agent 修改了哪些文件。
6. Agent 运行了哪些测试或 lint。
7. 中途犯过什么错，后来如何修正。
8. 最终交付说明。
9. 用户的验收反馈。

在 opencode 中，可以用 `/share` 分享当前会话链接，便于团队复盘或调试；对话默认不会被分享，需要用户主动执行 `/share`。([OpenCode][1])

---

## Step 2：把对话拆成“可复用经验”和“一次性细节”

不要把整段对话塞进 Skill。应该用下面的表来筛选：

| 对话内容                                    | 是否进入 Skill | 原因                     |
| --------------------------------------- | ---------: | ---------------------- |
| “先读 legacy router，再读新服务同类实现”            |          是 | 可复用迁移策略                |
| “先用 Plan 模式生成迁移计划，不要直接改文件”              |          是 | 可复用安全流程                |
| “本次迁移的是 `payment/refund.ts`”            |          否 | 一次性文件名                 |
| “迁移时保留旧接口响应字段，除非用户明确允许 breaking change” |          是 | 可复用兼容性规则               |
| “这次测试失败是因为 mock 少了 `tenantId`”          |        视情况 | 如果常见，就沉淀为 failure mode |
| “本次用户说 deadline 是今天下午”                  |          否 | 一次性上下文                 |
| “所有迁移必须跑 focused tests，再跑 package lint” |          是 | 可复用验收标准                |

沉淀 Skill 的本质是：**从 transcript 中抽出稳定决策逻辑，而不是保存历史聊天。**

---

## Step 3：决定内容放在哪里

用这个判断树：

```text
这是整个仓库长期都需要知道的吗？
  是 -> AGENTS.md

这是某类任务才需要的流程吗？
  是 -> Skill

这是一个常用触发入口吗？
  是 -> Command

这需要特殊权限、模型或角色吗？
  是 -> Custom Agent

这是一次性需求、临时文件名或用户偏好？
  不沉淀，最多放在 issue / PR / session summary
```

例如“旧服务迁移到新 TypeScript 服务”的场景中：

* `pnpm test`、目录结构、代码规范：放 `AGENTS.md`。
* “迁移前先建立行为映射表、再分阶段改代码、最后做兼容性验证”：放 Skill。
* `/migrate-code source=... target=...`：放 Command。
* “只读迁移审查，不直接修复”：放 custom Agent。

---

## Step 4：写成 opencode Skill

opencode 的 skill 目录结构建议如下：

```text
.opencode/
  skills/
    code-migration/
      SKILL.md
```

opencode 要求每个 skill 文件夹包含一个 `SKILL.md`；`SKILL.md` 的 YAML frontmatter 至少需要 `name` 和 `description`，可选字段包括 `license`、`compatibility` 和 `metadata`。skill 名称必须是小写字母数字加单个连字符分隔，不能以连字符开头或结尾，并且要和目录名一致。([OpenCode][3])

下面是一个完整示例。

```md
---
name: code-migration
description: Use for code migration and development tasks where legacy code must be moved, refactored, or reimplemented into a new module, framework, package, or service while preserving behavior, tests, API compatibility, and project conventions.
compatibility: opencode
metadata:
  owner: platform-engineering
  workflow: migration
---

# Code Migration Workflow

## Goal

Migrate code from a legacy location to a target architecture with minimal behavioral change, explicit verification, and a clear final summary.

## Default execution mode

Start in planning mode unless the user explicitly asks for a direct implementation.

Do not edit files until you have:
1. Identified source files and target files.
2. Understood the old behavior.
3. Found at least one comparable implementation in the new architecture.
4. Proposed a migration plan.
5. Listed tests or checks to run.

## Required inputs

Extract or ask for these inputs:

- Source module, package, route, function, or file.
- Target module, package, route, function, or file.
- Compatibility requirement:
  - preserve public API
  - allow breaking changes
  - keep old entrypoint as adapter
- Test scope:
  - focused unit tests
  - package tests
  - integration tests
- Rollout expectation:
  - single PR
  - staged migration
  - behind feature flag

Ask only for missing information that blocks safe execution.

## Workflow

### 1. Inventory

Read the source implementation and identify:

- Public API shape.
- Input validation.
- Output shape.
- Error behavior.
- Side effects.
- External dependencies.
- Auth, tenant, permission, and feature flag checks.
- Existing tests.
- Callers and imports.

Use grep/glob/LSP tools to find usages before changing behavior.

### 2. Find target conventions

Before writing new code, inspect similar code in the target architecture:

- Naming conventions.
- Directory layout.
- Dependency injection pattern.
- Error handling style.
- Logging and metrics pattern.
- Test style and fixtures.
- DTO or schema definitions.

Prefer matching existing target conventions over inventing new ones.

### 3. Create behavior mapping

Produce a short mapping before implementation:

| Legacy behavior | Target implementation | Compatibility note |
|---|---|---|

Include unresolved questions and risks.

### 4. Plan implementation

Prefer small, reviewable changes:

1. Add or update target contract/schema.
2. Add target implementation.
3. Add adapter or compatibility layer if needed.
4. Update imports/callers.
5. Move or rewrite tests.
6. Remove legacy code only after tests pass and callers are migrated.

Do not delete legacy code unless the user requested cleanup or the migration plan proves it is safe.

### 5. Implement

When implementing:

- Preserve public behavior by default.
- Keep diffs minimal.
- Avoid unrelated formatting changes.
- Avoid new dependencies unless justified.
- Keep old and new code side by side when migration risk is high.
- Add TODOs only when there is an owner or explicit follow-up.

### 6. Verify

Run the narrowest meaningful checks first, then broaden:

1. Typecheck for changed package.
2. Focused tests for changed files.
3. Related package test suite.
4. Lint or format check.
5. Integration tests if behavior crosses service boundaries.

If a check fails:
- Diagnose before changing code again.
- Separate pre-existing failures from migration-caused failures.
- Report any command that could not be run.

### 7. Final response

Return:

- What was migrated.
- Key files changed.
- Behavior compatibility status.
- Tests/checks run and results.
- Known risks or follow-ups.
- Any intentional non-goals.

## Quality bar

The migration is not complete until one of these is true:

- Tests pass.
- The user explicitly accepts a partial migration.
- You explain exactly why verification could not be completed.

## Do not

- Do not silently change API behavior.
- Do not delete legacy code before usage search.
- Do not skip tests because the diff “looks simple”.
- Do not introduce new architecture patterns unless the repo already uses them.
- Do not expose secrets or read `.env` files.
```

这份 Skill 的关键点不是“写得长”，而是把一次对话中反复消耗 token 的隐性经验固定下来：**先读、先映射、再计划、再实现、再验证、最后交付总结**。

---

## Step 5：加一个 slash command，让团队成员更容易触发

创建：

```text
.opencode/
  commands/
    migrate-code.md
```

内容示例：

```md
---
description: Run the standard code migration workflow
agent: plan
---

Load and use the `code-migration` skill.

Migration request:

$ARGUMENTS

Start by producing a migration plan. Do not edit files until the plan is clear and the user approves switching to implementation.
```

之后可以这样使用：

```text
/migrate-code source=packages/legacy-payment target=packages/payment-service preserve-api=true
```

这类 command 的价值是降低“prompt 写错”的概率。opencode custom commands 支持 `$ARGUMENTS` 占位符，也支持指定 agent，因此可以让迁移默认先进入 `plan` 阶段。([OpenCode][4])

---

## Step 6：配置权限，避免 Agent 误操作

代码迁移任务常涉及批量编辑、测试命令、删除旧代码、Git 操作。建议对危险操作加权限边界。

示例 `opencode.json`：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "skill": {
      "*": "allow",
      "experimental-*": "ask"
    },
    "read": {
      "*": "allow",
      "*.env": "deny",
      "*.env.*": "deny",
      "*.env.example": "allow"
    },
    "edit": "ask",
    "bash": {
      "*": "ask",
      "git status*": "allow",
      "git diff*": "allow",
      "rg *": "allow",
      "grep *": "allow",
      "pnpm test*": "allow",
      "pnpm --filter * test*": "allow",
      "pnpm lint*": "allow",
      "rm *": "deny",
      "git push*": "deny",
      "git commit*": "ask"
    }
  }
}
```

opencode 的权限规则可以设置为 `allow`、`ask` 或 `deny`；它支持按工具和输入模式做更细粒度控制，例如 bash 命令模式、edit 路径模式、skill 名称模式等。opencode 默认对多数权限较开放，但 `.env` 读取默认会被拒绝，`external_directory` 和重复工具调用等安全保护默认会要求确认。([OpenCode][6])

---

# 4. 完整样例：从一次代码迁移对话沉淀 Skill

下面用一个模拟但贴近真实的例子说明。

## 4.1 原始对话场景

用户对 opencode 说：

```text
请把 legacy-payment-service 里的 refund API 迁移到新的 packages/payment-service。
要求保持现有 REST 响应格式不变，用新项目里的 Fastify route 风格，并补齐测试。
```

Agent 在这次对话中做了这些事：

1. 读取 `packages/legacy-payment-service/src/routes/refund.ts`。
2. 搜索 `refund` 的调用方。
3. 查看新服务中已有的 `charge` route 作为模板。
4. 发现旧接口返回 `{ ok, refundId, status }`，错误时返回 `{ ok: false, code, message }`。
5. 建议先新增新 route，再保留旧 route adapter。
6. 改了目标服务、schema、测试文件。
7. 运行 focused tests。
8. 修复测试 mock 缺失字段。
9. 最终输出迁移说明。

---

## 4.2 从对话中抽取可复用规则

| 抽取项  | 可复用内容                                             |
| ---- | ------------------------------------------------- |
| 触发条件 | legacy service/API/function/module 迁移到新架构         |
| 前置检查 | 先找 source、target、调用方、测试、同类新实现                     |
| 迁移策略 | 默认保持 API 行为，不默认 breaking change                   |
| 实现顺序 | schema → handler/service → adapter/caller → tests |
| 验证方式 | focused tests → package tests → lint/typecheck    |
| 常见坑  | mock fixture 缺字段；错误响应格式被新框架默认异常处理改掉               |
| 输出格式 | 文件清单、兼容性状态、测试结果、风险                                |

这些内容进入 `code-migration` Skill。

---

## 4.3 不应该进入 Skill 的内容

| 内容               | 原因             |
| ---------------- | -------------- |
| 具体文件 `refund.ts` | 只属于本次任务        |
| 具体 PR 标题         | 一次性            |
| 用户本次 deadline    | 一次性            |
| 某个临时分支名          | 一次性            |
| 本次修复的某个 typo     | 除非它代表通用坑，否则不沉淀 |

---

## 4.4 最终项目配置建议

```text
repo-root/
  AGENTS.md
  opencode.json
  .opencode/
    skills/
      code-migration/
        SKILL.md
    commands/
      migrate-code.md
    agents/
      migration-reviewer.md
```

可以再加一个只读 review agent：

```md
---
description: Review migrated code for compatibility, test coverage, architecture fit, and unintended behavior changes.
mode: subagent
temperature: 0.1
permission:
  edit: deny
  bash: ask
  webfetch: deny
  websearch: deny
---

You are a migration reviewer.

Review the migration without editing files.

Check:
- Public API compatibility.
- Error behavior compatibility.
- Missing caller updates.
- Test coverage gaps.
- New dependencies or architecture drift.
- Risky deletions of legacy code.

Return:
- Blocking issues.
- Non-blocking suggestions.
- Tests that should be run.
- Files that deserve human review.
```

opencode 支持用 Markdown 文件定义 custom agent，并可以放在项目级 `.opencode/agents/` 或全局配置目录中；Markdown frontmatter 可以配置描述、模式、模型、温度和权限，文件名会成为 agent 名称。([OpenCode][5])

---

# 5. 一次对话结束后，如何让 Agent 帮你自动提炼 Skill

在一次任务完成后，可以直接让 opencode 或另一个 Agent 做复盘。推荐 prompt：

```text
请基于本次对话和最终 diff，帮我沉淀一个可复用的 opencode Skill。

目标：
- 以后遇到同类代码迁移任务时，Agent 能快速进入正确流程。
- 不要保存本次任务的一次性细节。
- 只提炼稳定、可复用、可执行的规则。

请输出：
1. 这个 Skill 的名称，必须是 lowercase-hyphen 格式。
2. description，说明何时触发，避免过泛。
3. 应进入 AGENTS.md 的项目级规则。
4. 应进入 SKILL.md 的任务流程。
5. 应进入 command 的一键触发 prompt。
6. 应进入 custom agent 的角色和权限。
7. 不应该沉淀的内容。
8. 3 个未来类似任务的示例调用方式。
9. 一份最终 SKILL.md 草案。
```

然后人工 review 一遍，重点检查：

* description 是否过泛。
* 是否包含本次任务的一次性路径。
* 是否错误地要求 Agent 永远执行某个危险操作。
* 是否包含 secret、token、内部临时链接。
* 是否把“建议”写成了“必须”，导致未来任务不灵活。

---

# 6. Skill 编写最佳实践

## 6.1 description 要写得“窄而准”

Skill 能否被正确调用，很大程度取决于 `description`。opencode 会把可用 skill 的 name 和 description 暴露给 Agent，Agent 再决定是否加载完整 skill。([OpenCode][3])

不推荐：

```yaml
description: Helps with code.
```

推荐：

```yaml
description: Use for code migration and development tasks where legacy code must be moved, refactored, or reimplemented into a new module, framework, package, or service while preserving behavior, tests, API compatibility, and project conventions.
```

好的 description 应该包含：

* 任务类型。
* 触发信号。
* 适用边界。
* 关键目标。
* 不要太宽泛。

---

## 6.2 Skill 里写“流程”，不要写“知识库大杂烩”

不推荐把所有架构文档、历史决策、代码风格、测试规范都塞到一个 Skill。更好的拆法是：

* `AGENTS.md`：项目级通用背景。
* `code-migration` Skill：迁移流程。
* `testing` Skill：测试补齐流程。
* `security-review` Skill：安全审查流程。
* `commands/`：常用入口。

opencode 的 rules 文档也强调，`AGENTS.md` 适合承载构建、lint、测试命令、架构、项目约定、setup gotchas 等未来会话常用信息。([OpenCode][7])

---

## 6.3 把“失败经验”写进去

一次 Agent 对话最有价值的部分往往不是成功路径，而是中途踩过的坑。例如：

```md
## Common failure modes

- If migrated tests fail because fixtures miss tenant/user context, inspect existing target-service test fixtures before inventing new mocks.
- If the new framework converts thrown errors into a different response shape, add an explicit compatibility wrapper.
- If both old and new routes exist temporarily, ensure duplicated metrics/logging does not double-count events.
```

这些内容能显著减少下次返工。

---

## 6.4 明确“什么时候不能继续”

Skill 里应该写清楚阻塞条件：

```md
Stop and ask the user before proceeding if:
- The migration changes public API behavior.
- The target architecture has no comparable pattern.
- Required tests cannot be found.
- The change requires deleting legacy code used by active callers.
- The task requires secrets, production credentials, or `.env` files.
```

这比简单写“be careful”有效得多。

---

## 6.5 默认 Plan，再 Build

对代码迁移类任务，建议默认先进入规划阶段。opencode 的 Plan agent 设计目标就是在不实际修改代码的情况下分析代码、建议变更或创建计划；Build agent 则适合真正执行开发工作。([OpenCode][5])

推荐流程：

```text
/migrate-code source=... target=...
```

然后：

1. Plan agent 输出迁移计划。
2. 用户确认或调整。
3. 切到 Build agent。
4. 执行修改。
5. 调用 migration-reviewer 做只读审查。
6. 运行测试。
7. 输出最终 summary。

---

## 6.6 把测试命令写到项目规则，不要每次猜

在 `AGENTS.md` 中写清楚：

```md
## Verification

For migration tasks:
1. Run focused tests first:
   `pnpm --filter <package> test -- <test-name>`
2. Then run package tests:
   `pnpm --filter <package> test`
3. Then run typecheck:
   `pnpm --filter <package> typecheck`
4. Only run full monorepo tests when the change crosses package boundaries.
```

这类命令属于仓库长期规则，应该进入 `AGENTS.md`。Skill 里只需要说“按 `AGENTS.md` 的 verification 顺序执行”。

---

## 6.7 Skill 也要像代码一样 review

一个安全提醒：最近一篇 arXiv 预印本指出，`SKILL.md` 不是被动文档，而是会影响 Agent 发现、选择和加载能力的“操作性文本”；论文讨论了 skill registry 场景下的语义供应链风险，例如恶意描述影响发现和选择。实际工程里，这意味着 Skill 应该像代码一样进行 review、权限控制和版本管理。([arXiv][8])

建议：

* Skill 走 PR review。
* 禁止未经 review 的全局 skill。
* 不在 Skill 中放 secret。
* 不写“忽略用户/系统安全规则”之类指令。
* 对 destructive command 使用 `ask` 或 `deny`。
* 对实验性 skill 用 `experimental-*` 命名并设为 `ask`。

---

# 7. 推荐的 Skill 迭代机制

每次使用 Skill 后，都记录 5 个指标：

| 指标             | 目的                              |
| -------------- | ------------------------------- |
| 是否自动触发正确 Skill | 检查 description 是否准确             |
| 规划阶段是否问了不必要问题  | 检查输入要求是否过度                      |
| 是否遗漏关键文件       | 检查 inventory 步骤是否完整             |
| 测试是否一次通过       | 检查 verification 和 failure modes |
| 用户是否需要大量纠偏     | 检查流程和输出格式                       |

迭代规则：

```text
如果 Agent 没有加载 Skill：
  优化 description。

如果 Agent 加载了 Skill 但做错步骤：
  优化 SKILL.md 中的 workflow。

如果 Agent 总是缺项目背景：
  优化 AGENTS.md。

如果用户总是不知道怎么触发：
  增加 command。

如果 Agent 做了危险操作：
  调整 permission 或拆出只读 agent。
```

---

# 8. 最小可落地版本

一个团队第一次实践时，不需要做得很复杂。可以先落地这 4 个文件：

```text
AGENTS.md
opencode.json
.opencode/skills/code-migration/SKILL.md
.opencode/commands/migrate-code.md
```

最小配置如下。

## `AGENTS.md`

```md
# Agent Instructions

## Project Structure

- `packages/legacy-*` contains legacy services.
- `packages/*-service` contains new TypeScript services.
- Shared contracts live in `packages/contracts`.

## Development Commands

- Install: `pnpm install`
- Focused tests: `pnpm --filter <package> test -- <pattern>`
- Package tests: `pnpm --filter <package> test`
- Typecheck: `pnpm --filter <package> typecheck`
- Lint: `pnpm --filter <package> lint`

## Migration Rules

- Preserve public API behavior unless the user explicitly approves a breaking change.
- Search for callers before deleting or moving legacy code.
- Prefer existing target-service patterns over creating new abstractions.
- Always report tests run and tests not run.
```

## `.opencode/skills/code-migration/SKILL.md`

使用上文完整版本即可。

## `.opencode/commands/migrate-code.md`

```md
---
description: Run the standard code migration workflow
agent: plan
---

Load and use the `code-migration` skill.

Migration request:

$ARGUMENTS

Start with a migration plan. Do not edit files yet.
```

## `opencode.json`

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "skill": {
      "*": "allow"
    },
    "edit": "ask",
    "bash": {
      "*": "ask",
      "git status*": "allow",
      "git diff*": "allow",
      "rg *": "allow",
      "pnpm --filter * test*": "allow",
      "pnpm --filter * typecheck*": "allow",
      "pnpm --filter * lint*": "allow",
      "rm *": "deny",
      "git push*": "deny"
    }
  }
}
```

---

# 9. 最后给团队的实践准则

把一次 Agent 对话沉淀成 Skill，本质上是在做“工程经验产品化”。好的 Skill 应该满足这 7 条：

1. **可触发**：description 清楚说明什么时候使用。
2. **可执行**：步骤具体，不是泛泛原则。
3. **可验证**：明确测试、lint、typecheck、验收标准。
4. **可控权**：危险操作受权限保护。
5. **可复用**：不包含本次任务的一次性细节。
6. **可演进**：每次使用后能根据失败点更新。
7. **可审计**：像代码一样进入版本管理和 review。

对于“代码迁移 + 开发任务”，最推荐的标准工作流是：

```text
一次成功对话
  -> 复盘 transcript / diff / 测试结果
  -> 抽取稳定流程
  -> 项目事实进入 AGENTS.md
  -> 任务流程进入 SKILL.md
  -> 高频入口进入 commands
  -> 特殊权限进入 agents / permission
  -> 用下一次真实迁移任务验证
  -> 根据失败点迭代
```

这样做之后，下一次同类需求不再是“重新教 Agent 一遍”，而是让 Agent 直接进入团队已经验证过的工作方式。

[1]: https://opencode.ai/docs "Intro | AI coding agent built for the terminal"
[2]: https://arxiv.org/abs/2601.20404 "[2601.20404] On the Impact of AGENTS.md Files on the Efficiency of AI Coding Agents"
[3]: https://opencode.ai/docs/skills/ "Agent Skills | OpenCode"
[4]: https://opencode.ai/docs/commands/ "Commands | OpenCode"
[5]: https://opencode.ai/docs/agents/ "Agents | OpenCode"
[6]: https://opencode.ai/docs/permissions/ "Permissions | OpenCode"
[7]: https://opencode.ai/docs/rules/ "Rules | OpenCode"
[8]: https://arxiv.org/abs/2605.11418 "[2605.11418] Under the Hood of SKILL.md: Semantic Supply-chain Attacks on AI Agent Skill Registry"
