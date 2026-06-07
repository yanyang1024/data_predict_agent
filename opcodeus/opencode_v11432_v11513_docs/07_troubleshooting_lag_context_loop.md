# 07. 卡顿、上下文混乱、thinking 异常与工具死循环

> 适用版本：`v1.14.32` / `v1.15.13`。  
> 本文回答用户提出的两个重点问题：OpenCode 在 VSCode 服务器/终端里很卡；模型上下文混乱、thinking 出现用户没输入的话、工具调用死循环。

## 1. VSCode 打开服务器后，终端使用 OpenCode 很卡

### 1.1 常见诱因

| 类别 | 诱因 | 解释 |
|---|---|---|
| 终端渲染 | VSCode/Cursor 集成终端、xterm.js、长输出、长会话 | 大量流式文本和 tool output 会让终端渲染变慢 |
| WSL/远程 | WSL2、VSCode Server、远程文件系统、Windows VM | 文件 IO、PTY、渲染层叠加，容易放大延迟 |
| 大仓库 | snapshot、watcher、LSP、node_modules、dist、submodule | OpenCode 需要跟踪/索引/观察文件变化 |
| 长命令 | 后台 dev server、测试输出过长、日志不截断 | bash tool 可能持续输出，TUI 持续重绘 |
| MCP/插件 | 启用大量 MCP 或 plugin | 工具描述和执行结果占上下文，插件也可能拖慢启动 |
| 长会话 | 几百条消息、大量工具结果、上下文压缩 | 内存、渲染、模型请求都变重 |

### 1.2 优先排查顺序

#### Step 1：换终端验证

如果在 VSCode/Cursor 集成终端卡，先试：

```text
Windows Terminal / WezTerm / Alacritty / Ghostty / iTerm2 / 原生终端
```

如果原生终端不卡，问题多半在 VSCode 集成终端渲染或远程终端层。

#### Step 2：缩小工作目录

不要在巨型 monorepo 根随便启动：

```bash
cd packages/etch-service
opencode
```

或者用 worktree/子仓库切分任务。

#### Step 3：减少 watcher 噪音

`opencode.jsonc`：

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "watcher": {
    "ignore": [
      "node_modules/**",
      "dist/**",
      "build/**",
      ".git/**",
      "coverage/**",
      ".next/**",
      ".turbo/**",
      "target/**",
      "logs/**"
    ]
  }
}
```

#### Step 4：大仓库临时关闭 snapshot

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "snapshot": false
}
```

注意：关闭 snapshot 后，OpenCode 的 undo/revert 不再能回滚文件变化。必须用 Git checkpoint 兜底。

#### Step 5：不要让 agent 启动长跑服务

长跑服务放外部终端：

```bash
pnpm dev
```

OpenCode 内只让 agent 跑短命令：

```bash
pnpm test <file>
pnpm typecheck
git diff
```

#### Step 6：限制 tool output

`v1.14.32/v1.15.13` 源码配置里已有 `tool_output.max_lines` / `max_bytes` 相关字段。可以考虑：

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "tool_output": {
    "max_lines": 800,
    "max_bytes": 30000
  }
}
```

不要让 agent 直接 `cat` 大日志；改用：

```bash
tail -n 200 logs/app.log
rg "ERROR|WARN" logs/app.log | head -n 100
```

#### Step 7：禁用暂不需要的 LSP/MCP/插件

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "lsp": false,
  "mcp": {},
  "plugin": []
}
```

若是 Desktop 或 IDE 集成异常，先按官方 troubleshooting：看日志、禁用插件、清 cache。

#### Step 8：开新 session

长会话卡顿时，不要硬撑：

1. 让 agent 输出阶段摘要；
2. 人类复制摘要到新 session；
3. 新 session 只带当前阶段必要文件和目标。

示例：

```text
请输出一个可复制到新 session 的交接摘要：任务目标、已确认事实、已修改文件、未完成事项、下一步验证命令。不要继续调用工具。
```

