# OpenCode 配置系统详解

OpenCode 采用了一套灵活而强大的分级配置体系，支持从个人全局设置到项目级覆盖的多层配置策略。理解其配置优先级、合并规则和环境变量机制，是在团队协作和多项目开发中高效使用 OpenCode 的关键。本章将深入解析 OpenCode 的配置系统架构，帮助你构建可维护、可复用的配置方案。

---

## 1. 配置文件类型与格式

### 1.1 支持的配置文件名

OpenCode 支持以下几种配置文件名，按加载优先级排序：

| 文件名 | 说明 | JSONC 支持 | 优先级 |
|--------|------|-----------|--------|
| `opencode.json` | 标准配置文件名 | ❌ | 高 |
| `opencode.jsonc` | 标准配置（带注释） | ✅ | 高 |
| `tui.json` | TUI 专用配置 | ❌ | 中 |
| `tui.jsonc` | TUI 专用配置（带注释） | ✅ | 中 |
| `config.json` | 旧版兼容名 | ❌ | 低（最先加载） |

**推荐使用 `opencode.jsonc`**，它允许在 JSON 中添加注释，便于团队协作时标注配置意图：

```jsonc
// opencode.jsonc - 项目级配置示例
{
  // 主力模型：使用 Claude 3.5 Sonnet 处理复杂任务
  "model": "claude-3.5-sonnet",

  // 轻量模型：使用 GPT-4o-mini 处理简单任务
  "small_model": "gpt-4o-mini",

  /* MCP 服务器配置 */
  "mcp": {
    "servers": [
      {
        "name": "filesystem",
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "."]
      }
    ]
  }
}
```

### 1.2 JSON Schema 验证

OpenCode 提供了官方 JSON Schema 用于配置验证和 IDE 自动补全：

```json
{
  "$schema": "https://opencode.ai/config.json"
}
```

在支持 JSON Schema 的编辑器（VS Code、JetBrains 系列等）中，添加 `$schema` 字段后可获得：

- **属性自动补全**：输入时提示可用的配置项
- **类型检查**：实时校验值类型是否匹配
- **悬停文档**：鼠标悬停查看配置项说明
- **格式验证**：高亮不符合 Schema 的配置

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "claude-3.5-sonnet",
  "small_model": "gpt-4o-mini"
}
```

### 1.3 TUI 专用配置

`tui.json` / `tui.jsonc` 用于存储终端用户界面（TUI）相关的配置，如主题颜色、布局偏好、快捷键绑定等。这类配置通常属于个人偏好，建议放在全局配置目录而非项目配置中。

---

## 2. 配置优先级体系（核心）

OpenCode 的配置系统采用**多层覆盖**策略，共有 9 个优先级层级。当同一配置项在多个层级中出现时，**高优先级层的值覆盖低优先级层的值**。

### 2.1 优先级总览图

```
优先级（从低到高）

  1. ┌─────────────────────┐  ← 内置默认值（最低优先级）
     │   Built-in Defaults │
  2. ├─────────────────────┤  ← 远程配置（.well-known/opencode）
     │   Remote Config     │
  3. ├─────────────────────┤  ← 全局配置（~/.config/opencode/）
     │   Global Config     │
  4. ├─────────────────────┤  ← 自定义路径（OPENCODE_CONFIG）
     │   Custom Path       │
  5. ├─────────────────────┤  ← 项目配置（./opencode.json）
     │   Project Config    │
  6. ├─────────────────────┤  ← .opencode/ 目录
     │   .opencode/ Dir    │
  7. ├─────────────────────┤  ← 内联配置（OPENCODE_CONFIG_CONTENT）
     │   Inline Config     │
  8. ├─────────────────────┤  ← 托管配置文件
     │   Managed Config    │
  9. └─────────────────────┘  ← macOS MDM（最高优先级）
        macOS MDM Profile
```

### 2.2 各层级详解

#### Layer 1: 内置默认值（Built-in Defaults）

OpenCode 内置的默认配置是最低优先级层，确保软件在没有用户配置时也能正常运行。这些默认值涵盖模型选择、超时设置、权限策略等基础参数。

#### Layer 2: 远程配置（Remote Config via `.well-known/opencode`）

企业或团队可以通过在域名下部署 `.well-known/opencode` 端点来分发统一配置。这适用于需要为整个组织标准化 OpenCode 行为的场景。

例如，公司可以在 `https://company.internal/.well-known/opencode` 提供：

```json
{
  "model": "claude-3.5-sonnet",
  "disabled_providers": ["openai"],
  "instructions": ["./company-coding-standards.md"],
  "permission": {
    "allow": ["read", "edit"],
    "deny": ["execute", "network"]
  }
}
```

OpenCode 启动时会自动检测并加载远程配置，适用于企业级统一管控。

#### Layer 3: 全局配置（Global Config）

全局配置存储在用户主目录下，对当前用户的所有 OpenCode 会话生效：

- **Linux/macOS**: `~/.config/opencode/opencode.json`
- **Windows**: `%APPDATA%\opencode\opencode.json`

全局配置用于存储个人偏好设置，如默认模型选择、个人 API Key、常用插件等。

