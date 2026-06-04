# OpenCode 1.15.10 自定义 Tool 与 Subagent 完全教程

> **版本要求**: OpenCode 1.15.10+
> **目标读者**: 希望扩展 OpenCode 能力、构建自定义工具和多 Agent 协作流程的开发者
> **学习目标**: 掌握将 API 调用和对话式 Agent 包装为 Tool/Subagent 的方法，理解两者定位差异，构建多 Subagent 交互流程

---

## 目录

1. [核心概念与架构概览](#1-核心概念与架构概览)
2. [OpenCode Tool 深度解析](#2-opencode-tool-深度解析)
3. [OpenCode Subagent 深度解析](#3-opencode-subagent-深度解析)
4. [将 API 调用包装为 Tool/Subagent](#4-将-api-调用包装为-toolsubagent)
5. [将对话式 Skill Agent 包装为 Tool/Subagent](#5-将对话式-skill-agent-包装为-toolsubagent)
6. [Tool 与 Subagent 的定位、区别与联系](#6-tool-与-subagent-的定位区别与联系)
7. [构建自定义 Tool 和 Subagent 的最佳实践](#7-构建自定义-tool-和-subagent-的最佳实践)
8. [多 Subagent 交互流程构建](#8-多-subagent-交互流程构建)
9. [完整示例：构建一个多 Agent 协作系统](#9-完整示例构建一个多-agent-协作系统)
10. [常见问题与故障排查](#10-常见问题与故障排查)

---

## 1. 核心概念与架构概览

### 1.1 OpenCode 的 Agent 架构

OpenCode 采用分层 Agent 架构，主要分为主代理（Primary Agent）和子代理（Subagent）两种类型：

```
OpenCode Agent 架构
├── 主代理 (Primary Agents) - 用户直接交互
│   ├── Build Agent (默认)    - 完整工具访问，用于开发工作
│   └── Plan Agent            - 只读分析，用于规划和审查
│
└── 子代理 (Subagents) - 被主代理调用执行专项任务
    ├── @general              - 多步骤复杂任务（并行执行）
    ├── @explore              - 代码库快速只读探索
    ├── @scout                - 外部文档和依赖研究
    └── 自定义 Subagents       - 用户创建的专用代理
```

**主代理**是用户直接对话的主要助手，通过 `Tab` 键切换。它们处理主要的开发工作流。

**子代理**是被调用的专家助手，可以通过以下方式触发：
- `@mention` 方式在消息中提及（如 `@general 帮我搜索这个函数`）
- 主代理根据描述**自动**调用
- 通过 Task 工具**程序化**调用（确定性最强）

### 1.2 Tool 在 OpenCode 中的角色

Tool（工具）是 LLM 可调用的函数，用于扩展 AI 的能力。OpenCode 的工具体系包括：

| 工具类型 | 示例 | 说明 |
|---------|------|------|
| 内置工具 | `read`, `write`, `edit`, `bash`, `grep`, `glob` | OpenCode 原生提供 |
| 自定义工具 | `.opencode/tools/*.ts` | 用户/项目定义的 TypeScript/JavaScript 工具 |
| MCP 工具 | 通过 MCP Server 接入 | 外部服务通过 Model Context Protocol 提供 |
| 插件工具 | 通过 OpenCode 插件注册 | 插件系统扩展的工具 |

### 1.3 关键区别速览

| 维度 | Tool | Subagent |
|------|------|----------|
| **本质** | 单个函数调用 | 完整的 Agent 会话 |
| **上下文** | 共享主代理上下文 | 独立的上下文隔离 |
| **能力** | 执行特定计算/操作 | 自主决策、多步推理 |
| **调用方式** | LLM 自动选择调用 | `@mention` 或 Task 工具调用 |
| **生命周期** | 同步执行，立即返回 | 异步会话，可长时间运行 |
| **状态管理** | 无状态 | 可在会话内维护状态 |
| **工具访问** | 无法调用其他工具 | 拥有独立的工具集 |

---

## 2. OpenCode Tool 深度解析

### 2.1 工具的基本结构

创建工具最简单的方式是使用 `tool()` 辅助函数，它提供类型安全和参数校验。

#### 文件位置

- **项目级**: `.opencode/tools/<tool-name>.ts`（推荐，随项目共享）
- **全局级**: `~/.config/opencode/tools/<tool-name>.ts`（个人使用）

#### 单工具定义（默认导出）

```typescript
// .opencode/tools/database.ts
import { tool } from "@opencode-ai/plugin"

export default tool({
  description: "Query the project database",
  args: {
    query: tool.schema.string().describe("SQL query to execute"),
  },
  async execute(args) {
    // 你的数据库逻辑
    return `Executed query: ${args.query}`
  },
})
```

**文件名即为工具名称**。上面的示例创建了一个名为 `database` 的工具。

#### 多工具定义（命名导出）

```typescript
// .opencode/tools/math.ts
import { tool } from "@opencode-ai/plugin"

export const add = tool({
  description: "Add two numbers",
  args: {
    a: tool.schema.number().describe("First number"),
    b: tool.schema.number().describe("Second number"),
  },
  async execute(args) {
    return args.a + args.b
  },
})

export const multiply = tool({
  description: "Multiply two numbers",
  args: {
    a: tool.schema.number().describe("First number"),
    b: tool.schema.number().describe("Second number"),
  },
  async execute(args) {
    return args.a * args.b
  },
})
```

这会创建两个工具：`math_add` 和 `math_multiply`（命名格式为 `<filename>_<exportname>`）。

### 2.2 参数定义（Zod Schema）

工具使用 Zod 进行参数校验：

```typescript
import { tool } from "@opencode-ai/plugin"
import { z } from "zod"

export default tool({
  description: "Search documentation",
  args: {
    // 基础类型
    keyword: tool.schema.string().describe("Search keyword"),
    
    // 带约束的字符串
    category: tool.schema.string().min(1).max(50).describe("Document category"),
    
    // 数字类型
    limit: tool.schema.number().min(1).max(100).default(10).describe("Result limit"),
    
    // 枚举类型
    sort: tool.schema.enum(["relevance", "date", "title"]).default("relevance"),
    
    // 可选参数
    filters: tool.schema.string().optional().describe("Optional filters"),
    
    // 布尔类型
    includeDrafts: tool.schema.boolean().default(false),
  },
  async execute(args) {
    // args 的类型会被自动推断
    const { keyword, category, limit, sort, filters, includeDrafts } = args
    // ... 执行搜索
    return results
  },
})
```

### 2.3 上下文访问

工具可以接收当前会话的上下文信息：

```typescript
import { tool } from "@opencode-ai/plugin"

export default tool({
  description: "Get project information",
  args: {},
  async execute(args, context) {
    const { agent, sessionID, messageID, directory, worktree } = context
    
    return `Agent: ${agent}, Session: ${sessionID}, Directory: ${directory}, Worktree: ${worktree}`
  },
})
```

**上下文字段说明：**

| 字段 | 类型 | 说明 |
|------|------|------|
| `agent` | string | 当前使用的 Agent 名称 |
| `sessionID` | string | 会话 ID |
| `messageID` | string | 消息 ID |
| `directory` | string | 会话的工作目录 |
| `worktree` | string | Git worktree 根目录 |

### 2.4 用其他语言编写工具

工具定义必须是 TypeScript/JavaScript，但执行逻辑可以调用任何语言：

```typescript
// .opencode/tools/python-add.ts
import { tool } from "@opencode-ai/plugin"
import path from "path"

export default tool({
  description: "Add two numbers using Python",
  args: {
    a: tool.schema.number().describe("First number"),
    b: tool.schema.number().describe("Second number"),
  },
  async execute(args, context) {
    const script = path.join(context.worktree, ".opencode/tools/add.py")
    const result = await Bun.$`python3 ${script} ${args.a} ${args.b}`.text()
    return result.trim()
  },
})
```

```python
# .opencode/tools/add.py
import sys

a = int(sys.argv[1])
b = int(sys.argv[2])
print(a + b)
```

### 2.5 覆盖内置工具

自定义工具通过工具名称进行索引。如果与内置工具同名，会优先使用自定义版本：

```typescript
// .opencode/tools/bash.ts - 替换内置 bash 工具
import { tool } from "@opencode-ai/plugin"

export default tool({
  description: "Restricted bash wrapper",
  args: {
    command: tool.schema.string(),
  },
  async execute(args) {
    // 添加安全检查、日志记录等
    const allowedCommands = ["git", "npm", "node", "python"]
    const cmd = args.command.split(" ")[0]
    
    if (!allowedCommands.includes(cmd)) {
      return `Blocked: command '${cmd}' is not in the allowlist`
    }
    
    const result = await Bun.$`${args.command}`.text()
    return result
  },
})
```

> **注意**: 除非有意替换内置工具，否则建议使用独特的名称。如果想禁用内置工具但不想覆盖它，可以使用权限配置。

---

## 3. OpenCode Subagent 深度解析

### 3.1 Subagent 的定义方式

Subagent 通过 Markdown 文件配合 YAML frontmatter 定义：

#### 文件位置

- **项目级**: `.opencode/agent/<agent-name>.md`（推荐，随项目共享）
- **全局级**: `~/.config/opencode/agent/<agent-name>.md`（个人使用）

#### 基础结构

```markdown
---
description: Code review agent that checks for best practices and potential issues
mode: subagent
temperature: 0.1
tools:
  read: true
  grep: true
  bash: false
permission:
  edit: deny
  bash:
    "*": ask
    "git diff": allow
    "git log*": allow
    "grep *": allow
---

You are a senior code reviewer. Focus on:
- Code quality and best practices
- Potential bugs and edge cases
- Performance implications
- Security considerations

Provide constructive feedback without making direct changes.
```

**文件名即为 Agent 名称**。上面的示例创建了一个名为 `review` 的 subagent。

### 3.2 配置选项详解

#### 必需字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `description` | string | Agent 的功能和使用场景描述（**必需**） |

#### 可选字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `mode` | `primary` \| `subagent` \| `all` | 代理模式（默认 `all`） |
| `model` | string | 覆盖模型，格式 `provider/model-id` |
| `temperature` | number | 响应随机性，0.0-1.0 |
| `top_p` | number | 替代采样参数 |
| `maxSteps` | number | 最大迭代步数 |
| `prompt` | string | 提示词文件路径，如 `{file:./prompt.txt}` |
| `tools` | object | 启用/禁用工具（布尔值） |
| `permission` | object | 工具权限：`ask`\|`allow`\|`deny` |
| `disable` | boolean | 是否禁用该代理 |
| `hidden` | boolean | 是否在 `@` 自动补全中隐藏 |
| `color` | string | UI 显示颜色（hex 或主题色名称） |

#### 权限配置

```yaml
# 基础权限 - 工具级别
permission:
  edit: deny        # 禁止编辑
  bash: ask         # 执行前询问
  webfetch: allow   # 允许无限制使用

# 细粒度 bash 权限 - 支持 glob 模式
permission:
  bash:
    "*": ask                    # 默认：所有命令询问
    "git status*": allow        # git status 允许
    "git diff*": allow          # git diff 允许
    "grep*": allow              # grep 命令允许
    "rm*": deny                 # rm 命令禁止
    "mv*": deny                 # mv 命令禁止

# 任务权限 - 控制可调用哪些子代理
permission:
  task:
    "*": deny                   # 默认：禁止调用所有子代理
    "orchestrator-*": allow     # 允许调用 orchestrator- 开头的子代理
    "code-reviewer": ask        # 调用 code-reviewer 需要询问
```

> **规则匹配顺序**: 按顺序评估，**最后匹配的规则优先**。

### 3.3 JSON 配置方式（opencode.json）

也可以在 `opencode.json` 中配置代理：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "agent": {
    "review": {
      "mode": "subagent",
      "description": "Code review agent",
      "temperature": 0.1,
      "model": "anthropic/claude-haiku-4-20250514",
      "tools": {
        "write": false,
        "edit": false,
        "bash": false
      },
      "permission": {
        "edit": "deny",
        "bash": {
          "*": "ask",
          "git diff": "allow"
        }
      }
    }
  }
}
```

> **优先级**: Markdown 文件定义 > JSON 配置。建议优先使用 Markdown 方式，更易于版本控制。

### 3.4 调用 Subagent 的三种方式

#### 方式一：@mention 调用（交互式）

```
@review 请帮我检查 auth.ts 文件中的潜在安全问题
@general 搜索项目中所有使用 eval 的地方
@explore 查找用户认证相关的代码文件
```

- 支持 Tab 补全
- 用户主动发起
- **注意**: `@mention` 不保证一定创建子代理会话，主代理可能直接处理（见常见问题）

#### 方式二：Task 工具调用（程序化，确定性）

```typescript
// 在主代理或另一个子代理中调用
const result = await task({
  subagent_type: "review",    // 指定子代理类型
  prompt: "Review auth.ts for security issues:\n\n[file content]"
})
```

这是最可靠的程序化调用方式。

#### 方式三：主代理自动调用

主代理根据子代理的 `description` 自动判断何时调用合适的子代理。良好的 `description` 是关键。

---

## 4. 将 API 调用包装为 Tool/Subagent

### 4.1 场景分析

| 场景 | 推荐方案 | 理由 |
|------|---------|------|
| 简单的 HTTP GET 请求，返回结构化数据 | **Tool** | 单次调用，无副作用，确定性输出 |
| 需要多次 API 调用、错误重试、数据转换 | **Subagent** | 需要多步推理和错误处理 |
| 需要用户确认或交互的 API 操作 | **Subagent** | 可以调用 question 工具与用户交互 |
| 耗时较长的异步 API 任务 | **Subagent** | 独立上下文，不阻塞主代理 |
| 需要缓存或状态管理的 API 调用 | **Tool** | 可以在工具内实现缓存逻辑 |

### 4.2 包装为 Tool（推荐用于简单 API）

```typescript
// .opencode/tools/weather.ts
import { tool } from "@opencode-ai/plugin"

interface WeatherResponse {
  current: {
    temperature: number
    humidity: number
    condition: string
  }
  forecast: Array<{
    date: string
    high: number
    low: number
    condition: string
  }>
}

export default tool({
  description: "Get weather information for a city. Use this when the user asks about weather conditions.",
  args: {
    city: tool.schema.string().describe("City name (e.g., 'Beijing', 'New York')"),
    days: tool.schema.number().min(1).max(7).default(3).describe("Number of forecast days (1-7)"),
  },
  async execute(args) {
    const apiKey = process.env.WEATHER_API_KEY
    if (!apiKey) {
      return "Error: WEATHER_API_KEY environment variable not set"
    }

    try {
      const response = await fetch(
        `https://api.weather.com/v1/current?city=${encodeURIComponent(args.city)}&days=${args.days}&apiKey=${apiKey}`
      )
      
      if (!response.ok) {
        return `Error: Failed to fetch weather data (status ${response.status})`
      }

      const data: WeatherResponse = await response.json()
      
      // 格式化输出
      const current = `Current weather in ${args.city}: ${data.current.temperature}°C, ${data.current.condition}, ${data.current.humidity}% humidity`
      const forecast = data.forecast.map(day => 
        `- ${day.date}: ${day.low}°C ~ ${day.high}°C, ${day.condition}`
      ).join("\n")
      
      return `${current}\n\nForecast:\n${forecast}`
    } catch (error) {
      return `Error: ${error instanceof Error ? error.message : String(error)}`
    }
  },
})
```

### 4.3 包装为 Subagent（推荐用于复杂 API 工作流）

```markdown
---
description: Weather analysis agent that fetches weather data and provides travel recommendations based on conditions. Use this when the user needs weather-based decision making or multi-city weather comparison.
mode: subagent
model: openai/gpt-4o
temperature: 0.3
tools:
  read: true
  bash: true
  webfetch: true
permission:
  bash:
    "curl*": allow
    "*": ask
  webfetch: allow
---

You are a weather analysis specialist. Your job is to:

1. Fetch weather data from multiple sources when needed
2. Analyze weather patterns and trends
3. Provide actionable recommendations

When given a task:
1. First check if WEATHER_API_KEY is available in environment
2. Use curl to call the weather API with proper parameters
3. Parse and analyze the response
4. Provide comprehensive recommendations

For travel planning:
- Compare weather across multiple cities
- Identify the best travel windows
- Warn about severe weather conditions
- Suggest alternative dates if needed

Always include:
- Current conditions
- Forecast summary
- Confidence level of predictions
- Recommendations with rationale
```

### 4.4 带身份验证的 API Tool

```typescript
// .opencode/tools/github-api.ts
import { tool } from "@opencode-ai/plugin"

export default tool({
  description: "Call GitHub API to fetch repository information, issues, or PRs",
  args: {
    endpoint: tool.schema.string().describe("API endpoint path (e.g., 'repos/owner/repo/issues')"),
    method: tool.schema.enum(["GET", "POST", "PATCH"]).default("GET"),
    body: tool.schema.string().optional().describe("Request body for POST/PATCH requests"),
  },
  async execute(args) {
    const token = process.env.GITHUB_TOKEN
    if (!token) {
      return "Error: GITHUB_TOKEN not configured"
    }

    const url = `https://api.github.com/${args.endpoint}`
    
    try {
      const response = await fetch(url, {
        method: args.method,
        headers: {
          "Authorization": `Bearer ${token}`,
          "Accept": "application/vnd.github.v3+json",
          "User-Agent": "OpenCode-Tool",
          ...(args.body ? { "Content-Type": "application/json" } : {}),
        },
        ...(args.body ? { body: args.body } : {}),
      })

      const data = await response.json()
      
      if (!response.ok) {
        return `GitHub API Error (${response.status}): ${data.message || JSON.stringify(data)}`
      }

      return JSON.stringify(data, null, 2)
    } catch (error) {
      return `Error: ${error instanceof Error ? error.message : String(error)}`
    }
  },
})
```

---

## 5. 将对话式 Skill Agent 包装为 Tool/Subagent

### 5.1 什么是 Skill

Skill 是一组预定义的指令和知识，用于指导 Agent 完成特定领域的任务。OpenCode 支持通过 SKILL.md 文件定义技能。

### 5.2 对话式 Skill Agent 的特征

对话式 Skill Agent 通常具有以下特征：
- 需要多轮交互澄清需求
- 依赖领域特定的知识和模式
- 需要维护对话上下文
- 可能涉及 creative/generative 任务

### 5.3 包装为 Subagent（推荐方案）

对话式 Agent 最好包装为 Subagent，因为它需要维护上下文和进行多轮推理。

#### 示例：技术文档写作 Agent

```markdown
---
description: Technical documentation writer that creates comprehensive docs from code analysis. Use this when the user needs API docs, README updates, or technical guides written.
mode: subagent
model: anthropic/claude-sonnet-4-20250514
temperature: 0.4
maxSteps: 20
tools:
  read: true
  grep: true
  write: true
  edit: true
permission:
  edit: allow
  write: allow
  bash: deny
---

You are an expert technical documentation writer. Your workflow:

## Phase 1: Analysis
1. Read the target code files thoroughly
2. Identify all public APIs, functions, classes
3. Note parameters, return types, and side effects
4. Look for existing documentation patterns in the project

## Phase 2: Planning
1. Determine the documentation type needed:
   - API Reference: Function-level docs with types
   - Guide: Step-by-step instructions
   - README: Project overview and quickstart
   - Architecture: System design explanation

2. Create an outline before writing

## Phase 3: Writing
1. Follow the project's existing documentation style
2. Include code examples for all APIs
3. Add type information for TypeScript/Python code
4. Document edge cases and error conditions
5. Use clear, concise language

## Phase 4: Review
1. Verify all links are correct
2. Check code examples compile/run
3. Ensure consistency with codebase

Output the final documentation in the requested format.
Always confirm the documentation location with the user before writing files.
```

#### 示例：代码审查对话 Agent

```markdown
---
description: Security-focused code reviewer with interactive feedback. Use this when reviewing authentication, authorization, data handling, or any security-sensitive code.
mode: subagent
model: anthropic/claude-sonnet-4-20250514
temperature: 0.2
tools:
  read: true
  grep: true
permission:
  edit: deny
  bash: deny
---

You are a security-focused code reviewer. Analyze code for:

## Security Checklist
- [ ] SQL Injection vulnerabilities
- [ ] XSS (Cross-Site Scripting)
- [ ] CSRF protection
- [ ] Authentication bypass
- [ ] Sensitive data exposure
- [ ] Input validation
- [ ] Rate limiting
- [ ] Error handling (no info leakage)

## Review Process
1. Read all relevant files
2. Trace data flow from input to output
3. Identify trust boundaries
4. Check for defense in depth

## Output Format
For each issue found, provide:
- **Severity**: Critical / High / Medium / Low
- **Location**: File and line number
- **Description**: What the issue is
- **Impact**: What could happen
- **Recommendation**: How to fix
- **Code Example**: Secure alternative

Be thorough but constructive. Explain the "why" behind each recommendation.
```

### 5.4 包装为 Tool（适用于确定性 Skill）

如果 Skill 的执行流程是确定性的（不需要多轮交互），可以包装为 Tool：

```typescript
// .opencode/tools/linter.ts
import { tool } from "@opencode-ai/plugin"
import { $ } from "bun"

export default tool({
  description: "Run project linter and return formatted results. Use this to check code style and catch common issues.",
  args: {
    scope: tool.schema.string().default(".").describe("Files or directories to lint"),
    fix: tool.schema.boolean().default(false).describe("Whether to auto-fix issues"),
  },
  async execute(args, context) {
    const projectRoot = context.worktree
    
    try {
      // Detect linter configuration
      const hasEslint = await $`test -f ${projectRoot}/eslint.config.*`.quiet().exitCode === 0
      const hasBiome = await $`test -f ${projectRoot}/biome.json`.quiet().exitCode === 0
      
      if (hasBiome) {
        const cmd = args.fix 
          ? $`cd ${projectRoot} && npx @biomejs/biome check --write ${args.scope}`
          : $`cd ${projectRoot} && npx @biomejs/biome check ${args.scope}`
        
        const output = await cmd.text()
        return `## Biome Check Results\n\n\`\`\`\n${output}\n\`\`\``
      }
      
      if (hasEslint) {
        const cmd = args.fix
          ? $`cd ${projectRoot} && npx eslint --fix ${args.scope}`
          : $`cd ${projectRoot} && npx eslint ${args.scope}`
        
        const output = await cmd.text()
        return `## ESLint Results\n\n\`\`\`\n${output}\n\`\`\``
      }
      
      return "No linter configuration found (checked for Biome and ESLint)"
    } catch (error) {
      // Linter exits with non-zero when there are issues
      return `Linter output:\n\`\`\`\n${error}\n\`\`\``
    }
  },
})
```

---

## 6. Tool 与 Subagent 的定位、区别与联系

### 6.1 核心差异对比

| 维度 | Tool | Subagent |
|------|------|----------|
| **抽象层级** | 函数级（Function） | Agent 级（Agent） |
| **执行模型** | 同步调用，立即返回 | 异步会话，独立生命周期 |
| **上下文管理** | 继承主代理上下文 | 完全隔离的上下文 |
| **决策能力** | 无，纯执行 | 有，可自主决策 |
| **工具调用** | 不能调用其他工具 | 拥有独立工具集 |
| **状态保持** | 无状态 | 可在会话内保持状态 |
| **错误处理** | 简单 try/catch | 可重试、回退、多策略 |
| **成本** | 低（单次 LLM 调用） | 较高（多轮对话） |

### 6.2 决策树：何时使用 Tool，何时使用 Subagent

```
开始
│
├─ 任务是单一、确定性的操作？
│  ├─ 是 → 需要调用外部 API？
│  │  ├─ 是 → API 调用简单（单次请求）？
│  │  │  ├─ 是 → **使用 Tool** ✓
│  │  │  └─ 否（需要重试、分页等）→ **使用 Subagent** ✓
│  │  └─ 否（本地计算）→ **使用 Tool** ✓
│  └─ 否（需要多步推理）→ 需要上下文隔离？
│     ├─ 是 → **使用 Subagent** ✓
│     └─ 否 → 需要与其他工具协作？
│        ├─ 是 → **使用 Subagent** ✓
│        └─ 否 → 主代理可直接完成
│
└─ 需要专门的知识/角色？
   ├─ 是 → 需要维护对话状态？
   │  ├─ 是 → **使用 Subagent** ✓
   │  └─ 否 → **使用 Tool**（带详细描述）✓
   └─ 否 → 主代理直接处理
```

### 6.3 具体场景对照表

| 场景 | Tool | Subagent | 说明 |
|------|:----:|:--------:|------|
| 计算器/数学运算 | ✅ | ❌ | 确定性计算，Tool 更高效 |
| 天气查询 | ✅ | ⚠️ | 简单查询用 Tool，旅行规划用 Subagent |
| 代码搜索 | ✅ | ✅ | 简单搜索用 Tool，深度分析用 Subagent |
| 代码审查 | ⚠️ | ✅ | 需要多文件分析和交互，Subagent 更合适 |
| 文档写作 | ❌ | ✅ | 需要多轮交互和上下文维护 |
| 测试生成 | ⚠️ | ✅ | 复杂场景需要 Subagent |
| Git 操作 | ✅ | ⚠️ | 简单命令用 Tool，复杂工作流用 Subagent |
| 数据库查询 | ✅ | ⚠️ | 简单查询用 Tool，复杂分析用 Subagent |
| API 集成开发 | ❌ | ✅ | 需要多步推理和错误处理 |
| 重构规划 | ❌ | ✅ | 需要分析和规划的复杂任务 |

### 6.4 两者之间的联系

Tool 和 Subagent 并非互斥，它们可以协同工作：

1. **Subagent 内部可以调用 Tool**: 子代理拥有完整的工具访问权限，可以调用自定义 Tool
2. **Tool 可以触发 Subagent**: 在 Tool 的复杂场景中，可以通过返回值建议主代理调用 Subagent
3. **共同构成能力层**: Tool 提供原子能力，Subagent 提供编排能力

```
┌─────────────────────────────────────────┐
│          Primary Agent (Build)          │
│         用户交互 + 任务编排              │
└─────────────┬───────────────────────────┘
              │
      ┌───────┴───────┐
      ▼               ▼
┌──────────┐   ┌──────────────┐
│   Tool   │   │  Subagent    │
│ (原子操作) │   │ (复杂任务编排) │
│          │   │              │
│ • API调用 │   │ • 代码审查    │
│ • 文件读取 │   │ • 文档写作    │
│ • 数据转换 │   │ • 多步推理    │
│ • 格式转换 │   │ • 决策制定    │
└──────────┘   └──────┬───────┘
                      │
              ┌───────┴───────┐
              ▼               ▼
        ┌──────────┐   ┌──────────┐
        │ 内置工具  │   │ 自定义工具 │
        └──────────┘   └──────────┘
```

---

## 7. 构建自定义 Tool 和 Subagent 的最佳实践

### 7.1 Tool 开发最佳实践

#### 描述设计（关键！）

Tool 的 `description` 是 LLM 决定何时调用该工具的依据，必须清晰明确：

```typescript
// ✅ 好的描述 - 明确说明用途和触发条件
export default tool({
  description: "Search the project's documentation and README files. Use this when the user asks about project setup, configuration options, or how to use specific features.",
  // ...
})

// ❌ 差的描述 - 过于模糊
export default tool({
  description: "Search docs",
  // ...
})
```

#### 参数命名与描述

```typescript
// ✅ 好的参数定义
args: {
  filePath: tool.schema.string().describe("Absolute or relative path to the file to analyze"),
  depth: tool.schema.number().min(1).max(5).default(3).describe("Analysis depth: 1=overview, 3=detailed, 5=exhaustive"),
}

// ❌ 差的参数定义
args: {
  path: tool.schema.string(),  // 缺少描述
  d: tool.schema.number(),     // 命名不清晰
}
```

#### 错误处理

```typescript
async execute(args) {
  try {
    const result = await performOperation(args)
    
    // 返回结构化结果
    return JSON.stringify({
      success: true,
      data: result,
      summary: `Processed ${result.length} items`
    })
  } catch (error) {
    // 返回有用的错误信息
    return JSON.stringify({
      success: false,
      error: error instanceof Error ? error.message : String(error),
      suggestion: "Check if the file exists and you have read permissions"
    })
  }
}
```

#### 性能优化

```typescript
// ✅ 使用缓存避免重复请求
const cache = new Map<string, any>()

export default tool({
  description: "Fetch npm package info",
  args: {
    packageName: tool.schema.string(),
  },
  async execute(args) {
    if (cache.has(args.packageName)) {
      return cache.get(args.packageName)
    }
    
    const result = await fetchPackageInfo(args.packageName)
    cache.set(args.packageName, result)
    return result
  },
})
```

### 7.2 Subagent 开发最佳实践

#### Description 是关键

Subagent 的 `description` 决定了主代理何时调用它，必须包含：
- **功能描述**: 这个 Agent 做什么
- **使用场景**: 什么时候应该调用它
- **输入期望**: 期望接收什么信息

```yaml
# ✅ 好的 description
description: Database migration specialist that creates, reviews, and executes safe schema changes. Use this when the user needs to add tables, modify columns, create indexes, or migrate data. Expects a description of the schema change needed.

# ❌ 差的 description
description: Database helper
```

#### 提示词工程

```markdown
---
description: SQL query optimizer and reviewer
mode: subagent
temperature: 0.1
---

You are a SQL optimization expert. Follow these rules:

1. ALWAYS check for N+1 queries
2. Verify indexes exist for JOIN and WHERE columns
3. Prefer parameterized queries over string concatenation
4. Check for potential deadlock scenarios
5. Ensure transactions are properly scoped

## Review Checklist
- [ ] Query uses appropriate indexes
- [ ] No SELECT * in production code
- [ ] Pagination for large result sets
- [ ] Proper error handling

## Output Format
Provide your analysis in this structure:
1. **Summary**: Overall assessment
2. **Issues**: List of problems found
3. **Optimized Query**: Improved version
4. **Explanation**: Why changes help
```

#### 权限最小化原则

```yaml
# ✅ 最小权限原则
permission:
  edit: deny      # 默认禁止编辑
  bash:
    "*": ask      # 所有命令需要确认
    "git log*": allow  # 只放行安全的命令
  write: deny

# 除非必要，不要授予编辑权限
```

#### 工具选择与限制

```yaml
# ✅ 只启用必要的工具
tools:
  read: true
  grep: true
  bash: false    # 禁用不需要的工具
  write: false
  edit: false
```

### 7.3 安全最佳实践

1. **环境变量管理**: 不要在工具中硬编码 API 密钥
   ```typescript
   const apiKey = process.env.API_KEY
   if (!apiKey) throw new Error("API_KEY not configured")
   ```

2. **输入验证**: 始终验证和清理用户输入
   ```typescript
   args: {
     url: tool.schema.string().url(),  // 使用 Zod 验证
   }
   ```

3. **权限隔离**: Subagent 的权限应严格限制
   ```yaml
   permission:
     bash:
       "rm*": deny
       "sudo*": deny
       "*": ask
   ```

4. **敏感操作确认**: 破坏性操作前要求确认
   ```typescript
   if (args.destructive) {
     return "This operation will delete data. Please confirm by setting confirm=true"
   }
   ```

---

## 8. 多 Subagent 交互流程构建

### 8.1 常见编排模式

#### 模式一：顺序管道（Pipeline）

```
输入 → [Agent A: 分析] → [Agent B: 实现] → [Agent C: 审查] → 输出
```

适用场景：任务之间有明确的依赖关系，如先分析再实现再审查。

```typescript
// 主代理编排代码
async function pipelineWorkflow(requirement: string) {
  // Phase 1: 分析
  const analysis = await task({
    subagent_type: "analyzer",
    prompt: `Analyze this requirement and produce a technical design:\n${requirement}`
  })
  
  // Phase 2: 实现（基于分析结果）
  const implementation = await task({
    subagent_type: "implementer",
    prompt: `Implement based on this design:\n${analysis}`
  })
  
  // Phase 3: 审查（基于实现结果）
  const review = await task({
    subagent_type: "reviewer",
    prompt: `Review this implementation:\n${implementation}`
  })
  
  return { analysis, implementation, review }
}
```

#### 模式二：并行扇出/扇入（Fan-out/Fan-in）

```
输入 → [Agent A: 安全审查] ─┐
     → [Agent B: 性能审查] ─┼→ [Aggregator: 汇总报告] → 输出
     → [Agent C: 代码质量] ─┘
```

适用场景：多个独立的审查/分析任务可以并行执行。

```typescript
async function parallelReview(code: string) {
  // 并行发起多个审查任务
  const [security, performance, quality] = await Promise.all([
    task({
      subagent_type: "security-reviewer",
      prompt: `Review for security issues:\n${code}`
    }),
    task({
      subagent_type: "performance-reviewer",
      prompt: `Review for performance issues:\n${code}`
    }),
    task({
      subagent_type: "quality-reviewer",
      prompt: `Review code quality:\n${code}`
    }),
  ])
  
  // 汇总结果
  return {
    security: { passed: !security.includes("CRITICAL"), details: security },
    performance: { passed: !performance.includes("CRITICAL"), details: performance },
    quality: { passed: quality.includes("LGTM"), details: quality },
    overall: (!security.includes("CRITICAL") && !performance.includes("CRITICAL"))
  }
}
```

#### 模式三：专家池（Expert Pool）

```
输入 → [Router] → 根据问题类型选择专家 → [Expert A/B/C] → 输出
```

适用场景：不同类型的问题需要不同的专家处理。

```markdown
---
description: Technical support router that directs questions to the right specialist. Use this as the first point of contact for any technical question.
mode: subagent
tools:
  task: true
permission:
  task:
    "frontend-expert": allow
    "backend-expert": allow
    "devops-expert": allow
    "*": deny
---

You are a technical support router. Your job is to:

1. Understand the user's technical question
2. Classify it into one of these categories:
   - **frontend**: UI, React, CSS, browser issues
   - **backend**: API, database, server logic
   - **devops**: Deployment, CI/CD, infrastructure

3. Route to the appropriate expert using the Task tool:
   - Frontend questions → frontend-expert
   - Backend questions → backend-expert
   - DevOps questions → devops-expert

Always provide a brief summary of why you chose that expert.
```

#### 模式四：生产者-审查者循环（Producer-Reviewer Loop）

```
[Producer: 生成] → [Reviewer: 审查] 
       ↑                  │
       └──── FIX ─────────┘ (if not passed)
```

适用场景：需要高质量输出的生成任务。

```typescript
async function producerReviewerLoop(spec: string, maxIterations = 3) {
  let implementation = ""
  
  for (let i = 0; i < maxIterations; i++) {
    // 生产阶段
    implementation = await task({
      subagent_type: "implementer",
      prompt: `Implement this spec (iteration ${i + 1}):\n${spec}\n\nPrevious review: ${i > 0 ? review : "None"}`
    })
    
    // 审查阶段
    const review = await task({
      subagent_type: "reviewer",
      prompt: `Review this implementation. Reply with PASS if acceptable, or provide specific fixes needed:\n${implementation}`
    })
    
    if (review.includes("PASS")) {
      return { implementation, review, iterations: i + 1 }
    }
  }
  
  return { implementation, review: "Max iterations reached", iterations: maxIterations }
}
```

#### 模式五：监督者模式（Supervisor）

```
[Supervisor Agent] 
   ├── 分配任务给 Worker A
   ├── 分配任务给 Worker B
   ├── 监控进度
   └── 聚合最终结果
```

适用场景：复杂的项目需要协调多个 Agent。

```markdown
---
description: Project supervisor that coordinates multiple workers for complex tasks. Use this when a task requires multiple specialists working together.
mode: subagent
tools:
  read: true
  task: true
permission:
  task:
    "*": deny
    "worker-*": allow
    "reviewer": allow
---

You are a project supervisor. Your responsibilities:

1. **Task Decomposition**: Break complex tasks into sub-tasks
2. **Worker Assignment**: Assign sub-tasks to appropriate workers
3. **Quality Control**: Review outputs before final delivery
4. **Conflict Resolution**: Handle disagreements between workers

## Workflow
1. Analyze the overall task
2. Create a task plan with clear deliverables
3. Assign tasks to workers in parallel where possible
4. Review all outputs
5. Integrate into coherent final result

## Worker Pool
- worker-research: Research and information gathering
- worker-code: Code implementation
- worker-docs: Documentation writing
- reviewer: Quality review
```

### 8.2 权限控制与隔离

多 Agent 系统中，权限控制至关重要：

```yaml
# 编排者 Agent - 可以调用工作节点
---
description: Task orchestrator
mode: subagent
tools:
  task: true
permission:
  task:
    "*": deny
    "worker-*": allow     # 只能调用 worker 开头的子代理
---

# 工作节点 Agent - 只能执行具体任务
---
description: Code implementation worker
mode: subagent
tools:
  read: true
  write: true
  edit: true
permission:
  edit: allow
  write: allow
  bash:
    "*": deny             # 禁止所有 bash 命令
---

# 审查者 Agent - 只读权限
---
description: Code reviewer
mode: subagent
tools:
  read: true
grep: true
permission:
  edit: deny              # 禁止编辑
  write: deny             # 禁止写入
  bash: deny
---
```

### 8.3 避免递归和循环

多 Agent 系统容易出现递归调用问题，需要设置保护机制：

```yaml
# 在子代理提示词中添加限制
---
description: Research assistant
mode: subagent
---

You are a research assistant.

## IMPORTANT LIMITS
- You CANNOT spawn other subagents
- You CANNOT use the Task tool
- Maximum 10 steps
- If you cannot find the answer in 10 steps, report what you found
```

```typescript
// 在主代理层面添加深度控制
const MAX_DEPTH = 3

async function orchestrate(task: string, depth = 0): Promise<string> {
  if (depth >= MAX_DEPTH) {
    return "Maximum delegation depth reached. Completing task with current context."
  }
  
  // ... 编排逻辑
  
  const result = await subagentTask({
    subagent_type: "worker",
    prompt: task,
    // 传递当前深度信息
    context: { currentDepth: depth }
  })
  
  return result
}
```

### 8.4 上下文管理

在多 Agent 协作中，上下文管理是关键：

1. **自包含提示**: 每个子代理的提示应该包含完成任务所需的所有信息
   ```typescript
   // ✅ 好的做法 - 提供完整上下文
   await task({
     subagent_type: "reviewer",
     prompt: `Review this function for security issues:\n\nFile: src/auth.ts\n\n${fileContent}\n\nFocus on: SQL injection, XSS, auth bypass`
   })
   ```

2. **结果传递**: 清晰地传递前一个 Agent 的结果
   ```typescript
   const analysis = await task({ subagent_type: "analyzer", prompt: "..." })
   const implementation = await task({
     subagent_type: "implementer",
     prompt: `Based on this analysis, implement the solution:\n${analysis}`
   })
   ```

3. **避免上下文污染**: 子代理不应该访问不相关的信息
   ```yaml
   # 使用工具限制来隔离上下文
   tools:
     read: true     # 只能读取文件
     write: false   # 不能写入
     bash: false    # 不能执行命令
   ```

---

## 9. 完整示例：构建一个多 Agent 协作系统

### 9.1 系统架构

构建一个完整的代码审查系统，包含以下 Agent：

```
代码审查系统
├── orchestrator (主控) - 协调整个审查流程
├── security-reviewer (安全审查员) - 安全检查
├── performance-reviewer (性能审查员) - 性能分析
├── style-reviewer (风格审查员) - 代码风格
└── report-generator (报告生成器) - 汇总报告
```

### 9.2 Agent 定义

#### 主控 Agent

```markdown
---
description: Code review orchestrator that coordinates security, performance, and style reviews. Use this when the user wants a comprehensive code review. This agent will automatically dispatch specialized reviewers and compile the final report.
mode: subagent
tools:
  read: true
  task: true
permission:
  task:
    "*": deny
    "security-reviewer": allow
    "performance-reviewer": allow
    "style-reviewer": allow
    "report-generator": allow
---

You are a code review orchestrator. Your workflow:

1. **Read** the code files to be reviewed
2. **Dispatch** three specialist reviewers in parallel:
   - @security-reviewer: Check for security vulnerabilities
   - @performance-reviewer: Analyze performance implications
   - @style-reviewer: Review code style and best practices
3. **Collect** all review results
4. **Generate** a comprehensive report via @report-generator

Always provide a summary of findings and recommendations.
```

#### 安全审查员

```markdown
---
description: Security-focused code reviewer specializing in vulnerability detection. Checks for SQL injection, XSS, authentication bypass, sensitive data exposure, and other security risks. Use this for any code handling user input, authentication, or data access.
mode: subagent
temperature: 0.1
tools:
  read: true
  grep: true
permission:
  edit: deny
  write: deny
  bash: deny
---

You are a security code reviewer. Focus areas:

## OWASP Top 10 Checks
- [ ] Injection (SQL, NoSQL, Command, LDAP)
- [ ] Broken Authentication
- [ ] Sensitive Data Exposure
- [ ] XML External Entities (XXE)
- [ ] Broken Access Control
- [ ] Security Misconfiguration
- [ ] Cross-Site Scripting (XSS)
- [ ] Insecure Deserialization
- [ ] Using Components with Known Vulnerabilities
- [ ] Insufficient Logging & Monitoring

## Output Format
### Critical Issues
List issues that MUST be fixed before deployment

### Warnings
List issues that should be addressed

### Recommendations
List security best practices to consider

Rate each finding as: CRITICAL / HIGH / MEDIUM / LOW
```

#### 性能审查员

```markdown
---
description: Performance code reviewer specializing in optimization analysis. Checks for N+1 queries, memory leaks, inefficient algorithms, unnecessary re-renders, and resource usage. Use this for any performance-sensitive code or when the user reports slow operations.
mode: subagent
temperature: 0.1
tools:
  read: true
  grep: true
permission:
  edit: deny
  write: deny
---

You are a performance code reviewer. Check for:

## Database
- [ ] N+1 query problems
- [ ] Missing indexes
- [ ] Unnecessary queries
- [ ] Large result sets without pagination

## Algorithms
- [ ] Time complexity issues (O(n²) or worse)
- [ ] Unnecessary iterations
- [ ] Inefficient data structures

## Memory
- [ ] Memory leaks
- [ ] Large object retention
- [ ] Unnecessary cloning/coping

## Frontend (if applicable)
- [ ] Unnecessary re-renders
- [ ] Large bundle sizes
- [ ] Blocking operations

Rate each finding with estimated impact: CRITICAL / HIGH / MEDIUM / LOW
```

#### 风格审查员

```markdown
---
description: Code style and best practices reviewer. Checks for code consistency, naming conventions, documentation, error handling, and language-specific idioms. Use this for maintaining code quality and consistency across the codebase.
mode: subagent
temperature: 0.2
tools:
  read: true
  grep: true
permission:
  edit: deny
  write: deny
---

You are a code style reviewer. Check for:

## Code Quality
- [ ] Consistent naming conventions
- [ ] Proper error handling
- [ ] Adequate documentation/comments
- [ ] Test coverage

## Best Practices
- [ ] Language-specific idioms
- [ ] Design patterns usage
- [ ] SOLID principles
- [ ] DRY principle

## Maintainability
- [ ] Function/class length
- [ ] Cyclomatic complexity
- [ ] Code organization
- [ ] Dependency management

Provide specific line references and suggested improvements.
```

#### 报告生成器

```markdown
---
description: Code review report generator that consolidates findings from multiple reviewers into a comprehensive, actionable report. Use this to compile review results into a final deliverable.
mode: subagent
temperature: 0.3
tools:
  read: true
  write: true
permission:
  write: allow
  edit: allow
---

You are a code review report generator. Your task:

1. Consolidate findings from all reviewers
2. Deduplicate overlapping issues
3. Prioritize by severity
4. Create an actionable report

## Report Structure
```markdown
# Code Review Report

## Summary
- Total issues found: X
- Critical: X, High: X, Medium: X, Low: X
- Overall assessment: PASS / CONDITIONAL PASS / FAIL

## Critical Issues (Must Fix)
1. [Issue description with file/line reference]
   - Suggested fix: ...

## High Priority (Should Fix)
...

## Medium Priority (Consider)
...

## Low Priority (Nice to Have)
...

## Positive Findings
...

## Recommendations
...
```

Save the report to the specified file location.
```

### 9.3 使用示例

用户可以这样使用这个系统：

```
@reviewer 请审查 src/auth.ts 和 src/api/users.ts 文件
```

主控 Agent 会自动：
1. 读取这两个文件
2. 并行分发给三个专业审查员
3. 收集所有审查结果
4. 生成综合报告

### 9.4 项目结构

```
project/
├── .opencode/
│   ├── agent/
│   │   ├── code-review-orchestrator.md    # 主控
│   │   ├── security-reviewer.md           # 安全审查
│   │   ├── performance-reviewer.md        # 性能审查
│   │   ├── style-reviewer.md              # 风格审查
│   │   └── report-generator.md            # 报告生成
│   └── tools/
│       └── github-api.ts                  # 可选：GitHub API 工具
├── src/
│   └── ...
└── opencode.json                          # 主配置
```

---

## 10. 常见问题与故障排查

### Q1: @mention 不保证创建子代理会话

**问题**: 使用 `@general` 时，有时主代理会直接处理，而不是创建子代理会话。

**解决方案**: 如果需要确定性调用，使用 Task 工具：

```typescript
// ✅ 确定性调用
await task({
  subagent_type: "general",
  prompt: "Your task here"
})

// 或在提示中明确要求
"Spawn a general subagent to handle this task..."
```

### Q2: 子代理无法访问主代理的工具

**问题**: 子代理尝试使用 `question` 工具失败。

**原因**: 子代理会话有独立的工具集，某些工具（如 `question`）只在主代理中可用。

**解决方案**: 
- 检查子代理的 `tools` 配置
- 不要在子代理中依赖主代理专属工具

### Q3: 自定义子代理无法通过 Task 工具调用

**问题**: Task 工具的 `subagent_type` 只接受内置值（`explore`, `general`）。

**解决方案** (OpenCode 1.15.10+):
- 确保子代理配置正确
- 使用 `@mention` 方式调用自定义子代理
- 或在 opencode.json 中配置 `permission.task` 允许调用

### Q4: 工具名称冲突

**问题**: 自定义工具与内置工具同名。

**解决方案**: 
- 自定义工具会覆盖内置工具
- 使用独特的命名，如前缀 `myproject-`
- 或使用权限系统禁用内置工具

### Q5: 多 Agent 递归调用

**问题**: 子代理继续创建子代理，导致无限递归。

**解决方案**:
- 在提示词中明确禁止子代理创建子代理
- 设置最大深度限制
- 使用 `permission.task` 限制子代理的任务权限

### Q6: 子代理权限不生效

**问题**: 配置了权限但子代理似乎可以执行被禁止的操作。

**排查步骤**:
1. 检查 YAML frontmatter 语法是否正确
2. 确认 `mode: subagent` 已设置
3. 验证权限格式（使用 glob 模式时检查引号）
4. 重启 OpenCode 使配置生效

### Q7: 工具修改后未生效

**解决方案**:
- OpenCode 会自动检测工具文件变更
- 如果未生效，尝试重启 OpenCode
- 检查文件路径是否正确（`.opencode/tools/`）

---

## 附录 A：配置速查表

### Agent 配置（YAML Frontmatter）

```yaml
---
description: "Required: Agent purpose description"
mode: subagent                    # primary | subagent | all
model: "anthropic/claude-sonnet-4-20250514"
temperature: 0.1                  # 0.0-1.0
maxSteps: 20                      # Maximum iterations
hidden: false                     # Hide from @ autocomplete
color: "#ff6b6b"                  # UI color

tools:
  read: true
  write: true
  edit: true
  bash: true
  grep: true
  glob: true
  webfetch: false

permission:
  edit: ask                       # ask | allow | deny
  write: allow
  bash:
    "*": ask
    "git *": allow
    "rm *": deny
  webfetch: deny
  task:
    "*": deny
    "worker-*": allow
---
```

### Tool 配置（TypeScript）

```typescript
import { tool } from "@opencode-ai/plugin"

export default tool({
  description: "Clear description of what this tool does",
  args: {
    param1: tool.schema.string().describe("Parameter description"),
    param2: tool.schema.number().default(10).describe("Parameter with default"),
    param3: tool.schema.enum(["a", "b", "c"]).describe("Enum parameter"),
  },
  async execute(args, context) {
    const { agent, sessionID, directory, worktree } = context
    // Implementation
    return "result"
  },
})
```

### 内置工具列表

| 工具 | 说明 |
|------|------|
| `read` | 读取文件内容 |
| `write` | 写入文件 |
| `edit` | 编辑文件（补丁方式） |
| `bash` | 执行 shell 命令 |
| `grep` | 文本搜索 |
| `glob` | 文件匹配 |
| `task` | 调用子代理 |
| `webfetch` | 获取网页内容 |
| `skill` | 加载技能 |
| `todowrite` | 写待办事项 |
| `todoread` | 读待办事项 |

---

## 附录 B：参考资源

- [OpenCode 官方文档](https://opencode.ai/docs)
- [自定义工具文档](https://opencode.ai/docs/custom-tools/)
- [Agent 配置文档](https://opencode.ai/docs/agents/)
- [权限系统文档](https://opencode.ai/docs/permissions/)
- [OpenCode GitHub](https://github.com/anomalyco/opencode)
- [@opencode-ai/plugin API](https://opencode.ai/docs/plugin/)

---

> **最后更新**: 2026年6月
> **适用版本**: OpenCode 1.15.10+
