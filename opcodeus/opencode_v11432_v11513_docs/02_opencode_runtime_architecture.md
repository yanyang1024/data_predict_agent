# 02. OpenCode Runtime 架构视角

> 适用版本：`v1.14.32` / `v1.15.13`。  
> 本文以官方文档公开能力为主，辅以源码模块名称帮助理解。内部源码目录可能变动，教学时不要把内部路径当成稳定 API。

## 1. Agent 抽象的六个槽位

| Agent 抽象 | 研发语义 | OpenCode 对应能力 / 模块 |
|---|---|---|
| Goal 目标 | 这次要修什么、验收标准是什么 | 用户 prompt、自定义 command、`AGENTS.md`、`instructions` |
| State 状态 | 当前会话、消息、todo、打开过的上下文、快照 | session/message/todo/summary/snapshot 相关模块 |
| Actions 动作空间 | 能读、搜、改、跑、查文档、问问题、加载 skill | 内置工具、自定义 tools、MCP、plugins |
| Observations 观察 | 命令输出、测试失败、文件内容、LSP 结果 | tool output、truncation、message parts |
| Policy 策略 | 用哪个 agent、哪个模型、是否能改代码 | `agent`、`permission`、`model`、provider policy |
| Runtime 运行时 | 调度、权限、回滚、压缩、扩展、服务化 | session processor、permission、snapshot、compaction、server |

## 2. session：Agent loop 的主控层

`session` 可以看作 OpenCode 的会话大脑，负责：

- 构造系统提示、规则、agent 配置、provider/model 配置；
- 接收 LLM 流式输出；
- 解析 tool call；
- 执行权限判断；
- 记录 tool result；
- 处理长上下文压缩；
- 维护 snapshot / undo / redo 需要的状态。

简化执行流：

```text
用户输入
  -> 创建 session message
  -> 构造 system prompt / instructions / agent config
  -> 调用 LLM
  -> LLM 输出文本或 tool call
  -> 记录 tool call 状态
  -> permission 判断 allow / ask / deny
  -> tool 执行并返回 observation
  -> LLM 基于 observation 继续
  -> 生成最终答复
  -> snapshot / summary / todo / status 更新
```

## 3. tool：Agent 的“手”和“眼”

按官方 Tools 文档，v1.14.32/v1.15.13 教程中建议稳定使用这些工具名：

| 类别 | 工具 |
|---|---|
| 观察类 | `read`、`grep`、`glob`、`lsp`（实验性） |
| 修改类 | `edit`、`write`、`apply_patch` |
| 执行类 | `bash` |
| 编排/交互类 | `skill`、`todowrite`、`question` |
| 外部信息类 | `webfetch`、`websearch` |
| 扩展类 | custom tools、MCP tools、plugin tools |

注意：

- `write` 会创建新文件或覆盖已有文件，并且受 `edit` 权限控制。
- `edit` 是更安全的修改方式，因为它强调精确替换。
- `bash` 能运行任意 shell 命令，是最高风险工具之一。
- `lsp` 在文档中被标注为实验性能力，团队模板里建议默认 `ask` 或先禁用。
- `grep` / `glob` 底层会受 ignore 规则影响；如果生成目录、fixtures、dist 被 `.gitignore` 排除，agent 可能搜不到。

## 4. permission：把自治变成可控

OpenCode 的 permission 决定一个动作是：

```text
allow -> 直接运行
ask   -> 先问用户
deny  -> 阻止
```

团队落地时，permission 是最重要的安全阀。尤其要控制：

- `bash`
- `edit`
- `write` / `apply_patch`，它们受 `edit` 权限覆盖
- `external_directory`
- `doom_loop`
- `skill`
- `webfetch` / `websearch`
- MCP 工具
- 自定义工具

权限对象支持按输入内容细分，并且“最后匹配规则优先”。所以推荐模板里把 `"*"` 放在前面，把更具体规则放在后面。

## 5. agent：不同角色的策略封装

OpenCode 支持 primary agent 与 subagent。primary agent 可通过 Tab 或 keybind 切换，subagent 可以由 primary agent 自动调用，也可以用 `@name` 手动提及。

推荐研发团队这样映射角色：

| Agent | 建议角色 | 是否允许改代码 |
|---|---|---|
| `plan` | 需求澄清、方案设计、风险分析 | 否 |
| `explore` | 只读代码探索、定位入口 | 否 |
| `scout` | 查外部依赖、上游实现、文档 | 否 |
| `build` | 最小实现、补测试、跑验证 | 是，但需权限控制 |
| `review` 自定义 | 安全、正确性、测试覆盖审查 | 否 |

## 6. snapshot 与 `/undo`：方便但不能替代 Git

OpenCode 有 snapshot / undo / redo 能力，用于跟踪 agent 操作期间的文件变化。官方配置中 snapshot 默认启用；但在大仓库、多 submodule、生成目录多的项目中，snapshot 可能造成慢索引和较高磁盘占用。

正确姿势：

```text
Git checkpoint 是主保险
OpenCode /undo 是辅助保险
```

尤其在多轮修改、子代理、长命令、跨平台文件系统、Windows 保留文件名、snapshot lock 异常等场景下，必须用 Git 自己做明确 checkpoint。

## 7. compaction：长会话不是无限上下文

长会话会增长上下文。OpenCode 提供 `compaction` 配置，默认会在上下文接近满时自动压缩。团队使用时需要理解：

- 压缩是必要的，但它可能丢失细节。
- 长会话越久，模型越容易出现“上下文错位、重复工具调用、忘记约束”。
- 对复杂任务，建议按阶段开新 session：探索、实现、验证、review 分开。
- 对关键结论，要求 agent 输出阶段性摘要并写入人工可读文件，而不是只依赖聊天历史。

## 8. 可以公开讲，不能过度承诺的源码细节

可以在教程里讲这些“工程概念”：

- session processor 负责 agent loop；
- tool registry 负责加载内置工具、自定义工具、MCP/plugin 工具；
- permission gate 负责 allow/ask/deny；
- snapshot 负责会话级 undo/redo；
- config loader 会合并远程、全局、项目、`.opencode/` 等配置层；
- provider/model 配置会决定可用模型、上下文限制、输出限制。

不建议把以下内容写成稳定 API：

- 某个内部 TypeScript 文件名一定存在；
- 某个未在官方 Tools 文档中出现的 tool 一定可用；
- 某个内部阈值（例如 doom loop 次数）在后续版本不会变；
- 某个 issue 里提到的 bug 在所有平台必然复现。
