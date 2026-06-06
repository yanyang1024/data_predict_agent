# 面向研发人员的 OpenCode 使用 SOP

> **适用版本**: OpenCode v1.14.32 / v1.15.13  
> **目标读者**: 有编码经验的软件研发人员  
> **前置条件**: 已完成 OpenCode 安装与基础配置（参见 01-installation.md 和 02-configuration.md）

---

## 概述

本章节提供一套经过实践验证的标准操作流程（SOP），帮助研发人员在使用 OpenCode 进行日常编码辅助时，建立安全、可控、可回溯的工作范式。整个流程分为 6 个 Phase，从进入工作前的安全边界建立，到最终的人工 review 与 checkpoint，形成完整的闭环。

**为什么需要这套 SOP？**

OpenCode 作为 AI 编程助手，拥有读取和修改代码的能力。虽然 `/undo` 提供了回滚机制，但它不应被视为唯一的回滚手段。在团队协作环境中，无约束的 AI 操作可能导致：

- 主分支代码被意外修改
- 敏感文件被误删或泄露
- 测试未通过即提交的代码进入版本控制
- 不同开发者的 AI 配置互相干扰

本 SOP 通过**分支隔离、计划先行、最小修改、独立验证、人工把关**五大原则，确保 AI 辅助编码的安全性和可预测性。

---

## Phase 0：进入工作前先建安全边界

在任何 AI 辅助编码之前，必须先建立清晰的安全边界。这是整个 SOP 中最重要的一步——安全边界不是可选项，而是必选项。

### 0.1 检查当前工作区状态

```bash
# 查看当前 Git 状态，确认没有未提交的修改
git status --short
```

**要求**：输出必须为空（`--short` 无输出），或仅有已明确理解的变更。如果存在未提交的修改，先决定是提交、stash 还是丢弃。

### 0.2 创建任务专属分支

```bash
# 为每个独立任务创建一个独立分支
git switch -c ai/<ticket-or-task>

# 示例
git switch -c ai/fix-login-bug-127
git switch -c ai/refactor-user-service
git switch -c ai/add-oauth-integration
```

**分支命名规范**:

| 前缀 | 用途 |
|------|------|
| `ai/fix-` | Bug 修复 |
| `ai/refactor-` | 代码重构 |
| `ai/feature-` | 新功能开发 |
| `ai/docs-` | 文档更新 |
| `ai/test-` | 测试相关 |

### 0.3 安全红线（不可违背）

以下规则必须严格遵守，没有例外：

| # | 规则 | 违反后果 |
|---|------|---------|
| 1 | **每个独立任务一个分支** | 防止不同任务的修改互相污染 |
| 2 | **不在主分支让 agent 改代码** | 主分支是团队协作的基准线，AI 不应直接触碰 |
| 3 | **不把 `/undo` 当唯一回滚机制** | `/undo` 只撤销 OpenCode 内部的最后一步，不覆盖所有场景 |
| 4 | **禁止 agent 自动 `git push`** | AI 不应将代码推送到远程仓库 |
| 5 | **禁止 agent 自动 `git reset --hard`** | 硬重置会丢失工作成果 |
| 6 | **禁止 agent 自动 `git clean -fd`** | 强制清理会删除未跟踪文件 |
| 7 | **"广义 kill 命令"必须人工确认** | 任何可能导致数据丢失的操作（`rm -rf`、数据库删除等）需要人工二次确认 |

> **v1.15.13 补充**: 新版增强了权限配置规则顺序（Permission Configuration Rule Ordering），`permission` 字段中定义的规则现在按预期顺序评估。建议在项目配置中显式设置权限边界：
>
> ```json
> {
>   "$schema": "https://opencode.ai/config.json",
>   "permission": {
>     "edit": "ask",
>     "bash": {
>       "*": "allow",
>       "rm -rf *": "deny",
>       "sudo *": "ask",
>       "git push*": "ask",
>       "git reset --hard*": "deny"
>     }
>   }
> }
> ```

### 0.4 使用 `--cwd` 参数明确工作目录

