# 03. 全局配置、项目配置、模型与 API Key

> 适用版本：`v1.14.32` / `v1.15.13`。  
> 重点回答：`config.json` / `opencode.json` / `opencode.jsonc` 分别放哪、谁覆盖谁；全局和项目如何选择模型；LLM API Key 填哪里；私有部署模型如何配置。

## 1. 配置文件格式

OpenCode 使用 JSON/JSONC 配置。推荐写法：

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "model": "anthropic/claude-sonnet-4-5",
  "autoupdate": false
}
```

建议团队统一使用：

- 全局：`~/.config/opencode/opencode.jsonc`
- 项目：`<project-root>/opencode.jsonc` 或 `<project-root>/opencode.json`
- `.opencode/`：放 agents、commands、skills、tools、plugins 等目录化扩展

`config.json` 在 v1.14.32 和 v1.15.13 源码里仍会被加载，属于兼容/历史路径。新文档建议不要主推 `config.json`，避免团队混乱。

## 2. 配置优先级与合并逻辑

官方文档的配置加载顺序大致是：

```text
远程组织配置
-> 全局配置 ~/.config/opencode/opencode.json
-> OPENCODE_CONFIG 指定的自定义配置
-> 项目配置 opencode.json
-> .opencode/ 目录中的 agents/commands/plugins/skills/tools 等
-> OPENCODE_CONFIG_CONTENT 内联配置
-> 管理员/MDM 管理配置
```

关键点：

1. 配置是“合并”，不是整个文件替换。
2. 后加载的配置对冲突键有更高优先级。
3. 非冲突键会保留。
4. `instructions` 这类数组字段在源码里有去重合并逻辑，不应简单理解为“后者完全覆盖前者”。
5. `v1.15.13` release 明确提到“Config now loads from the opened location upward”，也就是从打开位置向上加载目录相关配置，目录级配置和 provider policy 的应用更可预测。

## 3. 全局配置、项目配置、`.opencode/` 的职责分工

### 3.1 全局配置

适合放“个人机器级偏好”：

```text
~/.config/opencode/opencode.jsonc
~/.config/opencode/AGENTS.md
~/.config/opencode/agents/*.md
~/.config/opencode/commands/*.md
~/.config/opencode/skills/*/SKILL.md
~/.config/opencode/tools/*.ts
~/.config/opencode/plugins/*.ts
```

建议放：

- 默认模型；
- 默认 provider；
- 个人常用 keybind/theme；
- 个人 API Key 引用；
- 通用安全权限；
- 通用 agents / commands / skills。

不建议放：

- 项目特定测试命令；
- 项目私有脚本路径；
- 会影响所有项目的高风险 `bash: allow`；
- 项目仓库内相对路径。

### 3.2 项目配置

适合放“仓库级规则”：

```text
<project-root>/opencode.jsonc
<project-root>/AGENTS.md
<project-root>/.opencode/agents/*.md
<project-root>/.opencode/commands/*.md
<project-root>/.opencode/skills/*/SKILL.md
<project-root>/.opencode/tools/*.ts
<project-root>/.opencode/plugins/*.ts
```

建议放：

- 项目默认模型；
- 项目专用子代理；
- 项目测试/lint/typecheck 命令；
- 读写权限边界；
- 自定义 tools；
- skill 定义；
- watcher ignore；
- snapshot 是否启用。

### 3.3 `.opencode/` 目录

`.opencode/` 更适合承载“目录化扩展资源”：

```text
.opencode/
  agents/
  commands/
  skills/
  tools/
  plugins/
```

v1.14.32/v1.15.13 源码中还会加载 `.opencode/opencode.json` 与 `.opencode/opencode.jsonc`。但官方 Config 文档主推“项目根 `opencode.json`”，所以团队约定上建议：

- 项目根 `opencode.jsonc`：放主项目配置；
- `.opencode/`：放 agents/commands/skills/tools/plugins；
- 避免同时在项目根和 `.opencode/` 下都写主配置，除非你明确知道合并顺序和覆盖关系。

## 4. 规则文件与 instructions

OpenCode 规则文件加载顺序：

```text
从当前目录向上找本地 AGENTS.md / CLAUDE.md
-> 全局 ~/.config/opencode/AGENTS.md
-> ~/.claude/CLAUDE.md（除非禁用）
```

注意：

- 同一类别里“第一个匹配文件赢”。如果同目录同时有 `AGENTS.md` 和 `CLAUDE.md`，通常只用 `AGENTS.md`。
- 如果你要复用更多规则文件，不要只在 `AGENTS.md` 里写“参考某文件”，因为 OpenCode 不会自动解析普通 Markdown 文本里的文件引用。
- 推荐在 `opencode.jsonc` 中显式配置：

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "instructions": [
    "CONTRIBUTING.md",
    "docs/development-standards.md",
    ".cursor/rules/*.md",
    "packages/*/AGENTS.md"
  ]
}
```

## 5. 模型选择优先级

模型 ID 的格式：

```text
<provider_id>/<model_id>
```

例如：

```text
anthropic/claude-sonnet-4-20250514
openai/gpt-5
openrouter/moonshotai/kimi-k2
lmstudio/google/gemma-3n-e4b
ollama/llama2
```

模型加载优先级：

```text
CLI 参数 --model 或 -m
-> config 中的 model
-> 上次使用模型
```

### CLI 临时指定模型

```bash
opencode --model anthropic/claude-sonnet-4-20250514
opencode run "review this diff" --model openai/gpt-5
```

### 全局默认模型

`~/.config/opencode/opencode.jsonc`：

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "model": "anthropic/claude-sonnet-4-20250514"
}
```

