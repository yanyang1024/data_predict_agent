# 第八章 路径坑点详解

> 适用版本: OpenCode v1.14.32 — v1.15.13

路径处理是 OpenCode 工具与 Skill 开发中最容易出问题的领域之一。同样的代码在 CLI 模式下运行正常，切换到 Desktop App 或 Web Daemon 时却可能完全失效。本章深入剖析 OpenCode 的路径系统，逐一讲解十个最常见的路径坑点，并提供经过验证的解决方案。

核心原则 upfront：**永远不要使用 `process.cwd()` 构建路径**。这是贯穿本章的黄金法则。

---

## 8.1 路径原点 — 不同运行模式下的差异

OpenCode 支持多种运行模式（CLI、Desktop App、Web Daemon、`task()` 子 agent），每种模式下路径原点的行为差异巨大。理解这些差异是避免路径问题的第一步。

### 8.1.1 路径原点对比表

| 运行模式 | `process.cwd()` | `context.directory` | 风险等级 |
|----------|----------------|---------------------|----------|
| CLI（在项目目录启动） | 项目目录 | 项目目录 | 低 |
| CLI（带 `--dir` 参数） | 启动目录 | `--dir` 指定的目录 | **高** |
| Desktop App | `/`（系统根目录） | 项目目录 | **极高** |
| Web Daemon | 启动 daemon 的目录 | Web UI 选择的项目目录 | **高** |
| `task()` 子 agent | 父进程 cwd | `ctx.directory`（应然） | **高** |

**关键洞察**：`process.cwd()` 的返回值在不同模式下可能是项目目录、启动目录、甚至是系统根目录 `/`。唯有 `context.directory` 能够稳定指向当前会话的实际工作目录。

### 8.1.2 为什么 Desktop App 的 cwd 是 `/`

Desktop App 采用 Electron 架构，主进程在启动时并未 `chdir` 到项目目录，而是保持在了操作系统层面的进程启动位置。在 macOS 上这通常表现为 `/`，在 Windows 上则可能是 `C:\Windows\System32` 类似的系统目录。这意味着：

```typescript
// 在 Desktop App 中，这段代码试图读取系统根目录下的文件！
const content = await fs.readFile("./README.md", "utf-8");  // 读取 /README.md
```

这段代码在 CLI 模式下可以正确读取项目的 README.md，但在 Desktop App 中却会尝试读取系统根目录下的 `README.md` 文件，通常会导致 `ENOENT` 错误。

### 8.1.3 `--dir` 参数带来的双重路径

CLI 模式下使用 `--dir` 参数时，`process.cwd()` 和 `context.directory` 会出现分离：

```bash
# 当前在 ~/workspace
$ opencode --dir ./projects/my-app "分析代码"

# process.cwd() → ~/workspace
# context.directory → ~/workspace/projects/my-app
```

这种情况下使用 `process.cwd()` 构建路径会指向错误的目录。这看似直观的行为差异，是导致工具在 `--dir` 模式下失效的头号原因。

---

## 8.2 Skill 路径系统详解

Skill 是 OpenCode 的核心扩展机制，其路径系统采用双层架构：项目级与全局级。

### 8.2.1 Skill 的存储位置

Skill 文件遵循固定的目录结构和命名约定：

**项目级 Skill**（推荐，便于版本控制和团队协作）：

```
项目根目录/
├── .opencode/
│   └── skills/
│       ├── my-skill/
│       │   └── SKILL.md          # Skill 定义文件
│       ├── code-review/
│       │   └── SKILL.md
│       └── documentation/
│           ├── SKILL.md
│           └── references/       # Skill 相关资源
│               └── guide.md
```

**全局级 Skill**（适用于个人常用工具）：

```
~/.config/opencode/skills/
├── my-skill/
│   └── SKILL.md
└── global-helper/
    └── SKILL.md
```

### 8.2.2 Skill 发现机制

OpenCode 的 Skill 发现采用**从 CWD 向上遍历**的策略，直至到达 git worktree 根目录。具体流程如下：

```
1. 获取当前工作目录（context.directory，非 process.cwd()）
2. 检查 <cwd>/.opencode/skills/ 下是否存在匹配的技能目录
3. 若未找到，向上一级目录移动
4. 重复步骤 2-3，直到到达 git worktree 根目录
5. 仍未找到时，检查全局级 ~/.config/opencode/skills/
```

这个向上遍历机制意味着：在 monorepo 的子包目录中运行 OpenCode 时，可以自动发现 repo 根目录定义的 Skill。

```bash
# 假设 monorepo 结构：
# /repo/.opencode/skills/shared/SKILL.md
# /repo/packages/frontend/

$ cd /repo/packages/frontend
$ opencode "使用 shared skill"

# OpenCode 会向上遍历，最终在 /repo/.opencode/skills/shared/ 找到该 Skill
```

### 8.2.3 Skill 命名规范

Skill 名称必须满足正则表达式 `^[a-z0-9]+(-[a-z0-9]+)*$`，即：

- 只能包含小写字母、数字和连字符
- 必须以字母或数字开头和结尾
- 不能出现连续连字符
- **必须与目录名完全一致**

```
有效名称: my-skill, code-review, v2-migrator, doc-generator
无效名称: My_Skill, code_review, my--skill, -starter, skill-
```

命名不匹配是最常见的问题之一。如果目录名为 `code_review`（下划线），而引用时使用 `code-review`（连字符），OpenCode 将无法找到该 Skill。

---

## 8.3 Tool 路径系统详解

自定义 Tool 的路径系统与 Skill 类似，同样采用项目级和全局级双层架构，但组织方式有所不同。

