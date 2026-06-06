# OpenCode 模型配置系统深度研究报告

> 研究时间: 2026-06-07
> 研究范围: OpenCode (https://github.com/anomalyco/opencode) 模型配置系统
> 目标版本: v1.15.13 (最新稳定版) 及历史版本对比

---

## 目录

1. [概述](#1-概述)
2. [支持的模型提供商列表](#2-支持的模型提供商列表)
3. [配置文件系统](#3-配置文件系统)
4. [全局模型配置方法](#4-全局模型配置方法)
5. [API Key 设置方法](#5-api-key-设置方法)
6. [项目级模型配置方法](#6-项目级模型配置方法)
7. [私有部署模型配置详解](#7-私有部署模型配置详解)
8. [多模型切换与模型选择](#8-多模型切换与模型选择)
9. [模型变体 (Variants) 配置](#9-模型变体-variants-配置)
10. [配置示例汇总](#10-配置示例汇总)
11. [常见问题与解决方案](#11-常见问题与解决方案)
12. [版本差异与更新历史](#12-版本差异与更新历史)
13. [关键发现总结](#13-关键发现总结)

---

## 1. 概述

OpenCode 是一个开源的 AI 编程助手，支持通过终端界面 (TUI)、桌面应用或 IDE 扩展使用。它通过 AI SDK 和 Models.dev 支持 **75+ 个 LLM 提供商**，包括 Anthropic、OpenAI、Google、OpenRouter、DeepSeek、Groq、Ollama 等，同时也支持本地私有部署的模型。

**核心特点：**
- 支持 75+ 个 LLM 提供商 (通过 AI SDK 和 Models.dev)
- 支持本地模型运行 (Ollama、vLLM、LM Studio、llama.cpp 等)
- 多层配置系统 (远程/全局/项目级/环境变量)
- 认证信息 (API Key) 与配置分离存储
- 支持自定义 OpenAI 兼容的提供商
- 模型变体系统 (Variants) 支持不同推理预算配置

**来源**: [OpenCode 官方文档](https://opencode.ai/docs/), [GitHub 仓库](https://github.com/anomalyco/opencode)

---

## 2. 支持的模型提供商列表

### 2.1 内置主要提供商

| 提供商 | 认证方式 | 说明 |
|--------|---------|------|
| **Anthropic (Claude)** | API Key 或 Claude Pro/Max 订阅 (OAuth) | 支持浏览器 OAuth 认证 |
| **OpenAI (GPT)** | API Key 或 ChatGPT Plus/Pro 订阅 (OAuth) | 支持浏览器 OAuth 认证 |
| **Google (Gemini)** | API Key (GOOGLE_GENERATIVE_AI_API_KEY) | 原生支持 |
| **OpenRouter** | API Key | 聚合多家模型的统一接口 |
| **OpenCode Zen** | OpenCode 官方 API Key | 官方测试验证过的模型列表 |
| **GitHub Copilot** | GitHub 设备码认证 (OAuth) | 需 Copilot 订阅 |
| **DeepSeek** | API Key | 国产高性能模型 |
| **Groq** | API Key | 高速推理服务 |
| **AWS Bedrock** | AWS 凭证 (Access Key/Profile/OAuth) | 支持多种 AWS 认证方式 |
| **Cloudflare AI Gateway** | Account ID + Gateway ID + API Token | 统一计费网关 |
| **OpenAI Azure** | Azure API Key | Azure 托管的 OpenAI 服务 |
| **Moonshot AI (Kimi)** | API Key | Kimi K2 系列模型 |
| **MiniMax** | API Key | M2.1 等模型 |
| **NVIDIA** | API Key (nvapi-*) | Nemotron 等模型，部分免费 |
| **Together AI** | API Key | 多种开源模型 |
| **xAI (Grok)** | API Key | Grok 系列模型 |
| **Z.AI (智谱)** | API Key | GLM 系列模型 |
| **Ollama Cloud** | API Key | Ollama 云端服务 |
| **Vercel AI Gateway** | API Key | 统一接入多家模型 |
| **Snowflake Cortex** | Programmatic Access Token (PAT) | 企业级数据平台 |
| **GitLab Duo** | GitLab Token (OAuth/PAT) | 支持自托管实例 |

**来源**: [OpenCode Providers 文档](https://opencode.ai/docs/providers/)

### 2.2 本地/私有部署提供商

| 提供商 | 默认端点 | 说明 |
|--------|---------|------|
| **Ollama** | `http://localhost:11434/v1` | 本地模型运行 |
| **LM Studio** | `http://localhost:1234/v1` | 本地模型运行 |
| **vLLM** | `http://localhost:8000/v1` | 高性能推理服务 |
| **llama.cpp** | `http://localhost:8080/v1` | llama-server 工具 |
| **Atomic Chat** | `http://127.0.0.1:1337/v1` | 桌面应用 |

**来源**: [OpenCode Providers 文档](https://opencode.ai/docs/providers/)

---

## 3. 配置文件系统

### 3.1 配置文件位置与优先级

OpenCode 使用 JSON/JSONC (带注释的 JSON) 格式进行配置。配置文件按以下优先级顺序加载（后面的覆盖前面的）：

| 优先级 | 配置源 | 文件路径/方式 | 用途 |
|--------|--------|-------------|------|
| 1 (最低) | 远程配置 | `.well-known/opencode` 端点 | 组织默认值 |
| 2 | 全局配置 | `~/.config/opencode/opencode.json` | 用户级偏好 |
| 3 | 自定义配置 | `OPENCODE_CONFIG` 环境变量指向的文件 | 自定义覆盖 |
| 4 | 项目配置 | 项目根目录的 `opencode.json` | 项目特定设置 |
| 5 | `.opencode` 目录 | `.opencode/opencode.json` | 代理/命令/插件配置 |
| 6 (最高) | 内联配置 | `OPENCODE_CONFIG_CONTENT` 环境变量 | 运行时覆盖 |

**重要特性**: 配置文件是**合并**的，而不是替换的。后面的配置仅在键冲突时覆盖前面的配置，非冲突设置会被保留。

**来源**: [OpenCode Config 文档](https://opencode.ai/docs/config/)

### 3.2 配置文件基本结构

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "anthropic/claude-sonnet-4-5",
  "small_model": "anthropic/claude-haiku-4-5",
  "provider": {},
  "autoupdate": true,
  "tools": {
    "write": true,
    "bash": true
  }
}
```

**来源**: [OpenCode Config 文档 - Schema](https://opencode.ai/docs/config/)

### 3.3 配置文件路径按操作系统

| 操作系统 | 全局配置路径 | 认证存储路径 |
|----------|-------------|-------------|
| Linux/macOS | `~/.config/opencode/opencode.json` | `~/.local/share/opencode/auth.json` |
| Windows | `%APPDATA%\opencode\config.json` 或 `C:\Users\<用户名>\.config\opencode\opencode.json` | `~/.opencode/auth.json` |
| 自定义 (XDG) | `$XDG_CONFIG_HOME/opencode/opencode.json` | `$XDG_DATA_HOME/opencode/auth.json` |

**来源**: [OpenCode Config 文档](https://opencode.ai/docs/config/), [GitHub opencode-multiclaude](https://github.com/nerkza/opencode-multiclaude)

---

## 4. 全局模型配置方法

### 4.1 配置默认模型

在全局配置文件中设置 `model` 和 `small_model`：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "anthropic/claude-sonnet-4-5",
  "small_model": "anthropic/claude-haiku-4-5"
}
```

- `model`: 主模型，用于代码生成等主要任务
- `small_model`: 轻量级模型，用于标题生成等轻量级任务。默认情况下，如果提供商有更便宜的模型，会自动使用，否则回退到主模型

**来源**: [OpenCode Config 文档 - Models](https://opencode.ai/docs/config/)

### 4.2 配置提供商选项

可以为每个提供商设置超时、缓存等选项：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "anthropic": {
      "options": {
        "timeout": 600000,
        "chunkTimeout": 30000,
        "setCacheKey": true
      }
    }
  }
}
```

选项说明：
- `timeout`: 请求超时时间（毫秒），默认 300000。设置为 `false` 禁用超时
- `chunkTimeout`: 流式响应块之间的超时时间（毫秒），如果超时则中止请求
- `setCacheKey`: 确保始终为指定提供商设置缓存键

**来源**: [OpenCode Config 文档 - Models](https://opencode.ai/docs/config/)

### 4.3 禁用/启用提供商

可以禁用自动加载的提供商：

```json
{
  "disabled_providers": ["openai", "gemini"]
}
```

也可以指定允许列表，只启用特定提供商：

```json
{
  "enabled_providers": ["anthropic", "openai"]
}
```

**来源**: [OpenCode Config 文档](https://opencode.ai/docs/config/)

---

## 5. API Key 设置方法

### 5.1 方式一：使用 `/connect` 命令 (推荐)

在 OpenCode TUI 中运行 `/connect` 命令，选择提供商并输入 API Key：

```
/connect
# 选择提供商 -> 输入 API Key -> 完成
```

**认证信息存储位置**: `~/.local/share/opencode/auth.json`

**来源**: [OpenCode Providers 文档](https://opencode.ai/docs/providers/)

### 5.2 方式二：使用 `opencode auth login` 命令

```bash
# 交互式登录
opencode auth login

# 指定提供商登录
opencode auth login --provider <provider_id> --method "API Key"

# 查看已保存的认证
opencode auth list

# 注销某个提供商
opencode auth logout
```

**来源**: [OpenCode CLI 文档](https://opencode.ai/docs/cli/)

### 5.3 方式三：直接编辑 auth.json

`auth.json` 格式：

```json
{
  "anthropic": {
    "type": "api",
    "key": "sk-ant-..."
  },
  "openai": {
    "type": "api",
    "key": "sk-..."
  },
  "github-copilot": {
    "type": "oauth",
    "access": "...",
    "refresh": "...",
    "expires": 1234567890
  }
}
```

认证类型：
- `api`: API Key 认证
- `oauth`: OAuth 认证 (含 access/refresh token)
- `wellknown`: 自定义认证端点

**来源**: [OpenCode CLI Auth 文档](https://mintlify.com/anomalyco/opencode/cli/auth)

### 5.4 方式四：环境变量

在启动 OpenCode 前设置环境变量：

```bash
# Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."

# OpenAI
export OPENAI_API_KEY="sk-..."

# Google
export GOOGLE_GENERATIVE_AI_API_KEY="..."

# OpenRouter
export OPENROUTER_API_KEY="sk-or-..."

# Groq
export GROQ_API_KEY="gsk-..."

# DeepSeek
export DEEPSEEK_API_KEY="sk-..."

# 然后启动 OpenCode
opencode
```

**来源**: [OpenCode Providers 文档](https://opencode.ai/docs/providers/), [ConverSun OpenCode 配置](https://conversun.com/opencode-config/)

### 5.5 方式五：配置文件中引用环境变量

在 `opencode.json` 中使用 `{env:VARIABLE_NAME}` 语法：

```json
{
  "$schema": "https://opencode.ai/config.json",
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

**来源**: [OpenCode Config 文档 - Variables](https://opencode.ai/docs/config/)

### 5.6 方式六：使用 `.env` 文件

在项目根目录创建 `.env` 文件：

```bash
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
PERPLEXITY_API_KEY=pplx-...
```

OpenCode 会自动加载项目目录下的 `.env` 文件中的环境变量。

**来源**: [Amirteymoori OpenCode 多代理设置](https://amirteymoori.com/opencode-multi-agent-setup-specialized-ai-coding-agents/)

### 5.7 方式七：引用文件内容

使用 `{file:path}` 语法从文件中读取 API Key：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "openai": {
      "options": {
        "apiKey": "{file:~/.secrets/openai-key}"
      }
    }
  }
}
```

**来源**: [OpenCode Config 文档 - Variables](https://opencode.ai/docs/config/)

### 5.8 API Key 优先级

当多种认证方式同时存在时，优先级如下：

1. 运行时通过 UI/API 设置的 Key
2. 环境变量 (如 `ANTHROPIC_API_KEY`)
3. `auth.json` 中存储的认证
4. 配置文件中的 `options.apiKey`

**来源**: [byok-ai 研究文档](https://github.com/TheOneWhoBurns/byok-ai/blob/main/RESEARCH.md)

---

## 6. 项目级模型配置方法

### 6.1 项目根目录配置

在项目根目录创建 `opencode.json` 文件，OpenCode 启动时会在当前目录查找，或向上遍历到最近的 Git 目录：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "anthropic/claude-sonnet-4-5",
  "provider": {
    "anthropic": {
      "options": {
        "timeout": 600000
      }
    }
  }
}
```

**项目配置具有最高优先级**，会覆盖全局配置和远程配置。

**来源**: [OpenCode Config 文档 - 项目级](https://opencode.ai/docs/config/)

### 6.2 `.opencode` 目录配置

在项目根目录创建 `.opencode/opencode.json`：

```
project-root/
  .opencode/
    opencode.json    # 项目配置
    agents/          # 自定义代理
    commands/        # 自定义命令
    plugins/         # 插件
```

**来源**: [OpenCode Config 文档](https://opencode.ai/docs/config/)

### 6.3 多代理项目配置示例

可以为不同任务配置不同的代理，每个代理使用不同的模型：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "anthropic/claude-opus-4-5-20251101",
  "agent": {
    "coder": {
      "description": "Primary coding agent using Claude Opus 4.5",
      "mode": "primary",
      "model": "anthropic/claude-opus-4-5-20251101",
      "temperature": 0.2,
      "tools": {
        "write": true,
        "edit": true,
        "bash": true
      }
    },
    "researcher": {
      "description": "Research agent using Perplexity Sonar Pro",
      "mode": "subagent",
      "model": "perplexity/sonar-pro",
      "temperature": 0.8,
      "tools": {
        "write": false,
        "edit": false,
        "bash": false
      }
    },
    "debugger": {
      "description": "Debug and testing agent using GPT-5.1 Codex",
      "mode": "subagent",
      "model": "openai/gpt-5.1-codex",
      "temperature": 0.3,
      "tools": {
        "write": true,
        "edit": true,
        "bash": true
      }
    }
  }
}
```

**来源**: [Amirteymoori OpenCode 多代理设置](https://amirteymoori.com/opencode-multi-agent-setup-specialized-ai-coding-agents/)

### 6.4 使用 `OPENCODE_CONFIG` 环境变量

指定自定义配置文件路径：

```bash
export OPENCODE_CONFIG=/path/to/my/custom-config.json
opencode run "Hello world"
```

此配置在优先级中位于全局配置和项目配置之间。

**来源**: [OpenCode Config 文档 - 自定义路径](https://opencode.ai/docs/config/)

---

## 7. 私有部署模型配置详解

### 7.1 Ollama 配置

#### 7.1.1 基本配置

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "ollama": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Ollama (local)",
      "options": {
        "baseURL": "http://localhost:11434/v1"
      },
      "models": {
        "qwen3-coder:30b": {
          "name": "Qwen3 Coder 30B"
        },
        "gemma4:latest": {
          "name": "Gemma 4"
        }
      }
    }
  }
}
```

#### 7.1.2 使用 Ollama 快捷启动

```bash
# 自动配置并启动
ollama launch opencode

# 只配置不启动
ollama launch opencode --config
```

`ollama launch opencode` 通过 `OPENCODE_CONFIG_CONTENT` 环境变量将配置传递给 OpenCode。

#### 7.1.3 认证占位符

如果 OpenCode 要求认证，可以使用占位符 Key：

```json
{
  "ollama": {
    "type": "api",
    "key": "ollama"
  }
}
```

或使用 `opencode auth login` 选择 "Other"，输入 `ollama` 作为 provider ID，输入任意非空 Key。

**来源**: [Ollama 官方 OpenCode 集成文档](https://docs.ollama.com/integrations/opencode), [OpenCode Providers 文档 - Ollama](https://opencode.ai/docs/providers/)

### 7.2 vLLM 配置

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "vllm": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "vLLM (local)",
      "options": {
        "baseURL": "http://localhost:8000/v1",
        "apiKey": "sk-no-key-required"
      },
      "models": {
        "Qwen/Qwen3-Coder-30B-A3B-Instruct": {
          "name": "Qwen3-Coder 30B A3B Instruct",
          "limit": {
            "context": 131072,
            "output": 8192
          }
        }
      }
    }
  },
  "model": "vllm/Qwen/Qwen3-Coder-30B-A3B-Instruct"
}
```

**来源**: [Hot Aisle + vLLM 配置指南](https://hotaisle.xyz/blog/opencode-vllm-hotaisle)

### 7.3 LM Studio 配置

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "lmstudio": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "LM Studio (local)",
      "options": {
        "baseURL": "http://127.0.0.1:1234/v1"
      },
      "models": {
        "google/gemma-3n-e4b": {
          "name": "Gemma 3n-e4b (local)"
        }
      }
    }
  }
}
```

**来源**: [OpenCode Providers 文档 - LM Studio](https://opencode.ai/docs/providers/)

### 7.4 llama.cpp 配置

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "llama.cpp": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "llama-server (local)",
      "options": {
        "baseURL": "http://127.0.0.1:8080/v1"
      },
      "models": {
        "qwen3-coder:a3b": {
          "name": "Qwen3-Coder: a3b-30b (local)",
          "limit": {
            "context": 128000,
            "output": 65536
          }
        }
      }
    }
  }
}
```

**来源**: [OpenCode Providers 文档 - llama.cpp](https://opencode.ai/docs/providers/)

### 7.5 Atomic Chat 配置

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "atomic-chat": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Atomic Chat (local)",
      "options": {
        "baseURL": "http://127.0.0.1:1337/v1"
      },
      "models": {
        "<your-model-id>": {
          "name": "<your-model-name>"
        }
      }
    }
  }
}
```

**来源**: [OpenCode Providers 文档 - Atomic Chat](https://opencode.ai/docs/providers/)

### 7.6 自定义 OpenAI 兼容提供商

对于任何 OpenAI 兼容 API，都可以使用以下模式配置：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "myprovider": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "My AI Provider Display Name",
      "options": {
        "baseURL": "https://api.myprovider.com/v1",
        "apiKey": "{env:MY_PROVIDER_API_KEY}",
        "headers": {
          "Authorization": "Bearer custom-token"
        }
      },
      "models": {
        "my-model-name": {
          "name": "My Model Display Name",
          "limit": {
            "context": 200000,
            "output": 65536
          }
        }
      }
    }
  }
}
```

配置选项说明：
- `npm`: AI SDK 包名，`@ai-sdk/openai-compatible` 用于 OpenAI 兼容 API (`/v1/chat/completions`)；如果使用 `/v1/responses`，则用 `@ai-sdk/openai`
- `name`: UI 中显示的提供商名称
- `options.baseURL`: API 端点 URL
- `options.apiKey`: API Key（可选，如果不使用 auth 系统）
- `options.headers`: 自定义请求头
- `models`: 可用模型列表
- `limit.context`: 模型最大输入 token 数
- `limit.output`: 模型最大输出 token 数

**来源**: [OpenCode Providers 文档 - Custom Provider](https://opencode.ai/docs/providers/)

### 7.7 远程/LAN 提供商配置

通过 Tailscale/Wireguard 等方式连接远程私有模型：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "tailscale-gpu": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Tailscale - Remote GPU",
      "options": {
        "baseURL": "http://100.100.100.100:1234/v1"
      },
      "models": {
        "llama3": {
          "name": "Llama 3 (Remote)"
        }
      }
    }
  }
}
```

**来源**: [GitHub opencode-local-setup](https://github.com/groxaxo/opencode-local-setup)

---

## 8. 多模型切换与模型选择

### 8.1 模型加载优先级

OpenCode 启动时按以下优先级检查模型：

1. `--model` 或 `-m` 命令行标志（格式: `provider_id/model_id`）
2. 配置文件中的 `model` 字段
3. 上次使用的模型
4. 内部优先级的第一个模型

**来源**: [OpenCode Models 文档](https://opencode.ai/docs/models/)

### 8.2 TUI 中切换模型

在 OpenCode TUI 中使用以下命令：

```
/models          # 查看并选择所有可用模型
/model           # 紧凑的编号选择器
/model <编号>     # 选择指定编号的模型
/model openai/gpt-5.4   # 直接指定模型
/model status    # 查看当前模型详情
```

**来源**: [OpenCode TUI 命令](https://quaily.com/jdevtw-en/p/opencode-tui-common-commands-slash-commands-system-commands-learning-once-opencode-002)

### 8.3 命令行指定模型

```bash
# 使用特定模型启动
opencode --model anthropic/claude-sonnet-4-5

# 使用特定模型运行单次命令
opencode run --model openai/gpt-5.1-codex "Explain closures"

# 使用特定模型创建代理
opencode agent create --model anthropic/claude-haiku-4-5
```

**来源**: [OpenCode CLI 文档](https://opencode.ai/docs/cli/), [OpenCode Models 文档](https://opencode.ai/docs/models/)

### 8.4 列出可用模型

```bash
# 列出所有模型
opencode models

# 列出特定提供商的模型
opencode models anthropic

# 刷新模型缓存
opencode models --refresh

# 详细输出（包含成本和元数据）
opencode models --verbose
```

**来源**: [OpenCode CLI 文档](https://opencode.ai/docs/cli/)

### 8.5 连接新提供商

```bash
# TUI 中运行
/connect
# -> 选择提供商 -> 输入 API Key -> 完成

# 命令行方式
opencode auth login --provider <provider_id> --method "API Key"
```

**来源**: [OpenCode Providers 文档](https://opencode.ai/docs/providers/)

---

## 9. 模型变体 (Variants) 配置

### 9.1 内置变体

OpenCode 为多个提供商提供内置的默认变体：

**Anthropic**:
- `high`: 高思考预算（默认）
- `max`: 最大思考预算

**OpenAI**:
- `none`: 不推理
- `minimal`: 最小推理努力
- `low`: 低推理努力
- `medium`: 中等推理努力
- `high`: 高推理努力
- `xhigh`: 极高推理努力

**Google**:
- `low`: 较低的努力/token 预算
- `high`: 较高的努力/token 预算

### 9.2 自定义变体

可以覆盖现有变体或添加自己的变体：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "openai": {
      "models": {
        "gpt-5": {
          "variants": {
            "thinking": {
              "reasoningEffort": "high",
              "textVerbosity": "low"
            },
            "fast": {
              "disabled": true
            }
          }
        }
      }
    }
  }
}
```

### 9.3 切换变体

使用 `variant_cycle` 快捷键快速在变体之间切换。

**来源**: [OpenCode Models 文档 - Variants](https://opencode.ai/docs/models/)

---

## 10. 配置示例汇总

### 10.1 完整全局配置示例

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "anthropic/claude-sonnet-4-5",
  "small_model": "anthropic/claude-haiku-4-5",
  "provider": {
    "anthropic": {
      "options": {
        "timeout": 600000,
        "setCacheKey": true
      }
    },
    "openai": {
      "options": {
        "timeout": 300000
      }
    },
    "ollama": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Ollama (local)",
      "options": {
        "baseURL": "http://localhost:11434/v1"
      },
      "models": {
        "qwen3-coder:30b": {
          "name": "Qwen3 Coder 30B",
          "tools": true
        }
      }
    }
  },
  "tools": {
    "write": true,
    "edit": true,
    "bash": true
  },
  "autoupdate": true
}
```

### 10.2 完整项目配置示例

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "openai/gpt-5.1-codex",
  "provider": {
    "openai": {
      "options": {
        "apiKey": "{env:OPENAI_API_KEY}",
        "timeout": 600000
      }
    }
  },
  "agent": {
    "build": {
      "mode": "primary",
      "model": "openai/gpt-5.1-codex",
      "temperature": 0.2
    }
  },
  "instructions": ["CONTRIBUTING.md", "docs/guidelines.md"],
  "tools": {
    "write": true,
    "bash": true
  }
}
```

### 10.3 多提供商配置示例

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "haimaker": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Haimaker",
      "options": {
        "baseURL": "https://api.haimaker.ai/v1"
      },
      "models": {
        "anthropic/claude-sonnet-4-6": {
          "name": "Claude Sonnet 4.6"
        },
        "openai/gpt-5.4-mini": {
          "name": "GPT-5.4 Mini"
        },
        "qwen/qwen3-coder": {
          "name": "Qwen3 Coder"
        }
      }
    }
  }
}
```

**来源**: [Haimaker OpenCode Custom Provider Setup](https://haimaker.ai/blog/opencode-custom-provider-setup/)

### 10.4 国内天翼云配置示例

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "xirang": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "xirang",
      "options": {
        "baseURL": "https://wishub-x6.ctyun.cn/coding/v1",
        "apiKey": "YOUR_API_KEY"
      },
      "models": {
        "GLM-5-Pro": {
          "name": "GLM-5-Pro"
        },
        "DeepSeek-V3.2-Pro": {
          "name": "DeepSeek-V3.2-Pro"
        }
      }
    }
  },
  "model": "xirang/GLM-5-Pro",
  "small_model": "xirang/GLM-5-Pro"
}
```

**来源**: [天翼云 OpenCode Token 服务文档](https://www.ctyun.cn/document/11061839/11092972)

### 10.5 ClaudeAPI.com 配置示例

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "claudeapi": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "ClaudeAPI.com",
      "options": {
        "baseURL": "https://gw.claudeapi.com/v1",
        "apiKey": "{env:CLAUDEAPI_API_KEY}"
      },
      "models": {
        "claude-sonnet-4-6": {
          "name": "Claude Sonnet 4.6"
        },
        "claude-opus-4-7": {
          "name": "Claude Opus 4.7"
        }
      }
    }
  }
}
```

**来源**: [ClaudeAPI.com OpenCode 配置指南](https://claudeapi.com/en/blog/tools/opencode-claudeapi-config-guide/)

---

## 11. 常见问题与解决方案

### 11.1 认证相关问题

| 问题 | 解决方案 |
|------|---------|
| `AI_LoadAPIKeyError` / "API key is missing" | 检查环境变量或 `auth.json` 中是否已配置对应提供商的认证信息 |
| `Token exchange failed: 403` (Windows) | 确保使用 `powershell.exe -NoProfile` 运行，检查防火墙设置 |
| `opencode auth login google` 失败 | `opencode auth login [url]` 将参数视为 URL，应不加参数运行 `opencode auth login` |
| 认证信息未保存 | 检查 `~/.local/share/opencode/auth.json` 文件权限，确保为 `600` |
| OAuth 认证成功但 UI 未显示 | 运行 `opencode auth list` 验证认证是否已存储 |

**来源**: [GitHub Issues - anomalyco/opencode](https://github.com/anomalyco/opencode/issues/21101), [GitHub opencode-antigravity-auth](https://github.com/NoeFabris/opencode-antigravity-auth/issues/478)

### 11.2 模型相关问题

| 问题 | 解决方案 |
|------|---------|
| 模型列表为空 | 检查 `models` 配置是否包含有效的模型 ID，运行 `opencode models --refresh` |
| 响应被截断 | 在 `options` 下添加 `"timeout": 600000`（毫秒） |
| 本地模型连接失败 | 确保端点包含 `/v1` 后缀（如 `http://localhost:11434/v1`） |
| `ProviderModelNotFoundError` | 使用 `opencode models` 确认模型 ID 是否正确，使用 `-m` 指定有效模型 |
| Ollama 需要 API Key | 使用 `opencode auth login` 选择 "Other"，provider ID 填 `ollama`，key 填任意非空字符串 |
| 模型不支持图像输入 | 检查模型能力配置，部分模型需要手动开启 vision 支持 |

**来源**: [ClaudeAPI.com OpenCode 配置指南](https://claudeapi.com/en/blog/tools/opencode-claudeapi-config-guide/), [GitHub Issues - anomalyco/opencode](https://github.com/anomalyco/opencode/issues/24823)

### 11.3 配置相关问题

| 问题 | 解决方案 |
|------|---------|
| Windows 找不到配置文件 | 使用 `%USERPROFILE%` 代替 `~`，两者不等价 |
| GUI 配置不生效 | 重启 OpenCode 以加载新的提供商设置 |
| 项目配置未加载 | 确保 `opencode.json` 在项目根目录或 `.opencode/` 目录下 |
| 多配置文件冲突 | 理解优先级顺序：项目 > 全局 > 远程，检查是否有重复设置 |
| 环境变量未生效 | 确保在启动 OpenCode 的同一 shell 会话中设置 |

**来源**: [ClaudeAPI.com OpenCode 配置指南](https://claudeapi.com/en/blog/tools/opencode-claudeapi-config-guide/), [ConverSun OpenCode 配置](https://conversun.com/opencode-config/)

### 11.4 本地模型相关问题

| 问题 | 解决方案 |
|------|---------|
| Ollama 默认上下文太小 (4096) | 创建新模型时增加上下文：`/set parameter num_ctx 16384` 然后 `/save <model-name>-16k` |
| 本地模型推理太慢 | 设置 `OLLAMA_KEEP_ALIVE="-1"` 保持模型常驻内存 |
| 工具调用失败 | 确保模型支持 tool calling，在配置中设置 `"tools": true` |
| vLLM 连接失败 | 确保 baseURL 格式为 `http://<host>:8000/v1`，包括 `/v1` 后缀 |

**来源**: [KDnuggets OpenCode + Ollama + Qwen3](https://www.kdnuggets.com/seeing-whats-possible-with-opencode-ollama-qwen3-coder), [Haimaker Ollama OpenCode 设置](https://haimaker.ai/blog/ollama-opencode-setup/)

---

## 12. 版本差异与更新历史

### 12.1 版本概况

| 版本 | 发布日期 | 主要变化 |
|------|---------|---------|
| v1.16.2 | 2026-06-05 | 最新版本，新增 Snowflake Cortex 提供商，修复 Bedrock 会话挂起问题 |
| v1.16.0 | 2026-05-29 | 新增 HTTP 记录器公测，改进子代理后台运行 |
| v1.15.13 | 2026-05-18 | 修复 Gateway Anthropic Opus 4.7+ 推理问题，配置文件从打开位置向上加载 |
| v1.15.12 | 2026-05-16 | 多项核心修复和改进 |
| v1.15.0 | 2026-04-25 | 新增多提供商支持，改进模型变体系统 |
| v1.14.x | 2026年3月 | 早期稳定版本 |

**注意**: 在 GitHub Releases 中未找到 v1.14.32 的具体版本标签。该版本号可能不存在，或者已被归档。OpenCode 的版本发布较为频繁，建议始终使用最新版本。

**来源**: [GitHub Releases - anomalyco/opencode](https://github.com/anomalyco/opencode/releases)

### 12.2 v1.15.13 版本重要变更

**Core 修复:**
- Gateway Anthropic Opus 4.7+ adaptive reasoning 现在保留 summarized thinking，而不是返回空的 thinking blocks

**改进:**
- Sessions 现在可以通过 API 和 SDK 存储自定义元数据
- Config 现在从打开位置向上加载，目录特定设置和提供商策略应用更可预测

**来源**: [GitHub Release v1.15.13](https://github.com/anomalyco/opencode/releases/tag/v1.15.13)

### 12.3 v1.16.x 版本新增功能

- **新增 Snowflake Cortex 提供商支持** (v1.16.2)
- **新增 HTTP Recorder 公测** (v1.16.0)
- **改进子代理后台运行** (v1.16.0)
- **新增 Diff viewer 导航** (v1.16.2)
- **修复 Bedrock 会话挂起问题** (v1.16.2)

**来源**: [GitHub Releases - anomalyco/opencode](https://github.com/anomalyco/opencode/releases)

---

## 13. 关键发现总结

### 13.1 核心架构

1. **认证与配置分离**: OpenCode 将认证信息 (API Key) 存储在 `~/.local/share/opencode/auth.json`，与配置文件分离。配置文件 (`opencode.json`) 存储提供商定义和模型设置。

2. **多层配置合并**: 配置文件按优先级合并（远程 < 全局 < 自定义 < 项目 < 内联），而非替换。

3. **环境变量支持**: 支持 `{env:VAR}` 和 `{file:path}` 语法在配置中引用环境变量和文件内容。

4. **OpenAI 兼容层**: 所有本地/私有部署模型都通过 `@ai-sdk/openai-compatible` 包接入，统一使用 OpenAI 兼容 API。

### 13.2 配置最佳实践

1. **API Key 管理**: 优先使用 `auth.json` 或环境变量管理 API Key，避免将 Key 硬编码在配置文件中。

2. **项目配置**: 将项目特定的模型配置放在项目根目录的 `opencode.json` 中，可安全提交到 Git。

3. **本地模型上下文**: 使用 Ollama 时务必增加上下文窗口（默认 4096 太小，建议至少 16k-64k）。

4. **多模型切换**: 使用 `/models` 命令在 TUI 中快速切换模型，使用 `-m` 标志在命令行中指定模型。

5. **超时设置**: 对于复杂任务，在提供商选项中设置 `timeout: 600000` (10分钟) 避免响应被截断。

### 13.3 版本建议

- **推荐使用 v1.15.13 或更高版本**，以获得最新的修复和功能。
- v1.14.32 版本在 GitHub Releases 中未找到对应标签，可能已被归档或不存在。
- v1.16.2 是最新版本，新增了 Snowflake Cortex 支持等多项改进。

### 13.4 来源汇总

| 来源 | URL | 用途 |
|------|-----|------|
| OpenCode 官方文档 | https://opencode.ai/docs/ | 主要参考 |
| OpenCode Config 文档 | https://opencode.ai/docs/config/ | 配置系统详情 |
| OpenCode Providers 文档 | https://opencode.ai/docs/providers/ | 提供商配置 |
| OpenCode Models 文档 | https://opencode.ai/docs/models/ | 模型配置 |
| OpenCode CLI 文档 | https://opencode.ai/docs/cli/ | CLI 命令 |
| GitHub 仓库 | https://github.com/anomalyco/opencode | 源码和 Releases |
| Ollama 集成文档 | https://docs.ollama.com/integrations/opencode | Ollama 配置 |
| ConverSun 配置指南 | https://conversun.com/opencode-config/ | 中文配置指南 |
| Haimaker 自定义提供商 | https://haimaker.ai/blog/opencode-custom-provider-setup/ | 自定义提供商 |
| KDnuggets Ollama 教程 | https://www.kdnuggets.com/seeing-whats-possible-with-opencode-ollama-qwen3-coder | Ollama 实践 |

---

*本报告基于 2026-06-07 的公开信息整理，OpenCode 的文档和功能可能会随版本更新而变化。建议参考官方文档获取最新信息。*
