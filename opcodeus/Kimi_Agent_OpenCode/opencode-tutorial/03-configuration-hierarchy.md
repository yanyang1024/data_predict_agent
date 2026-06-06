# 3. OpenCode 配置层级体系：全局 / 用户 / 项目

---

## 3.1 三级配置的物理位置与优先级

OpenCode 采用**三级配置覆盖**机制，优先级从高到低：

```text
项目配置（Project） > 用户配置（User） > 全局配置（Global）
```

| 层级 | 物理路径 | 作用范围 | 典型用途 |
|---|---|---|---|
| **全局配置** | `~/.config/opencode/opencode.json` | 本机所有用户、所有项目 | 默认模型、全局权限基线、通用工具路径 |
| **用户配置** | `~/.opencode/config.json` | 当前用户、所有项目 | 个人 API Key、个人偏好的模型、用户级 skill |
| **项目配置** | `<project-root>/.opencode/config.json` | 当前项目 | 项目特定规则、专用模型、项目级权限、AGENTS.md |

> **覆盖规则**：低优先级的配置项被高优先级的同名配置项覆盖。不是整个文件替换，而是**逐 key 合并**。

### 配置加载顺序（实际运行时）

```text
1. 读取 ~/.config/opencode/opencode.json（全局默认）
2. 读取 ~/.opencode/config.json（用户覆盖）
3. 读取 <project>/.opencode/config.json（项目覆盖）
4. 合并三层配置，项目 > 用户 > 全局
5. 环境变量最后覆盖（如 OPENCODE_API_KEY）
```

---

## 3.2 全局配置（Global Config）

### 位置

```bash
~/.config/opencode/opencode.json          # Linux/macOS
$HOME/AppData/Roaming/opencode/config.json # Windows
```

### 典型内容

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  // 默认 LLM 提供商和模型
  "provider": "anthropic",
  "model": "claude-sonnet-4-20250514",
  
  // 全局权限基线（最宽松不要超过这个）
  "permission": {
    "*": "ask",
    "read": { "*": "allow" },
    "grep": "allow",
    "glob": "allow"
  },
  
  // 全局自定义工具目录
  "toolsDir": "~/.config/opencode/tools",
  
  // 全局 Skill 目录
  "skillsDir": "~/.config/opencode/skills"
}
```

### 全局配置中如何选择模型和填写 API Key

全局配置**适合设置默认模型**，但**不建议在全局配置中硬编码 API Key**（因为可能多用户共享机器）。

#### 方法一：全局配置中直接指定 provider 和 model（不推荐放 key）

```jsonc
{
  // 只指定用哪个模型，key 从环境变量读取
  "provider": "anthropic",
  "model": "claude-sonnet-4-20250514"
  // API Key 通过环境变量 ANTHROPIC_API_KEY 提供
}
```

#### 方法二：OpenCode 支持的 Provider 列表及对应环境变量

| Provider | 配置名 | API Key 环境变量 | 备注 |
|---|---|---|---|
| Anthropic | `anthropic` | `ANTHROPIC_API_KEY` | Claude 系列模型 |
| OpenAI | `openai` | `OPENAI_API_KEY` | GPT-4o, o3 等 |
| Azure OpenAI | `azure-openai` | `AZURE_OPENAI_API_KEY` | 需额外配置 endpoint |
| Google Gemini | `google` | `GOOGLE_API_KEY` | Gemini 系列 |
| Ollama | `ollama` | 无需 key（本地） | 本地部署模型 |
| OpenRouter | `openrouter` | `OPENROUTER_API_KEY` | 聚合多模型路由 |

#### 方法三：全局配置中设置 provider 配置（含 API Key）

> ⚠️ 警告：在配置文件中写 API Key 会以明文存储，请确保文件权限为 `600`。

```jsonc
{
  "providers": {
    "anthropic": {
      "apiKey": "sk-ant-...",           // 直接从配置文件读取
      "model": "claude-sonnet-4-20250514"
    },
    "openai": {
      "apiKey": "sk-...",
      "model": "gpt-4o"
    },
    "ollama": {
      "baseUrl": "http://localhost:11434",
      "model": "qwen2.5-coder:14b"
    }
  }
}
```

环境变量也可以覆盖 provider 配置：

```bash
# 环境变量优先级高于配置文件
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."
```

---

## 3.3 用户配置（User Config）

### 位置

```bash
~/.opencode/config.json
```

### 典型用途

用户配置是**个人级**的，适合放：
- 个人的 API Key（如果不想每次 export 环境变量）
- 个人偏好的默认模型
- 个人常用的自定义 tool 和 skill

### 用户配置中选择模型和填写 API Key

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  
  // ===== 模型选择 =====
  // 覆盖全局的默认模型
  "provider": "openai",
  "model": "gpt-4o",
  
  // 或者为不同任务指定不同模型（如果支持）
  "agents": {
    "plan": {
      "provider": "anthropic",
      "model": "claude-sonnet-4-20250514"
    },
    "build": {
      "provider": "openai",
      "model": "gpt-4o"
    },
    "explore": {
      "provider": "anthropic",
      "model": "claude-haiku-..."
    }
  },
  
  // ===== API Key 配置 =====
  "providers": {
    "openai": {
      "apiKey": "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    },
    "anthropic": {
      "apiKey": "sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    }
  }
}
```