### 8.3.1 Tool 的存储位置

**项目级 Tool**：

```
项目根目录/
├── .opencode/
│   └── tools/
│       ├── code-analyzer.ts      # 工具名: code-analyzer
│       ├── doc-generator.js      # 工具名: doc-generator
│       └── git-helper.ts         # 工具名: git-helper
```

**全局级 Tool**：

```
~/.config/opencode/tools/
├── code-analyzer.ts
└── universal-formatter.js
```

### 8.3.2 Tool 命名规则

Tool 的命名方式非常直接：**文件名（不含扩展名）即工具名**。`code-analyzer.ts` 对应的工具名就是 `code-analyzer`。

支持的文件扩展名：
- `.ts` — TypeScript 文件（推荐，支持类型检查）
- `.js` — JavaScript 文件

### 8.3.3 Tool 的覆盖机制

自定义 Tool 与内置 Tool 同名时，**自定义 Tool 优先**，完全覆盖内置实现。这一机制既是强大的定制手段，也是潜在的风险来源。

```typescript
// .opencode/tools/read-file.ts
// 如果创建了名为 read-file 的自定义工具，
// 它将完全替代内置的 read-file 工具

export default async function readFile({ path }: { path: string }) {
  // 自定义实现...
}
```

**警告**：覆盖内置工具时需要确保接口兼容，否则会导致依赖该工具的其他功能出现异常。

### 8.3.4 Tool 发现路径

Tool 的发现路径与 Skill 类似，同样采用向上遍历策略：

```
1. 从 context.directory 开始
2. 检查 .opencode/tools/*.ts 和 .opencode/tools/*.js
3. 未找到时向上一级目录遍历（直到 git worktree 根）
4. 最后检查全局级 ~/.config/opencode/tools/
```

---

## 8.4 Tool Execute 的 Context 对象

Tool 脚本通过 Context 对象获取路径信息。理解 Context 对象的每个属性是编写健壮工具的前提。

### 8.4.1 Context 属性一览

| 属性 | 类型 | 说明 | 可靠性 |
|------|------|------|--------|
| `context.directory` | `string` | 会话的工作目录，**推荐用于路径构建** | 高，所有模式一致 |
| `context.worktree` | `string` | Git worktree 根目录 | 高，所有模式一致 |

### 8.4.2 `directory` vs `worktree` 的区别

在大多数项目中，`directory` 和 `worktree` 指向同一位置。但在以下场景中存在差异：

```bash
# 场景 1: 在 monorepo 子包中运行
# /repo/.git
# /repo/packages/frontend/
# directory → /repo/packages/frontend
# worktree → /repo

# 场景 2: 使用 git worktree 命令创建的独立工作树
# /repo/main/.git
# /repo/feature-branch/
# directory → /repo/feature-branch
# worktree → /repo/feature-branch
```

**选择原则**：
- 需要访问项目根目录文件（如 `.opencode/` 配置）→ 使用 `context.worktree`
- 需要访问当前工作目录下的文件 → 使用 `context.directory`
- 不确定时 → 优先使用 `context.worktree`

### 8.4.3 在 Tool 中访问 Context

```typescript
// .opencode/tools/my-tool.ts
import * as path from "path";
import * as fs from "fs/promises";

export default async function myTool(
  args: { target: string },
  context: { directory: string; worktree: string }
) {
  // 使用 context.worktree 构建可靠路径
  const configPath = path.join(context.worktree, ".opencode", "config.yaml");
  const config = await fs.readFile(configPath, "utf-8");

  // 使用 context.directory 作为操作基目录
  const targetPath = path.resolve(context.directory, args.target);

  return { config, targetPath };
}
```

---

## 8.5 十大路径坑点详解

以下是 OpenCode 开发者和用户在实际使用中遇到的十个最常见路径问题。每个坑点包含问题描述、复现步骤、解决方案和参考来源。

---

### 坑点 1: Desktop App 中 `process.cwd()` 是 `/`

**严重等级**: 🔴 极高  
**影响版本**: 所有版本（架构设计特性）

#### 问题描述

Desktop App 模式下，工具执行时的 `process.cwd()` 返回系统根目录 `/`（macOS/Linux）或系统目录（Windows），而非项目目录。任何基于 `process.cwd()` 或相对路径的文件操作都会失败或操作到错误的文件。

#### 复现步骤

```typescript
// .opencode/tools/reproduce-pitfall-1.ts
// 这个工具在 CLI 中正常工作，在 Desktop App 中必然失败

export default async function reproduce(args: {}, context: any) {
  const cwd = process.cwd();
  console.log("process.cwd() =", cwd);
  // Desktop App 输出: /
  // CLI 输出: /Users/you/project

  // 危险操作：尝试读取 "当前目录" 下的文件
  const fs = await import("fs/promises");
  try {
    // Desktop App 中这实际上读取的是 /package.json！
    const content = await fs.readFile("./package.json", "utf-8");
    return { success: true, content: content.slice(0, 100) };
  } catch (e: any) {
    // Desktop App 中几乎必然触发此错误
    return { success: false, error: e.message };
  }
}
```

**复现流程**：

1. 在项目的 `.opencode/tools/` 目录创建上述 Tool
2. 通过 CLI 运行 `opencode "调用 reproduce 工具"` → 成功
3. 通过 Desktop App 打开同一项目，执行相同指令 → 失败，报错 `ENOENT`

#### 解决方案

**始终使用 `context.worktree` 替代 `process.cwd()`**：

