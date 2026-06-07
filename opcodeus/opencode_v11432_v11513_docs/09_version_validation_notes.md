# 09. v1.14.32 / v1.15.13 适用性核对与原文修订说明

> 核对日期：2026-06-07。  
> 核对对象：OpenCode `v1.14.32` 与 `v1.15.13` 官方 release、官方文档、对应源码标签。  
> 注意：OpenCode 迭代很快，后续版本应重新核对。

## 1. 版本 release 重点

### v1.14.32

Release 重点包括：

- shell mode 在 prompt 中保持可编辑，退格、光标移动等按键恢复；
- HTTP API workspace adapter 修复；
- experimental workspace 创建请求修复；
- OpenAPI 参数 schema 修复；
- unsupported image format fallback；
- agents 可使用全局临时目录而不额外弹 permission；
- 修复 Bedrock sessions 在切换模型时包含 reasoning content 的问题；
- session archive timestamp 校验。

这说明：

- 你的文档里提到“thinking / reasoning content 混乱”是合理关注点；
- 但应避免把它写成所有 provider 都会发生的必现 bug，而应写成“provider/model/adapter/长会话组合下可能出现”。

### v1.15.13

Release 重点包括：

- Gateway Anthropic Opus 4.7+ adaptive reasoning 保留 summarized thinking；
- Sessions API/SDK 支持 custom metadata；
- Config 从 opened location upward 加载，目录级设置和 provider policies 更可预测；
- TUI inline tool 行对齐和失败详情展开修复。

这说明：

- 配置层级章节必须补充 v1.15.13 的“从打开位置向上加载”变化；
- 原文中只说“项目根配置”不够，应解释“从当前工作目录向上到 worktree”的发现逻辑。

## 2. 配置文件核对

### 2.1 官方主推

官方文档主推：

```text
opencode.json
opencode.jsonc
~/.config/opencode/opencode.json
~/.config/opencode/opencode.jsonc
```

### 2.2 源码兼容

v1.14.32 与 v1.15.13 源码均显示全局配置会加载：

```text
~/.config/opencode/config.json
~/.config/opencode/opencode.json
~/.config/opencode/opencode.jsonc
```

并且 `globalConfigFile()` 会优先寻找：

```text
opencode.jsonc -> opencode.json -> config.json
```

因此文档建议：

- 新教程统一写 `opencode.jsonc` 或 `opencode.json`；
- `config.json` 只作为兼容说明，不作为推荐文件名；
- 不要让团队同时维护多个主配置文件。

## 3. 配置加载与合并核对

官方文档说明配置是合并而非替换，后加载配置覆盖冲突键。源码也可看到 merge 逻辑。

应补充：

- `instructions` 在源码中存在数组合并去重逻辑；
- `.opencode/` 目录中的 `agents/commands/plugins/skills/tools` 会被加载；
- `.opencode/opencode.json` 与 `.opencode/opencode.jsonc` 在源码中也会被尝试加载；
- `OPENCODE_CONFIG`、`OPENCODE_CONFIG_CONTENT`、`OPENCODE_CONFIG_DIR` 都会影响加载；
- 管理员/MDM 配置优先级最高，不适合普通项目教程作为主要路径讲。

## 4. Tools 列表核对

原文工具列表：

```text
read、grep、glob、lsp、webfetch、websearch
edit、write、apply_patch
shell / bash
task、skill、todo、question
repo_clone、repo_overview
```

建议修订为：

```text
bash、edit、write、read、grep、glob、lsp（experimental）、apply_patch、skill、todowrite、webfetch、websearch、question
custom tools
MCP tools
plugin tools
```

修订理由：

- 官方 Tools 文档中写的是 `bash`，不是 `shell`；
- 官方 Tools 文档中写的是 `todowrite`，不是简单 `todo`；
- 官方 Tools 文档中没有稳定列出 `task`、`repo_clone`、`repo_overview`；
- 子代理调用应按 Agents 文档描述：自动调用或 `@subagent` 手动调用。

## 5. Skills 核对

原文需要补充：

```text
.opencode/skills/<name>/SKILL.md
~/.config/opencode/skills/<name>/SKILL.md
.claude/skills/<name>/SKILL.md
~/.claude/skills/<name>/SKILL.md
.agents/skills/<name>/SKILL.md
~/.agents/skills/<name>/SKILL.md
```

并补充：

- `SKILL.md` 必须有 frontmatter；
- `name` 和目录名一致；
- `description` 是 agent 选择 skill 的关键信号；
- skill 权限可通过 `permission.skill` 控制；
- per-agent 可以覆盖 skill 权限。

## 6. Custom Tools 路径核对

官方 Custom Tools 文档要点：

- custom tool 定义文件是 TypeScript/JavaScript；
- 放在项目 `.opencode/tools/` 或全局 `~/.config/opencode/tools/`；
- tool 可以调用任意语言脚本；
- 文件名决定 tool 名；
- 多 export 生成 `<filename>_<exportname>`；
- custom tool 与内置工具重名会覆盖内置工具；
- `context.directory` 表示 session working directory；
- `context.worktree` 表示 git worktree root。

因此必须在文档里强调：

