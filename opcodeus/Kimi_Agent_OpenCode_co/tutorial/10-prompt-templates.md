# 第 10 章 Prompt 模板与实战咒语

> 适用版本：OpenCode v1.14.32 / v1.15.13

本章提供一套经过实战验证的 Prompt 模板，覆盖 Coding Agent 工作流中的核心场景：代码探索、实现、验证、审查，以及 OpenCode 特有的配置管理和模型切换操作。这些模板可直接复制使用，也可根据团队规范自行调整。

---

## 10.1 只读探索模板

**使用场景**：刚接手陌生代码库，需要快速理解模块结构、调用关系和数据流，**严禁修改任何文件**。

```markdown
请只读探索，不要修改文件，不要运行会改变状态的命令。

目标：<描述任务，例如：理解用户认证模块的完整流程>

请输出：
1. 相关入口文件
2. 调用链（从 API 层到数据层的完整链路）
3. 数据结构 / API / 配置位置
4. 需要验证的假设
5. 建议的最小修改方案
```

### 使用要点

- **安全优先**：模板开头的约束语"只读探索，不要修改文件"是硬性指令，可降低 Agent 误操作风险
- **明确目标**：`<描述任务>`越具体，输出越聚焦。避免模糊的"看看这个项目"
- **结合 OpenCode 特性**：在 v1.15.13 中，可配合 `/models` 命令临时切换到更强的推理模型（如 `anthropic/claude-opus-4-5`）进行复杂代码分析，探索完成后再切回默认模型
- **Skill 增强**：如已安装 `opencode-skillful` 插件，可在探索前加载相关 Skill 以提供领域上下文

---

## 10.2 开始实现模板

**使用场景**：已确认技术方案，进入编码阶段，需要对代码进行最小化修改。

```markdown
请按已确认方案做最小实现。

约束：
- 不要提交代码（不要执行 git commit / git push）。
- 不要运行 pkill / killall / taskkill / rm -rf / git reset / git clean。
- 不要启动长时间后台服务（如 dev server、daemon 进程）。
- 优先使用 edit / apply_patch 进行局部修改，不要整体 rewrite 大文件。
- 修改完成后先给出 diff 摘要，再运行最小相关测试。
```

### 使用要点