```typescript
// ✅ 正确做法
import * as path from "path";
import * as fs from "fs/promises";

export default async function fixedTool(
  args: {},
  context: { directory: string; worktree: string }
) {
  // 使用 context.worktree 构建绝对路径
  const packagePath = path.join(context.worktree, "package.json");
  const content = await fs.readFile(packagePath, "utf-8");
  return { content: content.slice(0, 100) };
}
```

#### 参考来源

- OpenCode Desktop App 架构文档
- Node.js `process.cwd()` 行为说明

---

### 坑点 2: Skill 相对路径解析为 CWD 而非 Skill 目录 (Issue #17101)

**严重等级**: 🔴 高  
**影响版本**: v1.14.32 — v1.15.13  
**关联 Issue**: #17101

#### 问题描述

Agent 在执行 Skill 的 SKILL.md 时，将其中的 `references/`、`scripts/` 等相对路径解析为**当前工作目录（CWD）**，而非 Skill 文件所在的目录。这意味着 Skill 中的文档引用和脚本调用在不同执行位置会产生不同行为。

#### 复现步骤

假设有以下 Skill 结构：

```
.opencode/skills/my-skill/
├── SKILL.md
└── references/
    └── guide.md
```

SKILL.md 内容：

```markdown
# My Skill

请先阅读参考文档：

Read references/guide.md  ← 这里的相对路径
```

复现流程：

```bash
# 场景 A: 从项目根目录运行（"幸运"情况）
$ cd /project-root
$ opencode "使用 my-skill"
# 如果 /project-root/references/guide.md 存在，则意外成功
# 如果不存在，报错 ENOENT

# 场景 B: 从子目录运行（必然失败）
$ cd /project-root/src/components
$ opencode "使用 my-skill"
# 尝试读取 /project-root/src/components/references/guide.md
# 几乎必然 ENOENT
```

#### 根因分析

Agent 在解析 SKILL.md 中的相对路径时，使用了执行时的 `process.cwd()` 作为路径基点，而非 SKILL.md 文件所在目录。这导致 Skill 的可移植性严重受损 — 同一个 Skill 在不同位置执行会产生不同结果。

#### 解决方案

**方案 A：使用 `skill_resource` 工具（推荐）**

```markdown
# My Skill

请先阅读参考文档：

skill_resource skill_name="my-skill" relative_path="references/guide.md"
```

`skill_resource` 工具会正确解析相对路径，以 Skill 所在目录为基准，不受 CWD 影响。

**方案 B：安装 opencode-skills/opencode-skillful 插件**

该插件提供了增强的路径解析能力，能够正确处理 Skill 内部的相对路径。

**方案 C：在 Skill 中使用绝对路径引用**

```markdown
# 不推荐但可行：使用 {{WORKTREE}} 占位符（如果 Skill 引擎支持）
Read {{WORKTREE}}/.opencode/skills/my-skill/references/guide.md
```

#### 参考来源

- Issue #17101: "Skill relative paths resolved against CWD instead of skill directory"

---

### 坑点 3: `task()` 子 agent 使用 `process.cwd()` 解析 Skill

**严重等级**: 🔴 高  
**影响版本**: v1.14.32

#### 问题描述

`resolveSkillContent2` 函数在解析 Skill 内容时，未接收 `directory` 参数，导致回退到 `process.cwd()`。当父 agent 通过 `task()` 创建子 agent 时，子 agent 的 CWD 继承自父进程，可能与实际项目目录不一致。

#### 复现步骤

```typescript
// 父 agent 在某个目录中运行
task("分析代码", {
  // 子 agent 应该使用 ctx.directory 作为工作目录
  // 但实际上 resolveSkillContent2 使用了 process.cwd()
  skill: "code-analyzer"
});
```

```
复现流程：
1. 父 agent 在 /project-root/packages/frontend 运行
2. 父 agent 调用 task() 触发子 agent
3. 子 agent 的 process.cwd() → /project-root/packages/frontend（继承）
4. resolveSkillContent2 尝试在此目录解析 Skill
5. 如果 Skill 定义在 /project-root/.opencode/skills/，遍历机制应该能找到
6. 但如果涉及 Skill 内部路径引用，就会基于错误的 CWD 解析
```

#### 解决方案

在 v1.15.13 中，确保子 agent 正确接收并使用 `ctx.directory`：

```typescript
// 父 agent 中明确传递目录上下文
task("分析代码", {
  skill: "code-analyzer",
  directory: context.worktree  // 显式指定工作目录
});
```

对于 Tool 开发者，应在 Tool 中显式处理目录：

```typescript
export default async function myTool(
  args: {},
  context: { directory: string; worktree: string }
) {
  // 始终使用 context.directory，不依赖 process.cwd()
  const skillPath = path.join(context.worktree, ".opencode", "skills");
  // ...
}
```

#### 参考来源

- `resolveSkillContent2` 源码分析
- v1.15.12 Session directory persistence 修复说明

---

### 坑点 4: Plugin ToolContext 缺少 `directory` 和 `worktree`

**严重等级**: 🟡 中高  
**影响版本**: v1.14.32 — v1.15.13

#### 问题描述

自定义插件（Plugin）中 Tool 的 Context 对象**不包含 `directory` 或 `worktree` 属性**。这与原生 Tool 的 Context 接口不一致，导致插件开发者无法可靠地获取工作目录信息。

#### 复现步骤

```typescript
// my-plugin/index.ts
export default {
  tools: [
    {
      name: "plugin-tool",
      handler: async (args: any, context: any) => {
        console.log("context keys:", Object.keys(context));
        // 输出可能不包含 "directory" 或 "worktree"

        // 尝试访问会返回 undefined
        console.log(context.directory);  // undefined
        console.log(context.worktree);   // undefined

        // 被迫回退到 process.cwd() — 坑点 1 的陷阱！
        const cwd = process.cwd();
        // ...
      }
    }
  ]
};
```