v1.15.13 起，`--cwd` 参数可以显式设置工作目录，避免在 monorepo 或多目录环境中出现路径混乱：

```bash
# 显式指定工作目录
opencode --cwd /path/to/project

# 或简写形式
opencode -c ~/my-project
```

这在以下场景中特别有用：

- 从 repo 根目录启动但只修改子包
- 在 CI/CD 环境中需要精确控制工作目录
- 使用 `opencode web` 或 Desktop 模式时避免 `process.cwd()` 不一致问题

---

## Phase 1：初始化项目规则

在开始任何具体编码任务之前，先让 OpenCode 了解你的项目结构和规范。这样可以避免 agent 在后续工作中做出错误的假设。

### 1.1 生成项目规则文件

```bash
# 启动 OpenCode 并执行初始化
opencode

# 在 TUI 中执行
/init
```

`/init` 命令会分析你的项目结构，自动生成一个 `AGENTS.md` 文件，其中包含项目的基本信息和操作指南。

### 1.2 检查并补充 AGENTS.md

`/init` 生成的 `AGENTS.md` 只是一个起点，你需要手动检查并补充以下内容：

| 检查项 | 说明 | 示例 |
|--------|------|------|
| **项目结构** | 主要目录及其用途 | `src/` 源代码, `tests/` 测试, `docs/` 文档 |
| **包管理器** | 使用的包管理工具 | `pnpm`, `npm`, `yarn`, `pip`, `poetry` |
| **测试命令** | 运行测试的方式 | `pnpm test`, `pytest`, `go test ./...` |
| **Lint 命令** | 代码风格检查 | `pnpm lint`, `eslint .`, `golangci-lint run` |
| **Type Check 命令** | 类型检查（如有） | `pnpm typecheck`, `tsc --noEmit`, `mypy` |
| **分支和提交规范** | Git 工作流约定 | Conventional Commits, branch naming |
| **禁止事项** | Agent 不应该做的事 | 不要修改 `.env` 文件, 不要提交未审查的代码 |
| **常见坑点** | 项目特有的注意事项 | 某些文件是自动生成的，不要手动编辑 |
| **关键目录说明** | 特殊目录的含义 | `generated/` 目录内容由脚本生成 |

### 1.3 AGENTS.md 示例

```markdown
# Project Rules

## 项目结构

```
my-project/
├── src/                 # 源代码
│   ├── components/      # React 组件
│   ├── utils/           # 工具函数
│   └── types/           # TypeScript 类型定义
├── tests/               # 测试文件
├── docs/                # 文档
└── scripts/             # 构建和开发脚本
```

## 技术栈

- 前端框架: React 18 + TypeScript
- 样式: Tailwind CSS
- 测试: Vitest + Testing Library
- 包管理器: pnpm

## 命令

```bash
# 安装依赖
pnpm install

# 运行测试
pnpm test

# 类型检查
pnpm typecheck

# 代码检查
pnpm lint

# 构建
pnpm build
```

## Git 规范

- 分支命名: `ai/<ticket-or-task>`
- 提交格式: `<type>: <description>` (feat, fix, refactor, docs, test)
- 不允许直接提交到 main 分支

## 禁止事项

- 不要修改 `.env` 和 `.env.local` 文件
- 不要删除 `generated/` 目录下的文件
- 不要修改 `package.json` 除非明确要求
- 不要执行 `git push` 或 `git reset --hard`

## 常见坑点

- `src/types/generated.ts` 是由 `pnpm generate-types` 自动生成的，不要手动编辑
- 测试文件必须与源码放在同一目录下的 `__tests__` 文件夹中
```

### 1.4 v1.15.13 配置加载改进

v1.15.13 引入了一个重要的配置加载改进：**配置从打开位置向上加载，目录特定设置更可预测**。

这意味着：

- 在 monorepo 中从子包目录启动 OpenCode 时，配置会正确地从该目录开始向上搜索
- `opencode.json` 和 `.opencode/` 目录的解析更加可靠
- 非 Git 项目的配置加载问题已修复（v1.15.9 修复）