### 项目默认模型

`<project-root>/opencode.jsonc`：

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "model": "openrouter/moonshotai/kimi-k2"
}
```

### agent 级模型

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "agent": {
    "plan": {
      "mode": "primary",
      "model": "anthropic/claude-haiku-4-20250514",
      "permission": {
        "edit": "deny",
        "bash": "ask"
      }
    },
    "build": {
      "mode": "primary",
      "model": "anthropic/claude-sonnet-4-20250514",
      "permission": {
        "edit": "ask",
        "bash": "ask"
      }
    },
    "review": {
      "mode": "subagent",
      "description": "Review code for correctness, security and test coverage.",
      "model": "openai/gpt-5",
      "permission": {
        "edit": "deny",
        "bash": "deny"
      }
    }
  }
}
```

### command 级模型

`.opencode/commands/review.md`：

```markdown
---
description: Review recent git diff
agent: plan
model: openai/gpt-5
---

Review current git diff. Do not edit files.
```

## 6. API Key 填哪里

### 推荐方式：`/connect`

在 TUI 里运行：

```text
/connect
```

选择 provider，粘贴 API Key。OpenCode 会把凭据保存在：

```text
~/.local/share/opencode/auth.json
```

适合：

- Anthropic / OpenAI / OpenRouter / OpenCode Zen / 其他常见 provider；
- 个人机器使用；
- 不想把密钥暴露在配置文件里。

### 环境变量方式

`~/.config/opencode/opencode.jsonc`：

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
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

Shell：

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."
opencode
```

### 文件引用方式

```jsonc
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

注意：

- `{file:...}` 相对路径是相对配置文件目录解析，也可以用绝对路径或 `~`。
- 不要把 `.secrets` 或 API Key 文件放进项目仓库。
- 项目配置里如果必须引用 key，只写 `{env:...}`，不要写明文。

## 7. 私有部署 / OpenAI-compatible 模型配置