#### 影响范围

这个坑点的影响特别隐蔽：
- 开发阶段在 CLI 中测试插件 → 正常工作（因为 `process.cwd()` "恰好"正确）
- 用户在生产环境 Desktop App 中使用 → 路径错误，功能失效
- 调试困难：开发者复现不了用户报告的问题

#### 解决方案

**方案 A：通过其他方式传递路径**

```typescript
// 在插件配置中硬编码或使用环境变量
export default {
  tools: [
    {
      name: "plugin-tool",
      handler: async (args: any, context: any) => {
        // 尝试从参数中接收目录
        const workDir = args._workDir || process.env.OPENCODE_WORKDIR;
        if (!workDir) {
          throw new Error("Plugin tool requires _workDir argument");
        }
        // ...
      }
    }
  ]
};
```

**方案 B：检测缺失的 Context 属性并给出明确错误**

```typescript
handler: async (args: any, context: any) => {
  if (!context.directory || !context.worktree) {
    // 记录详细的诊断信息
    console.error("Plugin ToolContext missing required properties:");
    console.error("  Expected: directory, worktree");
    console.error("  Actual:", Object.keys(context));

    // 在 Desktop App 中给出用户友好的提示
    throw new Error(
      "此插件需要 directory/worktree 上下文。" +
      "如果在 Desktop App 中遇到此问题，请使用 CLI 模式或更新到最新版本。"
    );
  }
  // ...
}
```

#### 参考来源

- Plugin API 文档
- ToolContext 接口定义

---

### 坑点 5: Windows 子 agent 目录漂移到 LOCALAPPDATA

**严重等级**: 🟡 中  
**影响版本**: v1.14.32  
**影响平台**: Windows

#### 问题描述

在 Windows 平台上，子 agent（通过 `task()` 创建）的工作目录会异常漂移到 `LOCALAPPDATA` 目录（通常是 `C:\Users\<用户名>\AppData\Local`），而非预期的项目目录。这导致所有相对路径解析和文件操作都指向了错误的位置。

#### 复现步骤

```bash
# Windows PowerShell
PS C:\Users\Developer\MyProject> opencode "启动分析任务"
```

```typescript
// 父 agent
console.log("Parent directory:", context.directory);
// → C:\Users\Developer\MyProject

task("执行分析", {
  skill: "analyzer"
});

// 子 agent 中
console.log("Child directory:", context.directory);
// 预期: C:\Users\Developer\MyProject
// 实际: C:\Users\Developer\AppData\Local （错误！）
```

#### 根因分析

Windows 平台上子进程的 CWD 继承机制与 Unix 存在差异。当父进程在特定条件下（如 Electron 渲染进程发起的子进程），子进程可能被放置在系统的临时/本地数据目录中。

#### 解决方案

**显式传递并切换目录**：

```typescript
// 父 agent 中
task("执行分析", {
  skill: "analyzer",
  directory: context.worktree  // 显式指定，覆盖继承的 CWD
});
```

**子 agent Tool 中的防御性编程**：

```typescript
export default async function analyzerTool(
  args: {},
  context: { directory: string }
) {
  // 验证目录的合理性
  const expectedDir = context.directory;
  const fs = await import("fs");

  // 检查目录中是否存在预期的项目文件
  if (!fs.existsSync(path.join(expectedDir, "package.json"))) {
    // 目录可能不正确，尝试从 worktree 恢复
    console.warn(`Directory ${expectedDir} does not contain expected files`);
  }

  // 继续操作...
}
```

#### 参考来源

- Windows 子进程 CWD 继承行为
- v1.15.12 Session directory persistence 修复

---

### 坑点 6: glob 工具默认路径 `["."]` 继承不到正确的 cwd

**严重等级**: 🟡 中  
**影响版本**: v1.14.32 — v1.15.13

#### 问题描述

OpenCode 内置的 `glob` 工具在默认参数 `paths: ["."]` 下，使用 Node.js 的 glob 实现，其路径解析基于 `process.cwd()` 而非 `context.directory`。这意味着在不同运行模式下，相同的 glob 模式会匹配到不同的文件集合。

#### 复现步骤

```typescript
// 在 Tool 中使用 glob
glob({
  paths: ["."],           // 默认参数，危险！
  pattern: "**/*.ts"      // 搜索所有 TypeScript 文件
});

// CLI 模式：正确搜索项目目录下的 .ts 文件
// Desktop App：搜索 / 下的所有 .ts 文件（权限错误+结果为空）
// --dir 模式：搜索启动目录而非项目目录
```

#### 解决方案

**始终显式指定 glob 的 paths 参数**：

```typescript
// ✅ 正确做法：使用 context.directory 或 context.worktree
glob({
  paths: [context.directory],  // 明确指定搜索基目录
  pattern: "**/*.ts"
});

// 或者搜索整个项目
glob({
  paths: [context.worktree],
  pattern: "packages/*/src/**/*.ts"
});
```

**封装安全的 glob 调用**：

```typescript
// utils.ts
export async function safeGlob(
  pattern: string,
  context: { directory: string; worktree: string },
  scope: "directory" | "worktree" = "directory"
) {
  const basePath = scope === "directory" ? context.directory : context.worktree;

  // 确保基目录存在且有效
  const fs = await import("fs/promises");
  try {
    await fs.access(basePath);
  } catch {
    throw new Error(`Base path does not exist or is not accessible: ${basePath}`);
  }

  return glob({
    paths: [basePath],
    pattern
  });
}
```