**实际影响**: 在 monorepo 结构中，你可以在子包目录直接启动 OpenCode，它会正确地找到该子包及上层的配置，而不会混淆。

```bash
# 在 monorepo 的子包中工作
cd packages/frontend
opencode  # 会自动使用 packages/frontend/opencode.json（如果存在），并向上合并根目录配置
```

---

## Phase 2：先 Plan，不要直接 Build

### 2.1 核心原则：先计划，后执行

OpenCode 有两种主要工作模式：

| 模式 | 用途 | 何时使用 |
|------|------|---------|
| **Plan** | 只分析和计划，不修改任何文件 | 任务开始阶段，需要先理解问题和制定方案 |
| **Build** | 执行实际的代码修改 | 方案已确认，准备实施 |

**永远不要在还没有明确计划的情况下切换到 Build 模式。** 这类似于现实中的工程流程：没有设计图纸就不应该动工。

### 2.2 使用 Plan 模式制定方案

```
# 在 OpenCode TUI 中，明确要求使用 Plan 模式
"请使用 Plan 模式分析这个问题：

我们需要在用户登录流程中添加双因素认证（2FA）。
请先分析当前登录相关的代码结构，然后给出：
1. 需要修改的文件清单
2. 每个文件的修改点
3. 新增文件及其作用
4. 测试方案

请只做分析，不要修改任何代码。"
```

### 2.3 使用 @explore 子代理并行探索

在 Plan 阶段，可以利用 `@explore` 子代理进行并行的只读探索，加速信息收集：

```
"@explore 请帮我了解以下内容：

1. 当前用户认证相关的代码在哪里？（auth 模块、login 组件等）
2. 数据库中 user 表的 schema 是什么？是否有 2FA 相关字段？
3. 现有的 session/token 管理是如何实现的？
4. 有哪些现有的测试覆盖了登录流程？

请只读取文件，不要做任何修改。"
```

`@explore` 子代理的优势：

- **并行执行**: 多个探索任务同时进行
- **只读保证**: 不会意外修改代码
- **信息聚合**: 将分散在多个文件中的信息整合到一处

### 2.4 Plan 模式输出要求

一个合格的 Plan 应该包含：

```markdown
## 分析结果

### 当前状态
- 登录逻辑位于 `src/auth/login.ts`
- 使用 JWT token 管理 session
- User 表 schema: id, email, password_hash, created_at

### 修改计划

#### 1. 数据库变更
- **文件**: `migrations/002_add_2fa.sql`
- **内容**: 添加 `totp_secret`, `backup_codes`, `2fa_enabled` 字段

#### 2. 后端变更
- **文件**: `src/auth/totp.ts` (新增)
- **内容**: TOTP 生成和验证逻辑
- **文件**: `src/auth/login.ts` (修改)
- **内容**: 在密码验证后增加 2FA 验证步骤

#### 3. 前端变更
- **文件**: `src/components/TwoFactorSetup.tsx` (新增)
- **内容**: 2FA 设置界面（显示 QR 码、备份码）
- **文件**: `src/components/TwoFactorVerify.tsx` (新增)
- **内容**: 2FA 验证输入界面

#### 4. 测试
- **文件**: `src/auth/__tests__/totp.test.ts` (新增)
- **文件**: `src/auth/__tests__/login-2fa.test.ts` (新增)

### 依赖
- 需要安装 `otpauth` 包用于 TOTP 实现
```

### 2.5 v1.15.13 Plan 模式改进

v1.15.13 增强了 Plan 模式的安全性和可靠性：

- **Plan Mode Security Bypass 修复**（v1.14.46 已修复）: 之前 Plan 模式存在安全绕过漏洞，已修复
- **只读工具权限**: Plan 模式下 agent 只能使用只读工具（read、glob、search 等），不能调用 write、edit、bash 等修改性工具
- **配置向上加载**（v1.15.13）: Plan 阶段探索代码库时，配置解析更加可靠，特别是在 monorepo 结构中

---