#### Layer 4: 自定义路径（`OPENCODE_CONFIG` 环境变量）

通过 `OPENCODE_CONFIG` 环境变量指定一个自定义配置文件路径：

```bash
export OPENCODE_CONFIG=/path/to/my/custom-config.json
opencode
```

这在以下场景特别有用：

- 测试不同配置组合
- CI/CD 流水线中指定构建专用配置
- 在多个身份/角色间快速切换

#### Layer 5: 项目配置（Project Config）

项目配置是 OpenCode 配置系统的核心特性。OpenCode 从**当前工作目录**开始，**向上遍历至 Git 根目录**，查找 `opencode.json` 或 `opencode.jsonc` 文件。

```
查找过程示例：

/repo/
  ├── .git/                          ← 遍历到 Git 根目录停止
  ├── backend/
  │   └── service-a/
  │       └── opencode.json   ← 如果从这里启动，向上找到这里
  ├── frontend/
  │   └── opencode.json       ← 前端项目有自己的配置
  └── opencode.json           ← 仓库根级别的配置（也被加载）
```

**重要规则**：项目配置不是"找到最近的就停"，而是**加载路径上的所有配置**，从 Git 根目录开始向下合并。后匹配的规则优先。

假设目录结构如下：

```
/monorepo/
  ├── opencode.json           # 根配置：model="gpt-4o"
  ├── packages/
  │   ├── api/
  │   │   └── opencode.json   # API 包配置：model="claude-3.5-sonnet"
  │   └── web/
  │       └── opencode.json   # Web 包配置：small_model="gpt-4o-mini"
```

从 `/monorepo/packages/api/` 启动时：

1. 先加载 `/monorepo/opencode.json`（`model: "gpt-4o"`）
2. 再加载 `/monorepo/packages/api/opencode.json`（`model: "claude-3.5-sonnet"`）
3. 最终 `model` = `"claude-3.5-sonnet"`（后加载的覆盖）

#### Layer 6: `.opencode/` 目录

项目根目录下的 `.opencode/` 目录可以包含多个子目录和配置文件，作为项目配置的扩展：

```
.opencode/
├── agents/          # 自定义 Agent 定义
├── commands/        # 自定义命令
├── skills/          # 技能定义
├── plugins/         # 插件配置
├── tools/           # 工具定义
├── themes/          # 主题配置
└── modes/           # 模式配置
```

`.opencode/` 目录的内容比单独的 `opencode.json` 具有更高优先级，适合需要复杂配置结构的项目。

#### Layer 7: 内联配置（`OPENCODE_CONFIG_CONTENT`）

通过环境变量直接传递 JSON 配置内容，无需写入文件：

```bash
export OPENCODE_CONFIG_CONTENT='{"model":"claude-3.5-sonnet","small_model":"gpt-4o-mini"}'
opencode
```

这在以下场景非常实用：

- **一次性测试**：快速验证某个配置组合的效果
- **CI/CD 流水线**：在自动化脚本中动态注入配置
- **临时覆盖**：在不修改配置文件的情况下临时调整行为