## 2. thinking 里出现用户没有输入的交互语句

### 2.1 先区分几类现象

| 现象 | 可能原因 |
|---|---|
| thinking 中出现“用户说……”但你没说过 | 模型自行模拟对话、长上下文摘要混入、命令模板/规则文件里有示例对话 |
| thinking 中出现 `<think>` 标签原文 | 模型/自定义 provider 没有把 reasoning block 正确映射为平台可识别结构 |
| 模型引用了旧任务内容 | 长会话上下文残留、compaction 摘要保留旧目标、没有开新 session |
| 工具调用结果像用户消息 | 某些 provider/代理会把 tool result 转成 user role 或 synthetic user message |
| 子代理结果污染主会话 | subagent 摘要或返回内容被主 agent 当作用户约束 |
| 模型开始执行不存在的用户确认 | 模型遵循了 AGENTS.md / command / skill 里的示例，而不是当前用户输入 |

### 2.2 这不一定意味着“串号”

很多 LLM 会在 reasoning 中生成“假想对话”或“下一步我应该问用户”这类文本。尤其是：

- 本地模型；
- OpenAI-compatible 私有网关；
- chat template 不成熟的模型；
- `<think>` 标签模型；
- 工具调用能力弱的模型；
- 历史 tool result 很多的长会话。

更可靠的判断标准：

1. final answer 是否真的执行了错误目标；
2. tool call 是否访问了不相关文件；
3. 当前上下文是否有旧任务摘要；
4. `AGENTS.md`、commands、skills 中是否有示例对话；
5. provider 请求日志里是否真的送入了异常消息。

## 3. 模型陷入工具交互死循环

### 3.1 常见触发

| 触发 | 表现 |
|---|---|
| 模型工具调用能力弱 | 反复用同一参数调用同一工具 |
| 工具返回太长/被截断 | 模型看不到关键信息，继续重试 |
| 文件路径错误 | `read` / `bash` 找不到文件，模型反复猜路径 |
| 权限 ask/deny 后模型没调整计划 | 被拒绝后继续尝试同一动作 |
| 长会话上下文矛盾 | 模型同时遵循新旧目标 |
| 本地模型上下文过小 | 工具协议或系统提示被挤出上下文 |
| MCP schema 不兼容 | 模型反复给出不合法参数 |

### 3.2 处理方式

#### 立即止损

```text
按 Esc / 中止当前请求
```

然后输入：

```text
停止调用工具。请先总结你刚才重复调用的工具、参数、失败原因，并提出一个不再重复的下一步计划。不要继续执行工具。
```

#### 强制路径自检

```text
你刚才可能路径基准错误。不要继续读取文件。
请先说明：
1. 当前工作目录是什么
2. git worktree 根是什么
3. 目标文件应相对哪个目录
4. 下一次只允许调用一次 read/grep
```

#### 压缩或开新 session

```text
请输出当前任务的最小上下文摘要，用于新 session 继续。不要调用工具。
```

#### 降低工具复杂度

- 暂时禁用 MCP；
- 禁用 websearch；
- 用 `plan` 只读；
- 限制一次只读一个目录；
- 给出明确文件路径。

#### 换模型

对 coding agent 来说，工具调用能力比纯聊天能力更重要。若某模型频繁：

- 传错 JSON schema；
- 调不存在工具；
- 反复调用同一工具；
- 把 tool result 当用户消息；
- `<think>` 标签泄漏到正文；

就不要把它作为 Build 默认模型。可把它降级用于纯 review/总结，或仅作为 Scout/Plan。

## 4. 长会话上下文治理