## Phase 3：实现前先收敛范围

### 3.1 要求 Agent 给出"修改计划 + 文件范围"

在从 Plan 切换到 Build 之前，必须要求 agent 收敛范围，给出明确的承诺：

```
"基于刚才的 Plan，请给出具体的修改计划：

1. **文件范围**: 列出所有将被修改或创建的文件
2. **修改类型**: 每个文件是 'modify'（修改）还是 'create'（新建）
3. **变更摘要**: 每个文件的核心变更点（一句话）
4. **不修改保证**: 明确承诺不会触碰哪些相关文件

请严格按照这个列表执行，如果需要超出范围，必须再次征得同意。"
```

### 3.2 范围确认模板

Agent 应该输出类似以下的范围确认：

```markdown
## 修改范围确认

### 新建文件 (3)
| 文件 | 用途 |
|------|------|
| `src/auth/totp.ts` | TOTP 生成和验证逻辑 |
| `src/components/TwoFactorSetup.tsx` | 2FA 设置界面 |
| `src/components/TwoFactorVerify.tsx` | 2FA 验证界面 |

### 修改文件 (2)
| 文件 | 变更内容 |
|------|---------|
| `src/auth/login.ts` | 在密码验证后增加 2FA 检查分支 |
| `src/auth/types.ts` | 添加 2FA 相关类型定义 |

### 不触碰的文件
- `src/auth/register.ts` - 注册逻辑不需要修改
- `src/auth/oauth.ts` - OAuth 流程独立，不受影响
- `src/components/LoginForm.tsx` - 保持现状，2FA 验证使用新组件
- `.env*` - 不会修改任何环境变量文件
- `package.json` - 依赖安装将单独确认
```

### 3.3 使用 `--cwd` 控制修改范围

在 monorepo 或多包项目中，使用 `--cwd` 参数可以进一步限制 agent 的工作范围：

```bash
# 只让 agent 看到并修改 frontend 包
opencode --cwd packages/frontend
```

配合 `OPENCODE_DISABLE_PROJECT_CONFIG` 环境变量，可以完全控制配置加载：

```bash
# 禁用项目配置加载，只使用全局配置 + 命令行传入的配置
OPENCODE_DISABLE_PROJECT_CONFIG=1 opencode --cwd packages/frontend
```

---

## Phase 4：Build 模式做最小 Patch

### 4.1 切换到 Build 模式

在范围确认无误后，切换到 Build 模式执行实际修改：

```
"范围已确认，请切换到 Build 模式执行修改。

要求：
1. 严格按照确认的范围执行
2. 每个文件修改后执行相关测试
3. 如果测试失败，先修复再继续下一个文件
4. 保持 commit-ready 的代码质量（不要留 TODO、不要注释掉代码）"
```

### 4.2 最小 Patch 原则

每次 Build 应该只做**最小必要修改**。这包括：

- **一个变更一个 patch**: 不要把多个不相关的变更混在一起
- **行级最小化**: 只修改真正需要变更的行，不要"顺便"格式化或重构无关代码
- **测试跟随代码**: 每个功能变更配对应的测试变更
- **不要过度工程化**: 只做计划中的内容，不要"顺便"优化其他部分

### 4.3 使用 `opencode run` 进行非交互式执行

对于简单、明确的任务，可以使用 `opencode run` 命令非交互式执行：

```bash
# 单次运行，非交互式
opencode run "Implement a TOTP utility in src/auth/totp.ts with generateSecret, getQRCodeURL, and verifyToken functions. Use the otpauth package."
```

**适用场景**:

- 明确的单文件修改
- 生成代码骨架或模板
- 自动化脚本中调用 OpenCode

**不适用场景**:

- 需要多轮讨论的需求
- 涉及多个文件的复杂重构
- 需要人工判断的架构决策

### 4.4 v1.15.13 Build 模式改进

v1.15.x 系列对 Build 模式的改进包括：