> ⚠️ **版本差异注意**：在 v1.14.32 中，`OPENCODE_CONFIG_CONTENT` 的优先级存在 bug，可能会被 `.opencode/` 目录的配置覆盖。v1.15.13 已修复此问题。详见[第 8 节](#8-版本差异对比v11432-vs-v11513)。

#### Layer 8: 托管配置文件（Managed Config Files）

企业环境可以通过集中管理的配置文件分发策略控制 OpenCode 行为。这通常与远程配置配合使用。

#### Layer 9: macOS MDM 托管偏好设置（最高优先级）

在 macOS 平台上，Mobile Device Management (MDM) 系统可以通过 Managed Preferences 推送配置，这是整个优先级体系中的最高层级，企业管理员可以使用它来强制实施安全策略：

```xml
<!-- com.opencodeai.config.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" 
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>model</key>
    <string>claude-3.5-sonnet</string>
    <key>permission</key>
    <dict>
        <key>allow</key>
        <array>
            <string>read</string>
            <string>edit</string>
        </array>
        <key>deny</key>
        <array>
            <string>execute</string>
            <string>network</string>
        </array>
    </dict>
</dict>
</plist>
```

MDM 配置适用于：

- 强制锁定模型选择（如仅允许使用企业内部部署模型）
- 禁用危险权限（如代码执行、网络访问）
- 预配置企业 MCP 服务器

---

## 3. 合并策略与深度合并规则

### 3.1 核心原则：合并而非替换

OpenCode 的配置合并遵循"合并而非替换"的原则。当多个配置层级中存在非冲突的键时，**所有键都会被保留**，只有冲突的键才会按优先级覆盖。

```
层级 A (低优先级)          层级 B (高优先级)         合并结果
┌─────────────────┐       ┌─────────────────┐      ┌─────────────────┐
│ "model": "gpt-4o"│      │ "small_model":   │      │ "model": "gpt-4o"│  ← 保留
│                 │   +   │   "gpt-4o-mini"  │  =   │ "small_model":   │  ← 新增
│ "plugin": ["a"] │       │ "plugin": ["b"]  │      │   "gpt-4o-mini"  │
│                 │       │                 │      │ "plugin": ["a","b"]│ ← 合并
└─────────────────┘       └─────────────────┘      └─────────────────┘
                                                       ↑ 非冲突键全部保留
```

### 3.2 对象字段：深度合并

对于嵌套对象（如 `permission`、`agent`、`mcp` 等），OpenCode 使用**深度合并**（deep merge）策略：

```json
// 全局配置 (低优先级)
{
  "permission": {
    "allow": ["read", "edit"],
    "timeout": 30
  }
}

// 项目配置 (高优先级)
{
  "permission": {
    "allow": ["execute"],
    "max_tokens": 4096
  }
}

// 合并结果：同键覆盖，异键保留
{
  "permission": {
    "allow": ["execute"],        // ← 项目配置覆盖
    "timeout": 30,                // ← 全局配置保留
    "max_tokens": 4096            // ← 项目配置新增
  }
}
```

深度合并意味着对象的每个属性会单独比较和合并，而不是整个对象被替换。

### 3.3 数组字段：拼接并去重

对于数组类型的配置项（主要是 `plugin` 和 `instructions`），OpenCode 采用**拼接后去重**的策略：

```json
// 全局配置
{
  "plugin": ["git", "github"],
  "instructions": ["~/.config/opencode/global-prompt.md"]
}

// 项目配置
{
  "plugin": ["github", "docker"],        // "github" 重复
  "instructions": ["./project-prompt.md"]  // 新项目指令
}

// 合并结果
{
  "plugin": ["git", "github", "docker"],          // 拼接后去重
  "instructions": [
    "~/.config/opencode/global-prompt.md",          // 全局指令保留
    "./project-prompt.md"                            // 项目指令追加
  ]
}
```

**数组合并规则总结**：

| 配置项 | 合并行为 | 说明 |
|--------|---------|------|
| `plugin` | 拼接并去重 | 插件列表累加，重复项只保留一个 |
| `instructions` | 拼接不去重 | 指令文件按顺序加载，重复路径有意义 |
| `mcp.servers` | 按 `name` 去重 | 同名服务器后加载的覆盖 |
| `enabled_providers` | 拼接并去重 | 提供商列表累加 |
| `disabled_providers` | 拼接并去重 | 禁用列表累加 |

### 3.4 后匹配规则优先

在配置链中，当同一键出现在多个层级时，**后加载（高优先级）的值胜出**：

```bash
# 加载顺序示意（从低优先级到高优先级）
1. 内置默认值      → model="gpt-4o"
2. 全局配置        → model="claude-3.5-sonnet"   # 覆盖
3. 项目根配置      → (未设置 model，保留上值)
4. 子项目配置      → model="gpt-4o-mini"          # 再次覆盖
5. .opencode/      → (未设置 model，保留上值)
# 最终结果: model="gpt-4o-mini"
```

---

## 4. 环境变量

OpenCode 提供了一组环境变量用于控制配置加载行为和注入内联配置。

### 4.1 环境变量速查表

| 环境变量 | 作用 | 示例值 |
|----------|------|--------|
| `OPENCODE_CONFIG` | 指定自定义配置文件路径 | `/path/to/config.json` |
| `OPENCODE_CONFIG_CONTENT` | 内联 JSON 配置内容 | `'{"model":"gpt-4o"}'` |
| `OPENCODE_CONFIG_DIR` | 指定配置根目录 | `/custom/config/dir` |
| `OPENCODE_DISABLE_PROJECT_CONFIG` | 禁用项目配置查找 | `1` 或 `true` |
| `OPENCODE_DISABLE_GLOBAL_CONFIG` | 禁用全局配置加载 | `1` 或 `true` |
| `OPENCODE_NO_PARENT_CONFIG` | 禁止父目录配置继承 | `1` 或 `true` |

### 4.2 使用示例

#### 指定自定义配置文件

```bash
# 使用特定配置文件启动
OPENCODE_CONFIG=~/work/configs/opencode-work.json opencode

# 或者先导出环境变量
export OPENCODE_CONFIG=~/work/configs/opencode-work.json
opencode
```

#### 内联配置（快速测试）

```bash
# 临时切换到不同模型测试
OPENCODE_CONFIG_CONTENT='{"model":"gpt-4o","small_model":"gpt-4o-mini"}' opencode

# 在 CI 流水线中注入配置
OPENCODE_CONFIG_CONTENT='{
  "model": "gpt-4o-mini",
  "permission": {"allow":["read"],"deny":["execute","network"]}
}' opencode review --pr 123
```

#### 禁用项目配置（使用纯全局设置）

```bash
# 在不受信任的项目中工作时，禁用项目配置以防止恶意配置执行
OPENCODE_DISABLE_PROJECT_CONFIG=1 opencode
```

#### 禁止父目录配置继承

```bash
# 在 monorepo 的子包中工作时，只使用当前目录的配置
# 不继承上级目录的配置
OPENCODE_NO_PARENT_CONFIG=1 opencode
```

#### 组合使用

```bash
# 完全隔离：只使用指定的配置文件，不加载任何其他配置
OPENCODE_DISABLE_GLOBAL_CONFIG=1 \
OPENCODE_DISABLE_PROJECT_CONFIG=1 \
OPENCODE_CONFIG=/tmp/isolated-config.json \
opencode
```

### 4.3 环境变量配置 vs 文件配置

| 场景 | 推荐方式 | 原因 |
|------|---------|------|
| 长期个人偏好 | `~/.config/opencode/opencode.json` | 持久化，跨会话生效 |
| 项目级标准 | `./opencode.json` | 版本控制，团队协作 |
| 临时测试 | `OPENCODE_CONFIG_CONTENT` | 无需创建文件，快速验证 |
| CI/CD 流水线 | `OPENCODE_CONFIG` 或 `OPENCODE_CONFIG_CONTENT` | 环境隔离，动态注入 |
| 安全隔离 | `OPENCODE_DISABLE_PROJECT_CONFIG=1` | 防止不受信任配置执行 |

---

## 5. 全局配置

### 5.1 配置位置

全局配置存储在用户主目录的标准配置路径中：

**Linux / macOS:**
```
~/.config/opencode/opencode.json
```

**Windows:**
```
%APPDATA%\opencode\opencode.json
```

> 在 Windows 上，`%APPDATA%` 通常解析为 `C:\Users\<用户名>\AppData\Roaming\`。

### 5.2 全局配置搜索文件名顺序

在全局配置目录 `~/.config/opencode/` 下，OpenCode 按以下顺序搜索配置文件：

```
1. config.json          ← 旧版兼容名（最先加载，优先级最低）
2. kilo.json / kilo.jsonc   ← Kilo Code 配置兼容
3. opencode.json / opencode.jsonc   ← 标准配置名（最后加载，优先级最高）
```

**重要**：多个文件可以同时存在，OpenCode 会按顺序加载所有文件并合并。后加载的文件中的冲突键会覆盖先加载的。

```bash
# 示例：全局配置目录结构
~/.config/opencode/
├── config.json              # 旧配置（逐步迁移中）
├── opencode.jsonc           # 新配置（推荐，优先级更高）
├── tui.jsonc                # TUI 界面偏好
├── agents/                  # 自定义 Agent
│   ├── code-reviewer.json
│   └── doc-writer.json
├── commands/                # 自定义命令
├── skills/                  # 技能定义
├── plugins/                 # 插件
└── themes/                  # 主题
```

### 5.3 完整全局配置示例

以下是一个功能完整的全局配置示例：

```jsonc
// ~/.config/opencode/opencode.jsonc
{
  "$schema": "https://opencode.ai/config.json",

  // ===== 模型配置 =====
  "model": "claude-3.5-sonnet",
  "small_model": "gpt-4o-mini",

  // ===== 提供商配置 =====
  "provider": {
    "anthropic": {
      "api_key": "{env:ANTHROPIC_API_KEY}",
      "base_url": "https://api.anthropic.com"
    },
    "openai": {
      "api_key": "{env:OPENAI_API_KEY}"
    }
  },

  // ===== 权限配置 =====
  "permission": {
    "allow": ["read", "edit", "browser"],
    "deny": ["execute"]
  },

  // ===== Agent 配置 =====
  "agent": {
    "default": {
      "system_prompt": "你是一位资深软件工程师，擅长代码审查和重构。"
    }
  },

  // ===== 指令文件 =====
  "instructions": [
    "~/.config/opencode/instructions/coding-style.md",
    "~/.config/opencode/instructions/commit-convention.md"
  ],

  // ===== MCP 服务器 =====
  "mcp": {
    "servers": [
      {
        "name": "filesystem",
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "."]
      }
    ]
  },

  // ===== 插件列表 =====
  "plugin": ["git", "github"],

  // ===== 自动更新 =====
  "autoupdate": true
}
```

---

## 6. 项目配置

### 6.1 项目配置查找机制

OpenCode 的项目配置查找遵循以下规则：

1. 从**当前工作目录**（CWD）开始
2. 向上遍历目录树，查找 `opencode.json` 或 `opencode.jsonc`
3. 直到遇到 **Git 根目录**（`.git/` 所在目录）停止
4. **加载路径上的所有配置**，从 Git 根开始向下合并
5. 后加载的配置优先级更高

```
项目配置查找流程图：

  当前目录: /repo/packages/api/src/
                    │
                    ▼
  查找 /repo/packages/api/src/opencode.json ──→ 未找到
                    │
                    ▼
  查找 /repo/packages/api/opencode.json ──────→ ✅ 找到 (优先级 3)
                    │
                    ▼
  查找 /repo/packages/opencode.json ──────────→ 未找到
                    │
                    ▼
  查找 /repo/opencode.json ───────────────────→ ✅ 找到 (优先级 2)
                    │
                    ▼
              .git/ 目录存在 ─────────────────→ ⛔ 停止遍历
                    │
                    ▼
  加载顺序: /repo/opencode.json → /repo/packages/api/opencode.json
  合并优先级: 后加载的 api/opencode.json 覆盖冲突键