### 4.1 使用 compaction

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "compaction": {
    "auto": true,
    "prune": true,
    "reserved": 10000
  }
}
```

注意：压缩不是万能的。压缩后如果模型开始忘记约束，直接开新 session。

### 4.2 分阶段 session

推荐分为：

```text
Session A: 只读探索
Session B: 最小实现
Session C: 验证修复
Session D: Review diff
```

每个 session 开始时只带必要上下文。

### 4.3 上下文清洁提示

```text
忽略本 session 中与当前任务无关的旧讨论。
当前任务唯一目标是：<目标>。
当前允许修改的文件范围是：<路径>。
如果你发现上下文中有冲突指令，请列出来，不要自行选择。
```

## 5. Provider / 模型配置导致的问题

### 5.1 DeepSeek / reasoning_content 类问题

有些 provider 对 reasoning_content 的历史携带有严格要求。如果历史 reasoning 被重复拼进后续 turns，可能导致：

- token 增长；
- 成本变高；
- 响应变慢；
- thinking 里出现旧内容；
- 工具调用异常。

处理方式：

- 升级到已修复版本；
- 换 provider adapter；
- 禁用或降低 thinking；
- 开新 session；
- 对私有网关确认其消息格式转换逻辑。

### 5.2 OpenAI-compatible 本地模型

本地模型最常见问题：

- tool call JSON 不合法；
- `tool_use` / `tool_result` 格式不兼容；
- context 太小；
- chat template 不支持 OpenCode 的系统提示和工具协议；
- 输出 `<think>`，但 OpenCode/adapter 不把它识别成 reasoning block。

建议：

1. 从简单任务测试：`read test.txt`。
2. 再测试 `grep`。
3. 再测试 `edit`。
4. 再测试小范围 `bash`。
5. 通过后才作为 Build 模型。

## 6. 日志与 cache 排查

日志位置：

```text
macOS/Linux: ~/.local/share/opencode/log/
Windows: %USERPROFILE%\.local\share\opencode\log
```

提高日志：

```bash
opencode --log-level DEBUG
```

应用数据：

```text
macOS/Linux: ~/.local/share/opencode/
Windows: %USERPROFILE%\.local\share\opencode
```

provider package cache：

```text
~/.cache/opencode
```

如果 provider API 参数异常、模型包缓存异常，可退出 OpenCode 后清理 cache，再重启。

## 7. 针对“VSCode + 服务器 + OpenCode 卡顿”的推荐配置

项目 `opencode.jsonc`：

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "snapshot": false,
  "lsp": false,
  "watcher": {
    "ignore": [
      "node_modules/**",
      "dist/**",
      "build/**",
      ".git/**",
      "coverage/**",
      ".next/**",
      ".turbo/**",
      "target/**",
      "logs/**"
    ]
  },
  "tool_output": {
    "max_lines": 800,
    "max_bytes": 30000
  },
  "permission": {
    "bash": {
      "*": "ask",
      "git diff*": "allow",
      "git status*": "allow",
      "rg *": "allow",
      "cat logs/*": "deny",
      "tail -n *": "allow"
    }
  }
}
```

只在 Git checkpoint 完整时关闭 snapshot。

## 8. 故障处理速查

| 现象 | 立即处理 | 后续治理 |
|---|---|---|
| TUI 输入延迟 | 换原生终端、开新 session | watcher ignore、减少长输出、关闭不必要 LSP/MCP |
| 大量磁盘 IO | 检查 snapshot、大仓库、生成目录 | 缩小工作目录、Git checkpoint 后 `snapshot:false` |
| thinking 有奇怪用户话语 | 停止工具，要求复述当前任务 | 开新 session、检查 commands/skills/AGENTS 示例 |
| 工具死循环 | Esc 中止，要求总结重复原因 | 限制工具、换模型、减少上下文 |
| 模型调不存在工具 | 检查模型/tool prompt 兼容 | 换更可靠模型；不要用弱工具模型做 Build |
| 自定义 tool 找不到脚本 | 打印 `context.worktree`/`context.directory` | 所有脚本路径以 worktree 绝对拼接 |
| provider API error | 看日志、清 cache | 检查 provider npm 包、baseURL、模型 ID、limit |