- **Header Timeout 配置**（v1.15.0 新增）: 可以配置请求头超时时间，避免大文件操作时的超时中断
- **权限配置规则顺序修复**: Build 模式下的工具调用权限评估更加可预测
- **LSP 权限提示增强**: 语言服务器请求的权限提示更加清晰
- **后台 Agent 推送**（v1.15.0 新增）: Build 模式下支持后台 Agent 推送更新，可以并行处理多个任务
- **Diff Viewer**（v1.15.7/v1.15.9）: 重新设计的 diff 查看器，默认启用，代码审查更直观

```json
{
  "$schema": "https://opencode.ai/config.json",
  "server": {
    "port": 4096,
    "headerTimeout": 30000
  }
}
```

---

## Phase 5：验证必须独立于实现

### 5.1 验证原则

验证步骤必须由 agent **独立执行**，不能假设"刚才的修改肯定没问题"。每个验证步骤都是必需的：

| 验证步骤 | 命令 | 目的 |
|----------|------|------|
| **变更概览** | `git diff --stat` | 确认修改的文件数量和范围 |
| **详细 diff** | `git diff` | 逐行审查变更内容 |
| **运行相关测试** | `pnpm test <related-test>` | 确认修改没有破坏功能 |
| **类型检查** | `pnpm typecheck` | 确认 TypeScript 类型正确 |
| **代码检查** | `pnpm lint` | 确认代码风格合规 |

### 5.2 完整验证流程

```bash
# Step 1: 变更概览 - 确认修改范围
git diff --stat

# 预期输出示例：
#  src/auth/login.ts                  |  25 ++++++--
#  src/auth/totp.ts                   |  68 +++++++++++++
#  src/auth/types.ts                  |   8 ++-
#  src/components/TwoFactorSetup.tsx   | 112 +++++++++++++
#  src/components/TwoFactorVerify.tsx  |  45 +++++++++
#  5 files changed, 258 insertions(+), 2 deletions(-)

# Step 2: 详细 diff - 逐行审查
git diff

# Step 3: 运行相关测试
pnpm test src/auth/

# Step 4: 类型检查
pnpm typecheck

# Step 5: 代码检查
pnpm lint
```

### 5.3 验证失败的处理流程

```
如果任何验证步骤失败：
┌─────────────────────────────────────────────────────────────┐
│  1. 测试失败                                                 │
│     -> 让 agent 分析失败原因                                  │
│     -> 修复代码或测试                                         │
│     -> 重新运行失败的测试                                     │
│     -> 全部通过后继续下一步                                   │
│                                                             │
│  2. 类型检查失败                                             │
│     -> 让 agent 修复类型错误                                  │
│     -> 重新运行 pnpm typecheck                                │
│     -> 通过后继续                                             │
│                                                             │
│  3. Lint 失败                                                │
│     -> 让 agent 运行 lint --fix（如果可用）                    │
│     -> 或手动修复                                             │
│     -> 重新运行 pnpm lint                                     │
│     -> 通过后继续                                             │
│                                                             │
│  4. 发现意外修改                                             │
│     -> 如果 diff 包含范围外的文件                             │
│     -> 立即回滚（git checkout -- <file>）                     │
│     -> 要求 agent 解释为何超出范围                             │
│     -> 重新确认范围后再次执行                                 │
└─────────────────────────────────────────────────────────────┘
```

### 5.4 使用环境变量进行隔离验证

在 v1.15.13 中，可以使用环境变量来确保验证环境的隔离性，特别是在 CI/CD 或自动化脚本中：

```bash
# 完全隔离的配置环境
OPENCODE_DISABLE_GLOBAL_CONFIG=1 \
OPENCODE_DISABLE_PROJECT_CONFIG=1 \
OPENCODE_CONFIG_CONTENT='{"model":"anthropic/claude-sonnet-4-5","permission":{"bash":"allow","edit":"allow"}}' \
opencode run "Review the changes in git diff and verify they meet the coding standards"
```