```

### 6.2 Monorepo 配置策略

在 monorepo 结构中，推荐采用**分层配置**策略：

```
monorepo/
├── .git/
├── opencode.json                 # 根配置：通用设置
├── .opencode/
│   ├── agents/
│   └── commands/
├── packages/
│   ├── backend/
│   │   ├── api/
│   │   │   └── opencode.json     # API 服务特有配置
│   │   └── worker/
│   │       └── opencode.json     # Worker 服务特有配置
│   └── frontend/
│       └── opencode.json         # 前端特有配置
└── docs/
    └── opencode.json             # 文档相关配置
```

**根配置示例**（`monorepo/opencode.json`）：

```json
{
  "model": "claude-3.5-sonnet",
  "small_model": "gpt-4o-mini",
  "permission": {
    "allow": ["read", "edit"],
    "deny": ["execute"]
  },
  "instructions": ["./common-coding-standards.md"],
  "plugin": ["git"]
}
```

**后端配置示例**（`monorepo/packages/backend/api/opencode.json`）：

```json
{
  "instructions": ["./backend-specific-rules.md"],
  "plugin": ["docker", "postgres"],
  "mcp": {
    "servers": [
      {
        "name": "database",
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://localhost/dev"]
      }
    ]
  }
}
```

**前端配置示例**（`monorepo/packages/frontend/opencode.json`）：

```json
{
  "instructions": ["./frontend-specific-rules.md"],
  "plugin": ["eslint", "vite"]
}
```

### 6.3 完整项目配置示例

```jsonc
// opencode.jsonc - 项目级配置
{
  "$schema": "https://opencode.ai/config.json",

  // ===== 模型覆盖 =====
  // 本项目使用 Claude 3.5 Sonnet 作为主模型
  "model": "claude-3.5-sonnet",

  // ===== 项目指令 =====
  // 按顺序加载，后面的可以覆盖前面的
  "instructions": [
    "./docs/coding-standards.md",
    "./docs/architecture-decisions.md",
    "./docs/api-conventions.md"
  ],

  // ===== MCP 服务器 =====
  "mcp": {
    "servers": [
      {
        "name": "project-docs",
        "transport": "stdio",
        "command": "node",
        "args": ["./scripts/mcp-doc-server.js"]
      },
      {
        "name": "test-runner",
        "transport": "stdio",
        "command": "npm",
        "args": ["run", "test:watch"]
      }
    ]
  },

  // ===== 项目插件 =====
  "plugin": ["jest", "eslint"],

  // ===== 权限收紧 =====
  // 生产项目禁止执行命令
  "permission": {
    "allow": ["read", "edit", "browser"],
    "deny": ["execute", "network"]
  }
}
```

---

## 7. 变量替换

OpenCode 支持在配置文件中使用变量占位符，在加载时动态替换为实际值。

### 7.1 环境变量替换

使用 `{env:VARIABLE_NAME}` 语法引用环境变量：

```json
{
  "provider": {
    "anthropic": {
      "api_key": "{env:ANTHROPIC_API_KEY}",
      "base_url": "{env:ANTHROPIC_BASE_URL}"
    },
    "openai": {
      "api_key": "{env:OPENAI_API_KEY}"
    }
  },
  "mcp": {
    "servers": [
      {
        "name": "postgres",
        "command": "npx",
        "args": [
          "-y",
          "@modelcontextprotocol/server-postgres",
          "{env:DATABASE_URL}"
        ]
      }
    ]
  }
}
```

**实际使用**：

```bash
export ANTHROPIC_API_KEY=sk-ant-xxx
export DATABASE_URL=postgresql://user:pass@localhost:5432/mydb
opencode
```

### 7.2 文件内容替换

使用 `{file:path}` 语法将文件内容内联到配置中：

```json
{
  "agent": {
    "default": {
      "system_prompt": "{file:./prompts/system-prompt.txt}"
    }
  },
  "instructions": [
    "{file:./docs/coding-standards.md}"
  ]
}
```

这在需要：

- 引用外部 Prompt 文件（避免在 JSON 中转义）
- 共享长文本配置（如系统提示词）
- 将敏感信息与配置文件分离

### 7.3 变量替换执行时机

变量替换在配置加载时执行，遵循以下顺序：

1. 加载原始配置文件内容
2. 解析 JSON / JSONC
3. **执行变量替换**（递归替换所有 `{env:...}` 和 `{file:...}`）
4. 执行配置合并
5. 验证最终配置

**注意事项**：

- 如果环境变量未定义，替换后的值为空字符串（不会报错）
- 文件路径是相对于**配置文件所在目录**的
- 变量替换发生在合并之前，每个文件的变量独立解析

---

## 8. 版本差异对比：v1.14.32 vs v1.15.13

OpenCode 的配置系统在 v1.15.13 中进行了重要修复和改进。以下是需要关注的差异：

### 8.1 `OPENCODE_CONFIG_CONTENT` 优先级修复

| 版本 | 行为 | 影响 |
|------|------|------|
| v1.14.32 | `OPENCODE_CONFIG_CONTENT` 可能被 `.opencode/` 目录配置覆盖 | 内联配置在存在 `.opencode/` 目录时不生效 |
| v1.15.13 | `OPENCODE_CONFIG_CONTENT` 正确保持高优先级 | 内联配置始终生效（除非被 MDM 覆盖） |

**v1.14.32 的问题场景**：

```bash
# 在包含 .opencode/ 目录的项目中
export OPENCODE_CONFIG_CONTENT='{"model":"gpt-4o"}'
# 实际使用的 model 可能是 .opencode/ 中配置的，而非 gpt-4o
```

**v1.15.13 的正确行为**：

```bash
# 同样的场景
export OPENCODE_CONFIG_CONTENT='{"model":"gpt-4o"}'
# model 一定是 gpt-4o，.opencode/ 的配置不会覆盖
```

### 8.2 项目配置加载范围改进

| 版本 | 行为 |
|------|------|
| v1.14.32 | 项目配置从当前目录加载，但在某些情况下子目录配置加载不完整 |
| v1.15.13 | 配置从**打开位置**（当前工作目录）向上完整加载到 Git 根目录 |

**v1.15.13 改进说明**：确保 monorepo 中的每个子包都能正确继承根配置并应用自己的覆盖。

### 8.3 迁移建议

| 如果你在使用... | 建议操作 |
|----------------|---------|
| v1.14.32 | 升级到 v1.15.13 以获得正确的配置优先级行为 |
| v1.15.13 | 可以放心使用 `OPENCODE_CONFIG_CONTENT` 和分层项目配置 |

---

## 9. 实际场景配置模板

### 9.1 个人开发者全局配置

```jsonc
// ~/.config/opencode/opencode.jsonc
{
  "$schema": "https://opencode.ai/config.json",

  // 主力模型：Claude 3.5 Sonnet（代码能力强）
  "model": "claude-3.5-sonnet",

  // 轻量任务：GPT-4o Mini（响应快、成本低）
  "small_model": "gpt-4o-mini",

  // 个人 API Keys（通过环境变量注入）
  "provider": {
    "anthropic": {
      "api_key": "{env:ANTHROPIC_API_KEY}"
    },
    "openai": {
      "api_key": "{env:OPENAI_API_KEY}"
    }
  },

  // 个人编码风格指令
  "instructions": [
    "~/.config/opencode/instructions/personal-style.md"
  ],

  // 默认启用 Git 插件
  "plugin": ["git"],

  // 允许读取和编辑，禁止执行（安全第一）
  "permission": {
    "allow": ["read", "edit", "browser"],
    "deny": ["execute"]
  },

  // 启用自动更新
  "autoupdate": true
}
```

### 9.2 团队项目配置

```jsonc
// opencode.jsonc - 团队共享配置（应加入版本控制）
{
  "$schema": "https://opencode.ai/config.json",

  // 团队统一使用 Claude 3.5 Sonnet
  "model": "claude-3.5-sonnet",

  // 项目编码规范
  "instructions": [
    "./docs/CONTRIBUTING.md",
    "./docs/CODING_STANDARDS.md",
    "./docs/ARCHITECTURE.md"
  ],

  // 项目专用 MCP 服务器
  "mcp": {
    "servers": [
      {
        "name": "project-context",
        "transport": "stdio",
        "command": "node",
        "args": ["./scripts/mcp-context-server.js"]
      }
    ]
  },

  // 团队统一插件
  "plugin": ["git", "github", "eslint"],

  // 安全策略：严格限制
  "permission": {
    "allow": ["read", "edit"],
    "deny": ["execute", "network"]
  }
}
```

### 9.3 前端项目配置

```jsonc
// packages/frontend/opencode.jsonc
{
  // 前端开发偏好：轻量模型处理简单任务
  "small_model": "gpt-4o-mini",

  // 前端编码规范
  "instructions": [
    "./frontend-guidelines.md",
    "./component-conventions.md"
  ],

  // 前端工具链
  "plugin": ["eslint", "prettier", "vite"],

  // 前端权限：允许浏览器操作（查看文档）
  "permission": {
    "allow": ["read", "edit", "browser"],
    "deny": ["execute"]
  }
}
```

### 9.4 后端项目配置

```jsonc
// packages/backend/opencode.jsonc
{
  // 后端使用更强的模型处理复杂逻辑
  "model": "claude-3.5-sonnet",

  // 后端编码规范
  "instructions": [
    "./backend-guidelines.md",
    "./api-design-principles.md",
    "./database-conventions.md"
  ],

  // 后端工具链
  "plugin": ["docker", "postgres", "jest"],

  // 后端 MCP：数据库访问
  "mcp": {
    "servers": [
      {
        "name": "dev-database",
        "transport": "stdio",
        "command": "npx",
        "args": [
          "-y",
          "@modelcontextprotocol/server-postgres",
          "{env:DEV_DATABASE_URL}"
        ]
      }
    ]
  }
}
```

### 9.5 CI/CD 流水线配置

```bash
#!/bin/bash
# ci-opencode-review.sh - 在 CI 中运行 OpenCode 代码审查