#### 参考来源

- glob 工具文档
- Node.js glob 模块路径解析行为

---

### 坑点 7: 单数/复数目录名不一致 (`skill/` vs `skills/`)

**严重等级**: 🟢 低（但极易踩到）  
**影响版本**: 所有版本

#### 问题描述

OpenCode 的路径系统中同时存在单数和复数形式的目录名，容易混淆：

| 用途 | 正确路径 | 常见错误 |
|------|----------|----------|
| Skill 存储 | `.opencode/skills/` | `.opencode/skill/` |
| Tool 存储 | `.opencode/tools/` | `.opencode/tool/` |

创建目录时使用单数形式会导致 OpenCode 无法发现 Skill 或 Tool。

#### 复现步骤

```bash
# 错误创建
mkdir -p .opencode/skill/my-skill   # ❌ 单数 skill

# 正确创建
mkdir -p .opencode/skills/my-skill  # ✅ 复数 skills
```

#### 解决方案

使用自动化脚本或脚手架创建 Skill/Tool 目录，避免手动输入错误：

```bash
# 创建 Skill 的便捷脚本
#!/bin/bash
# create-skill.sh

SKILL_NAME=$1

if [ -z "$SKILL_NAME" ]; then
  echo "Usage: ./create-skill.sh <skill-name>"
  exit 1
fi

# 验证名称格式
if ! echo "$SKILL_NAME" | grep -qE '^[a-z0-9]+(-[a-z0-9]+)*$'; then
  echo "Invalid skill name: $SKILL_NAME"
  echo "Must match: ^[a-z0-9]+(-[a-z0-9]+)*$"
  exit 1
fi

# 使用正确的复数路径
SKILL_DIR=".opencode/skills/$SKILL_NAME"
mkdir -p "$SKILL_DIR"

# 创建 SKILL.md 模板
cat > "$SKILL_DIR/SKILL.md" << 'EOF'
# Skill Name

## Description

Describe what this skill does.

## Usage

Explain how to use this skill.
EOF

echo "Created skill at: $SKILL_DIR"
```

#### 参考来源

- OpenCode 目录结构文档
- Skill/Tool 命名规范

---

### 坑点 8: Symlink 目录导致 TUI 空白响应

**严重等级**: 🟡 中  
**影响版本**: v1.14.32 — v1.15.13

#### 问题描述

当 OpenCode 项目目录或 `.opencode` 目录是通过符号链接（symlink）挂载时，TUI（终端用户界面）可能出现空白响应或加载异常。路径解析在处理符号链接时的不一致性导致 TUI 无法正确渲染。

#### 复现步骤

```bash
# 创建实际项目目录
mkdir -p ~/real-projects/my-project/.opencode/skills/my-skill
echo "# Skill" > ~/real-projects/my-project/.opencode/skills/my-skill/SKILL.md

# 通过 symlink 访问
cd ~/workspace
ln -s ~/real-projects/my-project linked-project
cd linked-project

# 启动 OpenCode
opencode "使用 my-skill"
# TUI 可能显示空白或加载失败
```

#### 根因分析

符号链接导致了"物理路径"与"逻辑路径"的分裂：
- `process.cwd()` 返回逻辑路径（含 symlink）：`~/workspace/linked-project`
- `fs.realpath()` 返回物理路径：`~/real-projects/my-project`
- OpenCode 的内部路径缓存和文件监控基于物理路径
- TUI 的渲染逻辑可能使用了不一致的路径表示

#### 解决方案

**方案 A：使用物理路径启动 OpenCode**

```bash
# 使用 realpath 解析物理路径后再启动
cd $(realpath ~/workspace/linked-project)
opencode "使用 my-skill"
```

**方案 B：避免在 `.opencode` 目录使用 symlink**

```bash
# 如果只需要共享 Skill，复制而非链接
cp -r ~/shared-skills/my-skill .opencode/skills/

# 或者使用 Skill 的向上遍历机制（无需 symlink）
```

**方案 C：在 Tool 中处理 symlink**

```typescript
import * as fs from "fs/promises";

export default async function safeTool(
  args: { path: string },
  context: { directory: string }
) {
  // 解析符号链接到真实路径
  const realPath = await fs.realpath(
    path.resolve(context.directory, args.path)
  );

  // 验证路径仍在项目范围内（防止目录遍历攻击）
  const worktree = context.worktree || context.directory;
  if (!realPath.startsWith(worktree)) {
    throw new Error("Path escapes project directory");
  }

  // 使用解析后的路径进行操作
  const content = await fs.readFile(realPath, "utf-8");
  return { content };
}
```

#### 参考来源

- Node.js `fs.realpath()` 文档
- TUI 渲染路径解析逻辑

---

### 坑点 9: `opencode import` 忽略 CWD

**严重等级**: 🟡 中  
**影响版本**: v1.14.32 — v1.15.13

#### 问题描述

`opencode import` 命令在导入 Skill 或 Tool 时，**忽略当前工作目录**，可能将内容导入到非预期的位置。用户期望导入到当前项目，但实际可能导入到了全局配置或其他位置。

#### 复现步骤

```bash
# 在项目目录中
cd /my-project

# 期望：导入到 /my-project/.opencode/skills/
# 实际：可能导入到 ~/.config/opencode/skills/
opencode import skill some-skill

# 验证 — 发现项目目录中没有
ls .opencode/skills/some-skill
# ls: cannot access '.opencode/skills/some-skill': No such file or directory

# 但却在全局目录找到了
ls ~/.config/opencode/skills/some-skill
# SKILL.md
```

#### 根因分析