| 环境变量 | 用途 |
|----------|------|
| `OPENCODE_DISABLE_GLOBAL_CONFIG=1` | 禁用全局配置加载，避免个人设置干扰 |
| `OPENCODE_DISABLE_PROJECT_CONFIG=1` | 禁用项目配置加载，完全由传入配置控制 |
| `OPENCODE_CONFIG_CONTENT` | 内联 JSON 配置，具有最高用户优先级（v1.15.13 已修复优先级问题） |

> **版本差异注意**: 在 v1.14.x 中，`OPENCODE_CONFIG_CONTENT` 的优先级存在 bug，可能被 `.opencode/` 目录配置覆盖。v1.15.x 已修复此问题，确保 `OPENCODE_CONFIG_CONTENT` 具有正确的最高用户优先级。如果你在 v1.14.32 中使用此环境变量，建议同时设置 `OPENCODE_NO_PARENT_CONFIG=1` 防止父目录配置干扰。

---

## Phase 6：人工 Review + Checkpoint

### 6.1 让 OpenCode 输出交接摘要

在提交之前，让 OpenCode 生成一个交接摘要，方便人工 review：

```
"请输出本次修改的交接摘要（Handoff Summary），包括：

1. 修改的目的和背景
2. 修改的文件清单（含新建和修改）
3. 每个文件的核心变更点
4. 测试覆盖情况
5. 已知限制或后续工作（如有）
6. 建议的提交信息（commit message）"
```

### 6.2 交接摘要模板

```markdown
## Handoff Summary

### 背景
为用户登录流程添加 TOTP 双因素认证支持。

### 变更文件 (5)

#### 新建文件 (3)
| 文件 | 说明 |
|------|------|
| `src/auth/totp.ts` | TOTP 工具函数：secret 生成、QR 码 URL、token 验证 |
| `src/components/TwoFactorSetup.tsx` | 2FA 设置流程 UI |
| `src/components/TwoFactorVerify.tsx` | 2FA 验证码输入 UI |

#### 修改文件 (2)
| 文件 | 变更 |
|------|------|
| `src/auth/login.ts` | 在密码验证后增加 2FA 分支逻辑 |
| `src/auth/types.ts` | 添加 `TwoFactorInfo` 接口 |

### 测试覆盖
- ✅ `src/auth/__tests__/totp.test.ts` - TOTP 工具函数测试（6 cases）
- ✅ `src/auth/__tests__/login-2fa.test.ts` - 登录 + 2FA 集成测试（4 cases）
- 整体测试通过率: 142/142 passed

### 依赖变更
- 新增: `otpauth@^1.2.3` (TOTP 实现)

### 已知限制
- 备份码功能在当前 PR 中未实现，后续跟进
- 前端 UI 未适配移动端，需要后续优化

### 建议提交信息
```
feat(auth): add TOTP two-factor authentication

- Implement TOTP secret generation and token verification
- Add 2FA setup UI with QR code display
- Add 2FA verification step in login flow
- Update login types for 2FA support
```
```

### 6.3 人工 Review 检查清单

```markdown
## 人工 Review 检查清单

### 变更范围
- [ ] 所有修改的文件都在预先确认的范围内
- [ ] 没有意外修改无关文件
- [ ] 没有遗留的调试代码（console.log, debugger 等）

### 代码质量
- [ ] 代码风格符合项目规范
- [ ] 变量和函数命名清晰
- [ ] 没有硬编码的魔法数字或字符串
- [ ] 错误处理到位（try/catch, 错误提示）

### 测试
- [ ] 新增功能有对应的测试
- [ ] 所有测试通过
- [ ] 测试覆盖关键路径和边界情况

### 安全
- [ ] 没有敏感信息泄露（API keys, 密码等）
- [ ] 输入验证到位
- [ ] 没有引入 SQL 注入、XSS 等安全风险

### 提交准备
- [ ] commit message 清晰描述了变更
- [ ] 提交粒度合理（一个逻辑变更一个 commit）
```

### 6.4 使用 `git add -p` 精细控制提交内容

```bash
# 交互式选择要提交的变更
git add -p

# 在交互过程中：
# y - 将此 hunk 加入暂存区
# n - 不将此 hunk 加入暂存区
# s - 拆分此 hunk 为更小的部分
# e - 手动编辑此 hunk
# ? - 显示帮助
```

