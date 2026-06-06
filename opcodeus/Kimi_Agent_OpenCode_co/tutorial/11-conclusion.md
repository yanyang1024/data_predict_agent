# 第 11 章 总结与下一步

> 适用版本：OpenCode v1.14.32 / v1.15.13

本章汇总本教程的核心要点，提供面向研发团队的落地建议，并指引后续学习路线。

---

## 11.1 核心建议：研发人员应该带走什么

经过前面章节的学习，以下 10 条建议是你在实际工作中最应该记住的要点：

### 基础认知（第 1-3 条）

**1. Agent 不是模型，而是运行时中的决策循环。**

Coding Agent 的核心不是生成代码的能力，而是"观察 → 决策 → 执行 → 验证"的完整循环。OpenCode 的 Agent 通过 Tool Call 与文件系统、Shell、LSP 等工具交互，模型只是决策引擎的一部分。理解这一点，才能正确评估 Agent 的能力和边界。

**2. Coding Agent 的关键能力不是"写"，而是"查、改、跑、验、审、回滚"。**

一个成熟的 Coding Agent 工作流应该覆盖完整闭环：
- **查**：代码探索（`read_file`、`glob`、`find`）
- **改**：精准编辑（`edit_file`、`apply_patch`）
- **跑**：运行测试（`bash` 执行测试命令）
- **验**：验证结果（检查输出、对比预期）
- **审**：代码审查（自我审查或交叉审查）
- **回滚**：错误恢复（`/undo`、Git 回退）

缺少任何一个环节，Agent 的输出质量都会显著下降。

**3. OpenCode 的核心学习对象是模块边界：session、tool、permission、agent、snapshot。**

与其花大量时间研究模型 prompt 技巧，不如先理解 OpenCode 的五大核心模块：

| 模块 | 作用 | 关键掌握点 |
|------|------|-----------|
| Session | 会话状态管理 | `/new` 创建、`/load` 切换、持久化机制 |
| Tool | 工具调用体系 | 内置工具（read/edit/bash 等）、自定义 Tool、MCP Server |
| Permission | 权限控制 | 三层权限（ask/allow/deny）、路径级粒度、环境变量覆盖 |
| Agent | 智能体配置 | 多 Agent 协作、模式（primary/subagent）、模型绑定 |
| Snapshot | 变更快照 | 自动恢复点、`/undo` 回滚、与 Git 的关系 |

### 团队落地（第 4-6 条）

**4. 团队落地先做权限治理，再谈效率提升。**

在团队范围推广 OpenCode 之前，务必先建立权限基线：

```json
// 推荐的最小安全配置（opencode.json）
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "edit": "ask",
    "bash": {
      "*": "ask",
      "rm -rf *": "deny",
      "sudo *": "deny",
      "pkill *": "deny",
      "git reset *": "deny",
      "git clean *": "deny"
    }
  }
}
```

权限配置是项目级配置，应随代码仓库共享，确保团队内所有成员使用一致的安全策略。

**5. 永远用 Git 做主版本控制，OpenCode 的 `/undo` 只是辅助。**

Snapshot 机制适合快速回滚最近的几次变更，但它不能替代 Git：
- Snapshot 的保留策略受限于 `OPENCODE_DISABLE_PRUNE` 设置，旧 snapshot 可能被清理
- Git 提供完整的变更历史、分支管理和审计追踪
- 重要里程碑（功能完成、发布前）必须执行 `git commit`

**最佳实践**：将 Agent 的工作流与 Git 工作流结合——Agent 完成一个逻辑单元后，由开发者审查并手动提交。

**6. 不要让 Agent 执行广义 kill / destructive git / rm -rf 类命令。**

这类命令已在多个 GitHub Issues 中被报告为高风险操作：

