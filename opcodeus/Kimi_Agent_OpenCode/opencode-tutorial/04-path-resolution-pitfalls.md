# 4. 路径解析深度指南：Skill / Tool / Script 的引用与坑点

> **这是工程实践中最常见、最容易踩坑的部分。** Agent 对话时调用工具或脚本，路径解析规则与常规 shell 执行有显著差异。

---

## 4.1 核心问题：Agent 的"工作目录"原点在哪？

### 答案：以 OpenCode 启动时的目录为原点

```text
OpenCode 的默认工作目录 = 启动 opencode 命令时所在的目录
                         = 项目根目录（推荐在此启动）
```

### 典型场景

```bash
# 场景 A：正确——在项目根目录启动
cd /home/user/projects/my-app
opencode
# 此时工作原点是：/home/user/projects/my-app

# 场景 B：危险——在子目录启动
cd /home/user/projects/my-app/packages/server
opencode
# 此时工作原点是：/home/user/projects/my-app/packages/server
# agent 可能找不到 .opencode/config.json 和 AGENTS.md
```

### 验证当前工作原点

在 OpenCode 会话中：

```text
> 请告诉我当前的工作目录
# agent 会通过 bash 工具执行 pwd，输出当前目录

# 或者更准确地看 opencode 自己怎么解析
> /pwd
```

---

## 4.2 Skill 的路径解析规则

### Skill 的物理存储位置

Skill 可以存在于三个层级（与配置层级对应）：

```text
~/.config/opencode/skills/           # 全局 Skill（所有用户、所有项目可用）
~/.opencode/skills/                  # 用户 Skill（当前用户、所有项目可用）
<project>/.opencode/skills/          # 项目 Skill（仅当前项目可用）
```

每个 Skill 目录结构：

```text
.opencode/skills/
├── refactor/                        # Skill 名称 = 目录名
│   ├── SKILL.md                     # Skill 定义和说明
│   ├── scripts/
│   │   ├── extract-function.js      # Skill 使用的脚本
│   │   └── analyze-deps.py
│   └── templates/
│       └── function-template.ts
└── code-review/
    ├── SKILL.md
    └── scripts/
        └── security-check.sh
```

### SKILL.md 中如何描述脚本路径

**关键原则**：`SKILL.md` 中的路径描述应以 **Skill 自身目录** 为原点。

```markdown
<!-- SKILL.md -->
# Code Review Skill

## 工具脚本

- 安全检查脚本：`./scripts/security-check.sh`
  - 从本 Skill 目录下的 scripts 子目录执行
  - 接收参数：`<file-path>`

## 使用方法

1. 运行 `./scripts/security-check.sh <目标文件>` 进行安全检查
2. 参考 `./templates/checklist.md` 作为审查模板
```

### Agent 实际调用时路径如何解析

当 agent 读取到 `SKILL.md` 中的 `./scripts/security-check.sh` 时：

```text
实际解析路径 = <skill 所在目录>/scripts/security-check.sh

示例：
- 如果 skill 在 ~/.opencode/skills/code-review/
- 则脚本路径 = ~/.opencode/skills/code-review/scripts/security-check.sh
```

**OpenCode runtime 在调用 skill 时会自动处理这个路径映射**，但 agent 在对话中自行使用 bash 工具时**不会自动处理**。

---

## 4.3 Tool 的路径解析规则

### 内置 Tool 的引用

内置 tool 无需路径，直接通过名称调用：

```text
read、grep、glob、bash、edit、write、apply_patch、task、skill、webfetch
```

### 自定义 Tool 的存储位置

```text
~/.config/opencode/tools/            # 全局自定义工具
~/.opencode/tools/                   # 用户自定义工具
<project>/.opencode/tools/           # 项目自定义工具
```

### 自定义 Tool 的注册与引用

自定义 tool 需要在 `config.json` 中注册：

```jsonc
{
  "tools": [
    {
      "name": "deploy-check",
      "description": "检查部署前置条件",
      "command": "./tools/deploy-check.sh",    // 相对项目根目录
      "workingDir": "${PROJECT_ROOT}"          // 明确指定工作目录
    },
    {
      "name": "lint-staged",
      "description": "对暂存区文件运行 lint",
      "command": "npx lint-staged",
      "workingDir": "${PROJECT_ROOT}"
    }
  ]
}
```