### 通过命令行快速切换模型（无需改配置）

```bash
# 启动时指定模型
opencode --provider openai --model gpt-4o

# 会话中切换
/set model gpt-4o
/set provider anthropic
```

---

## 3.4 项目配置（Project Config）

### 位置

```bash
<project-root>/.opencode/config.json
```

### 项目配置中选择模型

项目配置**优先级最高**，适合：
- 项目团队统一使用的模型（确保结果一致性）
- 项目特定的权限收紧
- 项目特定的工具注册

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  
  // ===== 项目级模型选择 =====
  // 强制该项目使用特定模型（覆盖用户和全局配置）
  "provider": "anthropic",
  "model": "claude-sonnet-4-20250514",
  
  // 为不同 agent 角色指定不同模型
  "agents": {
    "plan": {
      "provider": "anthropic",
      "model": "claude-opus-4-20250514",
      "permission": {
        "edit": "deny",
        "bash": "ask"
      }
    },
    "build": {
      "provider": "openai",
      "model": "gpt-4o",
      "permission": {
        "edit": "ask",
        "bash": {
          "*": "ask",
          "git status*": "allow",
          "pnpm test*": "ask"
        }
      }
    }
  },
  
  // ===== 项目级 API Key（不推荐，建议用环境变量）=====
  "providers": {
    "anthropic": {
      "apiKey": "${ANTHROPIC_API_KEY}"  // 引用环境变量
    }
  }
}
```

### 多模型切换的实际场景

```bash
# 场景 1：项目 A 用 Claude，项目 B 用 GPT-4o
# 在项目 A 的 .opencode/config.json 中
{ "provider": "anthropic", "model": "claude-sonnet-4-20250514" }

# 在项目 B 的 .opencode/config.json 中
{ "provider": "openai", "model": "gpt-4o" }

# 场景 2：Plan 用强模型（Opus），Build 用快模型（Sonnet/GPT-4o）
# 在项目配置中
{
  "agents": {
    "plan": { "provider": "anthropic", "model": "claude-opus-4-20250514" },
    "build": { "provider": "openai", "model": "gpt-4o" }
  }
}

# 场景 3：本地开发用 Ollama（免费），CI/CD 用云端 API
# 本地 ~/.opencode/config.json
{ "provider": "ollama", "model": "qwen2.5-coder:14b" }