# 设置 CI 专用配置
export OPENCODE_DISABLE_GLOBAL_CONFIG=1
export OPENCODE_DISABLE_PROJECT_CONFIG=1
export OPENCODE_CONFIG_CONTENT='{
  "model": "gpt-4o-mini",
  "permission": {
    "allow": ["read"],
    "deny": ["edit", "execute", "network"]
  },
  "instructions": ["./ci-review-prompt.md"]
}'

# 运行代码审查
opencode review --diff "$(git diff HEAD~1)"
```

### 9.6 安全隔离配置（审查不受信任代码）

```bash
#!/bin/bash
# review-untrusted.sh - 审查外部 PR 或不受信任代码

# 完全隔离配置
export OPENCODE_DISABLE_PROJECT_CONFIG=1
export OPENCODE_DISABLE_GLOBAL_CONFIG=1
export OPENCODE_NO_PARENT_CONFIG=1

# 只读模式，禁止一切写操作和执行
export OPENCODE_CONFIG_CONTENT='{
  "model": "gpt-4o-mini",
  "permission": {
    "allow": ["read"],
    "deny": ["edit", "execute", "browser", "network"]
  }
}'

opencode review --pr "$1"
```

### 9.7 企业 MDM 强制配置

```xml
<!-- com.opencodeai.config.plist - macOS MDM 配置模板 -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <!-- 强制使用企业内部模型 -->
    <key>model</key>
    <string>enterprise-llm-v1</string>

    <!-- 禁用公共云提供商 -->
    <key>disabled_providers</key>
    <array>
        <string>openai</string>
        <string>anthropic</string>
    </array>

    <!-- 强制安全策略 -->
    <key>permission</key>
    <dict>
        <key>allow</key>
        <array>
            <string>read</string>
            <string>edit</string>
        </array>
        <key>deny</key>
        <array>
            <string>execute</string>
            <string>network</string>
        </array>
    </dict>

    <!-- 强制企业 MCP 服务器 -->
    <key>mcp</key>
    <dict>
        <key>servers</key>
        <array>
            <dict>
                <key>name</key>
                <string>enterprise-docs</string>
                <key>transport</key>
                <string>stdio</string>
                <key>command</key>
                <string>python3</string>
                <key>args</key>
                <array>
                    <string>/usr/local/lib/enterprise/mcp-server.py</string>
                </array>
            </dict>
        </array>
    </dict>