### 自定义 Tool 脚本中的路径原点

**坑点警告**：自定义 tool 的 `command` 字段如果是相对路径，其原点是 **OpenCode 启动时的目录**（通常是项目根目录），不是 tool 脚本所在的目录。

```text
错误写法（假设 tool 在 .opencode/tools/ 下）：
{
  "command": "./deploy-check.sh"   // 这会被解析为 <项目根目录>/deploy-check.sh
  // 但脚本实际在 <项目根目录>/.opencode/tools/deploy-check.sh
}

正确写法：
{
  "command": "./.opencode/tools/deploy-check.sh"
  // 或者使用绝对路径变量
  "command": "${PROJECT_ROOT}/.opencode/tools/deploy-check.sh"
}
```

---

## 4.4 Agent 对话中使用脚本时的路径问题（最常见坑点）

### 坑点 1：Agent 用 bash 执行脚本时，工作目录可能不是预期的

**现象**：

```text
Agent: 让我运行测试脚本
> bash: ./scripts/test.sh

错误：bash: ./scripts/test.sh: No such file or directory
```

**原因**：
- Agent 认为 `./scripts/test.sh` 在当前目录下
- 但当前 bash 的工作目录与 agent 预期的不同
- 或者 agent 之前 cd 到了子目录，但没有 cd 回来

**解决方案**：

```text
# 在 prompt 中明确要求使用绝对路径
"请在执行任何脚本前先用 pwd 确认当前目录，然后使用绝对路径执行"

# 在 AGENTS.md 中规定
## 路径规范
- 执行脚本前必须先 `pwd` 确认当前目录
- 优先使用绝对路径执行脚本
- 如果必须在子目录执行，执行后必须返回原目录
```

### 坑点 2：Skill 中引用的脚本路径，agent 用 bash 调用时找不到

**现象**：

```text
SKILL.md 中写道："运行 ./scripts/analyze.sh 进行分析"
Agent: > bash: ./scripts/analyze.sh
错误：找不到文件
```

**原因**：
- `SKILL.md` 中的 `./scripts/analyze.sh` 是以 skill 目录为原点的
- 但 agent 用 bash 工具执行时，bash 的工作目录是 OpenCode 启动目录
- 两者不是同一个目录

**解决方案**：

```markdown
<!-- 在 SKILL.md 中，用完整路径描述 -->
# 分析 Skill

## 脚本位置
- Skill 目录：`~/.opencode/skills/analyze/`（全局）或 `./.opencode/skills/analyze/`（项目）
- 分析脚本：`~/.opencode/skills/analyze/scripts/analyze.sh`

## 使用方法
1. 直接调用 skill 工具：`@analyze <参数>`（推荐，runtime 自动处理路径）
2. 如需用 bash 手动执行，使用绝对路径：
   `bash ~/.opencode/skills/analyze/scripts/analyze.sh <参数>`
```

### 坑点 3：`.opencode/tools/` 下的脚本权限问题

**现象**：

```text
Agent: > bash: ./.opencode/tools/my-tool.sh
错误：Permission denied
```

**解决方案**：

```bash
# 提前给脚本执行权限
chmod +x .opencode/tools/*.sh

# 或者在 AGENTS.md 中说明
## 工具脚本权限
如果执行 .opencode/tools/ 下的脚本遇到 Permission denied，
请先运行 `chmod +x .opencode/tools/<script-name>.sh`
```

### 坑点 4：相对路径原点在 agent 多轮对话中漂移

**现象**：

```text
Round 1: Agent cd packages/server && npm test    （现在在 packages/server/）
Round 2: Agent ./scripts/build.sh                （期望在项目根目录执行，但实际在 packages/server/）
错误：找不到 scripts/build.sh
```

**解决方案**：