`import` 命令的路径解析逻辑优先级：
1. 检查命令行是否显式指定了 `--dir` 或 `--global`
2. 如果未指定，按固定优先级选择目标位置
3. 该优先级可能与用户的 CWD 预期不符

#### 解决方案

**显式指定导入目标**：

```bash
# 导入到项目（显式指定目录）
opencode import skill some-skill --dir ./

# 或者先确保 .opencode 目录存在
mkdir -p .opencode/skills
opencode import skill some-skill

# 导入到全局（明确意图）
opencode import skill some-skill --global
```

**导入后验证**：

```bash
#!/bin/bash
# import-and-verify.sh

SKILL_NAME=$1
PROJECT_DIR=$(pwd)

opencode import skill "$SKILL_NAME"

# 验证导入位置
if [ -f "$PROJECT_DIR/.opencode/skills/$SKILL_NAME/SKILL.md" ]; then
  echo "✅ Skill imported to project: $PROJECT_DIR/.opencode/skills/$SKILL_NAME"
elif [ -f "$HOME/.config/opencode/skills/$SKILL_NAME/SKILL.md" ]; then
  echo "⚠️ Skill imported to global: ~/.config/opencode/skills/$SKILL_NAME"
  echo "   If you intended to import to project, use:"
  echo "   opencode import skill $SKILL_NAME --dir $PROJECT_DIR"
else
  echo "❌ Import failed: Skill not found in project or global location"
fi
```

#### 参考来源

- `opencode import` 命令帮助文档
- CLI 参数解析逻辑

---

### 坑点 10: Plugin skill 发现忽略 `skills.paths` 配置

**严重等级**: 🟡 中  
**影响版本**: v1.14.32 — v1.15.13

#### 问题描述

通过插件（Plugin）机制定义的 Skill 发现路径配置 `skills.paths` 被忽略。用户在 `.opencode/config.yaml` 或全局配置中自定义的 Skill 搜索路径对插件 Skill 不起作用。

#### 复现步骤

```yaml
# .opencode/config.yaml
skills:
  paths:
    - "./custom-skills"      # 自定义 Skill 目录
    - "../shared/skills"     # 共享 Skill 目录
```

```typescript
// my-plugin.ts
export default {
  // 插件内尝试使用自定义路径发现 Skill
  skills: {
    // 期望：从 config.skills.paths 中加载
    // 实际：仅使用默认路径，忽略配置
  }
};
```

#### 解决方案

**方案 A：使用标准 Skill 目录结构**

将 Skill 放在默认的发现路径中：

```
# 标准项目级路径
.opencode/skills/<name>/SKILL.md

# 标准全局路径
~/.config/opencode/skills/<name>/SKILL.md
```

**方案 B：在插件中手动读取配置**

```typescript
import * as fs from "fs/promises";
import * as path from "path";
import * as yaml from "yaml";

export default {
  async init(context: { worktree: string }) {
    // 手动读取并解析配置
    const configPath = path.join(context.worktree, ".opencode", "config.yaml");
    let customPaths: string[] = [];

    try {
      const configContent = await fs.readFile(configPath, "utf-8");
      const config = yaml.parse(configContent);
      customPaths = config.skills?.paths || [];
    } catch {
      // 配置文件不存在或解析失败
    }

    // 将自定义路径加入搜索列表
    const searchPaths = [
      ...customPaths.map(p => path.resolve(context.worktree, p)),
      path.join(context.worktree, ".opencode", "skills"),
      path.join(process.env.HOME || "", ".config", "opencode", "skills")
    ];

    return { searchPaths };
  }
};
```

#### 参考来源

- Plugin API 文档
- Skill 配置加载机制
- `.opencode/config.yaml` 配置规范

---

## 8.6 Tool 脚本引用最佳实践

以下代码示例展示了在 Tool 中引用外部脚本和文件的正确方式与错误方式。

### 8.6.1 构建脚本路径

```typescript
// .opencode/tools/run-analysis.ts
import * as path from "path";

export default async function runAnalysis(
  args: { target?: string },
  context: { directory: string; worktree: string }
) {
  // ✅ 正确：使用 context.worktree 构建脚本路径
  // 这样无论从哪里运行，都能找到项目内的脚本
  const scriptPath = path.join(context.worktree, ".opencode", "tools", "my-script.py");

  // ✅ 正确：验证脚本存在
  const fs = await import("fs/promises");
  try {
    await fs.access(scriptPath);
  } catch {
    throw new Error(`Script not found: ${scriptPath}`);
  }

  // ✅ 正确：使用 context.directory 作为命令执行目录
  // 这样脚本中的相对路径会基于项目目录解析
  const target = args.target || ".";
  const result = await Bun.$`cd ${context.directory} && python3 ${scriptPath} ${target}`;

  return {
    stdout: result.stdout.toString(),
    stderr: result.stderr.toString(),
    exitCode: result.exitCode
  };
}
```

### 8.6.2 读取配置文件

```typescript
// .opencode/tools/load-config.ts
import * as path from "path";
import * as fs from "fs/promises";

export default async function loadConfig(
  args: {},
  context: { directory: string; worktree: string }
) {
  // ✅ 正确：按优先级搜索配置文件
  const searchPaths = [
    // 1. 当前目录
    path.join(context.directory, ".opencode", "config.yaml"),
    // 2. 项目根目录
    path.join(context.worktree, ".opencode", "config.yaml"),
    // 3. 全局配置
    path.join(process.env.HOME || "", ".config", "opencode", "config.yaml")
  ];

  for (const configPath of searchPaths) {
    try {
      const content = await fs.readFile(configPath, "utf-8");
      return {
        found: true,
        path: configPath,
        content: content
      };
    } catch {
      continue;  // 文件不存在，尝试下一个
    }
  }

  return {
    found: false,
    message: "No config file found in any standard location"
  };
}
```

