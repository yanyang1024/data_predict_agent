# 05 - AGENTS.md：项目级 Agent 规则模板

> **适用版本**：OpenCode v1.14.32+、v1.15.13+
>
> **目标读者**：希望在团队或项目中规范 OpenCode Agent 行为的软件研发人员

---

## 目录

- [什么是 AGENTS.md](#什么是-agentsmd)
- [加载机制：全局配置与项目级配置](#加载机制全局配置与项目级配置)
- [v1.15.13 的改进](#v11513-的改进)
- [AGENTS.md 完整模板](#agentsmd-完整模板)
- [技术栈模板变体](#技术栈模板变体)
  - [Node.js / TypeScript 模板](#nodejs--typescript-模板)
  - [Python 模板](#python-模板)
  - [Go 模板](#go-模板)
- [通过 `instructions` 字段引用多个指令文件](#通过-instructions-字段引用多个指令文件)
- [最佳实践与注意事项](#最佳实践与注意事项)

---

## 什么是 AGENTS.md

`AGENTS.md` 是 OpenCode 支持的一种特殊配置文件，用于定义**项目级 Agent 行为规则**。当 OpenCode Agent 在项目中工作时，它会自动读取该文件中的指令，从而：

- 理解项目结构和上下文
- 遵循团队约定的工作流
- 执行正确的命令（测试、lint、类型检查等）
- 遵守安全和代码治理规则

你可以将 `AGENTS.md` 视为项目的"AI 协作契约"——它告诉 Agent 如何正确地与你的代码库交互。

---

## 加载机制：全局配置与项目级配置

OpenCode 支持**两级** `AGENTS.md` 配置，它们会**同时生效**（叠加而非覆盖）：

### 1. 全局 AGENTS.md（Global）

全局配置作用于所有项目，适用于个人开发习惯或组织级统一规范。

**配置位置**：

```
~/.config/opencode/AGENTS.md
```

**适用场景**：
- 个人偏好的编辑器设置
- 组织统一的 Git 工作流规范
- 通用的安全规则（如禁止 `rm -rf`）
- 跨项目一致的行为约束

### 2. 项目级 AGENTS.md（Project-level）

项目配置放置在代码库根目录，随代码一起版本控制，确保团队成员使用一致的 Agent 规则。

**配置位置**：

```
<project-root>/AGENTS.md
```

**适用场景**：
- 项目特定的技术栈说明
- 项目目录结构和工作流
- 项目专用的命令（如 `pnpm test`）
- 项目特定的安全约束

### 叠加规则

两级配置**都会生效**，内容会合并叠加。如果存在冲突，通常**项目级配置优先**。

```
最终生效的 Agent 规则 = 全局 AGENTS.md + 项目级 AGENTS.md
```

这意味着你可以：
- 在全局定义通用的安全规则
- 在项目级专注于技术栈和工作流
- 避免在每个项目重复相同的通用规则

---

## v1.15.13 的改进

从 **OpenCode v1.15.13** 开始，配置加载机制有了重要改进：

### 向上加载（Directory Traversal）

v1.15.13 引入了从**打开位置向上遍历加载**的机制。具体行为如下：

1. 当你打开一个文件或目录时，OpenCode 会从该位置开始**向上遍历父目录**
2. 沿途遇到的 `AGENTS.md` 文件都会被加载
3. 这使得**目录特定的设置**更加可预测

**示例场景**：

```
my-project/
├── AGENTS.md          ← 项目级规则（通用）
├── apps/
│   ├── web/
│   │   └── AGENTS.md  ← Web 应用特定规则
│   └── api/
│       └── AGENTS.md  ← API 服务特定规则
├── packages/
│   ├── ui/
│   │   └── AGENTS.md  ← UI 包特定规则
│   └── utils/
└── tools/
    └── AGENTS.md      ← 工具脚本特定规则
```

当你编辑 `apps/web/` 下的文件时：
- 先加载 `my-project/AGENTS.md`
- 再加载 `my-project/apps/web/AGENTS.md`
- 两者合并生效

**好处**：
- Monorepo 中不同子项目可以有自己的规则
- 共享库和应用的 Agent 行为可以差异化
- 更细粒度的控制，同时保持通用规则复用

---

## AGENTS.md 完整模板

以下是一个通用的 `AGENTS.md` 模板，保留了所有原文档的核心要点，你可以直接复制使用并替换 `<...>` 中的内容。

```markdown
# Project Agent Rules

## Project overview
- This is a <language/framework> project.
- Package manager: <npm/yarn/pnpm/pip/go modules>.
- Main app: `<path-to-main-app>`.
- Shared libraries: `<path-to-shared-libs>`.

## Required workflow
1. For non-trivial tasks, start in Plan mode.
2. Before editing, list files you plan to modify and why.
3. Prefer minimal patches. Do not rewrite large files unless explicitly asked.
4. After editing, run the smallest relevant test first.
5. Always summarize changed files, tests run, and remaining risks.

## Commands
- Install: `<install-command>`
- Test: `<test-command>`
- Typecheck: `<typecheck-command>`
- Lint: `<lint-command>`

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

### 模板字段说明

| 字段 | 说明 | 示例 |
|------|------|------|
| `<language/framework>` | 项目使用的主要语言和框架 | TypeScript / React |
| `<npm/yarn/pnpm/...>` | 包管理工具 | pnpm |
| `<path-to-main-app>` | 主应用目录 | `apps/web` |
| `<path-to-shared-libs>` | 共享库目录 | `packages/*` |
| `<install-command>` | 依赖安装命令 | `pnpm install` |
| `<test-command>` | 测试命令 | `pnpm test` |
| `<typecheck-command>` | 类型检查命令 | `pnpm typecheck` |
| `<lint-command>` | 代码检查命令 | `pnpm lint` |

---

## 技术栈模板变体

以下提供三种常见技术栈的完整模板，可直接复制使用。

### Node.js / TypeScript 模板

适用于基于 pnpm/npm/yarn 的 Node.js 项目，特别是 monorepo 架构。

```markdown
# Project Agent Rules

## Project overview
- This is a TypeScript / React project.
- Package manager: pnpm.
- Main app: `apps/web`.
- Shared libraries: `packages/*`.
- Uses TurboRepo for task orchestration.

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
- Build: `pnpm build`
- Dev (only when explicitly asked): `pnpm dev`

## Safety rules
- Do not run `git push`.
- Do not run `git reset --hard` or `git clean -fd`.
- Do not run `rm -rf`.
- Do not run broad process-kill commands such as `pkill -f`, `killall`, or `taskkill /IM node.exe`.
- Do not start long-running dev servers inside the agent unless explicitly approved.
- If a command may affect running processes, ask first and explain the exact PID / port / process name.
- Do not modify `pnpm-lock.yaml` directly; let pnpm manage it.

## Git workflow
- Human owns commits.
- Agent may inspect `git status`, `git diff`, and `git log`.
- Agent must not commit unless explicitly asked.
- Use `.gitignore` patterns for build outputs: `dist/`, `node_modules/`, `.turbo/`.

## Testing policy
- Add or update regression tests when fixing bugs.
- If tests cannot be run, explain why and give the exact command for humans to run.
- Prefer unit tests in `__tests__/` or `*.test.ts` co-located with source.
- Run `pnpm test -- <pattern>` to target specific tests.

## Code style
- Use TypeScript strict mode.
- Prefer `async/await` over raw Promises.
- Use named exports over default exports.
- Follow the existing code formatting (Prettier config in repo root).
```

### Python 模板

适用于 Python 项目，使用 uv/poetry/pip 作为包管理工具。

```markdown
# Project Agent Rules

## Project overview
- This is a Python project.
- Package manager: uv (preferred) / poetry / pip.
- Python version: 3.11+.
- Main application: `src/myapp/`.
- Entry point: `src/myapp/main.py`.

## Required workflow
1. For non-trivial tasks, start in Plan mode.
2. Before editing, list files you plan to modify and why.
3. Prefer minimal patches. Do not rewrite large files unless explicitly asked.
4. After editing, run the smallest relevant test first.
5. Always summarize changed files, tests run, and remaining risks.

## Commands
- Install: `uv sync` or `poetry install`
- Test: `uv run pytest` or `poetry run pytest`
- Typecheck: `uv run mypy src/` or `poetry run mypy src/`
- Lint: `uv run ruff check .` or `poetry run ruff check .`
- Format: `uv run ruff format .` or `poetry run ruff format .`

## Safety rules
- Do not run `git push`.
- Do not run `git reset --hard` or `git clean -fd`.
- Do not run `rm -rf`.
- Do not run broad process-kill commands such as `pkill -f`, `killall`, or `taskkill /IM node.exe`.
- Do not start long-running dev servers inside the agent unless explicitly approved.
- If a command may affect running processes, ask first and explain the exact PID / port / process name.
- Never modify `uv.lock` or `poetry.lock` directly.

## Git workflow
- Human owns commits.
- Agent may inspect `git status`, `git diff`, and `git log`.
- Agent must not commit unless explicitly asked.
- Use `.gitignore` for `__pycache__/`, `.venv/`, `*.pyc`, `.mypy_cache/`.

## Testing policy
- Add or update regression tests when fixing bugs.
- If tests cannot be run, explain why and give the exact command for humans to run.
- Use pytest as the test runner.
- Tests located in `tests/` directory mirroring `src/` structure.
- Run `pytest -xvs tests/path/to/test_file.py::test_function` for targeted tests.

## Code style
- Follow PEP 8.
- Use type hints for all function signatures.
- Use `ruff` for linting and formatting.
- Use `mypy` for static type checking (strict mode).
- Prefer `pathlib.Path` over `os.path`.
- Use f-strings for string formatting.
```

### Go 模板

适用于 Go 项目，使用 Go Modules 作为依赖管理工具。

```markdown
# Project Agent Rules

## Project overview
- This is a Go project.
- Go version: 1.22+.
- Module path: `github.com/org/project`.
- Main application: `cmd/server/`.
- Shared packages: `pkg/` and `internal/`.

## Required workflow
1. For non-trivial tasks, start in Plan mode.
2. Before editing, list files you plan to modify and why.
3. Prefer minimal patches. Do not rewrite large files unless explicitly asked.
4. After editing, run the smallest relevant test first.
5. Always summarize changed files, tests run, and remaining risks.

## Commands
- Install: `go mod download`
- Test: `go test ./...`
- Typecheck: `go vet ./...`
- Lint: `golangci-lint run`
- Build: `go build ./cmd/server`
- Tidy: `go mod tidy`

## Safety rules
- Do not run `git push`.
- Do not run `git reset --hard` or `git clean -fd`.
- Do not run `rm -rf`.
- Do not run broad process-kill commands such as `pkill -f`, `killall`, or `taskkill /IM node.exe`.
- Do not start long-running dev servers inside the agent unless explicitly approved.
- If a command may affect running processes, ask first and explain the exact PID / port / process name.
- Do not modify `go.mod` and `go.sum` directly; use `go mod tidy`.

## Git workflow
- Human owns commits.
- Agent may inspect `git status`, `git diff`, and `git log`.
- Agent must not commit unless explicitly asked.
- Use `.gitignore` for `bin/`, `vendor/` (if not vendoring), `*.test`.

## Testing policy
- Add or update regression tests when fixing bugs.
- If tests cannot be run, explain why and give the exact command for humans to run.
- Use standard Go testing: `go test ./...`.
- Table-driven tests are preferred.
- Run `go test -run TestFunctionName ./package` for targeted tests.
- Aim for test coverage of critical paths.

## Code style
- Follow standard Go conventions (`gofmt`, `go vet`).
- Use `golangci-lint` for comprehensive linting.
- Keep functions small and focused.
- Handle all errors explicitly; do not ignore return values.
- Use `context.Context` for cancellation and timeouts.
- Prefer composition over inheritance.
```

---

## 通过 `instructions` 字段引用多个指令文件

除了 `AGENTS.md`，OpenCode 还支持在 `opencode.json` 配置中通过 `instructions` 字段**引用多个指令文件**。这为更复杂的项目结构提供了灵活性。

### 基本用法

在 `opencode.json` 中添加 `instructions` 字段：

```json
{
  "instructions": [
    "./docs/agent-rules/common.md",
    "./docs/agent-rules/backend.md",
    "./docs/agent-rules/security.md"
  ]
}
```

### 加载优先级

指令文件按数组顺序加载，后加载的内容可以补充或覆盖前面的内容：

```
最终规则 = 全局 AGENTS.md + opencode.json instructions（按顺序） + 项目级 AGENTS.md
```

### 使用场景

**场景 1：按关注点分离规则**

```
project/
├── opencode.json
├── docs/
│   └── agent-rules/
│       ├── 00-common.md      # 通用行为规则
│       ├── 01-testing.md     # 测试策略
│       ├── 02-security.md    # 安全规则
│       └── 03-api.md         # API 开发规范
```

```json
{
  "instructions": [
    "./docs/agent-rules/00-common.md",
    "./docs/agent-rules/01-testing.md",
    "./docs/agent-rules/02-security.md",
    "./docs/agent-rules/03-api.md"
  ]
}
```

**场景 2：团队协作时按角色分配**

```json
{
  "instructions": [
    "./docs/agent-rules/team-common.md",
    "./docs/agent-rules/frontend-team.md"
  ]
}
```

**场景 3：渐进式规则启用**

在项目的不同阶段启用不同的规则集：

```json
{
  "instructions": [
    "./docs/agent-rules/base.md",
    "./docs/agent-rules/production-readiness.md"
  ]
}
```

### 注意事项

- `instructions` 中的路径**相对于 `opencode.json` 所在目录**
- 支持 `.md` 文件
- 如果文件不存在，OpenCode 会静默忽略（建议确认路径正确）
- `AGENTS.md` 和 `instructions` 可以同时存在，内容会合并

---

## 最佳实践与注意事项

### 1. 保持精简

`AGENTS.md` 应该只包含 Agent 需要知道的**行为规则**，不需要复制完整的编码规范文档。推荐长度在 50-100 行以内。

### 2. 与代码一起版本控制

项目级 `AGENTS.md` 应该提交到 Git 仓库，这样所有团队成员共享相同的 Agent 行为：

```bash
git add AGENTS.md
git commit -m "chore: add Agent behavior rules for OpenCode"
```

### 3. 分层配置策略

```
全局 AGENTS.md          → 个人习惯 + 通用安全规则
    ↓
opencode.json           → 项目结构说明
  instructions          → 细分规则文件
    ↓
项目级 AGENTS.md        → 核心工作流 + 项目命令
    ↓
子目录 AGENTS.md        → 子项目特定规则 (v1.15.13+)
```

### 4. 定期审查

随着项目演进，`AGENTS.md` 也需要更新：
- 新增脚本命令时同步更新 Commands 部分
- 工作流变更时更新 Required workflow
- 每季度审查一次是否仍然准确

### 5. 避免敏感信息

不要在 `AGENTS.md` 中放置：
- API 密钥或密码
- 个人访问令牌
- 内部网络地址
- 任何机密信息

### 6. 测试你的配置

编写完 `AGENTS.md` 后，可以通过以下方式验证：

1. 在 OpenCode 中打开项目
2. 让 Agent 执行一个简单的任务
3. 观察 Agent 是否遵循了 `AGENTS.md` 中的规则
4. 检查 Agent 是否使用了正确的命令

---

## 总结

`AGENTS.md` 是 OpenCode 中规范 Agent 行为的核心机制：

| 特性 | 说明 |
|------|------|
| **全局配置** | `~/.config/opencode/AGENTS.md`，作用于所有项目 |
| **项目配置** | `<project-root>/AGENTS.md`，随代码版本控制 |
| **子目录配置** | v1.15.13+ 支持从打开位置向上遍历加载 |
| **叠加机制** | 多级配置同时生效，项目级优先 |
| **扩展机制** | `instructions` 字段支持引用多个规则文件 |

通过合理配置 `AGENTS.md`，你可以让 OpenCode Agent 成为团队中一致、可预测、安全的协作者。
