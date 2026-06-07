# 05. Permission 与团队安全基线

> 适用版本：`v1.14.32` / `v1.15.13`。  
> 核心目标：让 agent 能查、能改、能验证，但不能默默破坏仓库、进程、远程分支或机密文件。

## 1. Permission 的三个动作

OpenCode permission 规则解析为：

```text
allow -> 允许，不询问
ask   -> 运行前询问用户
deny  -> 禁止
```

官方 permission 规则支持：

- 全局 `"*"`；
- 按工具名配置；
- 按工具输入做对象匹配；
- 通配符 `*` / `?`；
- `~` / `$HOME`；
- `external_directory`；
- agent 级覆盖。

规则匹配：**最后匹配规则优先**。

因此推荐：

```jsonc
{
  "permission": {
    "bash": {
      "*": "ask",
      "git status*": "allow",
      "git diff*": "allow",
      "git push*": "deny"
    }
  }
}
```

不要把 `"*"` 放在最后，否则它会覆盖前面的具体规则。

## 2. 推荐安全基线

见 `templates/global-opencode.jsonc` 与 `templates/project-opencode.jsonc`。

核心原则：

1. `read` / `grep` / `glob` 默认允许，但 `.env` 类文件禁止。
2. `edit` 默认 `ask`。
3. `bash` 默认 `ask`。
4. 只读 git 命令允许，破坏性 git 命令禁止。
5. 广义 kill 命令禁止或至少 `ask`。
6. 长时间服务启动默认 `ask`，并要求人类在外部终端管理。
7. `external_directory` 默认 `ask`。
8. `webfetch` / `websearch` 默认 `ask`，避免把私有代码/上下文无意带到外部。
9. `skill` 默认按名称 allow/ask/deny，而不是全放开内部实验 skill。
10. MCP 工具默认 `ask`，尤其是数据库、云资源、Issue/PR 写操作。

## 3. 推荐全局安全配置

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "*": "ask",

    "read": {
      "*": "allow",
      "*.env": "deny",
      "*.env.*": "deny",
      "**/.env": "deny",
      "**/.env.*": "deny",
      "*.env.example": "allow",
      "**/*.pem": "deny",
      "**/*.key": "deny"
    },

    "grep": "allow",
    "glob": "allow",

    "edit": "ask",

    "bash": {
      "*": "ask",

      "git status*": "allow",
      "git diff*": "allow",
      "git log*": "allow",
      "git branch*": "allow",
      "git rev-parse*": "allow",

      "rg *": "allow",
      "grep *": "allow",
      "ls *": "allow",
      "pwd": "allow",
      "cat *": "allow",

      "npm test*": "ask",
      "pnpm test*": "ask",
      "bun test*": "ask",
      "pytest*": "ask",
      "cargo test*": "ask",
      "go test*": "ask",
      "pnpm typecheck*": "ask",
      "pnpm lint*": "ask",

      "git push*": "deny",
      "git reset --hard*": "deny",
      "git clean*": "deny",
      "git checkout -- *": "deny",
      "git restore *": "ask",
      "rm -rf*": "deny",
      "sudo *": "ask",

      "pkill *": "deny",
      "killall *": "deny",
      "taskkill *": "ask",
      "kill *": "ask"
    },

    "external_directory": "ask",
    "doom_loop": "ask",
    "webfetch": "ask",
    "websearch": "ask",
    "skill": {
      "*": "ask",
      "project-*": "allow",
      "internal-*": "ask",
      "experimental-*": "deny"
    }
  }
}
```

## 4. Agent 级权限覆盖

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "agent": {
    "plan": {
      "mode": "primary",
      "permission": {
        "edit": "deny",
        "bash": {
          "*": "ask",
          "git status*": "allow",
          "git diff*": "allow",
          "rg *": "allow"
        }
      }
    },
    "build": {
      "mode": "primary",
      "permission": {
        "edit": "ask",
        "bash": {
          "*": "ask",
          "git status*": "allow",
          "git diff*": "allow",
          "rg *": "allow",
          "git push*": "deny",
          "git reset --hard*": "deny",
          "git clean*": "deny",
          "rm -rf*": "deny"
        }
      }
    },
    "review": {
      "description": "Review code without modifying files",
      "mode": "subagent",
      "permission": {
        "edit": "deny",
        "bash": {
          "*": "ask",
          "git diff*": "allow",
          "rg *": "allow"
        }
      }
    }
  }
}
```

## 5. 破坏性命令黑名单

强烈建议团队在 AGENTS.md 和 permission 里都禁止或强制确认：

```text
git push
git reset --hard
git clean -fd
git checkout -- .
git restore .
rm -rf
sudo
chmod -R
chown -R
pkill -f
killall
taskkill /IM node.exe
Docker prune 类命令
数据库 drop/truncate/migrate reset
云资源 delete/destroy
```

## 6. 为什么要禁止 `pkill -f`

`pkill -f` 会按完整命令行匹配，可能误杀：

- OpenCode 自身；
- OpenCode 启动的 shell 子进程；
- VSCode Server / node 进程；
- 当前终端会话；
- 与关键词相似的无关服务。

替代流程：

```bash
pgrep -af '<process-name-or-port>'
# 人类确认 PID 后再：
kill <PID>
```

按端口定位：

```bash
lsof -nP -iTCP:3000 -sTCP:LISTEN
# 人类确认 PID 后 kill
```

## 7. 长时间后台命令治理

不要让 agent 随意运行：

```bash
npm run dev &
pnpm start &
python server.py &
```

原因：

- stdout/stderr 可能不关闭，bash tool 以为命令没结束；
- 子进程可能残留；
- 后续 kill 进程风险更高；
- VSCode/WSL/远程服务器更容易卡顿。

建议：

1. 长跑服务放外部终端或 tmux，由人类管理。
2. agent 只跑短命令：测试、lint、typecheck、grep、git diff。
3. 如果必须启动服务，要求写 PID 和 log，并让人类确认停止：

```bash
mkdir -p .opencode/runtime .opencode/logs
nohup pnpm dev > .opencode/logs/dev.log 2>&1 < /dev/null & echo $! > .opencode/runtime/dev.pid
```

## 8. `.env` 与机密文件

建议：

- `read` deny `.env`、`.env.*`、`*.pem`、`*.key`；
- 用 `.env.example` 作为 agent 可读的接口说明；
- 在 `AGENTS.md` 里写明“不要读取或输出 secrets”；
- provider API Key 不进入项目配置，统一用 `/connect` 或 `{env:...}`。

## 9. external_directory

`external_directory` 用于控制工具访问启动目录之外的路径。默认建议 `ask`。

场景：

- monorepo 里从 package 子目录启动 OpenCode，但要读 repo 根；
- agent 要读 `~/Downloads/foo.log`；
- tool 要写 `/tmp`；
- 全局 tool 调用用户 home 目录脚本。

建议：

```jsonc
{
  "permission": {
    "external_directory": {
      "*": "ask",
      "/tmp/*": "allow",
      "$HOME/projects/*": "ask",
      "$HOME/.ssh/*": "deny"
    }
  }
}
```

## 10. 安全提示词

在任务开始时给 agent 明确边界：

```text
请先只读分析，不要修改文件，不要运行会改变状态的命令。
不要运行 git push、git reset --hard、git clean、rm -rf、pkill、killall、taskkill。
如果需要停止进程，先列出 PID、端口、命令行，并等待我确认。
如果需要读取 .env 或密钥文件，不要读取，改为让我提供必要的非敏感信息。
```