</dict>
</plist>
```

---

## 10. 配置项参考

### 10.1 顶层配置项

| 配置项 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| `model` | string | 默认使用的 AI 模型 | `"claude-3.5-sonnet"` |
| `small_model` | string | 轻量任务使用的模型 | `"gpt-4o-mini"` |
| `provider` | object | 模型提供商配置（含 API Key、Base URL） | 见下方示例 |
| `disabled_providers` | string[] | 禁用的提供商列表 | `["openai", "google"]` |
| `enabled_providers` | string[] | 启用的提供商列表（与 disabled 互斥） | `["anthropic"]` |
| `permission` | object | 权限配置（allow/deny） | 见下方示例 |
| `agent` | object | Agent 行为配置 | 见下方示例 |
| `instructions` | string[] | 指令文件路径列表 | `["./prompt.md"]` |
| `mcp` | object | MCP 服务器配置 | 见下方示例 |
| `plugin` | string[] | 启用的插件列表 | `["git", "github"]` |
| `autoupdate` | boolean | 是否自动检查更新 | `true` |

### 10.2 提供商配置示例

```json
{
  "provider": {
    "anthropic": {
      "api_key": "{env:ANTHROPIC_API_KEY}",
      "base_url": "https://api.anthropic.com",
      "default_model": "claude-3.5-sonnet"
    },
    "openai": {
      "api_key": "{env:OPENAI_API_KEY}",
      "base_url": "https://api.openai.com/v1",
      "organization": "org-xxx"
    },
    "ollama": {
      "base_url": "http://localhost:11434"
    }
  }
}
```

### 10.3 权限配置示例

```json
{
  "permission": {
    "allow": ["read", "edit", "browser"],
    "deny": ["execute", "network"],
    "timeout": 60,
    "max_tokens": 8192
  }
}
```

**权限值说明**：

| 权限值 | 说明 |
|--------|------|
| `read` | 读取文件和目录 |
| `edit` | 修改文件内容 |
| `execute` | 执行系统命令 |
| `browser` | 使用浏览器工具 |
| `network` | 发起网络请求 |

### 10.4 MCP 服务器配置示例

```json
{
  "mcp": {
    "servers": [
      {
        "name": "filesystem",
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "."]
      },
      {
        "name": "postgres",
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-postgres", "{env:DATABASE_URL}"]
      },
      {
        "name": "remote-server",
        "transport": "sse",
        "url": "https://mcp.example.com/events"
      }
    ]
  }
}
```

### 10.5 Agent 配置示例

```json
{
  "agent": {
    "default": {
      "system_prompt": "你是一位经验丰富的软件工程师。",
      "temperature": 0.7,
      "max_tokens": 4096
    },
    "reviewer": {
      "system_prompt": "你是一位严格的代码审查员，关注代码质量和安全性。",
      "temperature": 0.3
    }
  }
}
```

---

## 11. 配置调试与排错

### 11.1 查看当前生效配置

OpenCode 不提供直接的 `config dump` 命令，但你可以通过以下方式推断当前配置：

```bash
# 方法 1：使用 OPENCODE_CONFIG_CONTENT 测试优先级
echo '{"model":"test-model"}' > /tmp/test-config.json
OPENCODE_CONFIG=/tmp/test-config.json opencode --version
# 观察使用的模型是否变化