# CI 环境变量
export OPENCODE_PROVIDER=anthropic
export OPENCODE_MODEL=claude-sonnet-4-20250514
export ANTHROPIC_API_KEY=sk-ant-...
```

---

## 3.5 配置合并的实际行为

### 示例：三层配置如何合并

**全局配置** `~/.config/opencode/opencode.json`：

```jsonc
{
  "provider": "anthropic",
  "model": "claude-haiku-...",
  "permission": {
    "*": "ask",
    "read": "allow",
    "grep": "allow"
  }
}
```

**用户配置** `~/.opencode/config.json`：

```jsonc
{
  "model": "claude-sonnet-4-20250514",
  "providers": {
    "anthropic": {
      "apiKey": "sk-ant-用户自己的key"
    }
  }
}
```

**项目配置** `<project>/.opencode/config.json`：

```jsonc
{
  "model": "gpt-4o",
  "provider": "openai",
  "permission": {
    "edit": "deny"
  }
}
```

**最终生效的配置**（逐 key 合并）：

```jsonc
{
  "provider": "openai",           // 项目覆盖
  "model": "gpt-4o",              // 项目覆盖
  "providers": {
    "anthropic": {
      "apiKey": "sk-ant-用户自己的key"  // 用户配置保留
    }
  },
  "permission": {
    "*": "ask",                   // 全局保留
    "read": "allow",              // 全局保留
    "grep": "allow",              // 全局保留
    "edit": "deny"                // 项目追加
  }
}
```

### 配置检查命令

```bash
# 查看当前生效的完整配置（合并后）
opencode config get

# 查看特定配置项
opencode config get provider
opencode config get agents.build.model

# 设置配置项（默认写入用户配置）
opencode config set provider anthropic
opencode config set model claude-sonnet-4-20250514

# 查看配置来源
opencode config --verbose
```

---

## 3.6 团队配置管理最佳实践

### 模式一：项目仓库中包含推荐配置（最推荐）

```bash
# 项目仓库中
.opencode/
├── config.json          # 项目配置（模型、权限、工具）
├── AGENTS.md            # 项目规则
├── tools/               # 项目自定义工具
│   ├── internal-api.js
│   └── deploy-check.sh
└── skills/              # 项目自定义 skill
    └── refactor/
        ├── SKILL.md
        └── scripts/
```

`config.json` 中**不硬编码 API Key**，而是：

```jsonc
{
  "provider": "anthropic",
  "model": "claude-sonnet-4-20250514",
  "providers": {
    "anthropic": {
      "apiKey": "${ANTHROPIC_API_KEY}"  // 运行时从环境变量注入
    }
  }
}
```

团队成员各自在 `~/.opencode/config.json` 或环境变量中配置自己的 Key：

```bash
# ~/.bashrc 或 ~/.zshrc
export ANTHROPIC_API_KEY="sk-ant-..."
```

### 模式二：CI/CD 专用配置

```bash
# CI 环境变量
export OPENCODE_PROVIDER=openai
export OPENCODE_MODEL=gpt-4o
export OPENAI_API_KEY="${{ secrets.OPENAI_API_KEY }}"

# CI 中运行
opencode --non-interactive --config .opencode/ci-config.json
```

### 模式三：多模型冗余（容错）

```jsonc
{
  "providers": {
    "anthropic": {
      "apiKey": "${ANTHROPIC_API_KEY}",
      "model": "claude-sonnet-4-20250514",
      "fallback": true
    },
    "openai": {
      "apiKey": "${OPENAI_API_KEY}",
      "model": "gpt-4o",
      "fallback": true
    }
  },
  // 主 provider 失败时自动切换
  "fallbackProvider": "openai"
}
```

---

## 3.7 配置速查表

| 你想做的事 | 操作位置 | 命令/方式 |
|---|---|---|
| 设置全局默认模型 | `~/.config/opencode/opencode.json` | 编辑 `"provider"` + `"model"` |
| 设置个人默认模型 | `~/.opencode/config.json` | 编辑 `"provider"` + `"model"` |
| 设置项目专用模型 | `.opencode/config.json` | 编辑 `"provider"` + `"model"` |
| 临时切换模型 | 命令行 | `opencode --provider X --model Y` |
| 会话中切换模型 | TUI/CLI | `/set model gpt-4o` |
| 配置 API Key（全局）| 环境变量 | `export ANTHROPIC_API_KEY=...` |
| 配置 API Key（个人）| `~/.opencode/config.json` | `"providers": { "anthropic": { "apiKey": "..." } }` |
| 查看当前生效配置 | 命令行 | `opencode config get` |
| 查看配置来源 | 命令行 | `opencode config --verbose` |