### 6.5 最终提交

```bash
# 确认暂存区内容
git diff --cached --stat

# 提交
git commit -m "feat(auth): add TOTP two-factor authentication

- Implement TOTP secret generation and token verification
- Add 2FA setup UI with QR code display  
- Add 2FA verification step in login flow
- Update login types for 2FA support

Closes #127"
```

---

## CI/CD 中的 OpenCode 使用指南

### 环境变量配置矩阵

在 CI/CD 环境中使用 OpenCode 时，环境变量是控制配置的核心手段：

```bash
# ═══════════════════════════════════════════════════════
# 场景 1: 完全隔离（最安全，适用于自动化脚本）
# ═══════════════════════════════════════════════════════
OPENCODE_DISABLE_GLOBAL_CONFIG=1 \
OPENCODE_DISABLE_PROJECT_CONFIG=1 \
OPENCODE_CONFIG_CONTENT='{
  "model": "anthropic/claude-sonnet-4-5",
  "permission": {
    "edit": "allow",
    "bash": "allow"
  }
}' \
opencode run "Generate unit tests for src/utils/calculator.ts"

# ═══════════════════════════════════════════════════════
# 场景 2: 使用项目配置，但禁用全局配置
# ═══════════════════════════════════════════════════════
OPENCODE_DISABLE_GLOBAL_CONFIG=1 \
opencode run "Refactor the error handling in src/api/client.ts"

# ═══════════════════════════════════════════════════════
# 场景 3: 使用外部配置文件
# ═══════════════════════════════════════════════════════
export OPENCODE_CONFIG=/ci/configs/opencode-ci.json
opencode run "Review the code changes in git diff"

# ═══════════════════════════════════════════════════════
# 场景 4: 使用自定义配置目录
# ═══════════════════════════════════════════════════════
export OPENCODE_CONFIG_DIR=/ci/opencode-config/
opencode run "Run integration tests for the auth module"

# ═══════════════════════════════════════════════════════
# 场景 5: 禁止从父目录继承配置（monorepo 子包中）
# ═══════════════════════════════════════════════════════
OPENCODE_NO_PARENT_CONFIG=1 \
opencode --cwd packages/backend run "Fix the database migration script"
```

### 完整 CI/CD Pipeline 示例

```yaml
# .github/workflows/ai-code-review.yml
name: AI Code Review

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  ai-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install OpenCode
        run: npm install -g @opencode-ai/cli

      - name: Authenticate
        run: opencode auth login --provider anthropic --method "API Key"
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}

      - name: AI Code Review
        env:
          OPENCODE_DISABLE_GLOBAL_CONFIG: "1"
          OPENCODE_CONFIG_CONTENT: |
            {
              "model": "anthropic/claude-sonnet-4-5",
              "permission": {
                "edit": "deny",
                "bash": "deny"
              }
            }
        run: |
          opencode run "Review the code changes in this PR. 
          Focus on:
          1. Potential bugs or logic errors
          2. Security issues
          3. Performance concerns
          4. Code style violations
          Output a structured report with severity levels."
```

### CI 环境关键环境变量参考

| 环境变量 | 值 | 说明 |
|----------|-----|------|
| `OPENCODE_DISABLE_GLOBAL_CONFIG` | `1` | 禁用 `~/.config/opencode/` 的加载，避免 CI 环境读取不存在的全局配置 |
| `OPENCODE_DISABLE_PROJECT_CONFIG` | `1` | 禁用项目配置加载，完全由 `OPENCODE_CONFIG_CONTENT` 控制 |
| `OPENCODE_NO_PARENT_CONFIG` | `1` | 禁止从父目录向上搜索配置，确保只使用当前目录的配置 |
| `OPENCODE_CONFIG_CONTENT` | JSON 字符串 | 内联配置，最高用户优先级（v1.15.13 已修复优先级 bug） |
| `OPENCODE_CONFIG` | 文件路径 | 指定外部配置文件路径 |
| `OPENCODE_CONFIG_DIR` | 目录路径 | 指定配置目录（用于加载 agents、commands、skills 等） |
| `OPENCODE_DISABLE_AUTOUPDATE` | `1` | 禁用自动更新检查（CI 中不需要） |

