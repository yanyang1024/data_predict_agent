# OpenCode 权限安全基线配置

> **适用版本**: OpenCode CLI v1.14.32 / v1.15.13+
>
> **难度**: 初级 ~ 中级
>
> **前置知识**: JSON 配置语法、基础命令行工具

---

## 目录

- [1. 为什么需要权限配置](#1-为什么需要权限配置)
- [2. 权限字段速查表](#2-权限字段速查表)
- [3. 完整权限配置示例](#3-完整权限配置示例)
- [4. 权限规则优先级（核心机制）](#4-权限规则优先级核心机制)
- [5. 各权限字段详解与设计哲学](#5-各权限字段详解与设计哲学)
  - [5.1 `read` — 文件读取控制](#51-read--文件读取控制)
  - [5.2 `edit` — 文件编辑控制](#52-edit--文件编辑控制)
  - [5.3 `bash` — 命令执行控制](#53-bash--命令执行控制)
  - [5.4 网络与外部权限](#54-网络与外部权限)
- [6. Agent 级别独立权限（v1.15.x）](#6-agent-级别独立权限v115x)
- [7. v1.14.32 vs v1.15.13 版本差异](#8-v11432-vs-v11513-版本差异)
- [8. 常见问题 FAQ](#9-常见问题-faq)

---

## 1. 为什么需要权限配置

OpenCode 是一款 AI 驱动的编程助手，它能够读取你的代码、执行终端命令、修改文件内容，甚至访问外部网络。这种强大的能力在提升开发效率的同时，也带来了潜在的安全风险：

| 风险场景 | 说明 |
|---------|------|
| **敏感文件泄露** | AI 可能读取 `.env` 文件中的 API Key、数据库密码 |
| **破坏性操作** | AI 可能执行 `rm -rf /` 或 `git reset --hard` 等危险命令 |
| **非预期代码推送** | AI 可能在未经确认的情况下 `git push` 未审查的代码 |
| **外部攻击面** | 网络搜索和抓取可能泄露内部代码片段 |

OpenCode 的权限系统通过**白名单+分级授权**模式，让你在享受 AI 便利的同时，保持对关键操作的掌控权。

---

## 2. 权限字段速查表

### 2.1 基础权限字段

| 权限字段 | 控制范围 | 可选值 | v1.14.32 | v1.15.13+ |
|---------|---------|--------|----------|-----------|
| `read` | 文件读取 | `allow` / `deny` / `ask` | ✅ | ✅ |
| `edit` | 文件编辑 | `allow` / `deny` / `ask` | ✅ | ✅ |
| `bash` | 命令执行 | `allow` / `deny` / `ask` / 子规则 | ✅ | ✅ |
| `grep` | 文本搜索 | `allow` / `deny` / `ask` | ✅ | ✅ |
| `glob` | 文件匹配 | `allow` / `deny` / `ask` | ✅ | ✅ |
| `list` | 目录列出 | `allow` / `deny` / `ask` | ✅ | ✅ |
| `external_directory` | 外部目录访问 | `allow` / `deny` / `ask` | ✅ | ✅ |
| `webfetch` | 网页抓取 | `allow` / `deny` / `ask` | ✅ | ✅ |
| `websearch` | 网络搜索 | `allow` / `deny` / `ask` | ✅ | ✅ |
| `doom_loop` | 死循环检测 | `allow` / `deny` / `ask` | ✅ | ✅ |
| `skill` | 技能调用 | `allow` / `deny` / `ask` | ❌ | ✅ |

### 2.2 权限值含义

| 值 | 含义 | 适用场景 |
|----|------|---------|
| `allow` | **直接允许**，无需确认 | 安全、高频、只读操作 |
| `deny` | **直接拒绝**，无法执行 | 危险、破坏性操作 |
| `ask` | **每次询问**，需用户确认 | 敏感、有副作用的操作 |

---

## 3. 完整权限配置示例

以下是一份**生产环境推荐的安全基线配置**，涵盖了日常开发中的大多数场景：

```jsonc
{
  "$schema": "https://opencode.ai/config.json",

  "permission": {
    // ============================================================
    // 全局默认权限：所有未明确配置的操作都询问用户
    // 安全原则：默认拒绝，显式授权
    // ============================================================
    "*": "ask",

    // ============================================================
    // 1. 文件读取权限 (read)
    // ============================================================
    "read": {
      // 默认允许读取所有文件 —— AI 需要读取代码才能理解项目
      "*": "allow",

      // 严格保护环境变量文件（优先级高于上面的 *）
      "*.env": "deny",         // 拒绝 .env
      "*.env.*": "deny",       // 拒绝 .env.local, .env.production 等

      // 允许读取示例文件（不含真实密钥）
      "*.env.example": "allow"
    },

    // ============================================================
    // 2. 文本搜索与文件匹配 —— 只读操作，直接允许
    // ============================================================
    "grep": "allow",   // ripgrep/grep 代码搜索
    "glob": "allow",   // 文件 glob 匹配
    "list": "allow",   // 目录内容列出

    // ============================================================
    // 3. 文件编辑权限 —— 每次都需要确认（防止意外修改）
    // ============================================================
    "edit": "ask",

    // ============================================================
    // 4. 命令执行权限 (bash) —— 最严格的部分
    // ============================================================
    "bash": {
      // 默认：所有命令执行前询问
      "*": "ask",

      // ---- 安全只读命令：直接允许 ----
      "git status*": "allow",   // 查看工作区状态
      "git diff*": "allow",     // 查看变更差异
      "git log*": "allow",      // 查看提交历史
      "git branch*": "allow",   // 查看分支列表

      "rg *": "allow",          // ripgrep 快速搜索
      "grep *": "allow",        // grep 文本搜索
      "ls *": "allow",          // 列出文件
      "cat *": "allow",         // 查看文件内容

      // ---- 构建/测试命令：询问后执行 ----
      // 这些命令可能有副作用（生成文件、消耗资源），但通常安全
      "pnpm test*": "ask",
      "npm test*": "ask",
      "bun test*": "ask",
      "pnpm typecheck*": "ask",
      "pnpm lint*": "ask",

      // ---- 危险命令：严格拒绝 ----
      "git push*": "deny",          // 禁止自动推送代码（需人工审查）
      "git reset --hard*": "deny",  // 禁止强制重置（会丢失未提交工作）
      "git clean*": "deny",         // 禁止清理未跟踪文件（可能误删）
      "rm -rf*": "deny",            // 禁止递归强制删除

      // ---- 进程管理命令：分平台处理 ----
      "pkill *": "deny",        // Linux/macOS 终止进程 —— 拒绝
      "killall *": "deny",      // Linux/macOS 终止进程 —— 拒绝
      "taskkill *": "ask",      // Windows 终止进程 —— 询问（相对安全）
      "kill *": "ask"           // 通用 kill —— 询问
    },

    // ============================================================
    // 5. 外部访问权限 —— 默认询问
    // ============================================================
    "external_directory": "ask",  // 访问项目外部目录
    "doom_loop": "ask",           // 死循环检测触发时的行为
    "webfetch": "ask",            // 抓取外部网页内容
    "websearch": "ask"            // 执行网络搜索
  },

  // ================================================================
  // 6. Agent 级别独立权限（v1.15.x+ 特性）
  // ================================================================
  "agent": {
    // ---- Plan Agent：规划模式更保守 ----
    "plan": {
      "permission": {
        // 规划阶段不应修改代码，只允许分析
        "edit": "deny",
        "bash": "ask"
      }
    },

    // ---- Build Agent：构建模式允许编辑，但限制危险操作 ----
    "build": {
      "permission": {
        "edit": "ask",           // 编辑前询问
        "bash": {
          "*": "ask",
          "git status*": "allow",
          "git diff*": "allow",
          "rg *": "allow",
          "pnpm test*": "ask",
          // 以下危险命令在构建模式下同样拒绝
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

---

## 4. 权限规则优先级（核心机制）

理解 OpenCode 的权限匹配机制是正确配置的关键。**OpenCode 采用"后匹配规则优先"（Last Match Wins）策略**。

### 4.1 核心原则：后匹配优先

当一条命令或操作到达时，OpenCode 会按配置文件中**从上到下的顺序**逐一匹配规则。**最后一条匹配的规则生效**。

```
配置顺序（从上到下）：
1. "*": "ask"        ← 先匹配
2. "ls *": "allow"   ← 后匹配（最终生效）

结果：ls 命令被允许
```

### 4.2 为什么通配符要放在前面

```jsonc
{
  "bash": {
    // ❌ 错误顺序：具体规则在前，通配符在后
    "git status*": "allow",   // 这条会被后面的 * 覆盖！
    "*": "deny",              // 最后匹配，最终所有命令都被拒绝

    // ✅ 正确顺序：通配符在前，具体规则在后
    "*": "ask",               // 默认规则（先匹配）
    "git status*": "allow",   // 具体规则（后匹配，最终生效）
    "rm -rf*": "deny"         // 危险规则（最后匹配，覆盖默认值）
  }
}
```

### 4.3 匹配顺序图解

```
用户执行：git status

匹配流程：
┌──────────────────────────────────────┐
│ 1. "*": "ask"          → 匹配,暂存  │
│ 2. "git status*": "allow" → 匹配,覆盖 │
│ 3. "git push*": "deny"  → 不匹配    │
└──────────────────────────────────────┘
最终结果：allow（最后一条匹配的规则）
```

### 4.4 v1.15.13 权限顺序修复

> **版本标注**: v1.15.13

在 v1.15.13 之前的版本（包括 v1.14.32），权限规则的内部排序存在一个问题：**通配符规则可能被错误地优先于具体规则处理**。这意味着即使你按正确的顺序编写了配置，某些具体规则也可能被通配符覆盖。

**v1.15.13 修复内容**:

- 修复了权限规则排序算法，确保**严格遵循配置文件中声明的顺序**
- 具体规则现在能够可靠地覆盖通配符规则
- 建议在 v1.15.13+ 版本中重新检查权限配置的实际行为

**升级建议**:

```bash
# 检查当前版本
opencode --version

# 升级到最新版本（推荐）
npm install -g @opencode/cli@latest

# 升级后验证权限行为
opencode config validate
```

---

## 5. 各权限字段详解与设计哲学

### 5.1 `read` — 文件读取控制

```jsonc
"read": {
  "*": "allow",
  "*.env": "deny",
  "*.env.*": "deny",
  "*.env.example": "allow"
}
```

| 规则 | 设计理念 |
|------|---------|
| `"*": "allow"` | AI 需要读取项目文件才能理解上下文，全面禁止会导致 AI 无法工作 |
| `"*.env": "deny"` | `.env` 文件包含生产环境密钥（数据库密码、API Token），**绝对不可让 AI 接触** |
| `"*.env.*": "deny"` | 覆盖 `.env.local`、`.env.production`、`.env.staging` 等变体 |
| `"*.env.example": "allow"` | 示例文件只包含空模板，无敏感信息，可以读取 |

**为什么 `.env.example` 是安全的？**

```bash
# .env.example —— 只包含占位符，无真实值
DATABASE_URL=postgres://user:password@localhost:5432/db
API_KEY=your-api-key-here
```

### 5.2 `edit` — 文件编辑控制

```jsonc
"edit": "ask"
```

文件编辑是**不可逆操作**，设置为 `ask` 意味着每次 AI 尝试修改文件时，都会弹出确认提示。这防止了：

- AI 误解意图导致的错误修改
- 循环中的重复修改
- 对核心配置文件的意外篡改

**如果设置为 `allow` 的风险**：

```
场景：你要求 AI "优化代码"
结果：AI 可能同时修改 20+ 个文件，且无法撤销
```

### 5.3 `bash` — 命令执行控制

`bash` 是权限配置中最复杂的部分，也是**安全防护的核心**。

#### 5.3.1 安全只读命令（`allow`）

```jsonc
"git status*": "allow",
"git diff*": "allow",
"git log*": "allow",
"git branch*": "allow",
"rg *": "allow",
"grep *": "allow",
"ls *": "allow",
"cat *": "allow"
```

**设计理由**：这些命令只读取信息，不产生任何副作用。允许它们可以大幅提升 AI 的工作效率（AI 可以自主查看项目状态、搜索代码、了解历史），同时不带来任何安全风险。

#### 5.3.2 测试/构建命令（`ask`）

```jsonc
"pnpm test*": "ask",
"npm test*": "ask",
"bun test*": "ask",
"pnpm typecheck*": "ask",
"pnpm lint*": "ask"
```

**设计理由**：这些命令通常安全，但有**副作用**（消耗 CPU/内存、生成临时文件、可能修改缓存）。设置为 `ask` 让用户在适当的时机授权执行。

#### 5.3.3 危险命令（`deny`）

```jsonc
"git push*": "deny",          // 🔴 禁止原因：推送未经审查的代码到远程
"git reset --hard*": "deny",  // 🔴 禁止原因：永久丢失未提交的修改
"git clean*": "deny",         // 🔴 禁止原因：删除未跟踪的文件（可能包含重要内容）
"rm -rf*": "deny",            // 🔴 禁止原因：递归删除，破坏力极大
"pkill *": "deny",            // 🔴 禁止原因：终止系统进程，可能导致不稳定
"killall *": "deny"           // 🔴 禁止原因：同上
```

**`git push` 为什么必须 `deny`？**

AI 可能在以下场景下尝试 `git push`：

1. 你要求 "部署到生产环境"
2. AI 自动 commit 后认为 "应该推送"
3. 对话中的误解导致 AI 认为 push 是必要的

**后果**：未经人工 code review 的代码被推送到远程，可能引入 bug 或安全漏洞。

#### 5.3.4 进程管理命令的分平台策略

```jsonc
"pkill *": "deny",        // Linux/macOS
"killall *": "deny",      // Linux/macOS
"taskkill *": "ask",      // Windows
"kill *": "ask"           // 跨平台通用
```

**为什么 `taskkill` 是 `ask` 而 `pkill` 是 `deny`？**

- `pkill` / `killall` 支持**正则匹配进程名**，误杀风险高（如 `pkill node` 会杀死所有 Node 进程）
- `taskkill` 需要显式指定 PID 或进程名，误操作概率较低
- `kill` 需要指定 PID，通常是有明确意图的操作

### 5.4 网络与外部权限

```jsonc
"external_directory": "ask",  // 访问项目根目录之外的文件
"doom_loop": "ask",           // AI 陷入无限循环时的处理
"webfetch": "ask",            // 抓取指定 URL 的内容
"websearch": "ask"            // 使用搜索引擎查询
```

| 权限 | 说明 | 风险 |
|------|------|------|
| `external_directory` | 允许 AI 读取 `~/.ssh/`、`/etc/` 等系统目录 | 可能泄露系统配置和个人密钥 |
| `doom_loop` | AI 反复执行相同操作无法终止 | 消耗大量 API Token 和系统资源 |
| `webfetch` | AI 访问任意网页 | 可能访问恶意网站，或泄露内部信息到 URL 参数 |
| `websearch` | AI 使用搜索引擎 | 搜索关键词可能暴露项目内部信息 |

---

## 6. Agent 级别独立权限（v1.15.x）

> **版本要求**: v1.15.x+
>
> **v1.14.32 用户**: 此功能不可用，请跳过本节或使用全局权限配置

### 6.1 什么是 Agent 级别权限

OpenCode v1.15.x 引入了**多 Agent 架构**，不同的 Agent 承担不同的角色（如 `plan` 规划、`build` 构建）。每个 Agent 可以拥有**独立的权限配置**，覆盖全局权限。

```jsonc
{
  "permission": {
    // 全局权限（所有 Agent 的默认值）
    "edit": "ask",
    "bash": "ask"
  },
  "agent": {
    "plan": {
      "permission": {
        // Plan Agent 专属权限（覆盖全局）
        "edit": "deny"   // 规划阶段不允许修改文件
      }
    },
    "build": {
      "permission": {
        // Build Agent 专属权限
        "edit": "allow"  // 构建阶段可以编辑文件
      }
    }
  }
}
```

### 6.2 权限继承与覆盖规则

Agent 权限遵循**"就近优先"**原则：

```
权限查找顺序：
Agent 专属权限 → 全局权限 → 默认值（ask）

如果 Agent 权限中定义了某字段 → 使用 Agent 的值
如果 Agent 权限中未定义某字段 → 回退到全局权限
```

### 6.3 常见 Agent 类型

| Agent 名称 | 角色 | 推荐权限策略 |
|-----------|------|-------------|
| `plan` | 分析与规划 | 只读权限，`edit: deny` |
| `build` | 编码与构建 | 编辑权限，`edit: ask/allow` |

### 6.4 完整 Agent 权限示例

```jsonc
{
  "agent": {
    // ---- Plan Agent：保守策略 —— 只分析，不修改 ----
    "plan": {
      "permission": {
        "edit": "deny",        // ❌ 规划阶段禁止任何文件修改
        "bash": "ask"          // ⚠️ 命令执行需确认（只允许分析类命令）
      }
    },

    // ---- Build Agent：宽松策略 —— 允许编码，但限制危险操作 ----
    "build": {
      "permission": {
        "edit": "ask",         // ⚠️ 编辑前确认（防止误改）
        "bash": {
          "*": "ask",
          // 安全命令白名单
          "git status*": "allow",
          "git diff*": "allow",
          "rg *": "allow",
          "ls *": "allow",
          "cat *": "allow",

          // 测试命令
          "pnpm test*": "ask",
          "npm test*": "ask",

          // 危险命令（始终拒绝）
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

---

## 7. v1.14.32 vs v1.15.13 版本差异

| 特性 | v1.14.32 | v1.15.13+ | 说明 |
|------|----------|-----------|------|
| 全局权限配置 | ✅ | ✅ | 基础的 `permission` 字段 |
| Agent 独立权限 | ❌ | ✅ | v1.15.x 新增 `agent` 字段 |
| `skill` 权限控制 | ❌ | ✅ | v1.15.x 新增权限字段 |
| 权限规则排序 | ⚠️ 有问题 | ✅ 已修复 | v1.15.13 修复了规则排序 Bug |
| `doom_loop` 权限 | ✅ | ✅ | 两版本均支持 |

### 7.1 迁移指南（v1.14.32 → v1.15.13）

```jsonc
// v1.14.32 配置（仅全局权限）
{
  "permission": {
    "*": "ask",
    "edit": "ask",
    "bash": { "*": "ask" }
  }
}

// v1.15.13 配置（全局 + Agent 权限）
{
  "permission": {
    "*": "ask",
    "edit": "ask",
    "bash": { "*": "ask" }
    // "skill": "ask"  // v1.15.x 新增，可选
  },
  "agent": {
    "plan": {
      "permission": {
        "edit": "deny"  // 为 Plan Agent 单独配置
      }
    }
  }
}
```

**向后兼容说明**：v1.15.13 完全兼容 v1.14.32 的配置格式。旧配置无需修改即可在新版本中使用，Agent 权限是可选的增强功能。

---

## 8. 常见问题 FAQ

### Q1: 为什么我的 `*.env` 规则不生效？

**A**: 检查规则顺序。在 `read` 对象中，通配符 `"*": "allow"` 必须放在最前面，具体规则放在后面：

```jsonc
// ✅ 正确
"read": {
  "*": "allow",
  "*.env": "deny"
}

// ❌ 错误（deny 会被后面的 allow 覆盖）
"read": {
  "*.env": "deny",
  "*": "allow"
}
```

### Q2: 如何让 AI 能够执行特定脚本？

**A**: 在 `bash` 中添加具体规则：

```jsonc
"bash": {
  "*": "ask",
  "pnpm build*": "allow",     // 允许构建
  "pnpm dev*": "allow",       // 允许启动开发服务器
  "./scripts/deploy.sh*": "ask" // 自定义脚本需确认
}
```

### Q3: Agent 权限和全局权限冲突时怎么办？

**A**: Agent 权限**完全覆盖**全局权限，不存在合并行为：

```jsonc
{
  "permission": { "edit": "ask" },     // 全局：编辑前询问
  "agent": {
    "plan": {
      "permission": { "edit": "deny" } // Plan Agent：完全禁止编辑
    }
  }
}
// Plan Agent 的 edit 权限是 deny，不会继承全局的 ask
```

### Q4: 如何验证权限配置是否正确？

**A**: 使用配置验证命令：

```bash
# 验证 JSON 语法
opencode config validate

# 查看当前生效的权限规则
opencode config show --effective

# 测试特定命令的权限判定
opencode config test --command "git status"
```

### Q5: `skill` 权限是做什么的？

**A**: `skill` 是 v1.15.x 新增的权限字段，用于控制 AI **技能（Skill）**的调用。技能是预定义的高级功能模块（如代码重构、测试生成等）。

```jsonc
{
  "permission": {
    "skill": "ask"   // 每次调用技能前询问
  }
}
```

---

## 附录：快速配置模板

### 极简安全模板（推荐入门）

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "*": "ask",
    "read": { "*": "allow", "*.env*": "deny", "*.env.example": "allow" },
    "edit": "ask",
    "bash": {
      "*": "ask",
      "git status*": "allow",
      "git diff*": "allow",
      "ls *": "allow",
      "git push*": "deny",
      "rm -rf*": "deny"
    }
  }
}
```

### 团队协作模板（v1.15.x 推荐）

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "*": "ask",
    "read": { "*": "allow", "*.env*": "deny", "*.env.example": "allow" },
    "edit": "ask",
    "bash": {
      "*": "ask",
      "git status*": "allow", "git diff*": "allow",
      "git log*": "allow", "git branch*": "allow",
      "rg *": "allow", "ls *": "allow", "cat *": "allow",
      "pnpm test*": "ask", "npm test*": "ask",
      "git push*": "deny", "git reset --hard*": "deny",
      "git clean*": "deny", "rm -rf*": "deny",
      "pkill *": "deny", "killall *": "deny"
    }
  },
  "agent": {
    "plan": { "permission": { "edit": "deny", "bash": "ask" } },
    "build": {
      "permission": {
        "edit": "ask",
        "bash": {
          "*": "ask",
          "git status*": "allow", "git diff*": "allow",
          "rg *": "allow", "pnpm test*": "ask",
          "git push*": "deny", "git reset --hard*": "deny",
          "git clean*": "deny", "rm -rf*": "deny",
          "pkill *": "deny", "killall *": "deny"
        }
      }
    }
  }
}
```

---

> **文档版本**: 1.0.0
>
> **最后更新**: 适配 OpenCode CLI v1.14.32 / v1.15.13
>
> **相关文档**: [01-快速入门](./01-quickstart.md) | [02-配置文件详解](./02-config.md) | [03-Agent 模式](./03-agent-modes.md)
