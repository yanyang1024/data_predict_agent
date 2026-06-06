# OpenCode 配置系统深度研究报告

> 研究范围：OpenCode (https://github.com/opencode-ai/opencode) 配置体系
> 重点关注版本：v1.14.32 与 v1.15.13
> 研究日期：2025年
> 本报告中所有关键发现均标注了来源 URL

---

## 目录

1. [配置文件概述](#1-配置文件概述)
2. [全局配置详解](#2-全局配置详解)
3. [项目配置详解](#3-项目配置详解)
4. [配置优先级和继承规则](#4-配置优先级和继承规则)
5. [配置文件搜索路径与定位机制](#5-配置文件搜索路径与定位机制)
6. [环境变量控制](#6-环境变量控制)
7. [版本差异分析（v1.14.32 vs v1.15.13）](#7-版本差异分析v11432-vs-v11513)
8. [配置合并策略深度解析](#8-配置合并策略深度解析)
9. [最佳实践建议](#9-最佳实践建议)
10. [附录：完整配置项参考](#10-附录完整配置项参考)

---

## 1. 配置文件概述

### 1.1 支持的配置文件类型

OpenCode 使用 JSON/JSONC（JSON with Comments）格式的配置文件，官方支持以下配置文件：

| 配置文件 | 用途 | Schema URL |
|---------|------|-----------|
| `opencode.json` / `opencode.jsonc` | 主配置文件（server/runtime 配置） | `https://opencode.ai/config.json` |
| `tui.json` / `tui.jsonc` | TUI 界面专用配置 | `https://opencode.ai/tui.json` |
| `config.json` | 旧版全局配置名（仍兼容） | 同主配置 |
| `kilo.json` / `kilo.jsonc` | Kilo Code fork 的覆盖配置 | 同主配置 |

**关键发现：**
- OpenCode 同时支持 JSON 和 JSONC 格式（JSON with Comments），允许在配置中使用 `//` 单行注释和 `/* */` 多行注释
- JSON Schema 托管在 `https://opencode.ai/config.json`，编辑器可通过 `$schema` 字段实现自动补全和验证
- 旧版 `config.json` 文件名仍被支持（在 `~/.config/opencode/` 目录下会自动检测 `config.json`、`opencode.json`、`opencode.jsonc`）

> **来源：**
> - https://open-code.ai/en/docs/config
> - https://github.com/anomalyco/opencode/issues/12034
> - https://github.com/code-yeongyu/oh-my-opencode/issues/1458

### 1.2 配置文件格式示例

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  // 默认模型
  "model": "anthropic/claude-sonnet-4-5",
  "autoupdate": true,
  "server": {
    "port": 4096
  }
}
```

### 1.3 变量替换机制

配置文件中支持两种变量替换语法：

**环境变量替换：**
```json
{
  "model": "{env:OPENCODE_MODEL}",
  "provider": {
    "anthropic": {
      "options": {
        "apiKey": "{env:ANTHROPIC_API_KEY}"
      }
    }
  }
}
```

**文件内容替换：**
```json
{
  "instructions": ["./custom-instructions.md"],
  "provider": {
    "openai": {
      "options": {
        "apiKey": "{file:~/.secrets/openai-key}"
      }
    }
  }
}
```

> **来源：** https://open-code.ai/en/docs/config

---

## 2. 全局配置详解

### 2.1 文件位置

全局配置文件位于用户主目录的 XDG 配置目录中：

| 平台 | 全局配置路径 |
|------|-------------|
| Linux/macOS | `~/.config/opencode/opencode.json` |
| Windows | `%APPDATA%\opencode\opencode.json` 或 `%USERPROFILE%\.config\opencode\opencode.json` |

TUI 专用全局配置：
- `~/.config/opencode/tui.json`

### 2.2 全局配置搜索的文件名顺序

在 `~/.config/opencode/` 目录下，OpenCode 会按以下顺序搜索并合并（后面的覆盖前面的）：

1. `config.json`（旧版兼容名）
2. `kilo.json` / `kilo.jsonc`（Kilo Code fork 配置）
3. `opencode.json` / `opencode.jsonc`

**注意：** 实际加载顺序是代码控制的。根据 GitHub issue #7621 的分析，在 OpenCode 原始代码中，`opencode.json` 是最后加载的，因此优先级最高。Kilo Code 修复了这个问题，让 `kilo.json` 优先于 `opencode.json`。

> **来源：**
> - https://open-code.ai/en/docs/config
> - https://github.com/Kilo-Org/kilocode/issues/7621

### 2.3 全局配置用途

全局配置用于用户级别的服务器/运行时偏好设置，包括：

- **Provider 配置**：API keys、baseURL、timeout 等
- **模型选择**：默认模型、轻量任务模型（small_model）
- **权限设置**：编辑文件、执行命令等操作的权限
- **MCP 服务器**：全局 MCP 服务器配置
- **插件**：全局插件列表
- **主题/TUI 设置**（推荐放在 `tui.json`）
- **自定义 Agent、命令、技能**：通过 `~/.config/opencode/` 下的子目录

### 2.4 `.opencode` 等效目录（全局级别）

除了配置文件外，全局配置目录 `~/.config/opencode/` 还可以包含以下子目录：

| 子目录 | 用途 |
|--------|------|
| `agents/` | 自定义 Agent 定义（`.md` 文件） |
| `commands/` | 自定义命令（`.md` 文件） |
| `skills/` | 技能定义（`SKILL.md` 文件） |
| `plugins/` | 插件文件（`.js`/`.ts`） |
| `tools/` | 自定义工具 |
| `themes/` | 自定义主题 |
| `modes/` | 自定义模式 |

> **注意：** 子目录使用复数形式（`agents/`、`commands/`、`skills/` 等），但为向后兼容也支持单数形式（`agent/`、`command/`、`skill/` 等）。

> **来源：**
> - https://open-code.ai/en/docs/config
> - https://github.com/anomalyco/opencode/issues/16897

---

## 3. 项目配置详解

### 3.1 文件位置

项目配置文件位于项目根目录：

- `./opencode.json` 或 `./opencode.jsonc`
- 可安全地加入 Git 版本控制

项目级 TUI 配置：
- `./tui.json`（与 `opencode.json` 放在一起）

### 3.2 项目配置搜索机制

当 OpenCode 启动时，会按以下方式搜索项目配置：

1. **首先**在当前工作目录查找 `opencode.json` / `opencode.jsonc`
2. **如果未找到**，向上遍历目录树直到最近的 Git 仓库根目录
3. 这个过程类似于 `findUp` 算法

**注意：** 如果设置了 `OPENCODE_NO_PARENT_CONFIG` 环境变量，则限制只搜索当前目录，不向上遍历父目录。

> **来源：**
> - https://open-code.ai/en/docs/config
> - https://github.com/anomalyco/opencode/issues/10025

### 3.3 项目配置用途

项目配置用于覆盖全局配置，提供项目特定的设置：

- **项目特定的模型选择**
- **项目特定的权限设置**
- **项目特定的 MCP 服务器**
- **项目特定的指令文件**（`instructions`）
- **项目特定的 Agent 配置**
- **禁用/启用特定的 Provider**

### 3.4 项目级 `.opencode/` 目录

项目根目录下可以创建 `.opencode/` 目录，结构与全局配置目录相同：

```
project/
├── opencode.json          # 项目主配置
├── tui.json               # 项目 TUI 配置
├── .opencode/
│   ├── agents/            # 项目级自定义 Agent
│   ├── commands/          # 项目级自定义命令
│   ├── skills/            # 项目级技能
│   ├── plugins/           # 项目级插件
│   ├── tools/             # 项目级自定义工具
│   └── themes/            # 项目级自定义主题
└── ...
```

> **来源：**
> - https://open-code.ai/en/docs/config
> - https://github.com/wesammustafa/OpenCode-Everything-You-Need-to-Know

---

## 4. 配置优先级和继承规则

### 4.1 完整的优先级顺序（从低到高）

配置源按以下顺序加载，**后面的配置覆盖前面的配置**（仅冲突键，非冲突键保留）：

| 优先级 | 配置源 | 说明 |
|--------|--------|------|
| 1 | 内置默认值 | 应用程序硬编码的默认值 |
| 2 | 远程配置 | `.well-known/opencode` 端点（组织默认值） |
| 3 | 全局配置 | `~/.config/opencode/opencode.json` |
| 4 | 自定义路径配置 | `OPENCODE_CONFIG` 环境变量指定的文件 |
| 5 | 项目配置 | `./opencode.json`（向上搜索到 Git 根目录） |
| 6 | `.opencode/` 目录 | agents、commands、plugins、skills 等 |
| 7 | 内联配置 | `OPENCODE_CONFIG_CONTENT` 环境变量 |
| 8 | 托管配置文件 | `/Library/Application Support/opencode/`（macOS）等 |
| 9 | macOS 托管偏好设置 | `.mobileconfig` 通过 MDM 下发（最高优先级，用户不可覆盖） |

### 4.2 关键规则说明

1. **合并而非替换**：配置文件之间是合并关系，非冲突键会被保留。例如，如果全局配置设置 `autoupdate: true`，项目配置设置 `model: "anthropic/claude-sonnet-4-5"`，最终配置将同时包含两者。

2. **对象字段深度合并**：对于嵌套对象（如 `mcp`、`provider`、`permission` 等），采用深度合并策略。高优先级的配置会递归覆盖低优先级配置中的同名字段。

3. **数组字段拼接去重**：对于数组字段（如 `plugin`、`instructions`），采用拼接并去重（Set union）的策略，而不是直接替换。这意味着全局插件和项目插件都会被加载。

4. **托管配置不可覆盖**：通过 macOS MDM 或系统托管目录下发的配置具有最高优先级，用户和项目配置都无法覆盖。

### 4.3 已知问题与限制

**Issue #16897 - 配置层级缺陷：**
当一个项目级配置文件存在时，TypeScript 中编码的默认值可能会覆盖用户配置值。具体表现是：如果某个配置字段在项目配置中不存在但有默认值，而全局配置中已设置了该字段，则会使用默认值而非全局用户设置。

**Issue #11628 - `OPENCODE_CONFIG_CONTENT` 优先级问题：**
在 v1.14.x 中，`OPENCODE_CONFIG_CONTENT` 的加载顺序在 `.opencode/` 目录之前，导致项目级 `.opencode/opencode.jsonc` 覆盖了内联配置。这个问题在后续版本中被修复。

> **来源：**
> - https://open-code.ai/en/docs/config
> - https://github.com/anomalyco/opencode/issues/16897
> - https://github.com/anomalyco/opencode/issues/11628
> - https://github.com/anomalyco/opencode/issues/21264

---

## 5. 配置文件搜索路径与定位机制

### 5.1 项目配置搜索路径

```
项目配置搜索（findUp 算法）：

当前工作目录 (pwd)
  ├── opencode.json / opencode.jsonc  ← 首先查找
  └── .opencode/
       └── opencode.json / opencode.jsonc
       
如果未找到，向上遍历：

父目录/
  ├── opencode.json / opencode.jsonc
  └── .opencode/
       └── opencode.json / opencode.jsonc
       
...继续向上直到 Git 根目录或 $HOME
```

### 5.2 全局配置搜索的文件列表

在 `~/.config/opencode/` 目录中：

```
~/.config/opencode/
  ├── config.json          ← 旧版兼容（最先加载，优先级最低）
  ├── kilo.json            ← Kilo Code 配置
  ├── kilo.jsonc
  ├── opencode.json        ← 标准配置名
  ├── opencode.jsonc       ← 标准配置名（带注释，最后加载，优先级最高）
  ├── tui.json             ← TUI 配置
  ├── tui.jsonc
  ├── AGENTS.md            ← 全局指令文件
  ├── agents/              ← 全局 Agent 目录
  ├── commands/            ← 全局命令目录
  ├── skills/              ← 全局技能目录
  ├── plugins/             ← 全局插件目录
  ├── tools/               ← 全局工具目录
  └── themes/              ← 全局主题目录
```

### 5.3 托管配置路径

| 平台 | 托管配置路径 |
|------|-------------|
| macOS | `/Library/Application Support/opencode/` |
| Linux | `/etc/opencode/` |
| Windows | `%ProgramData%\opencode\` |

> **来源：** https://open-code.ai/en/docs/config

---

## 6. 环境变量控制

### 6.1 配置相关环境变量

| 环境变量 | 类型 | 说明 |
|----------|------|------|
| `OPENCODE_CONFIG` | string | 自定义配置文件路径 |
| `OPENCODE_CONFIG_CONTENT` | string | 内联 JSON 配置内容（最高非托管优先级） |
| `OPENCODE_CONFIG_DIR` | string | 自定义配置目录（搜索 agents、commands、plugins 等） |
| `OPENCODE_TUI_CONFIG` | string | 自定义 TUI 配置文件路径 |
| `OPENCODE_PERMISSION` | string | JSON 格式的权限配置覆盖 |
| `OPENCODE_DISABLE_PROJECT_CONFIG` | boolean | 禁用项目级配置加载 |
| `OPENCODE_DISABLE_GLOBAL_CONFIG` | boolean | 禁用全局配置加载 |
| `OPENCODE_NO_PARENT_CONFIG` | boolean | 禁止从父目录继承配置 |

### 6.2 运行时功能开关

| 环境变量 | 类型 | 说明 |
|----------|------|------|
| `OPENCODE_DISABLE_AUTOUPDATE` | boolean | 禁用自动更新检查 |
| `OPENCODE_DISABLE_PRUNE` | boolean | 禁用旧数据清理 |
| `OPENCODE_DISABLE_AUTOCOMPACT` | boolean | 禁用自动上下文压缩 |
| `OPENCODE_DISABLE_DEFAULT_PLUGINS` | boolean | 禁用默认插件 |
| `OPENCODE_DISABLE_LSP_DOWNLOAD` | boolean | 禁用自动 LSP 服务器下载 |
| `OPENCODE_DISABLE_CLAUDE_CODE` | boolean | 禁用从 `.claude` 读取 prompt 和 skills |
| `OPENCODE_ENABLE_EXPERIMENTAL_MODELS` | boolean | 启用实验性模型 |
| `OPENCODE_EXPERIMENTAL_WATCHER` | boolean | 启用实验性文件监控 |

### 6.3 典型使用场景

**场景 1：CI/CD 中完全隔离配置**
```bash
OPENCODE_DISABLE_GLOBAL_CONFIG=1 \
OPENCODE_DISABLE_PROJECT_CONFIG=1 \
OPENCODE_CONFIG_CONTENT='{"model":"anthropic/claude-sonnet-4-5","permission":{"bash":"allow","edit":"allow"}}' \
opencode run "run tests"
```

**场景 2：使用外部配置文件**
```bash
export OPENCODE_CONFIG=/path/to/my/custom-config.json
opencode run "Hello world"
```

**场景 3：使用自定义配置目录**
```bash
export OPENCODE_CONFIG_DIR=/path/to/my/config-directory
opencode run "Hello world"
```

> **来源：**
> - https://open-code.ai/en/docs/config
> - https://open-code.ai/en/docs/cli
> - https://github.com/anomalyco/opencode/issues/21264
> - https://github.com/anomalyco/opencode/issues/7559

---

## 7. 版本差异分析（v1.14.32 vs v1.15.13）

### 7.1 v1.14.32 变更摘要

根据 changelog，v1.14.32 主要修复包括：

- **核心提示编辑修复**：恢复了 prompt 中的可编辑 shell 模式
- **工作区修复**：修复了 HTTP API 工作区适配器和实验性工作区创建的问题
- **图像处理改进**：改进了图像格式处理
- **Agent 目录访问修复**：修复了 Agent 目录访问问题

> **来源：** https://changelogs.directory/tools/opencode/releases/v1.14.32

### 7.2 v1.15.0 主要变更

v1.15.0 引入了以下重要变化：

- **新增 header timeout 配置**
- **后台 Agent 推送更新**：启用后台 Agent 推送更新
- **Desktop v2 改进**
- **权限配置修复**：修复了权限配置规则顺序问题
- **LSP 改进**：增强 LSP 权限提示
- **Roslyn LSP 支持**：新增对 Razor 和 C# 文件的 Roslyn LSP 支持
- **GPT-5.5 上下文限制**：确保 OpenAI OAuth 下 GPT-5.5 的正确上下文限制

> **来源：** https://changelogs.directory/tools/opencode/releases/v1.15.0

### 7.3 v1.15.13 累积变更（从 v1.15.0 到 v1.15.13）

v1.15.x 系列持续改进：

- **Core improvements**：核心功能持续改进
- **TUI/Desktop refinements**：TUI 和桌面端优化
- **Extension fixes**：扩展修复
- **Bug fixes**：跨 Core、TUI、Desktop 组件的多个 bug 修复

> **来源：** https://changelogs.directory/tools/opencode/releases/v1.15.13

### 7.4 配置系统相关的关键变更

| 变更项 | v1.14.32 | v1.15.13 |
|--------|----------|----------|
| `OPENCODE_CONFIG_CONTENT` 优先级 | 存在被 `.opencode/` 覆盖的问题 | 修复了优先级问题 |
| 权限配置规则顺序 | 部分问题 | 修复了规则顺序 |
| LSP 权限提示 | 基础版本 | 增强版本 |
| Header timeout | 不支持 | 新增配置支持 |
| 后台 Agent 推送 | 不支持 | 支持 |
| 只读配置目录处理 | 可能崩溃 | 修复了依赖安装问题 |

### 7.5 `OPENCODE_CONFIG_CONTENT` 优先级修复

这是一个重要的配置系统修复。在 v1.14.x 中，`OPENCODE_CONFIG_CONTENT` 的文档说明它具有"最高用户优先级"，但实际上 `.opencode/` 目录的配置在它之后处理，导致项目配置覆盖了运行时配置。

修复后（v1.15.x），`OPENCODE_CONFIG_CONTENT` 的正确优先级得到保证：

```
// v1.15.x 修复前（有问题的顺序）
1. OPENCODE_CONFIG_CONTENT 处理
2. .opencode/ 目录处理 ← 覆盖了内联配置

// v1.15.x 修复后（正确顺序）
1. .opencode/ 目录处理
2. OPENCODE_CONFIG_CONTENT 处理 ← 正确覆盖
```

> **来源：**
> - https://github.com/anomalyco/opencode/issues/11628
> - https://github.com/adolago/zee/issues/314

---

## 8. 配置合并策略深度解析

### 8.1 合并函数机制

OpenCode 配置系统使用 `mergeConfigConcatArrays` 函数进行配置合并，其核心逻辑如下：

1. **基础合并**：使用 `mergeDeep` 进行深度合并
2. **数组字段特殊处理**：对于特定数组字段，采用拼接并去重而非覆盖

### 8.2 深度合并（Deep Merge）规则

- **对象字段**：递归合并，高优先级覆盖低优先级的同名字段
- **标量字段**：直接替换，高优先级覆盖低优先级
- **数组字段**：默认行为是替换，但特殊字段（`plugin`、`instructions`）采用拼接去重

### 8.3 特殊数组字段处理

以下数组字段在合并时采用 **拼接并去重**（Set Union）策略：

| 字段 | 合并策略 | 说明 |
|------|----------|------|
| `plugin` | 拼接 + 去重 | 全局插件和项目插件都会被加载 |
| `instructions` | 拼接 + 去重 | 全局指令和项目指令都会被加载 |
| `disabled_providers` | 拼接 + 去重 | 禁用列表合并 |

### 8.4 配置继承的边界案例

**案例 1：MCP 服务器继承**
- 全局配置定义了 MCP 服务器 A、B
- 项目配置定义了 MCP 服务器 C
- 最终配置包含 A、B、C 三个服务器
- 项目可以通过 `"enabled": false` 禁用全局 MCP 服务器

**案例 2：权限配置合并**
- 全局：`"permission": { "edit": "ask", "bash": "ask" }`
- 项目：`"permission": { "bash": "allow" }`
- 最终：`"permission": { "edit": "ask", "bash": "allow" }`

**案例 3：Provider 配置合并**
- 全局：配置了 anthropic provider 的 API key
- 项目：配置了 anthropic provider 的 timeout
- 最终：合并两个配置，API key 和 timeout 都生效

> **来源：**
> - https://github.com/anomalyco/opencode/issues/16897
> - https://github.com/anomalyco/opencode/issues/17605

---

## 9. 最佳实践建议

### 9.1 配置分层策略

**推荐的分层配置方法：**

| 层级 | 配置内容 | 示例 |
|------|----------|------|
| 全局配置 (`~/.config/opencode/opencode.json`) | 个人偏好、API keys、常用模型 | provider、model、theme |
| 项目配置 (`./opencode.json`) | 项目特定设置 | instructions、MCP servers、permissions |
| 环境变量 | 临时覆盖、CI/CD | `OPENCODE_CONFIG_CONTENT` |

### 9.2 最小安全配置模板

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "anthropic/claude-sonnet-4-20250514",
  "permission": {
    "edit": "ask",
    "bash": "ask"
  }
}
```

### 9.3 高级用户配置模板

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "anthropic/claude-sonnet-4-20250514",
  "autoupdate": true,
  "permission": {
    "edit": "allow",
    "bash": {
      "*": "allow",
      "rm -rf *": "deny",
      "sudo *": "ask"
    }
  },
  "instructions": ["CONTRIBUTING.md"]
}
```

### 9.4 团队项目配置模板

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "anthropic/claude-sonnet-4-20250514",
  "share": "auto",
  "instructions": [
    "docs/development.md",
    "docs/api-guidelines.md"
  ]
}
```

### 9.5 实用建议

1. **始终使用 `$schema`**：在配置文件中添加 `"$schema": "https://opencode.ai/config.json"` 以获得编辑器自动补全和验证

2. **使用 JSONC 格式**：利用注释功能记录每个配置项的目的

3. **敏感信息处理**：使用 `{env:VARIABLE_NAME}` 或 `{file:path}` 语法引用敏感信息，不要直接硬编码 API keys

4. **全局配置保持简洁**：只放真正跨项目共享的设置

5. **项目配置关注特定需求**：使用 `instructions` 引用项目特定的规则文件

6. **利用 `.opencode/` 目录**：将 agents、commands、skills 放在项目目录中，便于团队协作

7. **权限最小化原则**：默认设置较严格的权限，在需要时放宽

8. **使用 `OPENCODE_CONFIG_CONTENT` 进行测试**：在 CI/CD 或临时场景中快速覆盖配置

> **来源：**
> - https://open-code.ai/en/docs/config
> - https://eliteai.tools/agent-skills/opencode-config-3
> - https://www.cnblogs.com/2678066103hs/p/19969342

---

## 10. 附录：完整配置项参考

### 10.1 顶层配置项

| 配置项 | 类型 | 说明 |
|--------|------|------|
| `$schema` | string | JSON Schema URL |
| `model` | string | 默认模型（`provider_id/model_id` 格式） |
| `small_model` | string | 轻量任务模型（标题生成等） |
| `provider` | object | Provider 配置（API keys、baseURL 等） |
| `disabled_providers` | string[] | 禁用的 Provider 列表 |
| `enabled_providers` | string[] | 启用的 Provider 白名单 |
| `theme` | string | UI 主题（已废弃，迁移到 `tui.json`） |
| `autoupdate` | boolean/string | 自动更新（`true`/`false`/`"notify"`） |
| `snapshot` | boolean | 启用文件变更快照（默认 `true`） |
| `share` | string | 分享模式（`"manual"`/`"auto"`/`"disabled"`） |
| `username` | string | 用户名 |
| `shell` | string | 交互式终端使用的 shell |
| `server` | object | 服务器配置（`opencode serve`/`opencode web`） |
| `tools` | object | LLM 可用工具管理 |
| `permission` | object | 权限配置 |
| `agent` | object | Agent 配置 |
| `default_agent` | string | 默认 Agent |
| `command` | object | 自定义命令 |
| `keybinds` | object | 键盘快捷键（已废弃，迁移到 `tui.json`） |
| `instructions` | string[] | 指令文件路径列表（支持 glob） |
| `mcp` | object | MCP 服务器配置 |
| `plugin` | string[] | 插件列表 |
| `compaction` | object | 上下文压缩配置 |
| `watcher` | object | 文件监控配置 |
| `attachment` | object | 图像附件限制配置 |
| `experimental` | object | 实验性功能 |

### 10.2 Server 配置子项

| 配置项 | 类型 | 说明 |
|--------|------|------|
| `port` | number | 监听端口 |
| `hostname` | string | 监听主机名 |
| `mdns` | boolean | 启用 mDNS 服务发现 |
| `mdnsDomain` | string | mDNS 自定义域名（默认 `opencode.local`） |
| `cors` | string[] | 允许的 CORS 来源 |

### 10.3 Permission 配置子项

| 配置项 | 类型 | 可选值 |
|--------|------|--------|
| `edit` | string | `"ask"` / `"allow"` / `"deny"` |
| `bash` | string/object | `"ask"` / `"allow"` / `"deny"` 或 `{ "*": "allow", "rm -rf *": "deny" }` |
| `webfetch` | string | `"ask"` / `"allow"` / `"deny"` |
| `skill` | string/object | 技能权限（支持通配符模式） |

### 10.4 MCP 服务器配置

**Local 类型：**
```json
{
  "mcp": {
    "server-name": {
      "type": "local",
      "command": ["npx", "-y", "server"],
      "environment": { "KEY": "value" },
      "enabled": true,
      "timeout": 5000
    }
  }
}
```

**Remote 类型：**
```json
{
  "mcp": {
    "server-name": {
      "type": "remote",
      "url": "https://api.example.com/mcp",
      "headers": { "Authorization": "Bearer token" },
      "oauth": { "clientId": "id", "scope": "read" },
      "enabled": true,
      "timeout": 5000
    }
  }
}
```

### 10.5 Agent 配置子项

| 配置项 | 类型 | 说明 |
|--------|------|------|
| `description` | string | Agent 描述 |
| `model` | string | Agent 使用的模型 |
| `temperature` | number | 温度参数（0.0-2.0） |
| `top_p` | number | Top-p 采样 |
| `prompt` | string | 系统提示词 |
| `tools` | object | Agent 可用工具 |
| `disable` | boolean | 禁用 Agent |
| `mode` | string | `"subagent"` / `"primary"` / `"all"` |
| `color` | string | UI 颜色（hex） |
| `maxSteps` | number | 最大 Agent 迭代次数 |
| `permission` | object | Agent 特定权限 |

> **来源：**
> - https://open-code.ai/en/docs/config
> - https://open-code.ai/en/docs/agents
> - https://open-code.ai/en/docs/mcp-servers
> - https://github.com/pantheon-org/opencode-agent-loader-plugin

---

## 参考来源汇总

| # | URL | 说明 |
|---|-----|------|
| 1 | https://open-code.ai/en/docs/config | OpenCode 官方配置文档（核心参考） |
| 2 | https://open-code.ai/es/docs/config | OpenCode 配置文档（西班牙语版，内容一致） |
| 3 | https://opencode.ai/docs/config/ | OpenCode 配置文档（旧版 URL） |
| 4 | https://opencode.ai/docs/providers/ | Provider 配置文档 |
| 5 | https://opencode.ai/docs/models/ | 模型配置文档 |
| 6 | https://opencode.ai/docs/cli/ | CLI 环境变量文档 |
| 7 | https://opencode.ai/docs/skills/ | Agent Skills 文档 |
| 8 | https://opencode.ai/docs/rules/ | Rules 配置文档 |
| 9 | https://opencode.ai/docs/agents/ | Agents 配置文档 |
| 10 | https://github.com/anomalyco/opencode/issues/16897 | 配置层级缺陷报告 |
| 11 | https://github.com/anomalyco/opencode/issues/11628 | OPENCODE_CONFIG_CONTENT 优先级问题 |
| 12 | https://github.com/anomalyco/opencode/issues/21264 | OPENCODE_DISABLE_GLOBAL_CONFIG 功能请求 |
| 13 | https://github.com/anomalyco/opencode/issues/7559 | OPENCODE_DISABLE_PROJECT_CONFIG 功能请求 |
| 14 | https://github.com/anomalyco/opencode/issues/10025 | OPENCODE_NO_PARENT_CONFIG 功能请求 |
| 15 | https://github.com/anomalyco/opencode/issues/17605 | MCP 配置隔离功能请求 |
| 16 | https://github.com/Kilo-Org/kilocode/issues/7621 | kilo.json 与 opencode.json 优先级问题 |
| 17 | https://github.com/wesammustafa/OpenCode-Everything-You-Need-to-Know | 社区综合指南 |
| 18 | https://github.com/gotar/opencode-config | 社区配置示例 |
| 19 | https://changelogs.directory/tools/opencode/releases/v1.14.32 | v1.14.32 Changelog |
| 20 | https://changelogs.directory/tools/opencode/releases/v1.15.13 | v1.15.13 Changelog |
| 21 | https://www.cnblogs.com/2678066103hs/p/19969342 | OpenCode 完全学习指南（中文社区） |
| 22 | https://blog.csdn.net/oscar999/article/details/160347170 | OpenCode 配置完全指南（中文社区） |
| 23 | https://github.com/anomalyco/opencode/issues/12034 | 配置项文档完整性讨论 |
| 24 | https://github.com/pantheon-org/opencode-agent-loader-plugin | Agent 配置参考 |
| 25 | https://github.com/5kahoisaac/opencode-configs | 社区配置集合 |

---

*本报告基于公开文档、GitHub Issues 和社区资源整理而成。配置系统的具体实现细节可能随版本更新而变化，建议参考官方文档获取最新信息。*
