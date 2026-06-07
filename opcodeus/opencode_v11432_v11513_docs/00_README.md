# OpenCode v1.14.32 / v1.15.13 工程实践教程文档集

> 适用版本：OpenCode `v1.14.32` 与 `v1.15.13`。
> 本文档集由原始长文拆分、核对并补充而来，重点从“coding agent 原理”过渡到“OpenCode 可配置、可治理、可排错的本地研发运行时”。

## 文档结构

| 文件 | 主题 |
|---|---|
| `01_agent_evolution.md` | 从 ReAct / Tool Calling / SWE-agent 到 OpenCode 的技术演进主线 |
| `02_opencode_runtime_architecture.md` | OpenCode 的 session、tool、permission、agent、snapshot 等模块视角 |
| `03_config_hierarchy_and_models.md` | 全局配置、项目配置、配置优先级、模型选择、API Key、私有部署模型 |
| `04_tools_skills_commands_and_paths.md` | tools、skills、commands、scripts 的目录、引用方式与路径坑 |
| `05_permissions_and_safety_baseline.md` | 权限系统、团队安全基线、破坏性命令治理 |
| `06_sop_workflow.md` | 面向研发人员的 OpenCode 使用 SOP |
| `07_troubleshooting_lag_context_loop.md` | 卡顿、上下文混乱、thinking 异常、工具死循环、长会话治理 |
| `08_practical_tips_and_prompts.md` | 常用技巧、Prompt 模板、Review 模板 |
| `09_version_validation_notes.md` | v1.14.32 / v1.15.13 适用性核对、原文修订说明 |
| `templates/AGENTS.md` | 推荐项目规则模板 |
| `templates/global-opencode.jsonc` | 推荐全局配置模板 |
| `templates/project-opencode.jsonc` | 推荐项目配置模板 |
| `examples/skill-tool-path-example.md` | skill + tool + script 路径引用示例 |

## 重要结论

1. 教程应统一以 `opencode.json` / `opencode.jsonc` 为主配置文件名；`config.json` 在 v1.14.32 与 v1.15.13 源码里仍有兼容加载，但不建议新文档继续主推。
2. 全局配置主要放在 `~/.config/opencode/opencode.jsonc` 或 `~/.config/opencode/opencode.json`；项目配置主要放在项目根目录 `opencode.json` / `opencode.jsonc`，并可配合 `.opencode/` 目录承载 agents、commands、skills、tools、plugins。
3. 模型选择格式统一为 `<provider_id>/<model_id>`。CLI `--model/-m` 优先级最高，其次是配置里的 `model`，最后才是上次使用的模型。
4. API Key 推荐通过 `/connect` 写入 `~/.local/share/opencode/auth.json`，或者在配置中使用 `{env:XXX_API_KEY}` / `{file:~/.secrets/key}`，不要把明文密钥提交进项目仓库。
5. agent 调用脚本时，路径不要依赖“当前 shell 碰巧在哪”。自定义 tool 里应优先使用 `context.worktree` 作为仓库根，`context.directory` 作为当前会话工作目录。
6. VSCode/Cursor 集成终端、WSL、长会话、大输出、snapshot、watcher、LSP、MCP 都可能导致卡顿；治理思路是缩小工作目录、减少长输出、开新 session、控制 watcher/snapshot/LSP/MCP。
7. “thinking 里出现用户没说过的话”不一定是 OpenCode 把别人的消息串进来了，更常见原因是：模型把推理标签当普通文本、历史 reasoning_content 被重复送入上下文、长会话压缩/截断造成语义错位、自定义 provider/chat template 不兼容、命令模板或子任务上下文污染。
8. OpenCode 的 `/undo` 是会话级便利回滚，不能替代 Git checkpoint。

## 参考来源快照

- OpenCode 官方文档：Config、Providers、Models、Agents、Tools、Custom Tools、Skills、Commands、Permissions、Rules、Troubleshooting。
- OpenCode GitHub release：`v1.14.32` 与 `v1.15.13`。
- OpenCode 对应版本源码：`packages/opencode/src/config/config.ts`。
- 若你在团队内发放此文档，建议在文档头部写明“已按 2026-06-07 官方文档与 v1.14.32/v1.15.13 标签核对”。
