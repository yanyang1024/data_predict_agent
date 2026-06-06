# 从 Agent 技术演进到 OpenCode 工程实践：面向软件研发人员的 Coding Agent 教程

> 目标读者：有日常编码、调试、Code Review、测试经验的软件研发人员。
> 版本适用：OpenCode v1.14.32 和 v1.15.13
> 总章节：12 个 Markdown 文件，约 8,600+ 行

---

## 文档结构

本教程将原文档拆分为 12 个独立的 Markdown 文件，按学习路径组织：

### 第一部分：理念与架构

| 序号 | 文件 | 内容概要 |
|------|------|----------|
| 00 | [`00-introduction.md`](00-introduction.md) | 教程目标、一句话定位、版本适用性说明、文档导读 |
| 01 | [`01-agent-evolution.md`](01-agent-evolution.md) | 从 ReAct → Tool Calling → SWE-agent → OpenCode 的技术演进主线 |
| 02 | [`02-opencode-modules.md`](02-opencode-modules.md) | OpenCode 源码模块视角：session、tool、permission、agent、snapshot |

### 第二部分：工程实践

| 序号 | 文件 | 内容概要 |
|------|------|----------|
| 03 | [`03-usage-sop.md`](03-usage-sop.md) | 面向研发人员的 6 阶段使用 SOP（安全边界→初始化→Plan→收敛→Build→验证→Review） |
| 04 | [`04-permission-baseline.md`](04-permission-baseline.md) | 推荐 `opencode.json` 安全基线配置，含逐行注释和设计理念 |
| 05 | [`05-agents-md-template.md`](05-agents-md-template.md) | 推荐 `AGENTS.md` 模板（含 Node.js/Python/Go 三种技术栈） |

### 第三部分：配置与模型（新增）

| 序号 | 文件 | 内容概要 |
|------|------|----------|
| 06 | [`06-configuration-system.md`](06-configuration-system.md) | **新增**：OpenCode 全局配置与项目配置的分级配置方法，9 层优先级体系 |
| 07 | [`07-model-configuration.md`](07-model-configuration.md) | **新增**：模型选择与 LLM 配置（含私有部署模型 Ollama/vLLM/LM Studio 等） |
| 08 | [`08-path-pitfalls.md`](08-path-pitfalls.md) | **新增**：代码路径坑点详解，Skill/Tool/Script 路径引用机制与 10 大常见坑点 |

### 第四部分：参考与结尾

| 序号 | 文件 | 内容概要 |
|------|------|----------|
| 09 | [`09-common-pitfalls.md`](09-common-pitfalls.md) | 常见坑与解决方案（pkill、后台进程、/undo、write 覆盖、MCP 膨胀、.gitignore） |
| 10 | [`10-prompt-templates.md`](10-prompt-templates.md) | 可直接复用的 Prompt 模板（探索/实现/验证/Review/配置/模型切换） |
| 11 | [`11-conclusion.md`](11-conclusion.md) | 10 条核心建议、下一步学习路线、参考资料 |

---

## 相比原文档的主要改进

### 1. 结构拆分
- 将单一长文档拆分为 12 个独立的 Markdown 文件，便于按需阅读和团队协作
- 每个文件聚焦一个主题，层次分明

### 2. 信息核对与版本适配
- 所有内容已核对适用于 **OpenCode v1.14.32 和 v1.15.13**
- 标注了两个版本之间的关键差异
- 补充了 v1.15.13 的新增特性和修复项

### 3. 新增三大核心章节

#### `06-configuration-system.md` — 分级配置体系
- 详解 `opencode.json`、`opencode.jsonc`、`config.json` 的定位和作用
- 9 层配置优先级体系（内置默认值 → macOS MDM）
- 全局配置（`~/.config/opencode/`）与项目配置（`./opencode.json`）的层级关系
- 配置合并策略（深度合并、数组拼接去重、后匹配优先）
- 环境变量控制（`OPENCODE_CONFIG`、`OPENCODE_CONFIG_CONTENT` 等）
- 7 个实际场景的配置模板

#### `07-model-configuration.md` — 模型选择与 LLM 配置
- 75+ 个支持的模型提供商列表
- 7 种 API Key 设置方式（`/connect`、`auth login`、`auth.json`、环境变量、`{env:VAR}`、`.env`、`{file:path}`）
- 全局配置和项目配置中的模型选择方法
- 私有部署模型配置详解（Ollama、vLLM、LM Studio、llama.cpp），统一使用 `@ai-sdk/openai-compatible`
- 多模型切换方法（TUI `/models`、CLI `--model`）
- 模型变体 (Variants) 配置

#### `08-path-pitfalls.md` — 路径坑点详解
- 不同运行模式（CLI/Desktop/Web Daemon）下的路径原点差异
- Skill 路径系统（`.opencode/skills/<name>/SKILL.md`）
- Tool 路径系统（`.opencode/tools/*.ts`）
- SKILL.md 文档引用规范（`skill_resource` 工具）
- Tool Script 引用最佳实践（使用 `context.worktree`）
- **10 大路径坑点**，每个含问题描述、复现步骤、解决方案、参考来源

---

## 快速开始

建议按以下顺序阅读：

1. **新用户**：00 → 01 → 02 → 03 → 06 → 07 → 09
2. **已有经验，想深入配置**：06 → 07 → 08
3. **团队推广**：04 → 05 → 10 → 11
4. **问题排查**：08 → 09 → 10

---

*本教程基于 OpenCode v1.14.32 和 v1.15.13 编写。由于 OpenCode 迭代速度较快，建议以官方最新文档为准。*
