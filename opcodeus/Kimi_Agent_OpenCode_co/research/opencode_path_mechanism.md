# OpenCode 路径解析机制深度研究报告

> 研究版本: OpenCode v1.14.32 - v1.15.13
> 研究日期: 2025年6月
> 研究范围: Skill、Tool、Script 的路径引用机制、路径原点、常见坑点

---

## 目录

1. [路径解析机制概述](#1-路径解析机制概述)
2. [Skill 路径系统详解](#2-skill-路径系统详解)
3. [Tool 路径系统详解](#3-tool-路径系统详解)
4. [默认工作目录和路径原点](#4-默认工作目录和路径原点)
5. [SKILL.md 文档引用规范](#5-skillmd-文档引用规范)
6. [Tool Script 引用规范](#6-tool-script-引用规范)
7. [常见路径坑点和解决方案](#7-常见路径坑点和解决方案)
8. [最佳实践建议](#8-最佳实践建议)
9. [版本差异 (v1.14.32 vs v1.15.13)](#9-版本差异-v11432-vs-v11513)
10. [参考来源汇总](#10-参考来源汇总)

---

## 1. 路径解析机制概述

OpenCode 采用多层级的路径解析体系，核心原则是 **"从当前工作目录 (CWD) 向上遍历至 Git Worktree 根目录"**，同时结合全局配置目录。整个系统分为三个层次：

| 层次 | 作用 | 关键路径 |
|------|------|----------|
| 项目级 (Project) | 当前项目内的配置和技能 | `.opencode/skills/`, `.opencode/tools/`, `.opencode/plugins/` |
| 全局级 (Global) | 用户主目录下的全局配置 | `~/.config/opencode/skills/`, `~/.config/opencode/tools/` |
| 兼容级 (Compat) | 兼容 Claude Code 和 Codex 的路径 | `.claude/skills/`, `.agents/skills/`, `~/.claude/skills/` |

### 核心发现

1. **Skill 发现**: OpenCode 从 `Instance.directory`（通常是 process.cwd()）向上遍历到 git worktree 根，在此过程中发现所有匹配 `skills/*/SKILL.md` 的文件
2. **Tool 发现**: 工具文件直接从 `.opencode/tools/*.ts` 或 `~/.config/opencode/tools/*.ts` 加载
3. **路径原点**: CLI 模式下是 `process.cwd()`，Desktop 模式下可能是 `/`，Web daemon 模式下是启动目录
4. **相对路径解析**: Agent 默认将相对路径解析为项目根目录，而非 Skill 或 Tool 的安装目录——这是一个已知的重大坑点

> **来源**: [OpenCode 官方文档 - 代理技能](https://opencode.ai/docs/skills), [OpenCode 官方文档 - 自定义工具](https://opencode.ai/docs/custom-tools)

---

## 2. Skill 路径系统详解

### 2.1 Skill 目录结构

标准的 Skill 目录结构如下：

```
my-skill/
├── SKILL.md              # 必需 - 技能主定义文件
├── scripts/              # 可选 - 可执行脚本
│   ├── validate.sh
│   └── deploy.py
├── references/           # 可选 - 参考文档
│   ├── api-docs.md
│   └── examples.md
└── assets/               # 可选 - 静态资源
    └── template.html
```

### 2.2 Skill 发现路径（优先级从高到低）

| 优先级 | 路径类型 | 具体路径 |
|--------|----------|----------|
| 1 | 项目级 OpenCode | `.opencode/skills/<name>/SKILL.md` |
| 2 | 全局级 OpenCode | `~/.config/opencode/skills/<name>/SKILL.md` |
| 3 | 项目级 Claude 兼容 | `.claude/skills/<name>/SKILL.md` |
| 4 | 全局级 Claude 兼容 | `~/.claude/skills/<name>/SKILL.md` |
| 5 | 项目级 Agents 兼容 | `.agents/skills/<name>/SKILL.md` |
| 6 | 全局级 Agents 兼容 | `~/.agents/skills/<name>/SKILL.md` |

**重要**: 项目级 Skill 优先于全局级 Skill（同名时项目级覆盖全局级）。

### 2.3 Skill 发现机制

对于**项目本地路径**，OpenCode 采用以下算法：

```
1. 从当前工作目录 (CWD) 开始
2. 向上遍历目录树，直到到达 git worktree 根目录
3. 在此过程中，加载所有 .opencode/skills/*/SKILL.md
4. 同时也加载匹配的 .claude/skills/*/SKILL.md 和 .agents/skills/*/SKILL.md
5. 更高优先级的位置覆盖低优先级的同名 Skill
```

对于**全局路径**，直接从以下目录加载：
- `~/.config/opencode/skills/*/SKILL.md`
- `~/.claude/skills/*/SKILL.md`
- `~/.agents/skills/*/SKILL.md`

### 2.4 Skill 源码扫描逻辑

根据 OpenCode 源码解析，Skill 扫描过程如下：

```typescript
// packages/opencode/src/skill/skill.ts
export const state = Instance.state(async () => {
  const skills: Record<string, Info> = {}
  const dirs = new Set<string>()

  // 1. 外部技能目录（兼容 Claude Code）
  // 全局目录（~/.claude/skills/, ~/.agents/skills/）
  if (!Flag.OPENCODE_DISABLE_EXTERNAL_SKILLS) {
    for (const dir of [".claude", ".agents"]) {
      const root = path.join(Global.Path.home, dir)
      if (await Filesystem.isDir(root)) {
        await scanExternal(root, "global")
      }
    }
    // 项目级目录（从当前目录向上查找，直到 git worktree）
    for await (const root of Filesystem.up({
      targets: [".claude", ".agents"],
      start: Instance.directory,
      stop: Instance.worktree,
    })) {
      await scanExternal(root, "project")
    }
  }

  // 2. OpenCode 配置目录
  // .opencode/skills/ 或 .opencode/skill/
  for (const dir of await Config.directories()) {
    for await (const match of OPENCODE_SKILL_GLOB.scan({
      cwd: dir,
      absolute: true,
      onlyFiles: true,
      followSymlinks: true,
    })) {
      await addSkill(match)
    }
  }

  // 3. 配置的额外路径
  const config = await Config.get()
  for (const skillPath of config.skills?.paths ?? []) {
    const expanded = skillPath.startsWith("~/")
      ? path.join(os.homedir(), skillPath.slice(2))
      : skillPath
    const resolved = path.isAbsolute(expanded)
      ? expanded
      : path.join(Instance.directory, expanded)
    // ...
  }
  // ...
})
```

> **来源**: [CSDN - OpenCode 源码解析](https://devpress.csdn.net/xclaw/69c0d99f0a2f6a37c59989a3.html), [OpenCode 官方文档 - 代理技能](https://opencode.ai/docs/skills)

### 2.5 Skill 命名规则

- `name` 必须满足: `^[a-z0-9]+(-[a-z0-9]+)*$`
- 长度 1-64 个字符
- 仅包含小写字母和数字，可用单个连字符分隔
- 不以 `-` 开头或结尾
- **必须与包含 SKILL.md 的目录名称一致**
- 未知 frontmatter 字段会被忽略

---

## 3. Tool 路径系统详解

### 3.1 Tool 目录结构

Tool 采用文件级发现机制（非目录级）：

```
.opencode/tools/                    # 项目级工具目录
├── database.ts                     # 单个工具（工具名: database）
├── math.ts                         # 多个导出（工具名: math_add, math_multiply）
└── python-add.ts                   # 调用外部 Python 脚本的工具

~/.config/opencode/tools/           # 全局工具目录
└── my-global-tool.ts
```

### 3.2 Tool 发现路径

| 范围 | 路径 |
|------|------|
| 项目级 | `.opencode/tools/*.ts` 或 `.opencode/tools/*.js` |
| 全局级 | `~/.config/opencode/tools/*.ts` 或 `~/.config/opencode/tools/*.js` |

### 3.3 Tool 命名规则

- **文件名即工具名**（不含扩展名）
- 单文件多导出: `<filename>_<exportname>`
- 自定义工具与内置工具同名时会**覆盖**内置工具

### 3.4 Plugin 路径

| 范围 | 路径 |
|------|------|
| 项目级 Plugin | `.opencode/plugins/*.js` 或 `.opencode/plugin/*.js` |
| 全局级 Plugin | `~/.config/opencode/plugins/*.js` 或 `~/.config/opencode/plugin/*.js` |
| npm Plugin | 在 `opencode.json` 中配置 `"plugin": ["package-name"]` |

> **来源**: [OpenCode 官方文档 - 自定义工具](https://opencode.ai/docs/custom-tools)

---

## 4. 默认工作目录和路径原点

### 4.1 路径原点的定义

OpenCode 中涉及多个"目录"概念，极易混淆：

| 变量/属性 | 含义 | 获取方式 |
|-----------|------|----------|
| `process.cwd()` | Node.js 进程启动时的工作目录 | `process.cwd()` |
| `context.directory` | 当前会话/项目的目录 | Tool execute 的 context 参数 |
| `context.worktree` | Git worktree 根目录 | Tool execute 的 context 参数 |
| `Instance.directory` | OpenCode 实例的目录 | 内部状态 |
| `Instance.worktree` | 当前项目的 git worktree | 内部状态 |

### 4.2 不同运行模式下的路径原点

| 运行模式 | `process.cwd()` | `context.directory` | 说明 |
|----------|----------------|---------------------|------|
| CLI (在项目目录启动) | 项目目录 | 项目目录 | 一致，正常工作 |
| CLI (带 `--dir`) | 启动目录 | `--dir` 指定的目录 | process.cwd() 与项目目录不同 |
| CLI (带 `--cwd`) | `--cwd` 指定的目录 | `--cwd` 指定的目录 | 一致 |
| Desktop App | `/` (系统根!) | 项目目录 | **重大坑点** |
| Web Daemon | 启动 daemon 的目录 | Web UI 选择的项目目录 | **重大坑点** |
| `opencode serve` | 启动目录 | HTTP API 传入的目录 | 可能不一致 |
| `task()` 子 agent | 父进程 cwd | `ctx.directory` (应然) | **有 bug** |

### 4.3 --cwd 参数

OpenCode CLI 支持 `--cwd` 参数显式设置工作目录：

```bash
opencode --cwd /path/to/project
opencode -c ~/my-project
```

> 这会在启动前改变当前工作目录，并作为所有文件操作的根目录。

> **来源**: [OpenCode 官方文档 - CLI flags](https://mintlify.com/opencode-ai/opencode/reference/flags), [OpenCode Issue #9077](https://github.com/anomalyco/opencode/issues/9077)

---

## 5. SKILL.md 文档引用规范

### 5.1 Skill 内部资源引用方式

SKILL.md 中引用 `references/`、`scripts/`、`assets/` 目录下的文件时，存在**重大的路径解析问题**。

#### 问题：相对路径解析为 CWD

**这是 OpenCode 最著名的路径 Bug 之一** (Issue #17101, Issue #17094):

当 SKILL.md 中包含类似这样的指令时：
```markdown
Read references/investigation-tools.md
```

Agent 会尝试将 `references/investigation-tools.md` 解析为**当前工作目录 (CWD)** 下的路径，而不是 Skill 安装目录下的路径。

**错误结果**：
```
Error: File not found: /Users/.../current-project/references/investigation-tools.md
```

**根因**: Agent 的系统提示指示 Agent 始终将相对文件路径解析为项目根目录，而非 Skill 文件所在位置。Agent 不知道相对路径可能应该相对于 Skill 定义本身。

> **来源**: [GitHub Issue #17101](https://github.com/anomalyco/opencode/issues/17101), [GitHub Issue #17094](https://github.com/anomalyco/opencode/issues/17094)

### 5.2 解决方案

#### 方案 1: 使用 `skill_resource` 工具 (推荐)

通过 `skill_resource` 工具显式读取 Skill 资源，路径相对于 Skill 目录：

```javascript
skill_resource skill_name="my-skill" relative_path="references/api-docs.md"
```

#### 方案 2: 使用 Skill 插件 (如 opencode-skills, opencode-skillful)

社区插件提供路径自动解析功能。当 Skill 加载时，插件会注入 base directory context：

```
Base directory for this skill: /path/to/.opencode/skills/my-skill/
```

Agent 收到此上下文后，会自动将 `references/api.md` 解析为 `/path/to/.opencode/skills/my-skill/references/api.md`。

#### 方案 3: 使用绝对路径（通过变量替换）

一些 Skill 安装器会在安装时将 `__INSTALLED_SKILL_DIR__` 替换为实际的绝对路径：

```bash
python3 __INSTALLED_SKILL_DIR__/scripts/export_opencode_session.py .sessions ses_abc
```

#### 方案 4: 编写显式路径解析指令

在 SKILL.md 中明确告诉 Agent 如何找到文件：

```markdown
The scripts for this skill are located in the skill's install directory.
Use the skill tool to determine the base path, then resolve:
- <skill_base>/scripts/validate.sh
- <skill_base>/references/schema.md
```

### 5.3 社区插件提供的 `skill_resource` 工具

| 插件 | 工具名 | 用途 |
|------|--------|------|
| opencode-skillful | `skill_resource` | 读取 Skill 内的资源文件 |
| opencode-skills | 内置 path resolution | 自动解析相对路径 |
| oh-my-openagent | `skill_resource` | 带路径解析的资源读取 |

`skill_resource` 参数：
- `skill_name`: Skill 名称
- `relative_path`: 相对于 Skill 目录的路径（如 `references/guide.md`, `scripts/setup.sh`）

> **来源**: [opencode-skillful README](https://github.com/zenobi-us/opencode-skillful), [opencode-skills NPM](https://www.npmjs.com/package/@monotykamary/opencode-skills), [Lobehub - session-dump Skill](https://lobehub.com/zh/skills/thesobercoder-skills-session-dump)

---

## 6. Tool Script 引用规范

### 6.1 Tool 定义中引用外部脚本的正确方式

OpenCode 官方文档推荐的脚本引用方式：

```typescript
import { tool } from "@opencode-ai/plugin"
import path from "path"

export default tool({
  description: "Add two numbers using Python",
  args: {
    a: tool.schema.number().describe("First number"),
    b: tool.schema.number().describe("Second number"),
  },
  async execute(args, context) {
    // 正确方式：使用 context.worktree 构建绝对路径
    const script = path.join(context.worktree, ".opencode/tools/add.py")
    const result = await Bun.$`python3 ${script} ${args.a} ${args.b}`.text()
    return result.trim()
  },
})
```

### 6.2 Tool execute 的 Context 对象

Tool 的 `execute` 函数接收的 `context` 对象包含：

| 属性 | 类型 | 说明 |
|------|------|------|
| `agent` | string | 当前 agent 名称 |
| `sessionID` | string | 会话 ID |
| `messageID` | string | 消息 ID |
| `directory` | string | **会话的工作目录（推荐用于路径构建）** |
| `worktree` | string | **Git worktree 根目录** |
| `abort` | AbortSignal | 中止信号 |
| `metadata()` | function | 设置工具调用元数据 |
| `ask()` | function | 向用户提问 |

**关键区别**：
- `context.directory` → 当前会话的工作目录（可能是项目子目录）
- `context.worktree` → Git worktree 根目录（项目根目录）

### 6.3 Plugin Context 对象

Plugin 工厂函数接收的 `ctx` 对象包含：

| 属性 | 说明 |
|------|------|
| `ctx.directory` | 当前工作目录 |
| `ctx.worktree` | Git worktree 路径（`ctx.project.worktree` 的别名） |
| `ctx.project` | 当前项目信息 |
| `ctx.project.id` | 项目标识符（git hash 或 "global"） |
| `ctx.project.worktree` | Git worktree 根目录 |
| `ctx.client` | OpenCode SDK 客户端 |
| `ctx.$` | Bun Shell API |

### 6.4 引用脚本的最佳实践

| 场景 | 推荐写法 | 说明 |
|------|----------|------|
| 工具脚本在项目内 | `path.join(context.worktree, ".opencode/tools/script.py")` | 使用 worktree 确保稳定 |
| 工具脚本使用目录上下文 | `path.join(context.directory, "relative/path")` | 相对于当前会话目录 |
| Skill 脚本 | 通过 `skill_resource` 工具引用 | 让插件处理路径解析 |
| 全局工具脚本 | 硬编码 `~/.config/opencode/tools/` | 全局路径已知 |

### 6.5 在 Plugin Tool 中执行命令的工作目录

```typescript
// 正确：显式指定 cwd
async execute(args, context) {
  const cwd = args.cwd 
    ? path.join(context.directory, args.cwd) 
    : context.directory
  const result = await ctx.$`cd ${cwd} && ${args.command}`
  return result
}
```

> **来源**: [OpenCode 官方文档 - 自定义工具](https://opencode.ai/docs/custom-tools), [Mintlify - Plugin Tools 文档](https://mintlify.com/anomalyco/opencode/sdk/plugin-tools)

---

## 7. 常见路径坑点和解决方案

### 坑点 1: Desktop App 中 `process.cwd()` 是 `/` [CRITICAL]

**问题**: 在 OpenCode Desktop 中，工具的执行工作目录是系统根目录 `/`，而非项目目录。使用 `process.cwd()` 或相对路径的工具会失败。

**表现**:
```
Desktop sets cwd to /
script_path resolves to /.opencode/tool/add.py
Python fails with "No such file or directory"
```

**影响版本**: CLI v1.1.20, Desktop v1.1.25 及后续版本

**解决方案**:
```typescript
// 错误：依赖 process.cwd()
const script_path = path.resolve(".opencode/tool/add.py")

// 正确：使用 context.worktree
const script_path = path.join(context.worktree, ".opencode/tool/add.py")
```

> **来源**: [GitHub Issue #9077](https://github.com/anomalyco/opencode/issues/9077)

---

### 坑点 2: Skill 相对路径解析为 CWD 而非 Skill 目录 [CRITICAL]

**问题**: Agent 将 SKILL.md 中的 `references/`、`scripts/` 相对路径解析为当前工作目录。

**表现**:
```
Error: File not found: /Users/.../current-project/references/investigation-tools.md
```

**解决方案**: 使用 `skill_resource` 工具，或安装 opencode-skills/opencode-skillful 插件。

> **来源**: [GitHub Issue #17101](https://github.com/anomalyco/opencode/issues/17101), [GitHub Issue #17094](https://github.com/anomalyco/opencode/issues/17094)

---

### 坑点 3: `task()` 子 agent 使用 `process.cwd()` 解析 Skill

**问题**: `task()` 工具加载 Skill 时，`resolveSkillContent2` 未接收 `directory` 参数，导致 `discoverSkills` 回退到 `process.cwd()`（即服务器启动目录，而非工作区目录）。

**触发条件**:
- 从不同于项目的目录启动 opencode server
- 使用 `--dir` 参数附加到工作区
- 调用 `task(subagent_type="any-agent", load_skills=["my-skill"], ...)`

**表现**:
```
Skills not found: my-skill. Available:
```

**解决方案**: 在调用 task() 时显式传递完整路径，或使用全局 Skill。

> **来源**: [oh-my-openagent Issue #1982](https://github.com/code-yeongyu/oh-my-openagent/issues/1982)

---

### 坑点 4: Plugin ToolContext 缺少 `directory` 和 `worktree`

**问题**: 自定义工具通过 `@opencode-ai/plugin` 定义时，`ToolContext` 不包含 `directory` 或 `worktree` 属性。使用 `process.cwd()` 在 daemon 模式下返回 daemon 的 cwd 而非项目目录。

**受影响场景**:
- `opencode web` 作为 daemon 运行
- 多个项目共享一个 daemon

**ToolContext 实际内容**:
```json
{
  "context": {
    "sessionID": "ses_...",
    "messageID": "msg_...",
    "agent": "build",
    "callID": "toolu_...",
    "allKeys": ["sessionID", "abort", "messageID", "callID", "extra", "agent", "metadata", "ask"]
  },
  "cwd": "/Users/rick",
  "env": { "OPENCODE": "1", "HOME": "/Users/rick" }
}
```

**解决方案**:
1. 使用 Plugin 的 `ctx.directory`（Plugin 初始化时传入的上下文）
2. 通过环境变量传递项目目录
3. 等待官方修复（Issue #10477）

> **来源**: [GitHub Issue #10477](https://github.com/anomalyco/opencode/issues/10477)

---

### 坑点 5: Windows 子 agent 目录漂移到 LOCALAPPDATA

**问题**: 在 Windows 上，子 agent 会话间歇性地在 `C:\Users\<user>\AppData\Local\...` 目录中初始化，而非项目目录。

**影响**: 子 agent 报告 "no files found" 或尝试操作系统/配置文件。

**临时解决方案**:
```javascript
// 在 Plugin 入口点添加守卫
function resolveRuntimeDirectory(ctx) {
  if (isWindowsAppDataPath(ctx.directory) && !isWindowsAppDataPath(process.cwd())) {
    return process.cwd()  // 强制使用 process.cwd()
  }
  return ctx.directory
}
```

> **来源**: [oh-my-openagent Issue #1718](https://github.com/code-yeongyu/oh-my-openagent/issues/1718)

---

### 坑点 6: glob 工具默认路径 `["."]` 继承不到正确的 cwd

**问题**: glob 工具默认 `paths: ["."]` 在 Windows + WSL 环境中可能指向错误位置。

**临时解决方案**:
```javascript
// 显式指定 path 参数
glob(path="D:\\AI-Project\\AI-AgentWorkSpace-Ducky", pattern="AGENT.md")
```

> **来源**: [oh-my-openagent Issue #1617](https://github.com/code-yeongyu/oh-my-openagent/issues/1617)

---

### 坑点 7: 单数/复数目录名不一致 (`skill/` vs `skills/`)

**问题**: 早期版本和社区工具有时使用单数 `skill/`，有时用复数 `skills/`。

**OpenCode 官方路径** (复数):
- `.opencode/skills/` 
- `~/.config/opencode/skills/`

**已修复**: 早期 bug (Issue #810, #6292, #930) 已在 PR #966 中修复，统一为复数形式。

> **来源**: [GitHub Issue #36 - vercel-labs/skills](https://github.com/vercel-labs/skills/issues/36), [oh-my-openagent Issue #967](https://github.com/code-yeongyu/oh-my-openagent/issues/967)

---

### 坑点 8: Symlink 目录导致 TUI 空白响应

**问题**: 从 symlink 目录（指向 git repo）启动 opencode 时，TUI 显示空白响应。

**根因**: TUI 主线程从 `process.env.PWD` 解析目录（保留 symlink 路径），而 worker 使用 `process.cwd()`（返回物理/规范路径）。两者不一致导致事件不送达。

**解决方案**: 从真实路径启动 opencode，而非 symlink 路径。

> **来源**: [GitHub Issue #16528](https://github.com/anomalyco/opencode/issues/16528)

---

### 坑点 9: `opencode import` 忽略 CWD 分配 session 到 global

**问题**: `opencode import <file>` 始终将导入的 session 的 `project_id` 设为 `"global"`，忽略当前工作目录。

**解决方案**: 手动更新 SQLite 数据库中的 session 记录。

> **来源**: [GitHub Issue #15797](https://github.com/anomalyco/opencode/issues/15797)

---

### 坑点 10: Plugin skill 发现忽略 `skills.paths` 配置

**问题**: oh-my-openagent 等 Plugin 的 skill 发现只扫描硬编码目录，不读取 `opencode.json` 中的 `skills.paths` 配置。

**受影响目录** (硬编码):
- `~/.claude/skills/`
- `~/.config/opencode/skills/`
- `.opencode/skills/`
- `.agents/skills/`
- `~/.agents/skills/`

**解决方案**: 将 Skill 放在硬编码目录之一，或使用 `--pure` 模式。

> **来源**: [oh-my-openagent Issue #3787](https://github.com/code-yeongyu/oh-my-openagent/issues/3787)

---

## 8. 最佳实践建议

### 8.1 通用原则

1. **绝不使用 `process.cwd()` 构建路径** - 在 Desktop、Web Daemon、task() 子 agent 等场景下不可靠
2. **始终使用 `context.directory` 或 `context.worktree`** - 这是 OpenCode 提供的稳定路径引用
3. **使用 `path.join()` 而非字符串拼接** - 确保跨平台兼容性
4. **对 Skill 资源使用 `skill_resource` 工具** - 避免手动路径解析

### 8.2 Tool 开发最佳实践

```typescript
import { tool } from "@opencode-ai/plugin"
import path from "path"

export default tool({
  description: "My tool that references a script",
  args: { /* ... */ },
  async execute(args, context) {
    // ✅ 正确：使用 context.worktree 构建脚本路径
    const scriptPath = path.join(context.worktree, ".opencode/tools/my-script.py")
    
    // ✅ 正确：使用 context.directory 作为命令执行目录
    const result = await Bun.$`cd ${context.directory} && python3 ${scriptPath}`
    
    // ❌ 错误：依赖 process.cwd()
    // const scriptPath = path.resolve(".opencode/tools/my-script.py")
    
    return result.text()
  },
})
```

### 8.3 Skill 开发最佳实践

```markdown
---
name: my-skill
description: My skill with bundled resources
---

# My Skill

## Resources

This skill includes bundled scripts and references.

### For Agents:
- To read reference docs, use: `skill_resource skill_name="my-skill" relative_path="references/guide.md"`
- To run scripts, first determine the skill base path from the skill tool, then execute:
  ```bash
  bash <skill_base>/scripts/setup.sh
  ```

### Important:
Do NOT use relative paths like `references/guide.md` directly - they will resolve to the 
wrong directory. Always use the skill_resource tool or resolve absolute paths through the skill base directory.
```

### 8.4 目录结构建议

```
project/
├── .opencode/
│   ├── skills/           # 项目级 Skill
│   │   └── my-skill/
│   │       ├── SKILL.md
│   │       ├── scripts/
│   │       └── references/
│   ├── tools/            # 项目级 Tool
│   │   ├── database.ts
│   │   └── helper.py     # 被 Tool 引用的脚本
│   ├── plugins/          # 项目级 Plugin
│   └── instructions.md   # 项目级指令
└── opencode.json         # 项目配置
```

### 8.5 多环境兼容性检查清单

在开发 Tool 或 Skill 时，验证以下场景：

- [ ] CLI 模式下从项目目录直接启动
- [ ] CLI 模式下使用 `--dir /path/to/project`
- [ ] Desktop App 模式
- [ ] Web Daemon 模式 (多项目)
- [ ] `task()` 子 agent 调用
- [ ] Windows 环境
- [ ] WSL 环境

---

## 9. 版本差异 (v1.14.32 vs v1.15.13)

### 9.1 v1.14.x 系列关键变更 (v1.14.32 附近)

| 版本 | 日期 | 路径相关变更 |
|------|------|-------------|
| v1.14.37 | 2025年中 | Canceling a task now also cancels child subtask sessions |
| v1.14.38 | 2025年中 | Desktop: trust system CA certificates |
| v1.14.39 | 2025年中 | Desktop: respect HTTP_PROXY |
| v1.14.41 | 2025年中 | Warp session to another workspace carrying uncommitted changes |
| v1.14.45 | 2025年中 | Read tool permission rules now match worktree-relative paths |
| v1.14.46 | 2025年中 | Added built-in `customize-opencode` skill; Fix Plan Mode security bypass |
| v1.14.47 | 2025年中 | File/directory paths render relative to session directory; Scout materializes reference repos |
| v1.14.48 | 2025年中 | Preserve original image attachments |
| v1.14.51 | 2025年中 | Experimental background subagents; Fix truncated shell output |

### 9.2 v1.15.x 系列关键变更 (到 v1.15.13)

| 版本 | 日期 | 路径相关变更 |
|------|------|-------------|
| v1.15.3 | 2025年末 | Fix async commands losing active instance context |
| v1.15.4 | 2025年末 | Fix project-scoped bus events; Fix custom LSP refresh events |
| v1.15.7 | 2026年初 | Redesigned diff viewer; Copy worktree path from command palette |
| v1.15.9 | 2026年初 | Enable diff viewer by default; Fix non-git project paths |
| v1.15.12 | 2026年初 | Used persisted session directory for existing-session requests; Workspace management dialog |
| v1.15.13 | 2026年初 | Config loads from opened location upward; Directory-specific settings apply predictably |

### 9.3 关键路径修复时间线

| 修复项 | 引入版本 | 说明 |
|--------|----------|------|
| `skill/` → `skills/` 目录名统一 | ~v1.14.x | 修复单数/复数不一致 |
| task() Skill 路径解析 | oh-my-openagent v3.5.0 | "Skill @path Auto-Resolution" |
| Desktop cwd = `/` | 部分修复 | 需要通过 context.directory 绕过 |
| Plugin ToolContext directory | 部分修复 | 建议使用 Plugin ctx.directory |
| Windows 子 agent 目录漂移 | 部分修复 (PR #1895) | 仅修复 win32 平台 |
| Session directory persistence | v1.15.12 | 现有 session 请求使用持久化目录 |
| Config 向上加载 | v1.15.13 | 从打开位置向上加载配置 |

### 9.4 版本升级建议

- **v1.14.32 → v1.15.13**: 推荐升级，v1.15.13 修复了多个路径相关的问题，特别是 session 目录持久化和配置加载
- 升级后需要验证: Skill 发现、Tool 执行目录、子 agent 路径解析

---

## 10. 参考来源汇总

### 官方文档

| 来源 | URL |
|------|-----|
| OpenCode 官方文档 - 代理技能 | https://opencode.ai/docs/skills |
| OpenCode 官方文档 - 自定义工具 | https://opencode.ai/docs/custom-tools |
| OpenCode 官方文档 - CLI flags | https://mintlify.com/opencode-ai/opencode/reference/flags |
| Mintlify - Plugin Tools | https://mintlify.com/anomalyco/opencode/sdk/plugin-tools |
| OpenCode 自定义工具文档 | https://opencode.ai/docs/custom-tools/ |

### GitHub Issues (路径相关 Bug)

| Issue | URL | 主题 |
|-------|-----|------|
| #17101 | https://github.com/anomalyco/opencode/issues/17101 | Agent 将 Skill 相对路径解析为 CWD |
| #17094 | https://github.com/anomalyco/opencode/issues/17094 | Agent 将 Skill 资源路径解析为 CWD |
| #9077 | https://github.com/anomalyco/opencode/issues/9077 | Desktop 工具从 `/` 执行 |
| #10477 | https://github.com/anomalyco/opencode/issues/10477 | 自定义工具无法获取项目目录 |
| #1982 | https://github.com/code-yeongyu/oh-my-openagent/issues/1982 | task() 子 agent Skill 路径解析 |
| #1718 | https://github.com/code-yeongyu/oh-my-openagent/issues/1718 | Windows 子 agent 目录漂移 |
| #1617 | https://github.com/code-yeongyu/oh-my-openagent/issues/1617 | glob 工具路径问题 |
| #16528 | https://github.com/anomalyco/opencode/issues/16528 | Symlink 目录 TUI 空白 |
| #15797 | https://github.com/anomalyco/opencode/issues/15797 | import 忽略 CWD |
| #3787 | https://github.com/code-yeongyu/oh-my-openagent/issues/3787 | Plugin 忽略 skills.paths |
| #24082 | https://github.com/anomalyco/opencode/issues/24082 | Windows skill 发现 HOME 为空 |
| #1617 | https://github.com/code-yeongyu/oh-my-openagent/issues/1617 | glob 工具 Windows 路径 |
| #36 | https://github.com/vercel-labs/skills/issues/36 | skill/ vs skills/ 目录名 |
| #847 | https://github.com/obra/superpowers/issues/847 | Skill 路径不一致 |

### 社区插件和资源

| 来源 | URL | 主题 |
|------|-----|------|
| opencode-skillful | https://github.com/zenobi-us/opencode-skillful | Skill 路径解析插件 |
| opencode-skills NPM | https://www.npmjs.com/package/@monotykamary/opencode-skills | Path Resolution 实现 |
| opencode-skill-creator | https://github.com/antongulin/opencode-skill-creator | Skill 创建工具 |
| session-dump Skill | https://lobehub.com/zh/skills/thesobercoder-skills-session-dump | __INSTALLED_SKILL_DIR__ 替换 |

### 源码分析

| 来源 | URL | 主题 |
|------|-----|------|
| CSDN 源码解析 | https://devpress.csdn.net/xclaw/69c0d99f0a2f6a37c59989a3.html | Skill 扫描逻辑源码 |
| ADR-002 | https://github.com/Steffen025/pai-opencode/blob/main/docs/architecture/adr/ADR-002-directory-structure-claude-to-opencode.md | Claude→OpenCode 路径迁移 |

### Release Notes

| 版本 | URL |
|------|-----|
| v1.16.2 | https://github.com/anomalyco/opencode/releases/tag/v1.16.2 |
| v1.16.0 | https://github.com/anomalyco/opencode/releases/tag/v1.16.0 |
| v1.15.13 | https://github.com/anomalyco/opencode/releases/tag/v1.15.13 |
| v1.15.12 | https://github.com/anomalyco/opencode/releases/tag/v1.15.12 |
| v1.15.9 | https://github.com/anomalyco/opencode/releases/tag/v1.15.9 |
| v1.15.7 | https://github.com/anomalyco/opencode/releases/tag/v1.15.7 |
| v1.15.4 | https://github.com/anomalyco/opencode/releases/tag/v1.15.4 |
| v1.15.3 | https://github.com/anomalyco/opencode/releases/tag/v1.15.3 |
| v1.14.51 | https://github.com/anomalyco/opencode/releases/tag/v1.14.51 |
| v1.14.48 | https://github.com/anomalyco/opencode/releases/tag/v1.14.48 |
| v1.14.47 | https://github.com/anomalyco/opencode/releases/tag/v1.14.47 |
| v1.14.46 | https://github.com/anomalyco/opencode/releases/tag/v1.14.46 |
| v1.14.45 | https://github.com/anomalyco/opencode/releases/tag/v1.14.45 |
| v1.14.41 | https://github.com/anomalyco/opencode/releases/tag/v1.14.41 |
| v1.14.39 | https://github.com/anomalyco/opencode/releases/tag/v1.14.39 |
| v1.14.38 | https://github.com/anomalyco/opencode/releases/tag/v1.14.38 |
| v1.14.37 | https://github.com/anomalyco/opencode/releases/tag/v1.14.37 |

---

> **免责声明**: 本报告基于公开的 GitHub issues、官方文档和社区资源整理。OpenCode 正在快速迭代，部分信息可能在新版本中已发生变化。建议以官方最新文档为准。