# 方法 2：逐步排除法
OPENCODE_DISABLE_PROJECT_CONFIG=1 opencode    # 禁用项目配置，观察行为变化
OPENCODE_DISABLE_GLOBAL_CONFIG=1 opencode      # 禁用全局配置，观察行为变化
```

### 11.2 常见问题排查

#### 问题：项目配置不生效

**排查步骤**：

1. 确认 `opencode.json` 文件名拼写正确
2. 检查文件是否在 Git 根目录或子目录中
3. 验证 JSON 格式（可使用 `cat opencode.json | python3 -m json.tool`）
4. 检查是否有 `OPENCODE_DISABLE_PROJECT_CONFIG=1`
5. 检查父目录是否有配置覆盖了当前配置

#### 问题：环境变量配置未生效（v1.14.32）

**原因**：v1.14.32 中 `OPENCODE_CONFIG_CONTENT` 的优先级存在 bug。

**解决方案**：升级到 v1.15.13，或使用 `OPENCODE_CONFIG` 指向文件。

#### 问题：数组配置项被完全替换而非合并

**原因**：某些旧版本可能不完全支持数组拼接合并。

**解决方案**：确保使用 v1.15.13+，或在高层配置中重复定义低层需要的数组元素。

#### 问题：变量替换后配置解析失败

**排查步骤**：

```bash
# 检查环境变量是否设置
echo $ANTHROPIC_API_KEY

