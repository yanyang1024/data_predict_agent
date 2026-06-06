# 1. 技术演进主线：从"会想"到"能安全地改代码"

> **适用版本**: OpenCode v1.14.32 / v1.15.13

Coding Agent 的发展不是一蹴而就的。它经历了从"让模型学会推理"到"让模型能安全地操作真实代码库"的渐进过程。理解这条演进链，有助于你把握 OpenCode 的设计哲学——为什么它长成现在这个样子，以及每个模块存在的理由。

本章将沿着 **ReAct → Tool Calling → SWE-agent (ACI) → OpenCode** 的主线，梳理技术演进的关键节点，并说明 OpenCode 在整条链中所处的独特位置。

---

## 1.1 ReAct：Agent 的最小闭环

ReAct（Reasoning + Acting）由 Yao et al. 于 2023 年提出，是 Agent 架构的奠基性工作。[^1]

### ReAct 的核心价值

ReAct 的价值不是"让模型说出更多推理"，而是建立了一个**最小可运行的反馈循环**：

```
观察任务 -> 形成假设 -> 调用动作 -> 接收观察 -> 修正计划 -> 再行动
```

这个循环的本质是：**让模型不再一次性给出最终答案，而是在"思考"和"行动"之间反复迭代，根据环境反馈动态调整策略**。

### ReAct 的三阶段循环

每一轮 ReAct 循环都包含三个明确阶段：[^2]

| 阶段 | 作用 | 示例 |
|------|------|------|
| **Thought（思考）** | 模型输出显式推理过程，分析当前状态和下一步策略 | "Bug 可能与鉴权中间件有关，我需要先查看路由入口" |
| **Action（行动）** | 调用外部工具执行具体操作 | `grep "auth" src/middleware/` |
| **Observation（观察）** | 接收工具执行结果，纳入下一轮推理 | "找到 3 个文件：jwt.ts、oauth.ts、session.ts" |

### 放到研发场景里

```text
怀疑 bug 在鉴权中间件
  -> grep 路由入口
  -> read 认证逻辑
  -> 跑一条失败测试
  -> 发现根因在 token refresh
  -> 最小修改
  -> 再跑测试验证
```

ReAct 解决了一个根本问题：**模型如何从"纸上谈兵"变成"动手实践"**。但 ReAct 只定义了循环框架，没有规定"动作"具体长什么样——这就引出了下一步：Tool Calling。

---

## 1.2 Tool Calling：把"我想做"变成"可执行动作"

### 自然语言的问题

ReAct 框架中的 Action 如果只是自然语言描述，无法被稳定执行。比如模型说"我要搜索认证相关的代码"，这句话本身不能直接操作文件系统——需要一个**结构化的执行层**。

### 结构化工具调用

Tool Calling 的核心思想是：**把 Agent 可能需要的操作封装成带类型的函数接口**，让模型输出结构化调用指令而非自由文本。

每一步，模型不再说"我要读取文件"，而是生成：

```json
{
  "tool": "read",
  "params": {
    "file_path": "src/auth/middleware.ts",
    "offset": 1,
    "limit": 50
  }
}
```

### OpenCode 的工具集

这一步对应到 OpenCode，就是其内置的 **Tool Registry** 中的工具集合。以 OpenCode v1.15.13 为例，核心工具包括：[^3]

| 工具 | 用途 |
|------|------|
| `read` | 读取文件内容，支持行号范围和分页 |
| `grep` | 在代码库中搜索匹配文本 |
| `glob` | 按模式匹配文件路径 |
| `bash` | 执行终端命令 |
| `edit` | 精确编辑文件（替换指定行范围） |
| `write` | 写入新文件 |
| `apply_patch` | 应用统一 diff 补丁 |
| `task` | 创建子 Agent 执行并行任务 |
| `skill` | 调用预定义的技能脚本 |
| `webfetch` | 抓取网页内容 |

> **版本适配**: OpenCode v1.14.32 和 v1.15.13 在核心工具集上保持一致。v1.15.13 在 TUI 模式下优化了内联工具行的对齐显示，并支持失败工具的错误详情就地展开。

### Tool Calling 的意义

Tool Calling 解决了**从意图到执行**的鸿沟，但它仍然是"通用工具"——一把锤子敲所有钉子。对于软件工程这种高度专业化的领域，通用工具往往不够高效，甚至会把模型带入死胡同。比如：

- `cat` 一个 5000 行的文件会撑爆上下文窗口
- 无保护的 `edit` 可能制造语法错误
- `grep -r` 的冗长输出会让模型迷失方向

这就引出了第三次关键演进：**为软件工程专门设计 Agent-Computer Interface**。

---

