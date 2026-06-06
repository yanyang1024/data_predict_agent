# 7. Prompt 模板与教程结语

---

## 7.1 可直接复用的 Prompt 模板

### 7.1.1 只读探索模板

```text
请只读探索，不要修改文件，不要运行会改变状态的命令。

目标：<描述任务>

请输出：
1. 相关入口文件
2. 调用链
3. 数据结构 / API / 配置位置
4. 需要验证的假设
5. 建议的最小修改方案
```

### 7.1.2 开始实现模板

```text
请按已确认方案做最小实现。

约束：
- 不要提交代码。
- 不要运行 pkill/killall/taskkill/rm -rf/git reset/git clean。
- 不要启动长时间后台服务。
- 优先 edit/apply_patch，不要整体 rewrite 大文件。
- 修改完成后先给出 diff 摘要，再运行最小相关测试。
```

### 7.1.3 验证模板

```text
请验证本次改动。

步骤：
1. 先看 git diff --stat 和 git diff。
2. 运行最小相关测试。
3. 如果最小测试通过，再运行 typecheck/lint。
4. 如果失败，先解释失败，不要扩大修改面。
5. 最后输出已验证项、未验证项和风险。
```

### 7.1.4 Review 模板

```text
请以代码审查者身份审查本次 diff，不要修改文件。
重点看：
1. 正确性
2. 边界条件
3. 并发/幂等/事务风险
4. 安全风险
5. 测试覆盖
6. 是否有无关改动
```

### 7.1.5 路径诊断模板

当 agent 报告找不到文件或脚本时使用：

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

### 7.1.6 配置检查模板

```text
请帮我确认当前 OpenCode 配置：
1. 当前使用的 provider 和 model 是什么？
2. 配置是从哪个层级加载的（全局/用户/项目）？
3. 权限配置中，edit 和 bash 的当前设置是什么？
4. 如果我想切换到 <provider>/<model>，应该怎么操作？
```

---

## 7.2 教程结语：研发人员应该带走什么

1. **Agent 不是模型，而是运行时中的决策循环。** 模型的能力只是其中一环，session 管理、tool registry、permission gate 才是落地关键。

2. **Coding agent 的关键能力不是"写"，而是"查、改、跑、验、审、回滚"。** 让 agent 安全地改代码，比让 agent 写出漂亮代码更重要。

3. **OpenCode 的核心学习对象是模块边界：** session、tool、permission、agent、snapshot。** 理解这些模块的职责和交互，才能用好这个工具。

4. **团队落地先做权限治理，再谈效率提升。** 从保守的 `opencode.json` 基线开始，逐步放宽。

5. **永远用 Git 做主版本控制，OpenCode 的 `/undo` 只是辅助。** 每次让 agent 大改前，先建 Git checkpoint。

6. **不要让 agent 执行广义 kill / destructive git / rm -rf 类命令。** 在 permission 中 deny，在 AGENTS.md 中明确禁止。

7. **把 Plan / Explore / Review 变成默认工作流，把 Build 当成受控执行阶段。** 不要一上来就让 agent 改代码。

8. **理解配置层级的覆盖规则。** 全局 → 用户 → 项目，逐 key 合并。模型选择和 API Key 应该在正确的层级配置。

9. **路径问题是工程实践中最常见的坑。** 始终明确当前工作目录，使用绝对路径或相对于项目根目录的完整路径。

---

## 7.3 延伸阅读与参考资料

### 论文与范式

- ReAct: Synergizing Reasoning and Acting in Language Models (Yao et al., 2022)
- SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering (Princeton NLP, 2024)
- Function Calling / Tool Calling: OpenAI API 官方文档

### OpenCode 官方资源

- OpenCode 官方文档：Introduction, Agents, Tools, Permissions, Rules, Commands, Custom Tools, MCP Servers
- `anomalyco/opencode` GitHub 仓库：`session/`、`tool/`、`permission/`、`agent/`、`snapshot/` 相关源码目录

### 相关 Issue（路径与坑点参考）

- `pkill -f command causes tool call hang in opencode TUI #25664`
- `Snapshot .nothrow causes silent data loss #10589`
- `stale snapshot index.lock breaks Modified Files and undo #22275`
- `Reverting a message does not revert changed files #20638`
- `running scripts continue after interrupt #3057`
- `LSP processes remain orphaned #18632`

### 配置参考

- OpenCode Configuration Schema: `https://opencode.ai/config.json`
- 各 LLM Provider API 文档：Anthropic、OpenAI、Azure、Google、Ollama、OpenRouter
