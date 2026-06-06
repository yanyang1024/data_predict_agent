# 模型选择与 LLM 配置

OpenCode 支持 75+ 家模型提供商，从主流的 Claude、GPT、Gemini 到本地部署的 Ollama、vLLM，几乎覆盖了当前所有可用的 LLM 服务。本章将详细介绍如何在 OpenCode 中选择、配置和切换模型，以及如何安全地管理 API Key。

> **适用版本**: OpenCode v1.14.32, v1.15.13

---

## 目录

- [支持的模型提供商概览](#支持的模型提供商概览)
- [API Key 设置方式](#api-key-设置方式)
  - [方式 1: `/connect` 命令（推荐）](#方式-1-connect-命令推荐)
  - [方式 2: `opencode auth login` 命令](#方式-2-opencode-auth-login-命令)
  - [方式 3: 直接编辑 auth.json](#方式-3-直接编辑-authjson)
  - [方式 4: 环境变量](#方式-4-环境变量)
  - [方式 5: 配置文件中引用环境变量](#方式-5-配置文件中引用环境变量)
  - [方式 6: .env 文件](#方式-6-env-文件)
  - [方式 7: 引用文件内容](#方式-7-引用文件内容)
  - [API Key 优先级规则](#api-key-优先级规则)
- [全局模型配置](#全局模型配置)
- [项目级模型配置](#项目级模型配置)
- [私有部署模型配置](#私有部署模型配置)
  - [Ollama 配置](#ollama-配置)
  - [vLLM 配置](#vllm-配置)
  - [LM Studio 配置](#lm-studio-配置)
  - [llama.cpp 配置](#llamacpp-配置)
  - [统一配置模式解析](#统一配置模式解析)
- [多模型切换](#多模型切换)
  - [TUI 界面切换](#tui-界面切换)
  - [CLI 参数切换](#cli-参数切换)
  - [列出可用模型](#列出可用模型)
- [模型变体 (Variants)](#模型变体-variants)
- [双模型架构：model 与 small_model](#双模型架构model-与-small_model)
- [常见问题排查](#常见问题排查)
  - [AI_LoadAPIKeyError / API key is missing](#ai_loadapikeyerror--api-key-is-missing)
  - [Ollama 上下文长度不足](#ollama-上下文长度不足)
  - [本地模型连接失败](#本地模型连接失败)
  - [ProviderModelNotFoundError](#providermodelfounderror)
- [最佳实践总结](#最佳实践总结)

---

## 支持的模型提供商概览

OpenCode 通过 AI SDK 统一接入各家模型提供商，目前支持超过 75 家提供商，涵盖云端 API、私有化部署和本地运行三种模式。

### 主流云端提供商

| 提供商 | 说明 | 典型模型 |
|--------|------|----------|
| **Anthropic** | Claude 系列模型 | `claude-sonnet-4-5`, `claude-opus-4-5`, `claude-haiku-4-5` |
| **OpenAI** | GPT 系列模型 | `gpt-4.1`, `gpt-4o`, `o3`, `o4-mini` |
| **Google** | Gemini 系列模型 | `gemini-2.5-pro`, `gemini-2.5-flash` |
| **OpenRouter** | 统一路由平台，聚合多家模型 | 支持数百种模型 |
| **DeepSeek** | 国产开源模型 | `deepseek-chat`, `deepseek-reasoner` |
| **Groq** | 高速推理平台 | 支持 Llama、Mixtral 等 |
| **AWS Bedrock** | 亚马逊云托管模型 | Claude、Titan、Command 等 |
| **Moonshot AI** | Kimi 系列模型 | `kimi-k2` |
| **xAI** | Grok 系列模型 | `grok-3-beta` |

### 本地/私有部署提供商

| 提供商 | 默认端点 | 适用场景 |
|--------|----------|----------|
| **Ollama** | `http://localhost:11434/v1` | 本地个人开发 |
| **vLLM** | `http://localhost:8000/v1` | 高并发生产环境 |
| **LM Studio** | `http://localhost:1234/v1` | 本地 GUI 管理 |
| **llama.cpp** | `http://localhost:8080/v1` | 轻量级本地推理 |

### 模型 ID 格式

OpenCode 使用统一的模型 ID 格式：`{provider}/{model-name}`。例如：

- `anthropic/claude-sonnet-4-5` —— Anthropic 的 Claude Sonnet 4.5
- `openai/gpt-4.1` —— OpenAI 的 GPT-4.1
- `google/gemini-2.5-pro` —— Google 的 Gemini 2.5 Pro
- `ollama/qwen3-coder:30b` —— Ollama 本地部署的 Qwen3 Coder 30B

---

## API Key 设置方式

OpenCode 提供了 7 种灵活的 API Key 设置方式，适应不同的安全需求和使用场景。

### 方式 1: `/connect` 命令（推荐）

**TUI（交互式终端界面）中使用 `/connect` 命令**是最推荐的认证方式。Key 会被安全地存储在 `~/.local/share/opencode/auth.json` 中，并自动关联到对应的提供商。

**操作步骤：**

```
1. 启动 OpenCode TUI:  opencode
2. 在命令输入框中键入: /connect
3. 按提示选择提供商（如 Anthropic、OpenAI 等）
4. 粘贴 API Key
5. 系统自动保存并验证
```

**存储位置与格式：**

认证信息存储在 `~/.local/share/opencode/auth.json`，格式如下：

```json
{
  "anthropic": {
    "apiKey": "sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxx"
  },
  "openai": {
    "apiKey": "sk-proj-xxxxxxxxxxxxxxxxxxxxxxxx"
  },
  "google": {
    "apiKey": "AIxxxxxxxxxxxxxxxxxxxxxxxx"
  }
}
```

**优势：**
- 交互式引导，无需手动编辑文件
- Key 被集中管理，便于查看和更新
- 支持为不同提供商分别设置 Key
- 安全性高，文件权限默认仅用户可读

### 方式 2: `opencode auth login` 命令

CLI 提供了专门的认证命令，适合偏好命令行操作的开发者。

```bash
# 交互式登录（会提示选择提供商并输入 Key）
opencode auth login

# 为指定提供商设置 Key
opencode auth login --provider anthropic

# 直接传递 Key（适合脚本自动化）
opencode auth login --provider openai --key "sk-proj-xxxxx"
```

认证信息同样存储在 `~/.local/share/opencode/auth.json` 中，与 `/connect` 命令共用同一存储。

**查看已保存的认证：**

```bash
# 列出所有已认证的提供商
opencode auth list

# 输出示例:
# Provider: anthropic
# Provider: openai
# Provider: google
```

### 方式 3: 直接编辑 auth.json

如果你需要批量配置或自动化部署，可以直接编辑认证文件。

```bash
# 确保目录存在
mkdir -p ~/.local/share/opencode

# 创建或编辑认证文件
vim ~/.local/share/opencode/auth.json
```

文件内容示例（支持多个提供商）：

```json
{
  "anthropic": {
    "apiKey": "sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxx"
  },
  "openai": {
    "apiKey": "sk-proj-xxxxxxxxxxxxxxxxxxxxxxxx"
  },
  "deepseek": {
    "apiKey": "sk-xxxxxxxxxxxxxxxxxxxxxxxx"
  },
  "moonshot": {
    "apiKey": "sk-xxxxxxxxxxxxxxxxxxxxxxxx"
  }
}
```

**注意事项：**
- 确保文件权限设置为 `600`（仅用户可读可写）：`chmod 600 ~/.local/share/opencode/auth.json`
- JSON 格式必须合法，特别是逗号和引号
- 不支持注释，不要添加 `//` 或 `/* */` 注释

### 方式 4: 环境变量

环境变量是最适合 CI/CD 流水线、Docker 容器和临时测试场景的认证方式。OpenCode 会自动读取标准化的环境变量名称。

**各提供商对应的环境变量名：**

| 提供商 | 环境变量名 |
|--------|-----------|
| Anthropic | `ANTHROPIC_API_KEY` |
| OpenAI | `OPENAI_API_KEY` |
| Google (Gemini) | `GOOGLE_GENERATIVE_AI_API_KEY` |
| DeepSeek | `DEEPSEEK_API_KEY` |
| Groq | `GROQ_API_KEY` |
| Moonshot AI | `MOONSHOT_API_KEY` |
| xAI | `XAI_API_KEY` |
| OpenRouter | `OPENROUTER_API_KEY` |

**使用示例：**

```bash
# 临时设置（当前终端会话）
export ANTHROPIC_API_KEY="sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxx"
opencode

# 一次性使用（不保存到环境）
ANTHROPIC_API_KEY="sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxx" opencode

# 写入 shell 配置文件（永久生效）
echo 'export ANTHROPIC_API_KEY="sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxx"' >> ~/.bashrc
source ~/.bashrc
```

**Docker 中使用：**

```bash
docker run -it \
  -e ANTHROPIC_API_KEY="sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxx" \
  -e OPENAI_API_KEY="sk-proj-xxxxxxxxxxxxxxxxxxxxxxxx" \
  -v $(pwd):/workspace \
  opencode/opencode:latest
```

### 方式 5: 配置文件中引用环境变量

OpenCode 配置文件支持 `{env:VAR_NAME}` 语法，可以在配置中引用环境变量。这种方式结合了配置文件的可管理性和环境变量的安全性。

**`~/.config/opencode/opencode.json` 示例：**

```json
{
  "model": "anthropic/claude-sonnet-4-5",
  "provider": {
    "anthropic": {
      "options": {
        "apiKey": "{env:ANTHROPIC_API_KEY}"
      }
    },
    "openai": {
      "options": {
        "apiKey": "{env:OPENAI_API_KEY}"
      }
    }
  }
}
```

**`.env` 文件（与配置文件配合使用）：**

```bash
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxx
```

启动时加载：

```bash
# 使用 dotenv 加载
source .env && opencode

# 或在配置中自动加载（项目目录下的 .env 文件会被自动识别）
opencode
```

### 方式 6: .env 文件

OpenCode 会自动识别项目目录或用户主目录下的 `.env` 文件，无需在配置中显式引用。

**`.env` 文件示例：**

```bash
# Anthropic
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxx

# OpenAI
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxx

# Google
GOOGLE_GENERATIVE_AI_API_KEY=AIxxxxxxxxxxxxxxxxxxxxxxxx

# DeepSeek
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx

# Groq
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxx

# Moonshot
MOONSHOT_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
```

**自动加载规则：**

1. OpenCode 启动时，会自动在当前工作目录查找 `.env` 文件
2. 如果找不到，会继续向上遍历父目录
3. 最后检查用户主目录 `~/.env`
4. 所有找到的环境变量都会被加载

### 方式 7: 引用文件内容

对于需要从机密管理系统（如 HashiCorp Vault、AWS Secrets Manager）读取 Key 的场景，可以使用 `{file:path}` 语法引用文件内容。

**`~/.config/opencode/opencode.json` 示例：**

```json
{
  "model": "anthropic/claude-sonnet-4-5",
  "provider": {
    "anthropic": {
      "options": {
        "apiKey": "{file:/run/secrets/anthropic_api_key}"
      }
    }
  }
}
```

**典型使用场景：**

```bash
# Docker Secrets
echo "sk-ant-api03-xxxxx" | docker secret create anthropic_key -

# 然后在 Docker Compose 中挂载为文件
# /run/secrets/anthropic_api_key

# Kubernetes Secret
kubectl create secret generic anthropic-key \
  --from-literal=api-key=sk-ant-api03-xxxxx
# 挂载到 /etc/secrets/anthropic_api_key

# 临时文件（脚本中使用）
echo "$API_KEY" > /tmp/anthropic_key
opencode
rm /tmp/anthropic_key
```

### API Key 优先级规则

当多种认证方式同时存在时，OpenCode 按以下优先级（从高到低）选择 API Key：

1. **运行时 UI/API 设置的 Key** —— 当前会话中通过 `/connect` 或界面设置的 Key
2. **环境变量** —— 如 `ANTHROPIC_API_KEY`
3. **`auth.json` 中存储的认证** —— `~/.local/share/opencode/auth.json`
4. **配置文件中的 `options.apiKey`** —— `opencode.json` 中显式配置的 Key

**重要提示：** 优先级的存在意味着你可以为不同的使用场景设置不同的 Key。例如，在 `auth.json` 中保存个人开发用的 Key，而在生产部署时通过环境变量覆盖为服务账号的 Key。

---

## 全局模型配置

全局模型配置作用于所有 OpenCode 会话，除非被项目级配置覆盖。配置文件位于用户主目录：`~/.config/opencode/opencode.json`。

### 基本配置结构

```json
{
  "model": "anthropic/claude-sonnet-4-5",
  "small_model": "anthropic/claude-haiku-4-5"
}
```

### 配置说明

| 配置项 | 说明 | 示例值 |
|--------|------|--------|
| `model` | 主模型，用于代码生成、重构等复杂任务 | `anthropic/claude-sonnet-4-5` |
| `small_model` | 轻量模型，用于简单任务如标签生成、总结 | `anthropic/claude-haiku-4-5` |

### 带提供商选项的完整配置

```json
{
  "model": "anthropic/claude-sonnet-4-5",
  "small_model": "anthropic/claude-haiku-4-5",
  "provider": {
    "anthropic": {
      "options": {
        "timeout": 600000,
        "maxRetries": 3
      }
    }
  }
}
```

### 多个提供商的全局配置

```json
{
  "model": "anthropic/claude-sonnet-4-5",
  "small_model": "anthropic/claude-haiku-4-5",
  "provider": {
    "anthropic": {
      "options": {
        "timeout": 600000
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
      }
    }
  }
}
```

### 配置文件位置汇总

| 操作系统 | 全局配置路径 |
|----------|-------------|
| Linux | `~/.config/opencode/opencode.json` |
| macOS | `~/Library/Application Support/opencode/opencode.json` |
| Windows | `%APPDATA%\opencode\opencode.json` |

---

## 项目级模型配置

项目级配置位于项目根目录的 `opencode.json` 文件中，具有**最高优先级**，会覆盖全局配置。这是团队协作和项目标准化推荐的配置方式。

### 基本项目配置

```json
{
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

### 将项目配置加入版本控制

推荐将项目配置提交到 Git 仓库（**不包含 API Key**）：

```bash
# 初始化项目配置
echo '{
  "model": "anthropic/claude-sonnet-4-5",
  "provider": {
    "anthropic": {
      "options": {
        "timeout": 600000
      }
    }
  }
}' > opencode.json

# 添加到 Git
git add opencode.json
git commit -m "chore: add OpenCode project configuration"
```

**注意事项：**
- 不要在 `opencode.json` 中硬编码 API Key
- 使用环境变量或 `auth.json` 管理 Key
- 可以在 `.gitignore` 中忽略包含敏感信息的本地覆盖文件

### 配置优先级（从高到低）

1. **项目级 `opencode.json`** —— 项目根目录下的配置文件
2. **全局 `~/.config/opencode/opencode.json`** —— 用户级别的全局配置
3. **内置默认值** —— OpenCode 的默认模型设置

---

## 私有部署模型配置

OpenCode 通过 `@ai-sdk/openai-compatible` 适配器统一接入所有兼容 OpenAI API 格式的本地/私有部署模型。无论底层是 Ollama、vLLM、LM Studio 还是 llama.cpp，配置模式都是一致的。

### 统一配置模式

所有私有部署提供商都使用以下配置模板：

```json
{
  "provider": {
    "{provider-id}": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "{Display Name}",
      "options": {
        "baseURL": "http://{host}:{port}/v1",
        "apiKey": "{optional-api-key}"
      },
      "models": {
        "{model-id}": {
          "name": "{Display Model Name}"
        }
      }
    }
  }
}
```

**关键字段说明：**

| 字段 | 说明 | 必需 |
|------|------|------|
| `npm` | 固定值为 `@ai-sdk/openai-compatible` | 是 |
| `name` | 提供商的显示名称 | 是 |
| `options.baseURL` | API 端点地址，**必须以 `/v1` 结尾** | 是 |
| `options.apiKey` | API Key（如果本地服务需要认证） | 否 |
| `models` | 可用模型列表 | 是 |

### Ollama 配置

Ollama 是目前最流行的本地模型运行工具，支持大量开源模型。

#### 前提条件

```bash
# 1. 安装 Ollama
# macOS/Linux
curl -fsSL https://ollama.com/install.sh | sh

# 2. 拉取所需模型
ollama pull qwen3-coder:30b
ollama pull llama3.3:70b
ollama pull codellama:70b

# 3. 启动 Ollama 服务（默认端口 11434）
ollama serve
```

#### Ollama 配置文件

```json
{
  "model": "ollama/qwen3-coder:30b",
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
        "llama3.3:70b": {
          "name": "Llama 3.3 70B"
        },
        "codellama:70b": {
          "name": "CodeLlama 70B"
        }
      }
    }
  }
}
```

#### Ollama 配置多个端点

如果你有多个 Ollama 实例（如不同服务器或端口）：

```json
{
  "provider": {
    "ollama-desktop": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Ollama Desktop",
      "options": {
        "baseURL": "http://localhost:11434/v1"
      },
      "models": {
        "qwen3-coder:30b": {
          "name": "Qwen3 Coder 30B"
        }
      }
    },
    "ollama-server": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Ollama Server",
      "options": {
        "baseURL": "http://192.168.1.100:11434/v1"
      },
      "models": {
        "llama3.3:70b": {
          "name": "Llama 3.3 70B"
        }
      }
    }
  }
}
```

#### Ollama 上下文长度配置

**重要：** Ollama 默认上下文长度只有 **4096 tokens**，对于代码相关任务通常不够。需要在模型配置中显式设置：

```json
{
  "provider": {
    "ollama": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Ollama (local)",
      "options": {
        "baseURL": "http://localhost:11434/v1"
      },
      "models": {
        "qwen3-coder:30b": {
          "name": "Qwen3 Coder 30B",
          "options": {
            "num_ctx": 32768
          }
        }
      }
    }
  }
}
```

或者通过 Ollama 的 Modelfile 永久设置：

```dockerfile
# Modelfile
FROM qwen3-coder:30b
PARAMETER num_ctx 32768
PARAMETER num_predict 8192
```

```bash
ollama create qwen3-coder-32k -f Modelfile
```

### vLLM 配置

vLLM 是专为高吞吐量 Serving 设计的推理引擎，适合团队共享或生产环境。

#### 前提条件

```bash
# 1. 安装 vLLM
pip install vllm

# 2. 启动 vLLM 服务
python -m vllm.serve \
  "Qwen/Qwen3-30B-AWQ" \
  --host 0.0.0.0 \
  --port 8000 \
  --tensor-parallel-size 2 \
  --max-model-len 32768
```

#### vLLM 配置文件

```json
{
  "model": "vllm/Qwen3-30B-AWQ",
  "provider": {
    "vllm": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "vLLM (local)",
      "options": {
        "baseURL": "http://localhost:8000/v1",
        "apiKey": "dummy-key"
      },
      "models": {
        "Qwen3-30B-AWQ": {
          "name": "Qwen3 30B AWQ"
        }
      }
    }
  }
}
```

**注意：** vLLM 默认不需要 API Key，但某些版本会验证。如果未设置认证，可以传递任意字符串如 `dummy-key`。

#### vLLM 多 GPU 配置

```json
{
  "provider": {
    "vllm": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "vLLM Cluster",
      "options": {
        "baseURL": "http://vllm-cluster.internal:8000/v1"
      },
      "models": {
        "Llama-3.3-70B-Instruct-AWQ": {
          "name": "Llama 3.3 70B AWQ"
        },
        "Qwen3-30B-AWQ": {
          "name": "Qwen3 30B AWQ"
        }
      }
    }
  }
}
```

### LM Studio 配置

LM Studio 提供了图形化界面来管理和运行本地模型，适合不熟悉命令行的开发者。

#### 前提条件

1. 下载并安装 [LM Studio](https://lmstudio.ai/)
2. 在 LM Studio 中下载所需模型
3. 启动 Local Server（默认端口 1234）

#### LM Studio 配置文件

```json
{
  "model": "lmstudio/llama-3.3-70b",
  "provider": {
    "lmstudio": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "LM Studio (local)",
      "options": {
        "baseURL": "http://localhost:1234/v1"
      },
      "models": {
        "llama-3.3-70b": {
          "name": "Llama 3.3 70B"
        }
      }
    }
  }
}
```

### llama.cpp 配置

llama.cpp 是最轻量级的本地推理方案，适合资源受限的环境。

#### 前提条件

```bash
# 1. 编译 llama.cpp
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp && make -j

# 2. 启动服务器
./server \
  -m models/Qwen3-30B-Q4_K_M.gguf \
  --host 0.0.0.0 \
  --port 8080 \
  -c 32768 \
  -n 8192
```

#### llama.cpp 配置文件

```json
{
  "model": "llamacpp/qwen3-30b-q4",
  "provider": {
    "llamacpp": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "llama.cpp (local)",
      "options": {
        "baseURL": "http://localhost:8080/v1"
      },
      "models": {
        "qwen3-30b-q4": {
          "name": "Qwen3 30B Q4_K_M"
        }
      }
    }
  }
}
```

### 统一配置模式解析

所有私有部署提供商共享相同的配置模式，这带来了几个重要优势：

1. **一致性**：无论底层使用什么推理引擎，配置结构完全相同
2. **可移植性**：切换提供商只需修改 `baseURL` 和模型名
3. **扩展性**：可以轻松添加新的本地推理引擎

**关键要点：**
- `baseURL` **必须以 `/v1` 结尾**，这是 OpenAI API 兼容的端点路径
- `npm` 字段固定为 `@ai-sdk/openai-compatible`
- `models` 中定义的模型 ID 用于 `model` 字段的引用格式 `{provider-id}/{model-id}`
- 不需要为本地模型设置真实的 API Key（除非本地服务配置了认证）

---

## 多模型切换

OpenCode 支持在多个模型之间灵活切换，适应不同的任务需求。

### TUI 界面切换

在 OpenCode 的交互式终端界面中，使用 `/models` 命令打开模型选择器：

```
> /models
```

操作说明：
- 使用上下方向键浏览可用模型
- 按 `Enter` 确认选择
- 按 `Esc` 或 `q` 取消切换
- 支持搜索：直接输入关键词过滤模型列表

界面显示信息：
- 模型名称和 ID
- 所属提供商
- 当前是否被选中（标记为 `●`）

### CLI 参数切换

在命令行启动时通过 `--model` 参数指定模型：

```bash
# 使用特定模型启动
opencode --model anthropic/claude-sonnet-4-5

# 使用本地 Ollama 模型
opencode --model ollama/qwen3-coder:30b

# 在管道中使用特定模型
echo "Explain this code" | opencode --model openai/gpt-4.1
```

**CLI 模型参数的优先级：**

`--model` 参数 > 项目配置 `opencode.json` > 全局配置 `~/.config/opencode/opencode.json`

### 列出可用模型

使用 `opencode models` 命令查看所有已配置的模型：

```bash
# 列出所有可用模型
opencode models

# 输出示例:
# Provider: anthropic
#   claude-sonnet-4-5   Claude Sonnet 4.5
#   claude-opus-4-5     Claude Opus 4.5
#   claude-haiku-4-5    Claude Haiku 4.5
#
# Provider: openai
#   gpt-4.1             GPT-4.1
#   gpt-4o              GPT-4o
#
# Provider: ollama
#   qwen3-coder:30b     Qwen3 Coder 30B
#   llama3.3:70b        Llama 3.3 70B
```

**带详细信息：**

```bash
opencode models --verbose

# 显示模型 ID、名称、上下文长度、提供商选项等详细信息
```

---

## 模型变体 (Variants)

模型变体允许你覆盖模型提供商的默认参数，实现更精细的控制。这在需要调整推理强度、上下文长度或其他模型特定选项时非常有用。

### 支持的变体参数

不同提供商支持的变体参数不同。以下是常见变体：

#### Anthropic 变体

```json
{
  "model": "anthropic/claude-sonnet-4-5",
  "provider": {
    "anthropic": {
      "options": {
        "thinking": {
          "type": "enabled",
          "budget_tokens": 32000
        }
      },
      "variants": {
        "high": {
          "thinking": {
            "type": "enabled",
            "budget_tokens": 64000
          }
        },
        "max": {
          "thinking": {
            "type": "enabled",
            "budget_tokens": 128000
          }
        }
      }
    }
  }
}
```

| 变体名 | 说明 | thinking budget |
|--------|------|-----------------|
| 默认 | 标准推理 | 32000 tokens |
| `high` | 高级推理 | 64000 tokens |
| `max` | 最大推理 | 128000 tokens |

**使用变体：**

```bash
# 使用 high 变体（更多推理 token）
opencode --model "anthropic/claude-sonnet-4-5:high"

# 使用 max 变体（最多推理 token）
opencode --model "anthropic/claude-sonnet-4-5:max"
```

#### OpenAI 变体

```json
{
  "model": "openai/gpt-4.1",
  "provider": {
    "openai": {
      "variants": {
        "none": {
          "reasoning_effort": "none"
        },
        "minimal": {
          "reasoning_effort": "low"
        },
        "low": {
          "reasoning_effort": "low"
        },
        "medium": {
          "reasoning_effort": "medium"
        },
        "high": {
          "reasoning_effort": "high"
        },
        "xhigh": {
          "reasoning_effort": "high"
        }
      }
    }
  }
}
```

| 变体名 | reasoning_effort | 适用场景 |
|--------|------------------|----------|
| `none` | `none` | 不需要推理的简单任务 |
| `minimal` / `low` | `low` | 快速响应，低复杂度 |
| `medium` | `medium` | 平衡质量与速度 |
| `high` / `xhigh` | `high` | 复杂代码分析、架构设计 |

### 自定义变体

你也可以定义自己的变体：

```json
{
  "provider": {
    "anthropic": {
      "variants": {
        "quick": {
          "max_tokens": 4096,
          "thinking": {
            "type": "enabled",
            "budget_tokens": 8000
          }
        },
        "deep": {
          "max_tokens": 8192,
          "thinking": {
            "type": "enabled",
            "budget_tokens": 64000
          }
        }
      }
    }
  }
}
```

使用自定义变体：

```bash
opencode --model "anthropic/claude-sonnet-4-5:quick"
opencode --model "anthropic/claude-sonnet-4-5:deep"
```

### 变体 URL 格式

变体通过冒号后缀附加到模型 ID：

```
{provider}/{model-name}:{variant}
```

示例：
- `anthropic/claude-sonnet-4-5:high` —— 使用 Anthropic high 变体
- `openai/gpt-4.1:high` —— 使用 OpenAI high 变体
- `anthropic/claude-sonnet-4-5:custom` —— 使用自定义变体

---

## 双模型架构：model 与 small_model

OpenCode 内部采用双模型架构，根据任务复杂度自动选择使用主模型还是轻量模型，以优化成本和响应速度。

### 两个角色的分工

| 模型角色 | 配置项 | 用途 |
|----------|--------|------|
| **主模型** | `model` | 代码生成、重构、复杂分析、架构设计 |
| **轻量模型** | `small_model` | 文件标签生成、会话标题生成、简单总结 |

### 默认配置

```json
{
  "model": "anthropic/claude-sonnet-4-5",
  "small_model": "anthropic/claude-haiku-4-5"
}
```

### 自定义轻量模型

你可以将 `small_model` 配置为任何支持的模型，包括本地模型：

```json
{
  "model": "anthropic/claude-sonnet-4-5",
  "small_model": "ollama/qwen3-coder:30b"
}
```

这种配置的好处是：
- 复杂任务使用云端高性能模型（Claude Sonnet）
- 简单任务使用本地免费模型（Ollama），节省 API 费用

### 只使用单一模型

如果你希望所有任务都使用同一个模型，可以将 `small_model` 设置为与 `model` 相同：

```json
{
  "model": "anthropic/claude-sonnet-4-5",
  "small_model": "anthropic/claude-sonnet-4-5"
}
```

或者完全省略 `small_model` 配置（OpenCode 会使用内置默认值）。

---

## 常见问题排查

### AI_LoadAPIKeyError / API key is missing

**错误表现：**

```
AI_LoadAPIKeyError: API key is missing for provider "anthropic".
Please set the ANTHROPIC_API_KEY environment variable
or provide it via the auth configuration.
```

**排查步骤：**

1. **检查环境变量是否正确设置：**

```bash
echo $ANTHROPIC_API_KEY
# 应输出你的 API Key
```

2. **检查 auth.json 是否存在且格式正确：**

```bash
cat ~/.local/share/opencode/auth.json
# 确认 anthropic 字段和 apiKey 值存在
```

3. **检查配置文件中的 Key 引用语法：**

```bash
# 如果使用 {env:VAR} 语法，确认环境变量已导出
echo $ANTHROPIC_API_KEY

# 如果使用 {file:path} 语法，确认文件存在且可读
cat /run/secrets/anthropic_api_key
```

4. **检查 API Key 是否有效：**

```bash
# 测试 Anthropic API Key
curl https://api.anthropic.com/v1/models \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01"
```

**解决方案：**

```bash
# 方案 1: 使用 /connect 命令重新设置（TUI 中）
/connect

# 方案 2: 使用 auth login 命令
opencode auth login --provider anthropic --key "your-new-key"

# 方案 3: 直接设置环境变量
export ANTHROPIC_API_KEY="your-new-key"
```

### Ollama 上下文长度不足

**错误表现：**

- 模型返回截断的代码
- 长文件分析不完整
- 错误信息：`context length exceeded` 或类似的提示

**原因：** Ollama 默认上下文长度为 4096 tokens，对于现代代码库远远不够。

**解决方案：**

**方案 1: 在模型配置中设置上下文长度（推荐）**

```json
{
  "provider": {
    "ollama": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Ollama (local)",
      "options": {
        "baseURL": "http://localhost:11434/v1"
      },
      "models": {
        "qwen3-coder:30b": {
          "name": "Qwen3 Coder 30B",
          "options": {
            "num_ctx": 32768
          }
        }
      }
    }
  }
}
```

**方案 2: 使用 Modelfile 创建自定义模型**

```dockerfile
# File: Modelfile
FROM qwen3-coder:30b
PARAMETER num_ctx 65536
PARAMETER num_predict 16384
SYSTEM You are a helpful coding assistant.
```

```bash
ollama create qwen3-coder-64k -f Modelfile
```

然后在配置中使用新模型：

```json
{
  "model": "ollama/qwen3-coder-64k"
}
```

**方案 3: 启动 Ollama 时设置环境变量**

```bash
OLLAMA_CONTEXT_LENGTH=32768 ollama serve
```

**推荐的上下文长度：**

| 项目规模 | 推荐上下文长度 | 说明 |
|----------|---------------|------|
| 小型项目 | 8192 - 16384 | 单文件操作 |
| 中型项目 | 32768 - 65536 | 多文件分析 |
| 大型项目 | 131072+ | 全代码库分析 |

### 本地模型连接失败

**错误表现：**

```
ProviderError: Connection refused
FetchError: request to http://localhost:11434/v1/chat/completions failed
```

**排查步骤：**

1. **确认服务正在运行：**

```bash
# Ollama
curl http://localhost:11434/api/tags
# 应返回已安装的模型列表

# vLLM
curl http://localhost:8000/v1/models
# 应返回可用模型列表

# LM Studio
curl http://localhost:1234/v1/models
# 应返回可用模型列表
```

2. **确认 baseURL 以 `/v1` 结尾：**

```bash
# 正确
"baseURL": "http://localhost:11434/v1"

# 错误（缺少 /v1 后缀）
"baseURL": "http://localhost:11434"
```

3. **检查防火墙和网络：**

```bash
# 检查端口监听
netstat -tlnp | grep 11434
# 或
ss -tlnp | grep 11434

# 测试连接
telnet localhost 11434
```

4. **检查 CORS 设置（浏览器相关）：**

某些本地服务可能需要开启 CORS：

```bash
# Ollama 设置环境变量
export OLLAMA_ORIGINS="*"
ollama serve
```

**常见修复：**

```bash
# 重启 Ollama 服务
pkill ollama
ollama serve

# 检查 Ollama 日志
ollama serve 2>&1 | tee ollama.log
```

### ProviderModelNotFoundError

**错误表现：**

```
ProviderModelNotFoundError: Model "claude-sonnet-4-5" not found for provider "anthropic".
Available models: claude-sonnet-4-5, claude-opus-4-5, claude-haiku-4-5
```

**排查步骤：**

1. **检查模型名称拼写：**

```bash
# 列出可用模型确认正确名称
opencode models

# 常见拼写错误:
# 错误: claude-sonet-4-5    (缺少 n)
# 正确: claude-sonnet-4-5
```

2. **检查提供商名称拼写：**

```bash
# 常见错误:
# 错误: anthopic/claude-sonnet-4-5   (缺少 r)
# 正确: anthropic/claude-sonnet-4-5
```

3. **确认模型在提供商的 models 列表中定义：**

```json
{
  "provider": {
    "ollama": {
      "models": {
        "qwen3-coder:30b": {
          "name": "Qwen3 Coder 30B"
        }
      }
    }
  }
}
```

4. **如果模型不在预定义列表中，确保在配置中明确定义：**

```json
{
  "provider": {
    "anthropic": {
      "models": {
        "claude-sonnet-4-5": {
          "name": "Claude Sonnet 4.5"
        }
      }
    }
  }
}
```

---

## 最佳实践总结

### API Key 管理

1. **开发环境**：使用 `/connect` 或 `opencode auth login` 设置，Key 存储在 `auth.json` 中
2. **CI/CD 流水线**：使用环境变量，如 `ANTHROPIC_API_KEY`
3. **Docker/Kubernetes**：使用 `{file:path}` 语法引用挂载的 Secret 文件
4. **团队协作**：不要在水合 `opencode.json` 中硬编码 Key，使用 `.env` 文件（加入 `.gitignore`）

### 模型选择策略

1. **日常开发**：`anthropic/claude-sonnet-4-5` 或 `openai/gpt-4.1`，平衡质量与速度
2. **复杂架构任务**：`anthropic/claude-opus-4-5` 或 `openai/o3`
3. **快速轻量任务**：`anthropic/claude-haiku-4-5` 或 `openai/gpt-4o`
4. **离线/隐私场景**：使用 Ollama 本地部署 `qwen3-coder:30b` 或 `codellama:70b`
5. **成本敏感场景**：主模型用云端，轻量模型用本地（双模型架构）

### 配置层次化

```
项目 opencode.json  >  全局 ~/.config/opencode/opencode.json  >  内置默认值
     (团队标准)           (个人偏好)
```

- 将项目共享的配置（如 `model` 选择、超时时间）放在项目 `opencode.json` 中并提交到 Git
- 将个人偏好（如主题设置）放在全局配置中
- API Key 永远不要提交到版本控制

### 私有部署 checklist

- [ ] 推理服务已启动并可访问
- [ ] `baseURL` 以 `/v1` 结尾
- [ ] 模型已在 `models` 配置中定义
- [ ] 上下文长度已根据项目需求调整（Ollama 默认 4096 通常不够）
- [ ] 端口没有被防火墙阻挡
- [ ] GPU 显存足够加载目标模型

### 版本兼容性

本文档内容适用于 OpenCode **v1.14.32** 和 **v1.15.13**。不同版本的配置格式可能有所差异，建议升级到最新版本以获得完整的模型支持和配置功能。

---

## 参考

- [OpenCode 官方文档](https://opencode.ai/docs)
- [AI SDK Providers](https://sdk.vercel.ai/providers)
- [Ollama 文档](https://github.com/ollama/ollama/blob/main/docs/README.md)
- [vLLM 文档](https://docs.vllm.ai/)
- [LM Studio 文档](https://lmstudio.ai/docs)
- [llama.cpp 文档](https://github.com/ggerganov/llama.cpp/blob/master/docs/README.md)
