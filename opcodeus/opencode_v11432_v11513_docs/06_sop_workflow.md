# 06. 面向研发人员的 OpenCode 使用 SOP

> 适用版本：`v1.14.32` / `v1.15.13`。  
> 目标：把 OpenCode 当成一个受控开发协作者，而不是一个无限权限的自动脚本。

## Phase 0：进入工作前先建安全边界

```bash
git status --short
git switch -c ai/<ticket-or-task>
# 如果当前已有未提交工作，优先 stash 或 commit
# git stash push -u -m "before opencode <task>"
# 或 git add -A && git commit -m "checkpoint: before opencode <task>"
```

建议规则：

1. 每个独立任务一个分支或 worktree。
2. 不在主分支直接让 agent 改代码。
3. 不把 `/undo` 当唯一回滚机制。
4. 禁止 agent 自动 `git push`、`git reset --hard`、`git clean -fd`。
5. 广义 kill 命令必须人工确认。

## Phase 1：初始化项目规则

在项目根目录启动：

```bash
opencode
```

然后执行：

```text
/init
```

检查生成或已有的 `AGENTS.md`，补充：

- 项目结构；
- 包管理器；
- 测试命令；
- lint / typecheck 命令；
- 分支和提交规范；
- 禁止事项；
- 常见坑；
- 关键目录说明；
- 路径基准：所有项目路径默认相对 git worktree root。

提交它：

```bash
git add AGENTS.md opencode.jsonc .opencode/
git commit -m "docs: add opencode project rules"
```

## Phase 2：先 Plan，不要直接 Build

第一次给任务时，要求 OpenCode 只做计划：

```text
请先使用 Plan 模式。不要修改文件，不要运行会改变状态的命令。

任务：修复用户删除 note 后没有 soft delete 的问题。

请输出：
1. 你需要查看的文件列表
2. 可能的调用链
3. 最小实现方案
4. 需要补充的测试
5. 风险点和不确定点
6. 开始改代码前需要我确认的问题
```

适合让只读子代理探索：

```text
@explore 请只读分析 note 删除链路，找出 API、DB schema、测试入口，不要修改任何文件。
```

## Phase 3：实现前先收敛范围

要求 agent 给出“修改计划 + 文件范围”：

```text
在开始修改前，请列出你计划改动的文件和每个文件的改动目的。
如果需要新文件，请说明为什么不能改已有文件。
不要运行长时间后台服务，不要 kill 进程，不要提交代码。
```

检查：

- 是否涉及过多无关文件；
- 是否要重写大文件；
- 是否要引入新依赖；
- 是否要修改配置/迁移/脚本；
- 是否需要数据迁移；
- 是否需要人类确认产品行为。

## Phase 4：Build 模式做最小 patch

```text
切换到 Build 模式后，请按刚才确认的方案做最小修改。
要求：
- 优先 edit / apply_patch，不要整体 rewrite 大文件。
- 不要改无关格式。
- 不要自动提交。
- 每完成一个逻辑小步，说明改了什么以及下一步验证什么。
```

建议让 agent 每轮只改一个逻辑点：

```text
先只改 service 层，不要改 UI 和测试。改完后输出 diff 摘要。
```

## Phase 5：验证必须独立于实现

让 agent 跑最小验证：

```text
请先运行和本次改动最相关的最小测试。
如果失败，先解释失败原因，不要立刻扩大修改面。
然后再运行 lint / typecheck。
```

常见验证顺序：

```bash
git diff --stat
git diff
pnpm test <related-test>
pnpm typecheck
pnpm lint
```

验证规则：

- 先最小测试，再全量；
- 失败先定位，不要盲目改；
- 测试环境缺依赖时，不要让 agent 自动安装全局依赖；
- 不要让 agent 自动修所有 lint 格式导致大 diff；
- 对生成文件要先说明来源。

## Phase 6：人工 review + checkpoint

让 OpenCode 输出交接摘要：

```text
请总结本次变更：
1. 根因
2. 修改点
3. 新增/修改测试
4. 已运行验证命令和结果
5. 未覆盖风险
6. 建议 code review 重点
```

人工检查：

```bash
git diff
git add -p
git commit -m "fix: soft delete notes"
```

## Phase 7：让 Review 子代理审 diff

```text
@review 请审查当前 git diff，不要修改文件。
重点看：
1. 正确性
2. 边界条件
3. 并发/幂等/事务风险
4. 安全风险
5. 测试覆盖
6. 是否有无关改动
```

## Phase 8：收尾与知识沉淀

如果这次任务暴露出项目规则缺失，让 agent 帮你更新 `AGENTS.md` 或 docs：

```text
请根据本次踩坑，提出应该补充到 AGENTS.md 的规则。只输出建议文本，不要直接修改。
```

常见沉淀：

- 测试命令；
- monorepo 路径；
- 特定模块不能动的边界；
- 数据库迁移规则；
- 平台兼容问题；
- 发布/回滚流程；
- agent 经常找不到脚本的路径说明。

## 推荐工作流总览

```text
Git checkpoint
  -> /init + AGENTS.md
  -> Plan 只读分析
  -> Explore 子代理定位
  -> 人类确认改动范围
  -> Build 最小 patch
  -> 最小测试
  -> lint/typecheck
  -> Review 子代理审 diff
  -> 人类 git add -p + commit
```