## 1.3 SWE-agent：软件工程需要专门的 ACI

### 从通用到专用

SWE-agent（Yang et al., NeurIPS 2024）是这条演进链上的里程碑。它提出了 **ACI（Agent-Computer Interface，Agent-计算机接口）** 的概念：[^4][^5]

> 正如人类开发者受益于 IDE 这类专门工具，LLM Agent 作为一类全新的终端用户，也需要专门为其能力和局限而构建的接口。

### ACI 的核心设计原则

SWE-agent 的研究表明，**接口设计对性能的影响超过底层模型本身**。关键数据：[^6]

| 指标 | 数值 |
|------|------|
| SWE-bench 完整测试集解决率 | **12.5%**（GPT-4 Turbo） |
| 相比 RAG 基线提升 | 从 3.8% → 12.5%，提升 3.3 倍 |
| ACI 相比原始 Linux Shell | 多解决 **10.7 个百分点** |
| HumanEvalFix pass@1 | **87.7%** |

### ACI 的关键设计要素

SWE-agent 的 ACI 在以下几个方面做了专门优化：

**1. 文件查看器：100 行窗口**

不是 `cat` 整个文件，而是每次显示约 100 行，配合滚动命令。实验证明：窗口太小（30 行）损失 3.7pp 性能；窗口太大（整个文件）模型会失焦。

**2. 编辑循环内置 Linter**

每次编辑命令执行前先做语法检查，防止模型陷入"代码越改越错"的状态。

**3. 极简搜索反馈**

`search_dir` 只返回匹配文件名列表，不带周围上下文。对模型来说，"少即是多"——它需要的是决策线索，而非信息轰炸。

**4. 环境反馈格式化**

错误消息经过精心设计，包含路径、行号、错误类型和修复建议，而非原始的 shell 报错堆栈。

### ACI 的启示

SWE-agent 证明了一件事：**Coding Agent 的效率瓶颈不在模型智商，而在接口设计**。一套好的 ACI 应该具备：

- 简化的操作空间（结构化命令替代复杂 shell）
- 增强的反馈机制（清晰、简洁的状态反馈）
- 内置防护机制（语法检查、路径验证、错误恢复）

但 SWE-agent 仍是一个研究原型，运行在沙箱环境中。如何将 ACI 的理念落地到真实开发工作流中？这就是 OpenCode 要回答的问题。

---

## 1.4 OpenCode：把 Coding Agent 做成本地运行时

OpenCode 不是对 ACI 理念的简单复刻，而是将其**产品化、工程化、本地化**的产物。它是整条演进链上第一个把"Agent 改代码"做成**生产级本地运行时**的项目。

### OpenCode 的架构定位

```
OpenCode = 本地 TUI / CLI / Server
         + 多 provider LLM 调用
         + Agent 配置
         + Tool Registry
         + Permission Gate
         + Session Processor
         + Snapshot / Undo
         + AGENTS.md / Skills / Commands / MCP / Plugins
```

让我们逐一拆解每个模块在演进链中的意义。

### 1.4.1 三种运行形态：适配不同工作流

OpenCode 支持三种形态，对应不同的使用场景：[^7]

| 形态 | 适用场景 | 特点 |
|------|----------|------|
| **TUI** | 日常交互式编码 | 终端图形界面，支持 `/` 命令和实时预览 |
| **CLI** | 脚本化、自动化任务 | 非交互模式，可管道化集成 |
| **Server** | 集成到 IDE / 第三方工具 | 通过 Agent Client Protocol (ACP) 通信 |

```bash
# TUI 模式（交互式）
opencode

# CLI 模式（非交互式，v1.15.13 支持 --timeout 参数）
opencode -p "重构 auth 模块" -a coder --timeout 30m

# Server 模式（后台服务，IDE 插件连接）
opencode server --port 8080
```

### 1.4.2 75+ LLM 提供商：打破供应商锁定

OpenCode 通过 AI SDK 和 Models.dev 集成，支持 **75+ 个 LLM 提供商**，包括：[^8]

- **商业模型**：Claude (Anthropic)、GPT (OpenAI)、Gemini (Google)、Grok (xAI)
- **云平台**：Azure OpenAI、Google Vertex AI、AWS Bedrock、SAP AI Core
- **开源模型**：通过 Ollama、LM Studio 本地运行
- **聚合服务**：OpenRouter、Together AI、Fireworks AI、DeepSeek、Moonshot AI 等
- **已有订阅复用**：GitHub Copilot、ChatGPT Plus/Pro

模型使用 `provider/model-name` 格式指定：

```json
{
  "model": "anthropic/claude-sonnet-4-5",
  "small_model": "anthropic/claude-haiku-4-5"
}
```