### 8.6.3 处理用户输入的路径参数

```typescript
// .opencode/tools/read-project-file.ts
import * as path from "path";
import * as fs from "fs/promises";

export default async function readProjectFile(
  args: { filePath: string },
  context: { directory: string; worktree: string }
) {
  // ✅ 正确：解析用户输入的路径，以项目目录为基准
  const resolvedPath = path.resolve(context.directory, args.filePath);

  // ✅ 正确：安全检查 —— 防止目录遍历攻击
  const worktreeReal = await fs.realpath(context.worktree);
  const targetReal = await fs.realpath(resolvedPath).catch(() => resolvedPath);

  if (!targetReal.startsWith(worktreeReal)) {
    throw new Error(
      `Path "${args.filePath}" escapes project directory. ` +
      `Resolved to "${targetReal}" which is outside "${worktreeReal}".`
    );
  }

  // ✅ 正确：读取文件
  const content = await fs.readFile(resolvedPath, "utf-8");
  return { path: resolvedPath, content };
}
```

### 8.6.4 反模式：依赖 process.cwd()

```typescript
// .opencode/tools/anti-pattern.ts
import * as path from "path";
import * as fs from "fs/promises";

export default async function antiPattern(args: {}) {
  // ❌ 错误：依赖 process.cwd() — 在 Desktop App 中会失败
  const scriptPath = path.resolve(".opencode/tools/my-script.py");
  // Desktop App 中解析为 /.opencode/tools/my-script.py

  // ❌ 错误：使用相对路径读取文件
  const config = await fs.readFile("./package.json", "utf-8");
  // Desktop App 中读取 /package.json

  // ❌ 错误：假设 cwd 就是项目目录
  const result = await Bun.$`python3 my-script.py`;
  // 在当前目录下找不到 my-script.py

  return { scriptPath, config: config.slice(0, 50) };
}
```

---

## 8.7 SKILL.md 文档引用规范

SKILL.md 中引用其他文档或资源时，必须使用正确的引用方式，避免相对路径解析到错误位置。

### 8.7.1 推荐的引用方式

```markdown
# My Skill

## 参考资料

<!-- ✅ 推荐：使用 skill_resource 工具 -->
<!-- 该工具会相对于 Skill 所在目录解析路径 -->
skill_resource skill_name="my-skill" relative_path="references/guide.md"

<!-- ✅ 推荐：引用多个资源 -->
skill_resource skill_name="my-skill" relative_path="references/api-reference.md"
skill_resource skill_name="my-skill" relative_path="references/examples/

## 执行脚本

<!-- ✅ 推荐：使用完整路径构建 -->
Execute the script at:
skill_resource skill_name="my-skill" relative_path="scripts/setup.sh"
```

### 8.7.2 不推荐的引用方式

```markdown
# My Skill

## 参考资料

<!-- ❌ 不推荐：相对路径会解析为 CWD -->
Read references/guide.md
<!-- 如果 CWD 不是 Skill 所在目录，会找不到文件 -->

<!-- ❌ 不推荐：使用文件系统命令 -->
cat references/guide.md
<!-- 同样在 CWD 变化时会失败 -->

<!-- ❌ 不推荐：假设固定目录结构 -->
Read .opencode/skills/my-skill/references/guide.md
<!-- 如果 Skill 在全局目录或不同层级，路径会错误 -->
```

### 8.7.3 skill_resource 工具详解

`skill_resource` 是 OpenCode 提供的专门用于 Skill 内部资源引用的工具，其路径解析逻辑如下：

```
skill_resource skill_name="<name>" relative_path="<path>"

解析过程：
1. 根据 skill_name 查找 Skill 目录（使用标准发现机制）
2. 将 relative_path 相对于 Skill 目录解析
3. 返回文件内容或路径

优点：
- 不受 CWD 影响
- 支持项目级和全局级 Skill
- 路径解析与 Skill 发现一致
```

### 8.7.4 安装 opencode-skillful 插件

对于更复杂的 Skill 资源管理需求，可以安装 `opencode-skills/opencode-skillful` 插件：

```bash
# 安装插件
opencode plugin install opencode-skills/opencode-skillful
```

该插件提供了增强的路径解析能力，包括：
- 自动相对路径修正
- 多目录 Skill 资源发现
- 资源缓存和预加载

---

## 8.8 版本差异说明

### 8.8.1 v1.14.32 → v1.15.13 路径相关修复

| 版本 | 修复内容 | 影响 |
|------|----------|------|
| v1.15.12 | Session directory persistence 修复 | 子 agent 目录现在更稳定 |
| v1.15.13 | 配置向上加载机制 | 支持从子目录继承父目录配置 |
| v1.15.13 | `task()` 目录传递修复 | 子 agent 正确接收 `ctx.directory` |

### 8.8.2 升级建议

**从 v1.14.32 升级到 v1.15.13**：

1. 升级后测试 Desktop App 中的工具行为
2. 验证 `task()` 子 agent 的目录是否正确
3. 检查自定义插件的 ToolContext 是否包含 directory/worktree
4. 移除之前为绕过路径问题添加的临时修复代码