- **最小修改原则**：`edit` / `apply_patch` 是 OpenCode 的增量编辑工具，相比全文重写，它能保留文件中的注释、格式和未改动逻辑，降低冲突风险
- **安全红线**：`pkill`、`rm -rf`、`git reset` 等命令属于破坏性操作，已在多个 GitHub Issues 中被报告为高风险命令（如 [#9082](https://github.com/anomalyco/opencode/issues/9082)）。务必在约束中明确禁止
- **diff 优先**：要求 Agent 先输出 diff 摘要，让开发者在测试运行前有机会审查变更范围
- **版本适配**：v1.15.13 的权限系统增强了 LSP 权限提示，如果修改涉及 LSP 相关的代码（如语言服务器配置），Agent 可能会弹出权限确认，需提前在 `opencode.json` 中配置 `"permission": { "lsp": "allow" }` 或准备好手动确认

---

## 10.3 验证模板

**使用场景**：代码修改完成后，需要系统性地验证正确性。

```markdown
请验证本次改动。

步骤：
1. 先看 git diff --stat 和 git diff，确认变更范围。
2. 运行最小相关测试（与改动直接相关的单元测试 / 集成测试）。
3. 如果最小测试通过，再运行 typecheck / lint（如 tsc --noEmit、eslint、prettier --check）。
4. 如果失败，先解释失败原因，不要扩大修改面。
5. 最后输出：已验证项、未验证项、风险点。
```

### 使用要点

- **分层验证**：从最小测试到全量检查，逐层递进。避免一上来就运行完整测试套件浪费时间
- **失败即停**：第四步的"先解释失败原因，不要扩大修改面"是关键约束。Agent 在遇到测试失败时容易"过度修复"——试图同时修改多个地方来让测试通过，这往往引入更多问题
- **风险输出**：要求 Agent 明确列出未验证项（如"未验证边界条件 X"、"未验证并发场景 Y"），帮助开发者判断是否需要补充验证
- **结合 Snapshot**：OpenCode 的 snapshot 功能（`"snapshot": true`）会在文件变更时自动创建恢复点。验证前可通过 `/undo` 查看历史 snapshot，确保验证失败时可以快速回滚

---

## 10.4 Review 模板

**使用场景**：代码修改完成并通过测试后，进行代码审查（自审或他审）。

```markdown
请以代码审查者身份审查本次 diff，不要修改文件。

重点看：
1. 正确性：逻辑是否符合预期，有无明显的 Bug。
2. 边界条件：空值、越界、异常输入的处理。
3. 并发 / 幂等 / 事务风险：多线程、重试、分布式场景下的安全性。
4. 安全风险：注入、越权、敏感信息泄露。
5. 测试覆盖：是否覆盖了主路径和关键边界条件。
6. 是否有无关改动：diff 中是否混入了与本次任务无关的修改（如格式调整、换行符变更）。
```

### 使用要点

- **只读模式**：强调"不要修改文件"，Review 阶段的 Agent 应该纯粹是审查者角色
- **六维审查**：六个审查维度覆盖了从功能正确性到工程规范的完整范围，可根据项目特点调整权重
- **无关改动检查**：Agent 有时会"顺手"格式化代码或修复换行符，这些无关改动会污染 diff、增加 review 成本。第六项专门对此进行约束
- **模型建议**：Review 阶段建议切换到推理能力更强的模型（如通过 `/models` 选择 `anthropic/claude-opus-4-5` 或 `openai/gpt-5.1-codex`），以获得更深层的代码分析

---

## 10.5 配置相关操作模板（v1.15.13 新增）

**使用场景**：需要查看、修改或切换 OpenCode 配置，包括模型切换、权限调整、Provider 设置等。

```markdown
请帮我检查并调整 OpenCode 配置。

步骤：
1. 查看当前生效的配置（全局 + 项目级合并后的结果）。
2. 确认当前使用的模型：/model status
3. 检查权限配置是否合理（permission.edit、permission.bash 等）。
4. 如需修改，优先编辑项目级的 opencode.json，不要修改全局配置。
5. 修改后验证配置格式是否正确（JSON/JSONC 语法检查）。
6. 如需切换模型，使用 /models 命令列出可用模型并选择。

约束：
- 不要暴露 API Key 等敏感信息。
- 修改配置前先备份原文件。
- 涉及权限放宽时需说明理由。
```

### 使用要点

- **配置分层意识**：OpenCode 的配置系统采用多层合并策略（内置默认 → 远程 → 全局 → 项目 → `.opencode/` → 环境变量）。修改时应遵循"项目级优先于全局级"的原则，避免影响其他项目
- **模型切换**：v1.15.13 支持通过 `/models` 命令动态切换模型，无需重启。可在同一 session 中根据任务类型切换不同模型（如编码用 `claude-sonnet-4-5`，Review 用 `claude-opus-4-5`）
- **敏感信息保护**：配置中的 API Key 应使用 `{env:VARIABLE_NAME}` 或 `{file:path}` 语法引用，不要硬编码。参考第 6 章配置系统详解
- **权限最小化**：放宽权限（如 `"bash": "allow"`）时需明确说明理由，并在任务完成后恢复更严格的设置

---

## 10.6 模型切换与任务路由模板（v1.15.13 新增）

**使用场景**：根据任务类型动态选择最适合的模型，实现"多模型协作"工作流。

```markdown
本次任务需要分阶段使用不同模型，请按以下步骤执行：

阶段 1 - 探索分析（使用推理模型）：
模型：anthropic/claude-opus-4-5 或 openai/gpt-5.1-codex
任务：理解代码结构、分析依赖关系、识别关键路径
命令：/model anthropic/claude-opus-4-5

阶段 2 - 编码实现（使用快速模型）：
模型：anthropic/claude-sonnet-4-5 或 deepseek/deepseek-coder
任务：编写代码、应用 patch、局部修改
命令：/model anthropic/claude-sonnet-4-5

阶段 3 - 验证 Review（使用推理模型）：
模型：anthropic/claude-opus-4-5
任务：代码审查、边界条件检查、安全审计
命令：/model anthropic/claude-opus-4-5

约束：
- 每个阶段开始前明确切换模型。
- 阶段之间保存上下文，不要丢失已收集的信息。
- 如果当前模型无法胜任某阶段任务，及时切换并说明原因。
```

### 使用要点

- **模型特性匹配**：不同模型适合不同任务。Opus/GPT-5.1-Codex 擅长深度推理和复杂分析，Sonnet/DeepSeek-Coder 擅长快速编码实现。合理路由可兼顾质量与效率
- **动态切换**：OpenCode v1.15.13 的 `/models` 命令支持在会话中实时切换模型，无需重启。`/model status` 可查看当前模型详情
- **上下文保持**：模型切换不会丢失会话上下文，但不同模型的上下文窗口和注意力机制可能不同，重要信息建议显式总结
- **成本考量**：Opus 级别的模型调用成本显著高于 Sonnet/Haiku 级别，对于大批量文件操作或长对话，使用 Sonnet 更经济

---

## 10.7 环境变量与临时配置模板（v1.15.13 新增）

**使用场景**：CI/CD 环境、临时测试或需要完全隔离配置的场景。

```markdown
请使用临时配置执行以下任务，确保不影响现有配置。

要求：
1. 使用 OPENCODE_CONFIG_CONTENT 传入内联配置（最高优先级）。
2. 禁用全局配置加载：OPENCODE_DISABLE_GLOBAL_CONFIG=1。
3. 禁用项目配置加载：OPENCODE_DISABLE_PROJECT_CONFIG=1（可选，如需要完全隔离）。
4. 禁止从父目录继承配置：OPENCODE_NO_PARENT_CONFIG=1（可选）。

示例配置内容：
{
  "model": "anthropic/claude-sonnet-4-5",
  "permission": {
    "edit": "allow",
    "bash": "ask"
  }
}

执行命令格式：
OPENCODE_DISABLE_GLOBAL_CONFIG=1 \
OPENCODE_CONFIG_CONTENT='{"model":"anthropic/claude-sonnet-4-5","permission":{"edit":"allow","bash":"ask"}}' \
opencode run "<任务描述>"
```

### 使用要点

- **完全隔离**：通过 `OPENCODE_DISABLE_GLOBAL_CONFIG=1` + `OPENCODE_CONFIG_CONTENT` 可实现配置完全隔离，适用于 CI/CD 环境和自动化脚本
- **优先级保证**：v1.15.13 修复了 `OPENCODE_CONFIG_CONTENT` 的优先级问题（[Issue #11628](https://github.com/anomalyco/opencode/issues/11628)），确保内联配置确实具有最高用户优先级
- **敏感信息安全**：在 CI 环境中，将 API Key 通过环境变量传入（如 `ANTHROPIC_API_KEY`），不要在 `OPENCODE_CONFIG_CONTENT` 中硬编码
- **JSON 转义**：`OPENCODE_CONFIG_CONTENT` 的值是 JSON 字符串，注意转义引号。对于复杂配置，建议先用 `opencode.json` 文件测试，再压缩为单行

---

## 10.8 模板组合实战：完整工作流示例

以下是一个完整的 Plan → Explore → Build → Verify → Review 工作流，展示了如何在实际项目中组合使用上述模板。

### 步骤 1：Plan（计划）

```markdown
我要为项目添加一个 Redis 缓存层，用于缓存用户会话数据。

请帮我制定实施计划：
1. 需要修改哪些文件
2. 缓存策略（TTL、Key 格式、序列化方式）
3. 错误处理（Redis 不可用时的降级策略）
4. 测试策略

先不要写代码，先输出计划让我确认。
```

### 步骤 2：Explore（探索 —— 使用 10.1 模板）

```markdown
请只读探索，不要修改文件，不要运行会改变状态的命令。
目标：找到当前项目的会话管理模块，理解现有的 Session Store 接口和数据流。

请输出：
1. 相关入口文件
2. 调用链
3. 数据结构 / API / 配置位置
4. 需要验证的假设
5. 建议的最小修改方案
```

### 步骤 3：Build（实现 —— 使用 10.2 模板）

```markdown
请按已确认方案做最小实现。
约束：
- 不要提交代码。
- 不要运行 pkill/killall/taskkill/rm -rf/git reset/git clean。
- 不要启动长时间后台服务。
- 优先 edit/apply_patch，不要整体 rewrite 大文件。
- 修改完成后先给出 diff 摘要，再运行最小相关测试。
```

### 步骤 4：Verify（验证 —— 使用 10.3 模板）

```markdown
请验证本次改动。
步骤：
1. 先看 git diff --stat 和 git diff。
2. 运行最小相关测试。
3. 如果最小测试通过，再运行 typecheck/lint。
4. 如果失败，先解释失败，不要扩大修改面。
5. 最后输出已验证项、未验证项和风险。
```

### 步骤 5：Review（审查 —— 使用 10.4 模板）

```markdown
请以代码审查者身份审查本次 diff，不要修改文件。
重点看：
1. 正确性
2. 边界条件
3. 并发/幂等/事务风险
4. 安全风险
5. 测试覆盖
6. 是否有无关改动
```

---

## 10.9 模板定制建议

以上模板是通用基础版本，建议根据团队实际情况进行定制：

| 定制方向 | 建议 |
|---------|------|
| **技术栈适配** | 将 `typecheck/lint` 替换为团队实际使用的工具（如 `go test`、`pytest`、`cargo check`） |
| **权限策略** | 根据团队安全要求调整权限约束的严格程度 |
| **测试策略** | 补充团队特有的测试要求（如覆盖率阈值、E2E 测试） |
| **代码规范** | 在 Review 模板中增加团队编码规范的检查项 |
| **模型偏好** | 根据成本预算和模型可用性调整模型切换策略 |

---

## 10.10 常见错误与规避

| 错误模式 | 后果 | 规避方法 |
|---------|------|---------|
| 探索阶段未加"只读"约束 | Agent 误修改文件 | 模板 10.1 开头必须包含"只读探索，不要修改文件" |
| 实现阶段未禁止 destructive 命令 | 数据丢失或环境破坏 | 模板 10.2 中明确列出禁止的命令清单 |
| 验证阶段未要求 diff 优先 | 变更不可见，难以审查 | 模板 10.3 第一步要求 `git diff --stat` |
| Review 阶段 Agent 主动修改代码 | Review 结果不可复现 | 模板 10.4 开头强调"不要修改文件" |
| 配置修改未区分全局/项目级 | 影响其他项目 | 模板 10.5 要求优先编辑项目级配置 |

---

## 参考来源

- OpenCode 官方文档：Commands、Config、Models、Agents
- [anomalyco/opencode GitHub Issues](https://github.com/anomalyco/opencode/issues) — Issue #9082 (destructive commands)、Issue #11628 (OPENCODE_CONFIG_CONTENT 优先级修复)
- OpenCode v1.15.13 Changelog — `/models` 命令增强、权限系统改进
- [OpenCode 配置系统官方文档](https://open-code.ai/en/docs/config)
- [OpenCode 模型配置文档](https://opencode.ai/docs/models/)