> 自定义 tool 调项目脚本时，用 `context.worktree` 拼路径，不要依赖当前 shell 目录。

## 7. Commands 核对

官方 Commands 文档要点：

- command 可由 `opencode.json` 的 `command` 字段配置；
- 也可放在 `.opencode/commands/*.md` 或 `~/.config/opencode/commands/*.md`；
- 支持 `$ARGUMENTS`、`$1`、`$2`；
- 支持 `!\`command\`` 注入 shell 输出；
- 支持 `@file` 注入文件内容；
- command 可配置 `agent`、`subtask`、`model`。

原文应补充 command 级模型选择和 `!` shell 注入风险。

## 8. Permissions 核对

原文中“后匹配规则优先”正确。应补充：

- v1.1.1 后 legacy `tools` boolean config 已合并到 `permission`，旧写法还兼容但不推荐；
- `write` 受 `edit` permission 控制；
- `external_directory` 控制工作目录外路径访问；
- `skill` 有专门 pattern 权限；
- MCP 工具可用 wildcard 统一控制。

## 9. Snapshot / undo 核对

原文“Git checkpoint 是主保险，OpenCode `/undo` 是辅助保险”方向正确。应补充：

- 官方 config 里 snapshot 默认启用；
- 大仓库或多 submodule 场景可能导致慢索引和磁盘占用；
- 可以用 `"snapshot": false` 关闭，但关闭后 undo/revert 不再能回滚文件变化；
- 团队文档里不应把 `/undo` 描述成可靠替代 Git。

## 10. 卡顿问题核对

原文需要新增章节。基于官方 troubleshooting 和 GitHub issues，常见来源包括：

- VSCode/Cursor 集成终端在 WSL2 下长输出滚动严重卡顿；
- 长 session streaming 期间 TUI 渲染高 CPU；
- WSL + VSCode + OpenCode 同时运行可能触发大量磁盘 IO；
- snapshot 在大仓库中可能慢；
- watcher、LSP、MCP、插件会增加负载；
- provider package/cache 问题可通过查看日志和清 cache 排查。

建议文档补充治理方案：

- 换原生终端；
- 缩小工作目录；
- watcher ignore；
- Git checkpoint 后考虑 `snapshot:false`；
- 限制 tool output；
- 避免在 agent 内跑 dev server；
- 禁用不必要 LSP/MCP/plugins；
- 长会话输出摘要后开新 session。

## 11. 上下文混乱与工具死循环核对

原文需要新增章节。建议写成“可能原因与排查路径”，不要直接断言 OpenCode 必然串上下文。

常见原因：

- 模型自行模拟对话；
- thinking / reasoning block 映射不兼容；
- provider 把 tool result 转成 synthetic user message；
- DeepSeek 等 reasoning_content 历史携带问题；
- 命令模板、AGENTS.md、skill 里有示例对话；
- 长会话压缩/截断；
- 本地模型工具调用能力弱；
- MCP schema 或 tool 参数不兼容；
- 路径错误导致重复读/搜。

建议补充处理模板：

```text
停止调用工具。请总结刚才重复调用的工具、参数、失败原因，并提出一个不再重复的下一步计划。
```

## 12. 原文中建议保留的内容

以下内容方向正确，建议保留并扩写：

- “Agent 不是模型，而是运行时中的决策循环”；
- “查、改、跑、验、审、回滚”比“写代码”更重要；
- Plan / Explore / Review 优先，Build 受控；
- Git checkpoint；
- 禁止广义 kill / destructive git / `rm -rf`；
- `write` 会覆盖文件；
- MCP / Web 工具会膨胀上下文；
- `.gitignore` 会影响 grep/glob。

## 13. 原文中建议修正或降级的内容

| 原文内容 | 建议修正 |
|---|---|
| `list` 工具 | 不作为稳定内置工具写入，改用 `glob` / `bash ls` |
| `task` 工具 | 改写为 subagent 自动/手动调用机制 |
| `todo` 工具 | 写成 `todowrite` |
| `shell / bash` | 统一写 `bash` |
| `repo_clone` / `repo_overview` | 降级为“可能存在的内部/实验/插件能力”，不写入稳定工具表 |
| `config.json` 主推 | 改为 `opencode.jsonc` / `opencode.json` 主推，`config.json` 作为兼容说明 |
| 直接在 skill 里说“运行 scripts/foo.py” | 改成明确“相对 git worktree 根路径”或封装为 custom tool |
| `/undo` 可回滚 | 改为“会话级便利回滚，不能替代 Git” |

## 14. 后续维护建议

OpenCode 版本迭代很快。后续每次升级教程时，至少核对：

```text
opencode --version
opencode.ai/docs/config
opencode.ai/docs/providers
opencode.ai/docs/models
opencode.ai/docs/agents
opencode.ai/docs/tools
opencode.ai/docs/custom-tools
opencode.ai/docs/skills
opencode.ai/docs/permissions
opencode.ai/docs/commands
GitHub release notes
```

如果团队固定版本，建议在文档头部写：

```markdown
本文档只保证适用于 OpenCode v1.14.32 / v1.15.13；升级到其他版本前必须重新核对配置路径、工具名和 permission 行为。
```