> **版本适配**: OpenCode v1.15.13 修复了 Anthropic Opus 4.7+ adaptive reasoning 返回空 thinking block 的问题，现在会保留 summarized thinking。v1.14.32 用户如果遇到此问题建议升级到 v1.15.13。

### 1.4.3 四层配置体系：灵活与可控的平衡

OpenCode 的配置采用**分层覆盖**设计，兼顾团队统一规范和个人自定义需求：[^9][^10]

| 层级 | 位置 | 优先级 | 用途 |
|------|------|--------|------|
| **环境变量** | `OPENCODE_CONFIG` 等 | 最高 | CI/CD、敏感凭证 |
| **项目级配置** | `./opencode.json` | 高 | 团队共享的项目规范 |
| **全局配置** | `~/.config/opencode/opencode.json` | 中 | 个人默认偏好 |
| **远程配置** | 通过 URL 加载 | 低 | 组织级统一策略 |

配置合并规则：**项目级覆盖全局，环境变量覆盖一切**。

```json
// ~/.config/opencode/opencode.json — 全局默认
{
  "model": "anthropic/claude-sonnet-4-5",
  "provider": {
    "anthropic": {
      "options": {
        "apiKey": "{env:ANTHROPIC_API_KEY}"
      }
    }
  }
}

// ./opencode.json — 项目级覆盖
{
  "model": "openai/gpt-5.1-codex",
  "agents": {
    "reviewer": {
      "prompt": "你是代码审查专家，关注安全和性能..."
    }
  }
}
```

> **v1.15.13 改进**: Config 现在从打开的位置向上加载，目录特定的设置和 provider 策略应用更加可预测。

### 1.4.4 Permission Gate：安全改代码的底线

OpenCode 继承了 SWE-agent ACI 的防护理念，并增加了**权限门控机制**。每一次可能修改代码的操作（`edit`、`write`、`bash` 等）都需要经过 Permission Gate：

| 安全机制 | 说明 |
|----------|------|
| **操作前确认** | 敏感工具默认需要用户确认 |
| **自动审批规则** | 可配置 glob 模式自动批准低风险操作 |
| **Snapshot / Undo** | 每次编辑前自动创建快照，支持一键回滚 |
| **语法检查** | 编辑后自动运行 linter，防止语法错误 |

### 1.4.5 Session Processor：状态管理的核心

Session Processor 是 OpenCode 的"大脑"，负责：

- 维护多轮对话的上下文窗口
- 管理 ReAct 循环的执行节奏
- 协调 Tool Registry 的调用与结果反馈
- 处理子 Agent（`task` 工具）的并行执行

> **v1.15.13 新特性**: Session 现在支持通过 API 和 SDK 存储自定义 metadata，便于外部工具追踪会话状态。

### 1.4.6 可扩展体系：AGENTS.md / Skills / Commands / MCP / Plugins

OpenCode 的真正强大之处在于其**可扩展体系**，这让它超越了静态 ACI，成为一个**活的、可成长的 Agent 平台**。

| 扩展机制 | 作用 |
|----------|------|
| **AGENTS.md** | 项目级 Agent 行为规范，定义代码风格、架构约束 |
| **Skills** | 可复用的技能脚本，封装常见操作模式 |
| **Commands** | TUI 中的 `/` 命令，如 `/connect`、`/models`、`/undo` |
| **MCP** | Model Context Protocol，连接外部数据源和服务 |
| **Plugins** | 第三方插件扩展 Tool Registry 的能力 |

```text
# AGENTS.md 示例 — 定义项目规范
## 代码风格
- 使用 TypeScript strict mode
- 所有 API 端点必须带输入验证
- 数据库操作必须通过 Repository 层

## 架构约束
- 禁止在 Controller 中直接调用 ORM
- 所有外部 HTTP 调用必须走 Circuit Breaker
```

---

## 1.5 OpenCode 在演进链中的独特位置

理解完整条演进链后，我们可以清晰地定位 OpenCode 的独特价值：

### 演进链对比

| 阶段 | 代表 | 解决的问题 | 局限 |
|------|------|------------|------|
| **ReAct** | Yao et al. (2023) | 建立"思考-行动-观察"循环 | 只有框架，无具体工具 |
| **Tool Calling** | 各 LLM 平台 | 将意图结构化执行 | 通用工具，不适合代码场景 |
| **SWE-agent (ACI)** | Yang et al. (2024) | 为代码任务设计专用接口 | 研究原型，沙箱环境 |
| **OpenCode** | Anomaly (2025) | **将 ACI 产品化为本地运行时** | 需要一定配置学习成本 |

### OpenCode 的独特贡献

**1. 从沙箱到生产环境**