# 检查文件是否存在且可读
cat {file:path}  # 将 {file:path} 替换为实际路径

# 检查替换后的 JSON 是否有效
# 临时将变量值硬编码到配置中测试
```

---

## 12. 最佳实践

### 12.1 配置分层原则

```
推荐的分层策略：

全局配置 (~/.config/opencode/opencode.jsonc)
├── 个人 API Keys（通过 {env:...} 引用）
├── 个人偏好的默认模型
├── 个人编码风格指令
└── 个人常用插件

项目配置 (./opencode.jsonc)
├── 团队统一的模型选择
├── 项目编码规范指令
├── 项目专用 MCP 服务器
├── 项目工具链插件
└── 安全权限设置

.opencode/ 目录
├── 自定义 Agent 定义
├── 自定义命令
└── 技能定义
```

### 12.2 安全建议

1. **不要在配置文件中硬编码 API Key**：始终使用 `{env:...}` 引用
2. **将 `opencode.jsonc` 加入 `.gitignore`**（如果包含敏感信息），或使用环境变量
3. **审查项目配置后再加载**：在不受信任的项目中使用 `OPENCODE_DISABLE_PROJECT_CONFIG=1`
4. **使用最小权限原则**：默认禁用 `execute` 和 `network`，按需开启

### 12.3 团队协作建议

1. **根配置纳入版本控制**：项目根目录的 `opencode.json` 应加入 Git
2. **个人覆盖使用全局配置**：避免在项目中提交个人偏好
3. **编写清晰的配置注释**：使用 `opencode.jsonc` 格式添加注释说明
4. **文档化配置意图**：在 `docs/opencode-config.md` 中说明项目配置的设计决策

### 12.4 Monorepo 配置模式

```
推荐模式：继承 + 覆盖

monorepo/opencode.json          # 通用基础配置（所有包共享）
packages/
  ├── shared/
  │   └── opencode.json         # 共享库特有配置
  ├── api/
  │   └── opencode.json         # API 特有配置
  └── web/
      └── opencode.json         # Web 特有配置

每个子包的配置只包含与该包相关的覆盖项，
避免重复定义基础配置。
```

---

## 13. 总结

OpenCode 的配置系统通过 9 层优先级体系和智能合并策略，提供了从个人到团队、从简单到复杂的全场景覆盖能力。

**核心要点回顾**：

1. **9 层优先级**：从内置默认值到 macOS MDM，高优先级覆盖低优先级
2. **合并而非替换**：非冲突键全部保留，对象深度合并，数组拼接去重
3. **项目配置向上查找**：从当前目录到 Git 根目录，加载路径上所有配置
4. **环境变量灵活控制**：支持自定义路径、内联配置和配置禁用
5. **变量替换**：支持 `{env:...}` 和 `{file:...}` 动态注入
6. **版本差异**：v1.15.13 修复了 `OPENCODE_CONFIG_CONTENT` 优先级 bug

**建议的起步配置**：

1. 创建 `~/.config/opencode/opencode.jsonc` 存放个人全局设置
2. 在项目根目录创建 `opencode.jsonc` 存放团队共享配置
3. 使用 `{env:...}` 引用 API Keys，避免硬编码敏感信息
4. 根据项目特点启用合适的 MCP 服务器和插件
5. 设置合理的权限策略，遵循最小权限原则

通过合理规划配置分层，你可以在保持个人偏好的同时确保团队协作的一致性和安全性。