### 7.1 通用 OpenAI-compatible provider

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "myprovider": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "My Private Gateway",
      "options": {
        "baseURL": "https://llm.example.com/v1",
        "apiKey": "{env:MYPROVIDER_API_KEY}",
        "headers": {
          "X-Project": "etch-agent"
        }
      },
      "models": {
        "qwen3-coder-private": {
          "name": "Qwen3 Coder Private",
          "limit": {
            "context": 131072,
            "output": 32768
          }
        }
      }
    }
  },
  "model": "myprovider/qwen3-coder-private"
}
```

关键点：

- `provider` 下的 key（这里是 `myprovider`）就是 provider_id。
- `models` 下的 key（这里是 `qwen3-coder-private`）就是 model_id。
- 最终模型 ID 是 `myprovider/qwen3-coder-private`。
- 如果后端走 `/v1/chat/completions`，一般用 `@ai-sdk/openai-compatible`。
- 如果后端走 `/v1/responses`，根据官方说明应考虑 `@ai-sdk/openai`。
- `limit.context` / `limit.output` 很重要，尤其私有模型没有 models.dev 元数据时，OpenCode 需要这些值估算剩余上下文。

### 7.2 LM Studio 本地模型

```jsonc
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
          "name": "Gemma 3n-e4b (local)",
          "limit": {
            "context": 32768,
            "output": 8192
          }
        }
      }
    }
  },
  "model": "lmstudio/google/gemma-3n-e4b"
}
```

### 7.3 Ollama 本地模型

```jsonc
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
        "qwen2.5-coder:32b": {
          "name": "Qwen2.5 Coder 32B",
          "limit": {
            "context": 32768,
            "output": 8192
          }
        }
      }
    }
  },
  "model": "ollama/qwen2.5-coder:32b"
}
```

如果 tool calls 不稳定，优先检查：

1. 模型本身是否支持工具调用；
2. 本地引擎的 chat template 是否兼容工具调用；
3. Ollama / LM Studio 的上下文长度是否足够；
4. `limit.context` 是否写得过大或过小；
5. 输出 token 是否过大导致模型胡乱续写；
6. 是否应该换成更擅长 function calling 的模型。

## 8. provider 白名单/黑名单

如果全局有很多 provider 凭据，项目里可以限制可用 provider：

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "enabled_providers": ["anthropic", "openrouter", "myprovider"],
  "disabled_providers": ["openai"]
}
```

注意：`disabled_providers` 优先级高于 `enabled_providers`。

## 9. 推荐配置分层策略

```text
全局 opencode.jsonc
  - 个人 API Key 引用
  - 个人默认模型
  - 保守默认 permission
  - 常用全局 agents/commands/skills/tools

项目 opencode.jsonc
  - 项目默认模型或 provider allowlist
  - 项目测试命令
  - 项目 watcher/snapshot/lsp 设置
  - 项目级 permission 微调

AGENTS.md
  - 项目结构
  - 工作流
  - 禁止事项
  - 运行命令
  - review 标准

.opencode/
  - 目录化 agents/commands/skills/tools/plugins
```

## 10. 常见配置错误

| 现象 | 常见原因 | 处理方式 |
|---|---|---|
| `ProviderModelNotFoundError` | 模型 ID 写错，不是 `<provider>/<model>` | 跑 `opencode models` 或 TUI `/models` 检查 |
| `/models` 看不到私有 provider | `/connect` 的 provider id 和 `opencode.jsonc` 的 key 不一致 | 保持 provider_id 完全一致 |
| 项目配置不生效 | 启动目录不在项目/worktree 内，或存在多个配置覆盖 | 用 `--log-level DEBUG` 查看加载路径 |
| API Key 暴露 | 把 key 直接写在项目配置 | 改为 `/connect`、`{env:...}` 或 `{file:...}` |
| 本地模型工具调用乱 | 模型或 chat template 不支持 tool call | 换模型、升级引擎、降低工具复杂度、减少上下文 |
| config.json / opencode.json 混用 | 历史兼容文件和新文件同时存在 | 团队统一迁移到 `opencode.jsonc` |