SWE-agent 运行在受控沙箱中，而 OpenCode 直接操作你的本地代码库。这意味着：

- 与现有工具链集成（Git、LSP、测试框架）
- 利用真实的 IDE 和编辑器环境
- 代码不离开本地机器，保障隐私安全

**2. 从单一模型到模型联邦**

OpenCode 的 75+ 提供商支持让你可以为不同任务选择不同模型：[^11]

```json
{
  "agents": {
    "architect": {
      "model": "anthropic/claude-opus-4-5",
      "prompt": "你负责架构设计..."
    },
    "refactor": {
      "model": "openai/gpt-5.1-codex",
      "prompt": "你负责代码重构..."
    },
    "tester": {
      "model": "google/gemini-2.5-pro",
      "prompt": "你负责写测试..."
    }
  }
}
```

**3. 从静态接口到动态可扩展平台**

ACI 是固定的命令集，而 OpenCode 通过 Skills、MCP 和 Plugins 让接口动态进化：

- **Skills**：把团队的最佳实践编码为可复用脚本
- **MCP**：连接外部世界（数据库、API、文档）
- **Plugins**：社区贡献的新工具持续丰富 Tool Registry

**4. 从单一会话到多 Agent 并行**

OpenCode 支持**多会话并行 Agent**，同一项目可同时运行多个独立任务：[^12]

```bash
# 会话 A：修复 bug
opencode -p "修复登录超时问题" -s fix-login

# 会话 B：写测试（同时运行）
opencode -p "为 auth 模块补全测试" -s add-auth-tests

# 会话 C：重构（同时运行）
opencode -p "重构 utils 目录" -s refactor-utils
```

每个会话独立上下文、独立历史、可独立回滚。

### 一句话总结

> **ReAct 给了 Agent 会思考的能力，Tool Calling 给了它动手的能力，SWE-agent 的 ACI 给了它专业编程的接口，而 OpenCode 把这一切都装进了你的本地开发环境——让它真正成为一个能安全、高效、可扩展地改代码的工程伙伴。**

---

## 本章小结

| 关键概念 | 一句话解释 |
|----------|------------|
| **ReAct** | Agent 的"思考-行动-观察"最小循环 |
| **Tool Calling** | 将自然语言意图转化为结构化可执行操作 |
| **ACI** | 专为 LLM 设计的软件工程接口，而非人类 UI |
| **OpenCode** | 将 ACI 理念产品化为本地生产级 Coding Agent 运行时 |

**OpenCode v1.15.13 关键更新回顾**:

- Session 支持自定义 metadata（API & SDK）
- Config 加载从打开位置向上遍历，目录级设置更可预测
- Anthropic Opus 4.7+ adaptive reasoning 修复，保留 summarized thinking
- TUI 内联工具行对齐优化，失败工具支持就地展开错误详情

---

## 参考资料

[^1]: Yao et al., "ReAct: Synergizing Reasoning and Acting in Language Models," ICLR 2023. https://arxiv.org/abs/2210.03629

[^2]: "What Is the ReAct Loop? How AI Agents Reason, Act, and Iterate," MindStudio Blog, 2026. https://www.mindstudio.ai/blog/what-is-react-loop-ai-agent-reasoning/

[^3]: OpenCode Documentation, "OpenCode Tools Reference," https://open-code.ai/docs

[^4]: Yang et al., "SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering," NeurIPS 2024. https://arxiv.org/abs/2405.15793

[^5]: "SWE-agent: How Interface Design Unlocks Automated Software Engineering," Bean Labs Research Logs, 2026. https://beancount.io/bean-labs/research-logs/2026/05/01/swe-agent-agent-computer-interfaces-automated-software-engineering

[^6]: Yang et al., SWE-agent ablation study results, Table 2. https://arxiv.org/abs/2405.15793

[^7]: OpenCode v1.15.13 Release Notes, https://github.com/sst/opencode/releases/tag/v1.15.13

[^8]: OpenCode Documentation, "Model Selection - 75+ LLMs Supported," https://open-code.ai/docs/models

[^9]: OpenCode Documentation, "Providers - 75+ LLM Model Configuration," https://open-code.ai/docs/providers

[^10]: "OpenCode configuration system," LobeHub Skills Marketplace, 2026. https://lobehub.com/bg/skills/spillwavesolutions-opencode_cli

[^11]: "OpenCode: Open source AI coding agent with 75+ models," GTM Guide. https://gtmguide.hk/en/opencode

[^12]: "OpenCode: 140k Star 的开源 AI 编程 Agent," SOTA Sync, 2026. https://sotasync.com/reader/2026-04-23-opencode-open-source-coding-agent/