---

## 版本差异速查

### v1.14.32 vs v1.15.13 关键差异

| 特性 | v1.14.32 | v1.15.13 |
|------|----------|----------|
| `OPENCODE_CONFIG_CONTENT` 优先级 | 可能被 `.opencode/` 覆盖 | ✅ 已修复，正确为最高用户优先级 |
| 配置向上加载 | 从 Git 根目录 | ✅ 从打开位置向上加载，更精确 |
| Header Timeout | 不支持 | ✅ 新增配置 |
| 后台 Agent 推送 | 不支持 | ✅ 支持 |
| Diff Viewer | 旧版 | ✅ 重新设计，默认启用 |
| LSP 权限提示 | 基础 | ✅ 增强 |
| 权限配置规则顺序 | 部分问题 | ✅ 已修复 |
| 非 Git 项目路径处理 | 可能有问题 | ✅ v1.15.9 修复 |
| Session 目录持久化 | 不持久 | ✅ v1.15.12 起使用持久化目录 |
| Read tool 权限 | 基于工作目录 | ✅ v1.14.45 起匹配 worktree-relative 路径 |

### 升级建议

- **推荐升级路径**: v1.14.32 → v1.15.13，后者修复了多个关键问题，特别是配置优先级和路径解析
- **升级后验证**: 升级后建议检查 Skill 发现、Tool 执行目录、子 agent 路径解析是否正常

---

## 总结：6 个 Phase 速查卡

```
┌─────────────────────────────────────────────────────────────────┐
│  Phase 0: 安全边界                                              │
│  ├── git status --short                                         │
│  ├── git switch -c ai/<ticket-or-task>                          │
│  └── 确认安全红线（不 push, 不 reset --hard, 不 clean -fd）      │
├─────────────────────────────────────────────────────────────────┤
│  Phase 1: 初始化项目规则                                         │
│  ├── opencode /init                                             │
│  ├── 检查并补充 AGENTS.md                                        │
│  └── 确认项目结构、命令、规范、禁止事项                            │
├─────────────────────────────────────────────────────────────────┤
│  Phase 2: Plan 模式                                             │
│  ├── 使用 Plan 模式做分析                                        │
│  ├── @explore 子代理并行探索                                     │
│  └── 输出完整计划（文件清单 + 修改点 + 测试方案）                    │
├─────────────────────────────────────────────────────────────────┤
│  Phase 3: 收敛范围                                               │
│  ├── 要求"修改计划 + 文件范围"                                   │
│  ├── 每个文件标注 modify/create                                  │
│  └── 明确不触碰的文件清单                                         │
├─────────────────────────────────────────────────────────────────┤
│  Phase 4: Build 模式                                            │
│  ├── 切换到 Build 模式                                          │
│  ├── 严格按确认的范围执行                                        │
│  └── 最小 patch 原则（不超出范围、不留 TODO）                      │
├─────────────────────────────────────────────────────────────────┤
│  Phase 5: 独立验证                                               │
│  ├── git diff --stat                                            │
│  ├── git diff                                                   │
│  ├── pnpm test <related>                                        │
│  ├── pnpm typecheck                                             │
│  └── pnpm lint                                                  │
├─────────────────────────────────────────────────────────────────┤
│  Phase 6: 人工 Review                                           │
│  ├── 让 OpenCode 输出交接摘要                                     │
│  ├── 人工检查 git diff                                          │
│  ├── git add -p（精细控制）                                      │
│  └── git commit                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

*本文档基于 OpenCode v1.14.32 和 v1.15.13 的实践总结。配置系统和 CLI 接口可能随版本更新而变化，建议参考 [OpenCode 官方文档](https://open-code.ai/en/docs) 获取最新信息。*