```bash
# 版本检查
opencode --version

# 测试路径行为（创建一个诊断工具）
# .opencode/tools/diagnose-paths.ts
cat > .opencode/tools/diagnose-paths.ts << 'EOF'
import * as path from "path";
import * as fs from "fs/promises";

export default async function diagnosePaths(
  args: {},
  context: { directory: string; worktree: string }
) {
  const results: Record<string, any> = {};

  // 测试 context.directory
  results.contextDirectory = {
    value: context.directory,
    exists: await fs.access(context.directory).then(() => true).catch(() => false),
    hasPackageJson: await fs.access(path.join(context.directory, "package.json"))
      .then(() => true).catch(() => false)
  };

  // 测试 context.worktree
  results.contextWorktree = {
    value: context.worktree,
    exists: await fs.access(context.worktree).then(() => true).catch(() => false),
    isGitRepo: await fs.access(path.join(context.worktree, ".git"))
      .then(() => true).catch(() => false)
  };

  // 测试 process.cwd()（用于对比）
  results.processCwd = {
    value: process.cwd(),
    warning: process.cwd() === "/" ? "DESKTOP_APP_DETECTED" : null
  };

  return results;
}
EOF
```

---

## 8.9 核心原则：永不使用 process.cwd()

### 8.9.1 为什么 process.cwd() 不可信

`process.cwd()` 在以下场景中会给出错误结果：

| 场景 | `process.cwd()` 返回值 | 预期值 |
|------|------------------------|--------|
| Desktop App | `/` | 项目目录 |
| `--dir` 参数 | 启动目录 | `--dir` 指定目录 |
| Web Daemon | daemon 启动目录 | Web UI 选择的项目目录 |
| `task()` 子 agent | 父进程 CWD | `ctx.directory` |
| Windows 子进程 | `LOCALAPPDATA` | 项目目录 |
| Symlink 目录 | 逻辑路径 | 物理路径 |

**结论**：`process.cwd()` 的返回值在任何模式下都不可作为路径构建的可靠基础。

### 8.9.2 黄金法则

```typescript
// ❌ NEVER DO THIS
const configPath = path.resolve(".opencode/config.yaml");
const scriptPath = path.join(process.cwd(), "scripts", "build.sh");
const file = await fs.readFile("./README.md");

// ✅ ALWAYS DO THIS
const configPath = path.join(context.worktree, ".opencode", "config.yaml");
const scriptPath = path.join(context.worktree, "scripts", "build.sh");
const file = await fs.readFile(path.join(context.directory, "README.md"));
```

### 8.9.3 迁移检查清单

将现有工具迁移到正确的路径处理模式：

- [ ] 搜索所有 `process.cwd()` 的使用
- [ ] 搜索所有相对路径字面量（以 `./` 或 `../` 开头的字符串）
- [ ] 替换为 `context.directory` 或 `context.worktree`
- [ ] 在 CLI 模式下测试（基准测试）
- [ ] 在 Desktop App 模式下测试（关键验证）
- [ ] 使用 `--dir` 参数测试 CLI
- [ ] 在 monorepo 子包中测试
- [ ] 验证 `task()` 子 agent 行为

---

## 8.10 路径安全速查表

### 8.10.1 场景对照表

| 场景 | 推荐的 Context 属性 | 示例 |
|------|---------------------|------|
| 读取 `.opencode/config.yaml` | `context.worktree` | `path.join(worktree, ".opencode/config.yaml")` |
| 读取项目根目录的 `package.json` | `context.worktree` | `path.join(worktree, "package.json")` |
| 读取当前会话目录的文件 | `context.directory` | `path.join(directory, args.file)` |
| 执行项目级脚本 | `context.worktree` | `path.join(worktree, "scripts/build.sh")` |
| glob 搜索项目文件 | `context.worktree` | `glob({ paths: [worktree], pattern: "**/*.ts" })` |
| 引用 Skill 内部资源 | `skill_resource` 工具 | `skill_resource skill_name="x" relative_path="y"` |
| 验证用户输入路径 | 两者结合 | `path.resolve(directory, userPath)` + 安全检查 |

### 8.10.2 错误代码速查

| 错误信息 | 可能原因 | 解决方案 |
|----------|----------|----------|
| `ENOENT: no such file or directory` | 使用了 `process.cwd()` 或相对路径 | 改用 `context.directory`/`worktree` |
| `EACCES: permission denied` | Desktop App 中试图访问 `/` 下文件 | 使用 `context.worktree` 构建路径 |
| `Path escapes project directory` | 用户输入了 `../` 路径 | 添加路径安全检查 |
| `glob() returned empty array` | glob 基于错误的 cwd | 显式指定 `paths: [context.directory]` |
| `Skill not found` | 目录名单复数错误 | 检查 `skills/`（复数）vs `skill/`（单数）|
| TUI 空白响应 | Symlink 目录 | 使用 `realpath` 解析物理路径 |

---

## 8.11 总结

路径处理是 OpenCode 开发中最隐蔽也最容易出问题的地方。本章覆盖了十个核心坑点，每个都可能导致工具在特定运行模式下完全失效。

**最重要的三条原则**：

1. **永不使用 `process.cwd()`** — 它在 Desktop App 中是 `/`，在子 agent 中不可预测
2. **始终使用 `context.directory` 和 `context.worktree`** — 这是唯一可靠的路径来源
3. **在所有运行模式下测试** — CLI、Desktop App、Web Daemon、`task()` 子 agent 都要验证

遵循这些原则，可以显著减少路径相关的问题，编写出在各种 OpenCode 运行模式下都能稳定工作的工具与 Skill。

---

> **版本说明**：本章内容基于 OpenCode v1.14.32 和 v1.15.13。部分坑点（如坑点 3 和坑点 5）在 v1.15.12/v1.15.13 中已得到修复，但了解这些历史问题有助于理解路径系统的设计演进。建议所有用户升级到 v1.15.13 以获得最佳的路径处理体验。
