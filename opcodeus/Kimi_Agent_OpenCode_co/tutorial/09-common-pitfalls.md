# 常见坑与解决方案

> **适用版本**: OpenCode v1.14.32 / v1.15.13
>
> **目标读者**: 有编码经验的软件研发人员，已熟悉 OpenCode 基础操作
>
> **前置知识**: Session 管理、Permission 系统、Snapshot 机制、Git 基础

---

## 目录

- [1. `pkill -f` 可能误杀 OpenCode 或导致工具调用挂住](#1-pkill--f-可能误杀-opencode-或导致工具调用挂住)
- [2. 长时间后台命令导致 bash tool 挂起或残留进程](#2-长时间后台命令导致-bash-tool-挂起或残留进程)
- [3. `/undo` 或 message revert 不等价于 Git 回滚](#3-undo-或-message-revert-不等价于-git-回滚)
- [4. `write` 可能覆盖已有文件](#4-write-可能覆盖已有文件)
- [5. MCP / Web 工具过多导致上下文膨胀](#5-mcp--web-工具过多导致上下文膨胀)
- [6. `.gitignore` 会影响 grep / glob / list 的搜索范围](#6-gitignore-会影响-grep--glob--list-的搜索范围)
- [7. Desktop 模式下 `process.cwd()` 为 `/` 的路径问题](#7-desktop-模式下-processcwd-为--的路径问题)
- [8. 通用防御原则：三层治理模型](#8-通用防御原则三层治理模型)

---

## 1. `pkill -f` 可能误杀 OpenCode 或导致工具调用挂住

### 现象

在 TUI 中执行以下命令时，可能**挂住直到超时**：

```bash
pkill -f vim 2>/dev/null; echo "killed"
```

**根本原因**：`pkill -f` 按进程命令行匹配，可能误杀 OpenCode 自身的子进程（包括负责 tool 调用的内部进程）。一旦关键子进程被杀死，当前 tool call 无法完成返回，表现为**无限挂起直至超时**。

### 治理方式

**第一层：Permission 强制拦截（v1.15.13+）**

在 `opencode.jsonc` 中显式 deny 广义 kill 命令：

```jsonc
{
  "permission": {
    "bash": {
      "rules": [
        {
          "pattern": "^pkill",
          "action": "deny"
        },
        {
          "pattern": "^killall",
          "action": "deny"
        },
        {
          "pattern": "kill\s+-9",
          "action": "deny"
        }
      ]
    }
  }
}
```

> **v1.15.13 改进**: 权限规则现在按配置顺序评估，第一条匹配的规则立即生效。建议将最严格的 deny 规则放在前面。

**第二层：Prompt 中明确禁止**

在 system prompt 或项目规则中添加：

```
[安全规则]
- 禁止使用 pkill -f、pkill -9、killall 等模糊匹配命令
- 如需终止进程，先通过 ps / lsof / netstat 确认目标 PID，再使用 kill <PID>
- 优先通过服务管理工具（systemctl、pm2、nodemon）控制进程生命周期
```

**第三层：人工确认流程**

人类在 OpenCode **外部终端**确认 PID 后再执行 kill：

```bash
# 步骤 1：精确定位目标进程
ps aux | grep vim
# 或按端口查找
lsof -i :3000

# 步骤 2：确认 PID 无误后，精确 kill
kill 12345
# 而非：pkill -f vim
```

**第四层：优先按端口或 PID 文件管理开发服务**

为开发服务建立标准化的进程管理：

```bash
# 方案 A：使用 PID 文件
npm run dev &
echo $! > .pid/dev-server.pid

# 后续终止时
kill "$(cat .pid/dev-server.pid)"

# 方案 B：使用进程管理器
pm2 start npm --name "dev-server" -- run dev
pm2 stop dev-server
pm2 delete dev-server

# 方案 C：使用 tmux 独立 pane
tmux new-window -n dev-server 'npm run dev'
# 需要停止时切换到对应 pane 按 Ctrl+C
```

### 应急处理

如果命令已经挂住：

```bash
# 在外部终端查看 OpenCode 进程状态
ps aux | grep opencode

# 如需强制终止（会丢失当前 session 状态）
kill -9 <OPENCODE_PID>

# v1.15.13+ 提示: 新版增强了 tool timeout 处理，挂起命令会在默认超时时间（60s）后自动中断
```

---

## 2. 长时间后台命令导致 bash tool 挂起或残留进程

### 现象

Agent 执行以下命令后，bash tool 长时间不返回，或退出后子进程仍在运行：

```bash
# 常见触发命令
npm run dev &
pnpm start &
python manage.py runserver &
docker-compose up &
```

**根本原因**：后台进程的 stdout/stderr 仍连接到 OpenCode 的伪终端，或进程在后台持续输出导致 pipe 缓冲区满阻塞。

### 治理方式

**第一层：长跑服务放在单独终端或 tmux pane 中**

不要在 OpenCode 的 bash tool 中启动长时间运行的服务。改为：

```bash
# 方案 A：独立终端窗口
# Terminal 1: 运行开发服务器
npm run dev

# Terminal 2: 运行 OpenCode
opencode

# 方案 B：tmux 多 pane
tmux new-session -d -s dev -n 'editor'
tmux split-window -h -t dev 'npm run dev'
tmux attach -t dev
# 左侧 pane 运行 opencode，右侧 pane 运行 dev server

# 方案 C：使用 screen
screen -S dev-server -d -m npm run dev
# 随时 attach 查看日志
screen -r dev-server
```

**第二层：让 Agent 只运行短命令**

Agent 的 bash tool 适合执行**快速返回**的命令：

```bash
# ✅ 适合 Agent 执行（快速返回）
npm run build
npm run lint
npm test -- --run
npx tsc --noEmit
python manage.py migrate

# ❌ 不适合 Agent 执行（长时间运行）
npm run dev
npm run watch
npm run start
```

**第三层：如果必须临时启动服务，要求重定向并写 PID 文件**

在 permission prompt 中声明要求：

```
[服务启动规则]
如必须临时启动后台服务，必须同时满足：
1. stdout 和 stderr 重定向到日志文件：> server.log 2>&1
2. 写入 PID 文件：echo $! > .pid/server.pid
3. 使用 nohup 或 disown 断开终端关联
4. 在任务完成后主动终止并清理
```

正确示例：

```bash
# 启动时
nohup npm run dev > .logs/dev-server.log 2>&1 &
echo $! > .pid/dev-server.pid

# 停止时
kill "$(cat .pid/dev-server.pid)" 2>/dev/null
rm .pid/dev-server.pid
```

### 清理残留进程

如果发现已存在残留进程：

```bash
# 查找特定端口的占用进程
lsof -i :3000
# 或
netstat -tlnp | grep 3000

# 精确终止
kill -15 <PID>   # 先尝试 graceful 终止
kill -9 <PID>    # 强制终止（万不得已）

# v1.15.13+ 提示: 新增后台 Agent 推送功能，可能会创建额外的守护进程
# 如发现异常进程，可通过以下命令查看完整的进程树
pstree -p | grep opencode
```

---

## 3. `/undo` 或 message revert 不等价于 Git 回滚

### 已知问题清单

| # | 问题描述 | 影响范围 | 严重程度 |
|---|---------|---------|---------|
| 1 | `git add .` 失败后 snapshot 可能复用旧 tree hash | v1.14.32, **v1.15.13 已修复** | 高 |
| 2 | Snapshot cache 中残留 `index.lock` 导致后续操作失败 | v1.14.32, **v1.15.13 已修复** | 高 |
| 3 | TUI 或桌面端 message revert 后文件仍保持修改状态 | v1.14.32 - v1.15.13 | 中 |
| 4 | Windows 下禁止创建保留文件名（CON, PRN, AUX 等） | 所有版本 | 低 |

**v1.15.13 修复详情**：

- **Snapshot tree hash 复用问题**：修复了在 `git add` 失败后 snapshot 缓存逻辑，现在会正确生成新的 tree hash 而不是复用旧的
- **index.lock 残留问题**：增加了锁文件清理机制，在 snapshot 操作异常退出时会自动清理 `.git/index.lock`
- **后台 Agent 状态同步**：v1.15.x 新增的后台 Agent 推送机制现在会正确同步 snapshot 状态，避免并发修改导致的缓存不一致

### 治理方式

**第一层：每次让 Agent 大改前，先建 Git checkpoint**

```bash
# 进入工作区时立即建立安全基线
git status --short

# 如有未提交修改，先处理
git add -A && git commit -m "checkpoint: before ai refactoring"

# 大改前再建一个
git add -A && git commit -m "checkpoint: stable baseline"
```

**第二层：把 `/undo` 当作便利功能，而非安全网**

`/undo` 的设计意图是撤销**最后一次 tool call**，不是 Git 回滚的替代品：

```
使用场景对比：

/undo                  -> 撤销刚才那次 edit/write，相当于"反悔一步"
git reset --soft HEAD~1 -> 撤销最后一次 commit，保留修改在暂存区
git reset --hard HEAD~1 -> 彻底丢弃最后一次 commit 的所有修改
git revert HEAD         -> 创建一个新的 commit 来反向应用修改
```

**第三层：每轮后执行 `git diff --stat` / `git diff`**

养成每轮 Agent 交互后检查变更的习惯：

```bash
# 快速查看变更概览
git diff --stat

# 详细审查每个文件的变更
git diff

# 如果变更范围太大，按文件查看
git diff --name-only | while read f; do
    echo "=== $f ==="
    git diff "$f" | head -50
done
```

**第四层：退出 OpenCode 后备份 snapshot cache**

```bash
# Snapshot cache 位置（默认）
# macOS: ~/Library/Caches/opencode/snapshots/
# Linux: ~/.cache/opencode/snapshots/
# Windows: %LOCALAPPDATA%\opencode\snapshots\

# 退出前备份
BACKUP_DIR="$HOME/.opencode-backups/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r ~/.cache/opencode/snapshots "$BACKUP_DIR/"
echo "Snapshot backup saved to: $BACKUP_DIR"
```

**第五层：Windows 保留文件名规避**

如果在 Windows 上使用 OpenCode，注意以下文件名是系统保留的，无法创建：

```
CON, PRN, AUX, NUL,
COM1, COM2, COM3, COM4, COM5, COM6, COM7, COM8, COM9,
LPT1, LPT2, LPT3, LPT4, LPT5, LPT6, LPT7, LPT8, LPT9
```

Agent 在 Windows 上尝试 `write` 这些名称的文件时会失败。如需创建配置文件：

```bash
# 避免使用保留名称
# ❌ write CON.md -> 失败
# ✅ write console-config.md -> 成功
```

---

## 4. `write` 可能覆盖已有文件

### 现象

`write` tool 的语义是**"创建新文件或覆盖已有文件"**。Agent 可能无意中覆盖已有代码：

```
Agent: I'll write the updated content to src/utils.ts

[write] path: src/utils.ts
---
// 原有 200 行代码被整体替换为 15 行新代码
// 其他函数的修改全部丢失
```

### 风险场景

| 场景 | 说明 |
|------|------|
| Agent "重写整个文件" | 模型倾向于输出完整文件内容，而非精确 diff |
| 覆盖同事刚提交的代码 | 如果本地文件比 Agent 认知中更新 |
| 丢失未保存的手动修改 | 人类在 Agent 运行期间手动修改了文件 |

### 治理方式

**第一层：优先使用 `edit` / `apply_patch`**

`edit` 是基于 diff 的精确修改，不会意外删除未涉及的内容：

```
# ✅ 推荐：使用 edit，只修改需要的部分
[edit] path: src/utils.ts
old_string: |
  function oldHelper() {
    return 42;
  }
new_string: |
  function oldHelper() {
    // Added validation
    if (someCondition) return 0;
    return 42;
  }
```

**第二层：Prompt 中声明不要整体重写**

在 system prompt 或项目规则中明确约束：

```
[文件修改规则]
- 优先使用 edit tool 进行精确修改，而非 write tool 重写整个文件
- 只有在创建全新文件时才使用 write
- 修改前必须先 read 文件确认当前内容
- 如需多处修改，分多次 edit 调用，每次只改一个逻辑单元
```

**第三层：Permission 层面增加校验（v1.15.13+）**

```jsonc
{
  "permission": {
    "edit": "allow",
    "write": "ask"  // 覆盖已有文件时需要确认
  }
}
```

> **注意**: v1.14.32 中 `write` 的 `ask` 行为略有不同，会在所有 write 操作时弹出确认，包括创建新文件。v1.15.13+ 优化为仅对覆盖已有文件时询问。

**第四层：修改前 read 确认**

Agent 的标准操作序列应该是：

```
1. read    -> 读取文件当前内容
2. think   -> 规划需要修改的位置
3. edit    -> 精确修改目标位置
4. read    -> 验证修改结果
```

而非：

```
❌ 1. write -> 直接覆盖整个文件（丢失原有内容）
```

---

## 5. MCP / Web 工具过多导致上下文膨胀

### 现象

当配置了多个 MCP Server（如 filesystem、git、browser、database 等）或开启了 web search/fetch 时：

1. 每个 tool 的 schema 都会占用 prompt 上下文空间
2. MCP Server 的初始化描述可能很长
3. 模型需要 "选择" 使用哪个 tool，选项越多决策越慢
4. 总上下文可能快速接近模型的 token 上限

### 量化估算

| Tool 类型 | 大致 Token 开销 | 备注 |
|----------|----------------|------|
| 内置 tool (bash/read/edit/grep 等) | ~500-1000 | 基础工具集 |
| 单个 MCP Server (filesystem) | ~1000-3000 | 取决于 schema 复杂度 |
| 单个 MCP Server (browser) | ~2000-5000 | puppeteer/playwright 操作 |
| Web search tool | ~500 | 搜索描述 |
| Web fetch tool | ~300 | 抓取描述 |

> **10 个 MCP Server = 可能额外消耗 10K-30K tokens 的上下文空间**

### 治理方式

**第一层：默认关闭非必要 MCP**

```jsonc
{
  "mcp": {
    "servers": [
      // 只在需要时启用
      // {
      //   "name": "database",
      //   "transport": "stdio",
      //   "command": "npx",
      //   "args": ["-y", "@modelcontextprotocol/server-postgres"]
      // },
      {
        "name": "filesystem",
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "."]
      }
    ]
  }
}
```

**第二层：按 Agent 配置 MCP 权限**

v1.15.13+ 支持为不同 Agent 指定不同的 MCP 集合：

```jsonc
{
  "agents": {
    "code-writer": {
      "mcp_servers": ["filesystem"],
      "websearch": false,
      "webfetch": false
    },
    "researcher": {
      "mcp_servers": ["browser", "filesystem"],
      "websearch": true,
      "webfetch": true
    },
    "devops": {
      "mcp_servers": ["docker", "kubernetes"],
      "websearch": false
    }
  }
}
```

**第三层：按需动态启用**

```
# 交互式启用 MCP（TUI 模式）
/enable mcp:browser

# 完成任务后关闭
/disable mcp:browser
```

**第四层：监控上下文使用**

```
# TUI 中关注上下文指示器
# 当上下文接近上限时，模型响应质量会下降
# 考虑：
# 1. 开启新 session
# 2. 减少 MCP 数量
# 3. 切换到上下文窗口更大的模型
```

---

## 6. `.gitignore` 会影响 grep / glob / list 的搜索范围

### 现象

Agent 使用 `grep`、`glob` 或 `list` 工具搜索文件时，发现某些目录下的文件**搜索不到**：

```
Agent: [grep] pattern: "databaseURL", path: "."
# 结果为空，即使 prisma/schema.prisma 中存在该字符串

Agent: [glob] pattern: "**/*.prisma"
# 结果为空，即使 prisma/ 目录下有 .prisma 文件

Agent: [list] path: "node_modules/@types/react"
# 结果为空或权限被拒绝
```

**根本原因**：OpenCode 的搜索工具默认**尊重 `.gitignore`** 规则。如果 `node_modules/`、`.env`、`dist/` 等目录在 `.gitignore` 中，这些目录将被排除在搜索结果之外。

### 治理方式

**第一层：在项目 `.ignore` 中显式放开需要搜索的目录**

OpenCode 支持 `.ignore` 文件作为独立于 `.gitignore` 的搜索配置。在项目根目录创建 `.ignore` 文件：

```ignore
# .ignore - OpenCode 搜索范围配置
# 此文件控制 grep/glob/list 的搜索范围
# 语法与 .gitignore 相同

# 放开特定目录供搜索
!prisma/
!src/types/

# 放开特定文件
docs/
*.log

# 注意：.gitignore 中的规则仍然有效
# .ignore 是与 .gitignore 叠加的额外排除规则
```

**第二层：使用 `path` 参数直接指定搜索范围**

```
# 如果知道文件所在目录，直接指定路径
[grep] pattern: "databaseURL", path: "prisma"

# 搜索特定文件类型时指定目录
[glob] pattern: "*.prisma", path: "prisma"

# 列出特定目录内容
[list] path: "prisma"
```

**第三层：理解工具行为差异**

| Tool | 是否尊重 `.gitignore` | 是否受 `.ignore` 影响 | 说明 |
|------|---------------------|---------------------|------|
| `grep` | ✅ 是 | ✅ 是 | 搜索文本时排除 gitignore 目录 |
| `glob` | ✅ 是 | ✅ 是 | 文件匹配时排除 gitignore 目录 |
| `list` | ✅ 是 | ✅ 是 | 列出目录时排除 gitignore 目录 |
| `read` | ❌ 否 | ❌ 否 | 直接读取不受搜索范围影响 |
| `edit` | ❌ 否 | ❌ 否 | 直接编辑不受搜索范围影响 |

```
# read 可以直接读取 gitignore 内的文件
[read] path: "node_modules/@types/react/index.d.ts"
# ✅ 成功

# 但 grep 搜不到里面的内容
[grep] pattern: "Component", path: "node_modules/@types/react"
# ❌ 无结果（目录在 .gitignore 中）
```

**第四层：开发时临时放开搜索**

```bash
# 场景：需要搜索 node_modules 中某个包的源码来理解其行为

# 方案 A：在 .ignore 中临时放开
echo '!node_modules/some-package' >> .ignore
# 搜索完成后恢复
sed -i '/!node_modules\/some-package/d' .ignore

# 方案 B：直接在指定路径搜索
grep -r "targetFunction" node_modules/some-package/src/
# （在 OpenCode 外部终端执行）
```

---

## 7. Desktop 模式下 `process.cwd()` 为 `/` 的路径问题

### 现象

在 Desktop 模式（图形界面）下使用 OpenCode 时，Agent 执行的路径相关操作出现异常：

```
Agent: [bash] command: "pwd"
# 输出: /
# 预期: /home/user/my-project

Agent: [write] path: "config.json"
# 文件被写入到 /config.json 而不是项目目录下

Agent: [bash] command: "ls"
# 列出的是根目录内容，而非项目文件
```

**根本原因**：Desktop 模式下 OpenCode 的工作进程 `process.cwd()` 返回 `/`，而非用户预期的项目目录。这与 TUI/CLI 模式的行为不一致。

### 影响范围

| 场景 | 表现 | 严重程度 |
|------|------|---------|
| 相对路径文件操作 | 文件被写入/读取到错误位置 | 高 |
| 脚本执行 | 脚本在错误目录下运行 | 高 |
| 工具调用（如 `npm`） | 找不到 package.json | 高 |
| Snapshot 创建 | snapshot 路径解析错误 | 中 |

### 治理方式

**第一层：始终使用绝对路径**

在 Desktop 模式下，所有文件操作都应使用绝对路径：

```jsonc
{
  // opencode.jsonc - Desktop 模式专用配置
  "project_path": "/home/user/my-project",

  // 在 prompt 中提醒 Agent 使用绝对路径
  "system_prompt": "You are working in Desktop mode. Always use absolute paths for all file operations. The project root is /home/user/my-project."
}
```

Agent 操作示例：

```
# ✅ Desktop 模式下使用绝对路径
[write] path: "/home/user/my-project/src/config.ts"
[read] path: "/home/user/my-project/package.json"
[bash] command: "cd /home/user/my-project && npm run build"

# ❌ 避免使用相对路径
[write] path: "src/config.ts"          # 会写入 /src/config.ts
[bash] command: "npm run build"        # 在 / 下执行，找不到 package.json
```

**第二层：在 bash 命令中显式 `cd`**

所有 bash 命令都显式指定工作目录：

```bash
# ✅ 正确方式
cd /home/user/my-project && npm install
cd /home/user/my-project && npx tsc --noEmit
cd /home/user/my-project && git status

# ✅ 或者使用 env 设置工作目录
(cd /home/user/my-project && npm run test)

# ❌ Desktop 模式下不可靠
npm install   # 在 / 下执行
```

**第三层：使用环境变量指定项目路径**

```bash
# 启动 Desktop 前设置环境变量
export OPENCODE_PROJECT_PATH=/home/user/my-project
opencode --desktop

# 在 prompt 中引用
{
  "system_prompt": "The project root directory is set via environment variable: ${OPENCODE_PROJECT_PATH}. Always use this path as the base for all file operations."
}
```

**第四层：配置文件中固定路径**

```jsonc
// opencode.jsonc - 项目级配置
{
  "$schema": "https://opencode.ai/config.json",

  // 显式指定项目根目录（Desktop 模式必需）
  "project_path": "/home/user/my-project",

  // bash 命令的默认工作目录
  "bash_default_cwd": "/home/user/my-project",

  "permission": {
    "read": {
      "paths": ["/home/user/my-project"]
    },
    "edit": {
      "paths": ["/home/user/my-project"]
    },
    "bash": {
      "rules": [
        {
          // 限制操作范围在项目目录内
          "pattern": "^cd\s+/home/user/my-project",
          "action": "allow"
        }
      ]
    }
  }
}
```

**第五层：版本适配说明**

| 版本 | Desktop 路径行为 | 建议 |
|------|-----------------|------|
| v1.14.32 | `process.cwd()` 始终为 `/` | 必须使用绝对路径 |
| v1.15.13 | **部分修复**：可在启动参数中指定工作目录 `opencode --desktop --cwd /project/path` | 仍建议使用绝对路径，兼容性更好 |

```bash
# v1.15.13+ 启动方式
opencode --desktop --cwd /home/user/my-project

# 或通过配置文件指定
echo '{"project_path": "/home/user/my-project"}' > /home/user/.config/opencode/opencode.jsonc
```

---

## 8. 通用防御原则：三层治理模型

通过以上 7 个坑点的分析，可以归纳出一个通用的**三层治理模型**：

```
┌─────────────────────────────────────────────────────┐
│  第一层：Permission（权限层）- 硬性拦截              │
│  - deny 危险命令和模式                               │
│  - ask 敏感操作                                      │
│  - 按 agent 配置不同权限                             │
├─────────────────────────────────────────────────────┤
│  第二层：Prompt（引导层）- 软性约束                  │
│  - system prompt 中声明行为规则                      │
│  - 项目级 rules 文件约束                             │
│  - 明确禁止/推荐的操作模式                           │
├─────────────────────────────────────────────────────┤
│  第三层：Human（人工层）- 最终把关                   │
│  - 大改前建 Git checkpoint                          │
│  - 每轮后 git diff --stat 检查                      │
│  - 退出后备份 snapshot cache                        │
│  - 保留外部终端进行精确操作                          │
└─────────────────────────────────────────────────────┘
```

### 各坑点的治理层映射

| 坑点 | Permission | Prompt | Human |
|------|-----------|--------|-------|
| `pkill -f` 误杀 | deny `pkill`/`killall` | 声明禁止模糊 kill | 外部终端确认 PID |
| 后台命令挂起 | 限制超时命令 | 声明短命令原则 | 独立终端/tmux |
| `/undo` 不等价回滚 | - | 声明 `/undo` 局限性 | 建 Git checkpoint |
| `write` 覆盖文件 | write: ask (v1.15.13+) | 声明 edit 优先 | 修改前 read 确认 |
| MCP 上下文膨胀 | 按 agent 限制 MCP | - | 监控 token 使用 |
| `.gitignore` 影响搜索 | - | - | 配置 `.ignore` 文件 |
| Desktop 路径问题 | 限制操作路径 | 声明使用绝对路径 | 验证文件位置 |

### 快速检查清单

每次使用 OpenCode 前，确认以下事项：

```markdown
- [ ] 当前在独立分支，不在主分支
- [ ] Git 工作区干净或有明确的 checkpoint commit
- [ ] Permission 配置已加载并生效（/show rules 查看）
- [ ] 长时间运行的服务已在独立终端/tmux 启动
- [ ] 理解 `/undo` 不是 Git 回滚的替代品
- [ ] Desktop 模式下使用绝对路径
- [ ] 每轮 Agent 交互后执行 git diff --stat 检查变更
```

---

## 版本差异速查

| 特性/修复 | v1.14.32 | v1.15.13 | 影响 |
|----------|----------|----------|------|
| Snapshot tree hash 复用 | 存在问题 | **已修复** | 坑 3 |
| index.lock 残留 | 存在问题 | **已修复** | 坑 3 |
| 权限规则顺序 | 非确定性 | **按配置顺序评估** | 坑 1, 4 |
| write: ask 行为 | 所有 write 都询问 | **仅覆盖时询问** | 坑 4 |
| 后台 Agent 推送 | 不支持 | **新增** | 坑 2（进程管理） |
| Desktop --cwd 参数 | 不支持 | **新增** | 坑 7 |
| `OPENCODE_CONFIG_CONTENT` 优先级 | 存在优先级 bug | **已修复** | 配置系统 |

---

> **提示**: 以上坑点均来自实际使用经验和社区反馈。OpenCode 正在快速迭代中，部分问题可能在新版本中已修复或行为有变化。建议定期查看 [OpenCode 官方更新日志](https://opencode.ai/changelog) 和本教程的更新版本。
