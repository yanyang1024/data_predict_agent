# 6. 常见坑与解决方案

---

## 6.1 坑一：`pkill -f` 可能误杀 OpenCode 或导致工具调用挂住

### 现象

```bash
pkill -f vim 2>/dev/null; echo "killed"
```

在 TUI 中可能挂住直到超时；在 CLI 中可能导致 `opencode run` 自己被终止。根因通常是 `pkill -f` 按完整命令行匹配，可能匹配到 OpenCode 自身或它的子进程。

### 治理方式

1. **不要让 agent 执行 `pkill -f`。** 在 permission 中直接 `deny`：

```jsonc
"bash": {
  "*": "ask",
  "pkill *": "deny",
  "killall *": "deny",
  "taskkill *": "ask",
  "kill *": "ask"
}
```

2. 需要杀进程时，让人类在 OpenCode 外部终端确认：

```bash
pgrep -af '<process-name-or-port>'
# 确认 PID 后再 kill 指定 PID
kill <PID>
```

3. 优先按端口或 PID 文件管理开发服务，而不是按进程名模糊杀：

```bash
# 示例：先查看占用端口的 PID
lsof -nP -iTCP:3000 -sTCP:LISTEN
# 人工确认后再 kill
kill <PID>
```

4. 在 prompt 中明确禁止：

```text
不要运行 pkill -f、killall、taskkill /IM node.exe 这类广义杀进程命令。
如果你认为需要停止进程，先列出 PID、端口、命令行，并等待我确认。
```

---

## 6.2 坑二：长时间后台命令导致 bash tool 挂起或残留进程

### 常见触发

```bash
npm run dev &
pnpm start &
```

问题在于后台进程可能继承 stdout / stderr / stdin，tool 以为命令还没结束；或者 OpenCode 退出时子进程未被正确清理。

### 治理方式

- 长跑服务放在单独终端或 tmux pane 中，由人类控制。
- 让 agent 只运行短命令：测试、lint、typecheck、grep、git diff。
- 如果必须临时启动服务，要求重定向并写 PID 文件，且由人类确认：

```bash
mkdir -p .opencode/runtime .opencode/logs
nohup pnpm dev > .opencode/logs/dev.log 2>&1 < /dev/null & echo $! > .opencode/runtime/dev.pid
```

停止时：

```bash
cat .opencode/runtime/dev.pid
kill <PID>
```

不要让 agent 自动执行上述停止命令，除非 permission 是 `ask` 且你确认 PID。

---

## 6.3 坑三：`/undo` 或 message revert 不一定等价于 Git 回滚

OpenCode 官方提供 `/undo` 和 `/redo`，但公开 issue 中已经出现过几类 snapshot / revert 问题：

- `git add .` 失败后 snapshot 可能复用旧 tree hash，导致 `/undo` 或 `/redo` 回到很久之前的内容。
- snapshot cache 中残留 `index.lock` 后，某个 workspace 的 Modified Files 和 undo/revert 行为异常。
- TUI 或桌面端 message revert 后文件仍保持修改状态。

### 治理方式

1. 每次让 agent 大改前，先建 Git checkpoint：

```bash
git status --short
git switch -c ai/<task>
git add -A
git commit -m "checkpoint: before opencode <task>"
```

如果不想提交：

```bash
git stash push -u -m "before opencode <task>"
```

2. 把 `/undo` 当作便利功能，而不是唯一保险。
3. 每轮后执行：

```bash
git diff --stat
git diff
```

4. 如果 OpenCode 不显示 Modified Files 或 undo 异常：

```text
先退出 OpenCode。
先备份工作区和 ~/.local/share/opencode/snapshot 相关目录。
再检查是否存在 snapshot cache 的 stale index.lock。
确认后再清理对应 workspace 的 snapshot cache。
```

5. Windows 项目中，禁止 agent 创建保留文件名：`nul`、`con`、`aux`、`prn`、`com1`-`com9`、`lpt1`-`lpt9`。

---

## 6.4 坑四：`write` 可能覆盖已有文件

`write` 的语义是创建新文件或覆盖已有文件，并由 `edit` 权限统一控制。团队更安全的做法是：

- 对大多数任务让 agent 使用 `edit` / `apply_patch`。
- prompt 中声明"不要整体重写大文件"。
- 对新文件创建要求 agent 先说明文件路径和原因。

---

## 6.5 坑五：MCP / Web 工具过多导致上下文膨胀

MCP 工具会占用上下文。团队落地时不要一次性启用大量 MCP：

- 默认关闭非必要 MCP。
- 按 agent 配置 MCP 权限。
- 文档查找优先用 Scout / webfetch，而不是把所有外部系统工具都塞进主 agent。

---

## 6.6 坑六：`.gitignore` 会影响 grep / glob / list 的搜索范围

OpenCode 底层搜索工具会受 `.gitignore` 影响。如果你希望 agent 搜索某些被忽略目录，例如生成代码、dist、build、某些 fixtures，可以在项目 `.ignore` 中显式放开：

```gitignore
!dist/
!build/
!fixtures/generated/
```

---

## 6.7 坑七：环境变量未正确传递给 OpenCode

### 现象

```text
用户在终端 export 了 ANTHROPIC_API_KEY，但 OpenCode 报错说找不到 API Key。
```

### 原因

OpenCode 启动时读取环境变量，如果在 OpenCode 运行后再 export，不会生效。或者通过桌面应用/TUI 启动时，没有继承 shell 的环境变量。

### 解决方案

```bash
# 方法 1：在 ~/.bashrc / ~/.zshrc 中永久配置
echo 'export ANTHROPIC_API_KEY="sk-ant-..."' >> ~/.bashrc
source ~/.bashrc

# 方法 2：启动时显式传递
ANTHROPIC_API_KEY="sk-ant-..." opencode

# 方法 3：写入用户配置（推荐）
# ~/.opencode/config.json
{
  "providers": {
    "anthropic": {
      "apiKey": "sk-ant-..."
    }
  }
}

# 方法 4：使用 opencode 内置命令设置
opencode config set providers.anthropic.apiKey "sk-ant-..."
```

---

## 6.8 坑八：配置未按预期合并

### 现象

```text
项目 .opencode/config.json 配置了 model: gpt-4o，
但 OpenCode 实际使用的是 claude-sonnet。
```

### 原因

可能是配置格式错误、层级搞混、或环境变量覆盖了项目配置。

### 排查方法

```bash
# 查看最终合并后的配置
opencode config get

# 查看详细来源
opencode config --verbose

# 检查环境变量
env | grep -i "opencode\|anthropic\|openai"
```

### 常见错误

```jsonc
// 错误：把 providers 写在 permission 里面
{
  "permission": {
    "providers": {  // ❌ 位置错误
      "anthropic": { "apiKey": "..." }
    }
  }
}

// 正确：providers 是顶层 key
{
  "permission": { "*": "ask" },
  "providers": {
    "anthropic": { "apiKey": "..." }  // ✓ 正确
  }
}
```