```text
# 在 AGENTS.md 中强制规范
## 目录管理
- 每次使用 bash 工具时，不要依赖之前的 cd 状态
- 如需在特定目录执行命令，使用完整路径：
  正确：`bash cd /project/root && ./scripts/build.sh`
  正确：`bash /project/root/scripts/build.sh`
  错误：`bash ./scripts/build.sh`  （依赖当前目录，不可靠）

# 或者每次都用绝对路径
cd /home/user/project && ./scripts/build.sh
```

---

## 4.5 各级目录的默认路径原点速查

| 场景 | 路径原点 | 示例 |
|---|---|---|
| OpenCode 启动目录 | 执行 `opencode` 命令时的目录 | `cd ~/project && opencode` → 原点是 `~/project` |
| 项目配置加载 | 启动目录下的 `.opencode/config.json` | `~/project/.opencode/config.json` |
| `AGENTS.md` 加载 | 启动目录下的 `AGENTS.md` | `~/project/AGENTS.md` |
| 内置 tool 执行 | 不依赖路径，直接调用 | `read`、`grep`、`bash` 等 |
| 自定义 tool 的 `command` | OpenCode 启动目录 | `"command": "./scripts/test.sh"` → `~/project/scripts/test.sh` |
| Skill 的 `SKILL.md` 引用 | Skill 自身目录 | `~/.opencode/skills/X/SKILL.md` 中的 `./scripts` → `~/.opencode/skills/X/scripts` |
| Agent bash 执行 | bash 的当前工作目录 | 与 OpenCode 启动目录相同（除非 agent 之前 cd 过） |
| `snapshot/` 存储 | `~/.local/share/opencode/snapshot/` | 按 workspace hash 组织 |

---

## 4.6 安全使用路径的 AGENTS.md 模板

```markdown
## 路径与脚本执行规范

### 工作目录
- 本项目的根目录是 OpenCode 的启动目录
- 所有相对路径的原点都是项目根目录

### 执行脚本前的必做检查
1. 先执行 `pwd` 确认当前目录
2. 使用绝对路径或相对于项目根目录的完整路径
3. 如果脚本在 `.opencode/tools/` 下，使用 `./.opencode/tools/<name>`
4. 如果脚本在 Skill 目录下，使用 skill 工具调用（`@skillname`），
   而不是直接用 bash 执行

### 禁止的做法
- 不要假设当前目录就是项目根目录
- 不要在执行脚本后停留在子目录而不返回
- 不要使用 `cd <dir> && ./script` 然后期望下一轮对话还在原目录

### 常见脚本位置
- 自定义工具：`./.opencode/tools/`
- 项目脚本：`./scripts/`（项目根目录）
- Skill 脚本：通过 `@skillname` 调用，不要直接用 bash 执行

### 路径快速参考
```
项目根目录:   <opencode启动目录>
配置文件:     ./.opencode/config.json
项目规则:     ./AGENTS.md
自定义工具:   ./.opencode/tools/
项目 Skill:   ./.opencode/skills/
全局 Skill:   ~/.opencode/skills/ 或 ~/.config/opencode/skills/
```
```

---

## 4.7 诊断路径问题的调试方法

当 agent 报告找不到文件或脚本时，按以下顺序排查：

```text
1. 让 agent 执行 `pwd` → 确认当前工作目录
2. 让 agent 执行 `ls -la` → 确认当前目录内容
3. 让 agent 执行 `ls -la <期望的路径>` → 确认目标文件是否存在
4. 检查 .opencode/config.json 中 tool 的 command 路径
5. 检查 SKILL.md 中描述的路径是否以 skill 目录为原点
6. 检查脚本是否有执行权限（ls -l 看权限位）
7. 检查 .gitignore 是否排除了相关目录（影响 glob/grep）
```

### 实用诊断 prompt

```text
请帮我诊断路径问题：
1. 先执行 `pwd` 告诉我当前目录
2. 执行 `ls -la` 列出当前目录内容
3. 检查以下路径是否存在：
   - ./.opencode/config.json
   - ./AGENTS.md
   - ./.opencode/tools/
   - ./scripts/
4. 如果我要执行 <script-name>，正确的绝对路径是什么？
```