| 命令类型 | 风险 | 相关 Issue |
|---------|------|-----------|
| `pkill -f <pattern>` | 可能杀死 OpenCode 自身进程，导致 tool call hang | [#9082](https://github.com/anomalyco/opencode/issues/9082) |
| `rm -rf /path` | 不可逆的数据删除 | 通用安全风险 |
| `git reset --hard` | 丢失未提交的工作 | 通用安全风险 |
| `git clean -fd` | 删除未跟踪文件 | 通用安全风险 |

在 `opencode.json` 中显式 `deny` 这些命令模式，并在 Prompt 中重复约束。

### 工作流建设（第 7-10 条）

**7. 把 Plan / Explore / Review 变成默认工作流，把 Build 当成受控执行阶段。**

不要一上来就让 Agent 写代码。建立如下默认工作流：

```
Plan（人主导） → Explore（Agent 辅助） → Review Plan（人确认） → Build（Agent 执行） → Verify（Agent + 人） → Review Code（Agent + 人）
```

Build 阶段应该是"按已确认方案执行"，而不是"边想边做"。

**8. 理解配置分层体系，避免"配置污染"。（v1.15.13 新增）**

OpenCode 的配置是分层合并的（第 6 章），不理解的开发者容易遇到"为什么我的配置没生效"或"为什么全局配置被覆盖了"的问题。记住以下优先级：

```
内置默认 < 远程 < 全局(~/.config) < OPENCODE_CONFIG < 项目(./opencode.json) < .opencode/ < OPENCODE_CONFIG_CONTENT
```

项目级配置应只包含项目特定的设置（如 `instructions`、`mcp` 服务器），个人偏好（如主题、API Key）放在全局配置。

**9. 重视路径问题，它是跨平台稳定性的最大威胁。（v1.15.13 新增）**

OpenCode 的路径解析机制存在多个已知坑点（第 7 章），核心原则：

- **绝不在 Tool/Skill 中使用 `process.cwd()`** —— 在 Desktop 模式下它是 `/`，在 Web Daemon 模式下是启动目录
- **始终使用 `context.directory` 或 `context.worktree`** —— 这是 OpenCode 提供的稳定路径引用
- **对 Skill 资源使用 `skill_resource` 工具** —— 避免相对路径解析到错误位置

**10. 根据场景选择合适的版本和模型。（v1.15.13 新增）**

OpenCode 和底层模型都在快速迭代，建议：

- **版本选择**：v1.15.13 修复了 v1.14.x 中的多个关键问题（`OPENCODE_CONFIG_CONTENT` 优先级、LSP 权限提示、session 目录持久化），新用户直接从此版本开始
- **模型路由**：日常编码用 Sonnet 级别模型（速度快、成本低），复杂架构分析和 Review 用 Opus/GPT-5.1-Codex 级别模型（推理深度更强）
- **关注 Changelog**：OpenCode 的迭代速度很快，定期查看 [Releases 页面](https://github.com/anomalyco/opencode/releases) 了解新特性和已知问题修复

---

## 11.2 常见陷阱速查表

| 陷阱 | 症状 | 解决方案 |
|------|------|---------|
| Agent 修改了不该改的文件 | diff 中出现无关文件变更 | Review 模板中明确检查"无关改动"，权限中限制编辑范围 |
| 测试通过后才发现类型错误 | 缺少 typecheck 步骤 | 验证模板要求测试通过后运行 `tsc --noEmit` / `lint` |
| 配置修改不生效 | 全局配置被项目配置覆盖 | 使用 `/config` 命令查看合并后的配置，理解优先级规则 |
| Skill 中的相对路径解析失败 | `File not found` 错误 | 使用 `skill_resource` 工具或 opencode-skillful 插件 |
| Desktop 模式下 Tool 找不到文件 | `process.cwd()` 返回 `/` | Tool 中使用 `context.worktree` 替代 `process.cwd()` |
| 子 Agent 找不到 Skill | `Skills not found` 错误 | 使用全局 Skill 或在 task() 中显式传递路径 |
| CI 中配置行为不一致 | 全局配置干扰 | 使用 `OPENCODE_DISABLE_GLOBAL_CONFIG=1` + `OPENCODE_CONFIG_CONTENT` 完全隔离 |

---

## 11.3 下一步学习路线

完成本教程后，你可以根据角色和兴趣选择以下学习方向：

### 方向 A：深度使用（适合大多数研发人员）

1. **多 Agent 协作**：学习如何配置多个 Agent，让不同 Agent 负责不同任务（如编码、测试、文档）
2. **自定义 Tool 开发**：学习使用 `@opencode-ai/plugin` SDK 开发项目特定的 Tool
3. **MCP Server 集成**：学习连接外部 MCP Server（如数据库、文档系统）扩展 Agent 能力
4. **高级配置技巧**：掌握 `{env:}` 和 `{file:}` 变量替换、多 Provider 配置、模型变体（Variants）

### 方向 B：团队推广（适合 Tech Lead / 架构师）

1. **团队配置规范**：制定团队统一的 `opencode.json` 模板和权限策略
2. **CI/CD 集成**：将 OpenCode 接入 CI 流水线，实现自动化代码审查和文档生成
3. **知识库建设**：使用 Skill 系统建立团队知识库（编码规范、架构决策、常见模式）
4. **安全审计**：建立 Agent 操作审计机制，定期审查权限配置和使用日志

### 方向 C：底层研究（适合高级用户和贡献者）

1. **源码阅读**：阅读 OpenCode 开源代码，理解 Tool 调用循环、Session 管理、Snapshot 机制
2. **自定义 Agent 模式**：开发非标准 Agent 模式（如代码审查专用 Agent、文档生成专用 Agent）
3. **Plugin 开发**：开发可复用的 Plugin，发布到团队或社区
4. **贡献上游**：参与 OpenCode 开源项目，提交 Issue 和 PR

### 推荐学习资源

| 资源 | 地址 | 用途 |
|------|------|------|
| OpenCode 官方文档 | https://open-code.ai/en/docs | 权威参考，覆盖所有功能 |
| GitHub 仓库 | https://github.com/anomalyco/opencode | 源码、Issues、Releases |
| 配置系统文档 | https://open-code.ai/en/docs/config | 配置项完整参考 |
| 模型配置文档 | https://opencode.ai/docs/models/ | 模型选择和多 Provider 配置 |
| 自定义工具文档 | https://opencode.ai/docs/custom-tools/ | Tool 开发指南 |
| MCP Server 文档 | https://open-code.ai/en/docs/mcp-servers | MCP 集成指南 |
| 路径机制研究 | 第 7 章 | 本教程的路径坑点详解 |
| 配置系统研究 | 第 6 章 | 本教程的配置分层详解 |

---

## 11.4 版本演进与持续关注

OpenCode 正在快速迭代，以下是 v1.14.32 → v1.15.13 的关键演进，以及值得关注的未来方向：

### v1.15.13 关键改进

| 改进项 | 影响 |
|--------|------|
| `OPENCODE_CONFIG_CONTENT` 优先级修复 | 内联配置现在确实具有最高用户优先级 |
| LSP 权限提示增强 | LSP 相关操作有更清晰的权限确认流程 |
| Session 目录持久化 | 现有 session 请求使用持久化目录，减少路径漂移问题 |
| 配置向上加载修复 | 从打开位置向上加载配置，目录特定设置更可预测 |
| 后台 Agent 推送 | 支持后台 Agent 的推送更新 |

### 持续关注领域

- **多模态支持**：图像附件处理、视觉理解能力的增强
- **Agent 间协作**：subagent 和 background agent 的协作模式改进
- **配置管理**：更灵活的配置继承和覆盖机制
- **安全性**：权限系统的持续完善、destructive 命令的更强约束

建议定期查看 [OpenCode Releases](https://github.com/anomalyco/opencode/releases) 页面，关注与你的使用场景相关的变更。

---

## 11.5 写在最后

Coding Agent 不是替代开发者的工具，而是增强开发者能力的伙伴。它的价值不在于"自动生成代码"，而在于：

- **降低探索成本**：快速理解陌生代码库
- **减少重复劳动**：自动化模板化代码的编写
- **提高验证效率**：自动化测试运行和类型检查
- **增强代码质量**：系统性的 Review 和边界条件检查

但最终的决策权、代码质量和架构方向，仍然掌握在人手中。用好 Agent 的关键不是"让 Agent 做更多"，而是"在人机协作中找到最佳分工"。

祝你在 OpenCode 的使用中效率倍增，代码质量更上一层楼。

---

## 参考资料

### 官方文档

- OpenCode 官方文档 — Introduction: https://open-code.ai/en/docs
- OpenCode 官方文档 — Agents: https://opencode.ai/docs/agents/
- OpenCode 官方文档 — Tools: https://opencode.ai/docs/tools/
- OpenCode 官方文档 — Permissions: https://opencode.ai/docs/permissions/
- OpenCode 官方文档 — Rules: https://opencode.ai/docs/rules/
- OpenCode 官方文档 — Commands: https://opencode.ai/docs/commands/
- OpenCode 官方文档 — Custom Tools: https://opencode.ai/docs/custom-tools/
- OpenCode 官方文档 — MCP Servers: https://open-code.ai/en/docs/mcp-servers
- OpenCode 官方文档 — Config: https://open-code.ai/en/docs/config
- OpenCode 官方文档 — Models: https://opencode.ai/docs/models/

### GitHub 仓库与 Issues

- [anomalyco/opencode](https://github.com/anomalyco/opencode) — 主仓库
- Issue #9082 — pkill -f command causes tool call hang
- Issue #11628 — OPENCODE_CONFIG_CONTENT priority fix
- Issue #16897 — Config hierarchy defect
- Issue #17101 — Agent resolves Skill relative paths as CWD
- Issue #17094 — Agent resolves Skill resource paths as CWD
- Issue #9077 — Desktop tool execution from `/`
- Issue #10477 — Custom tool cannot get project directory
- Issue #16528 — Symlink directory TUI blank response

### 本教程相关章节

- 第 6 章 — OpenCode 配置系统详解
- 第 7 章 — 路径机制与坑点
- 第 8 章 — 权限管理与安全实践
- 第 9 章 — 多 Agent 与模型协作
- 第 10 章 — Prompt 模板与实战咒语
