# 面向代码研发工程师的 Agent Skill 设计教程

这篇教程讨论的 **skill**，不是传统意义上的“技能标签”，也不是单个脚本，而是 agent 应用，例如 OpenCode、Claude Code、Codex 类编码 agent 中的一种 **可复用能力包**：它用自然语言说明任务意图、流程、约束和判断标准，并把脚本、参考资料、模板、校验器等资源组织成一个 agent 可按需加载、可执行、可迭代的目录。

一句话概括：

> **Skill 是“资源 + 流程 + 场景判断 + 验证机制”的抽象；它把人类在某类任务中的隐性经验，沉淀成 agent 可以在合适时机加载并执行的上下文结构。**

---

## 1. 什么是智能体应用？

在传统对话应用里，用户问问题，模型给答案。智能体应用更进一步：它不仅回答，还能 **读取环境、调用工具、执行动作、观察结果、再调整策略**。

以编码 agent 为例，OpenCode 官方把自己定位为开源 AI coding agent，并支持终端界面、桌面应用和 IDE 扩展；它还区分 primary agents 与 subagents，并允许用 prompt、模型和工具权限配置不同 agent 的职责。比如 Build agent 适合做有写文件和执行命令权限的开发工作，Plan agent 更适合只分析和规划、不直接改代码的场景。([OpenCode][1])

一个智能体应用通常有五个核心部分：

1. **对话入口**：用户用自然语言描述目标，而不是填写固定表单。
2. **上下文系统**：系统提示、项目说明、AGENTS.md、skill、当前任务历史、文件内容、日志、测试结果等。
3. **工具系统**：读文件、写文件、grep、运行测试、访问浏览器、调用 API、查询数据库、打开 issue、发起 PR 等。
4. **决策循环**：根据目标选择下一步动作，执行后根据反馈修正。
5. **个性化后处理**：同一个任务结果可以按用户、团队、代码库、业务场景进行不同格式和粒度的输出。

所以，智能体应用不是“一个更会聊天的 UI”，而是：

> **一个以自然语言为入口、以工具执行为手脚、以上下文为工作记忆、以反馈循环为控制机制的应用运行时。**

---

## 2. Skill 的定位：它到底是什么？

Agent Skills 官方规范将 skill 描述为一种轻量开放格式：一个 skill 本质上是包含 `SKILL.md` 的目录，`SKILL.md` 里至少包含 `name` 和 `description`，并可以附带脚本、参考资料、模板等资源；agent 通过渐进式加载机制，先只读取 skill 名称和描述，需要时再加载完整说明和相关资源。([Agent Skills][2])

从工程角度看，skill 可以拆成五层：

| 层级  | 作用                      | 例子                                                     |
| --- | ----------------------- | ------------------------------------------------------ |
| 触发层 | 告诉 agent 什么时候该用这个 skill | “当用户要排查线上订单状态不一致时使用”                                   |
| 指令层 | 告诉 agent 如何完成任务         | 排查顺序、先看哪些日志、哪些表不能直接改                                   |
| 资源层 | 给 agent 可读取的知识          | 业务字段说明、API 文档、数据库表关系、错误码                               |
| 动作层 | 给 agent 可执行的工具          | `scripts/collect_trace.py`、`scripts/validate_patch.sh` |
| 验证层 | 告诉 agent 如何判断完成         | 测试命令、diff 检查、输出模板、人工确认点                                |

因此 skill 不是“提示词合集”，而是一个 **面向任务场景的 agent 能力模块**。

更具体地说：

> **Skill 是对资源流程的抽象。**
> 它用自然语言描述“在什么业务场景下，如何组织哪些资源，执行哪些动作，遇到哪些反馈时如何调整，并用什么标准验证结果”。

这也是 skill 和传统代码资产最大的区别：传统代码主要抽象“确定性计算逻辑”，skill 抽象的是“人在真实任务中如何组织信息、工具、判断和验证”。

---

## 3. Skill 与传统脚本、应用服务、workflow 的区别

很多工程师第一次接触 skill 时，会把它理解成“脚本的另一种包装”。这不准确。Skill 可以包含脚本，但它的核心不是脚本，而是 **让 agent 知道什么时候、为什么、如何使用这些脚本，以及脚本结果如何影响下一步决策**。

| 对比对象           | 它是什么               | Skill 与它的区别                                                |
| -------------- | ------------------ | ---------------------------------------------------------- |
| 脚本             | 输入参数，执行确定性逻辑，输出结果  | Skill 可以调用脚本，但还会说明触发条件、上下文读取、异常分支、验证方式                     |
| 应用服务           | 长期运行的 API 或 Web 服务 | Skill 通常不是常驻服务，而是 agent 运行时按需加载的能力说明和资源包                   |
| Workflow       | 预定义步骤或 DAG         | Skill 可以包含 workflow，但允许 agent 根据上下文跳步、补查资料、处理例外            |
| Custom command | 用户手动触发的固定 prompt   | Skill 更像“可自动选择的专业知识包”，不一定需要用户显式调用                          |
| Agent          | 具有角色、模型、工具权限的执行主体  | Skill 是 agent 可加载的能力模块；一个 agent 可以用多个 skill                |
| Tool / MCP     | 外部能力接口             | Skill 告诉 agent 什么时候用哪个工具、怎么组合、如何解释结果                       |
| AGENTS.md      | 项目级长期规则            | Skill 是场景级能力；AGENTS.md 更像项目 README for agents，skill 更像任务手册 |

OpenCode 的 custom commands 是为重复任务定义可执行 prompt，例如 `/test`；而 skills 是通过 `skill` 工具按需加载的可复用说明，agent 会先看到可用 skill 的名称和描述，再在需要时加载完整内容。([OpenCode][3])

可以用一句话区分：

> **脚本解决“怎么计算”，服务解决“怎么提供能力”，workflow 解决“固定步骤怎么跑”，skill 解决“agent 面对一类真实任务时，该如何组织知识、工具、判断和验证”。**

---

## 4. Skill 与 workflow 的关键差异

Workflow 通常强调 **流程编排**：第 1 步做什么，第 2 步做什么，失败走哪个分支。它适合确定性强、状态边界清晰的业务，例如 CI/CD、审批流、数据同步、定时任务。

Skill 强调 **场景能力**：它可以包含流程，但不把流程视为唯一真理。因为 agent 面对的是自然语言请求，用户需求经常不完整、上下文经常缺失、环境反馈经常意外。Skill 要告诉 agent：

* 先判断任务是否属于这个场景。
* 先找哪些信息，不要一上来改代码。
* 哪些步骤必须固定，哪些步骤可以灵活。
* 哪些工具输出是可信证据，哪些只是线索。
* 什么情况下停止、询问用户或升级人工确认。

举例：

```text
workflow:
1. 查询订单表
2. 查询支付表
3. 对比状态
4. 生成报告

skill:
当用户反馈“订单支付成功但订单未生效”时：
- 先确认订单号、支付渠道、环境和时间窗口。
- 读取 references/order-state-machine.md，理解订单状态流转。
- 用 scripts/collect_order_trace.py 拉取订单、支付、消息队列、回调日志。
- 如果支付成功但订单仍 pending，优先检查 webhook 幂等锁和消息消费失败。
- 不要直接修改生产数据；只能给出修复建议或生成经审批的 SQL 草案。
- 最终输出必须包含证据链、影响范围、建议修复和回归验证步骤。
```

前者是固定流程；后者是 **可被 agent 执行的场景化操作手册**。

---

## 5. 为什么现在需要 skill：从“塞满上下文”到“按需激活”

早期很多团队使用大模型优化项目代码时，常见做法是：

> 把尽可能多的项目代码、README、接口文档、错误日志一股脑塞进上下文，然后让模型修改。

这会带来几个问题：

1. **上下文噪声过大**：模型看到很多与当前任务无关的信息，反而难以聚焦。
2. **成本高**：每轮都携带大量 token。
3. **信息不新鲜**：模型读到的是某一刻的快照，缺少执行反馈。
4. **项目规则不稳定**：每次靠用户临时描述，容易遗漏团队约定。
5. **难以复用**：一次成功排查没有沉淀成下一次能自动使用的资产。

现在更好的方式是 **分层上下文 + 按需加载**。

以 AGENTS.md 为例，它被设计成面向 coding agents 的项目说明文件，类似“给 agent 的 README”，用于放置构建命令、测试方式、代码风格、项目约定、安全注意事项等内容；大型 monorepo 还可以使用嵌套的 AGENTS.md，让距离当前文件最近的说明生效。([AGENTS][4])

OpenCode 的 `/init` 也会扫描项目并创建或更新 `AGENTS.md`，重点记录未来 agent 会反复需要的构建、测试、架构、项目约定和特殊注意事项；OpenCode 还支持通过 `opencode.json` 引入额外 instruction 文件，或者在 AGENTS.md 中显式要求 agent 在需要时读取外部文件。([OpenCode][1])

所以新的上下文结构更像这样：

```text
稳定全局层：
- 系统提示
- agent 权限与角色
- 全局个人偏好

项目常驻层：
- AGENTS.md
- opencode.json instructions
- 项目级 coding conventions

任务临时层：
- 用户当前需求
- 当前文件 diff
- 相关源码片段
- 相关日志和测试结果

按需能力层：
- skill name + description 先常驻
- 命中后加载 SKILL.md
- 需要时再加载 references、assets、scripts

动态反馈层：
- grep / read / test / lint / browser / API / DB / logs 的执行结果
```

核心变化是：

> 不再试图让模型“一开始就知道所有东西”，而是让 agent 拥有一套 **发现、加载、执行、反馈、修正** 的机制。

Skill 正是这个机制中的“场景能力层”。

---

## 6. 三种知识：模型内化知识、上下文激活知识、环境反馈知识

设计 skill 时，必须理解 agent 的“知识来源”不是单一的。

### 6.1 模型参数内化的知识

这是模型训练时学到的通用知识，例如 TypeScript、React、PostgreSQL、HTTP、常见设计模式、调试方法、代码风格等。

它的优点是广、快、便宜。缺点是：

* 不知道你的私有代码库。
* 不知道你们团队的历史约定。
* 不知道线上真实状态。
* 容易用“看起来合理”的通用经验猜测特定项目。

所以，skill 不应该重复解释“什么是 REST API”“什么是单元测试”这类模型已经知道的内容，而应该补充模型不知道、但任务成败高度依赖的信息。

### 6.2 上下文结构带来的环境激活知识

这是运行时被放入上下文的信息，例如：

* AGENTS.md
* 当前用户需求
* 当前文件内容
* `SKILL.md`
* `references/schema.md`
* 团队 runbook
* 业务状态机说明
* API 错误码表

这类知识的特点是 **可控、可审计、可版本化**。Skill 的主要作用，就是把这类知识结构化，并告诉 agent 何时加载。

Agent Skills 规范明确采用渐进式披露：启动时只加载 skill 的 name 和 description；任务匹配时加载完整 `SKILL.md`；脚本、参考文件、模板等资源只在需要时加载。([Agent Skills][2])

### 6.3 环境动作和反馈带来的动态决策参考

这是 agent 执行动作后得到的反馈，例如：

* `npm test` 的失败堆栈
* `git diff` 的结果
* 线上日志中的 trace
* API 返回值
* 数据库查询结果
* 浏览器控制台错误
* CI 报告

这类知识不是“提前写进 skill”的，而是由 skill 指导 agent 如何获取、如何解释、如何用于下一步决策。

因此，一个好的 skill 不是只写“怎么做”，还要写“怎么验证”和“看到什么反馈时如何调整”。

---

## 7. ReAct 决策循环：为什么 skill 要围绕反馈设计

ReAct 是 “Reasoning + Acting” 的缩写，原始论文提出让语言模型交错地产生推理轨迹和任务相关动作：推理帮助更新计划、跟踪异常，动作让模型访问外部环境获得新信息。([arXiv][5])

在工程实践中，不需要要求模型输出隐藏思维链；更重要的是让 agent 形成可审计的执行循环：

```text
目标理解
  ↓
选择下一步观察对象
  ↓
执行动作：读文件 / grep / 运行测试 / 查日志 / 调 API
  ↓
观察反馈
  ↓
更新计划
  ↓
继续执行或停止
```

Skill 对这个循环的作用是：

1. **约束观察顺序**：先看状态机文档，再查订单日志。
2. **约束动作边界**：生产环境只能读，不能直接写。
3. **提供解释框架**：某个错误码代表支付回调重复，而不是支付失败。
4. **提供修正策略**：测试失败时先更新 fixture，再改业务逻辑。
5. **提供停止条件**：所有回归测试通过、证据链完整、输出包含风险说明。

也就是说：

> Skill 不是替 agent 做完所有决策，而是把专家经验变成 agent 决策循环中的“局部策略函数”。

---

## 8. Skill 的标准目录结构

Agent Skills 规范中的基本结构是一个目录，至少包含 `SKILL.md`，可选包含 `scripts/`、`references/`、`assets/` 等目录。`SKILL.md` 必须包含 YAML frontmatter 和 Markdown 正文；`name` 与 `description` 是必填字段。([Agent Skills][6])

推荐工程化目录如下：

```text
order-triage/
├── SKILL.md
├── references/
│   ├── order-state-machine.md
│   ├── payment-provider-errors.md
│   └── database-schema.md
├── scripts/
│   ├── collect_order_trace.py
│   ├── summarize_logs.py
│   └── validate_report.py
├── assets/
│   └── incident-report-template.md
├── evals/
│   ├── trigger_queries.json
│   └── regression_cases.md
└── CHANGELOG.md
```

其中：

* `SKILL.md` 是入口，写最核心的触发条件、流程和注意事项。
* `references/` 放 agent 需要按需读取的详细文档。
* `scripts/` 放可重复、易错、需要确定性的逻辑。
* `assets/` 放报告模板、配置模板、示例文件等。
* `evals/` 放触发测试、回归案例和质量检查。
* `CHANGELOG.md` 记录 skill 迭代原因，便于团队 review。

OpenCode 支持把 skill 放在项目、全局以及 Claude/agents 兼容路径下，例如 `.opencode/skills/<name>/SKILL.md`、`~/.config/opencode/skills/<name>/SKILL.md`、`.agents/skills/<name>/SKILL.md` 等；OpenCode 会发现这些 skill，并通过原生 `skill` 工具按需加载。([OpenCode][7])

---

## 9. `SKILL.md` 应该怎么写？

OpenCode 和 Agent Skills 规范都要求 skill 名称使用小写字母、数字和单个连字符，且目录名与 `name` 匹配；description 应该说明 skill 做什么、什么时候使用，并足够具体以便 agent 正确触发。([OpenCode][7])

一个面向代码研发任务的 `SKILL.md` 可以这样写：

````markdown
---
name: order-triage
description: Use this skill when investigating order, payment, refund, fulfillment, or webhook state inconsistencies in this codebase. Use it when the user reports that an order is paid but not fulfilled, refunded but still active, webhook callbacks are duplicated, or order state differs across services.
---

# Order triage workflow

## Goal

Investigate order-related state inconsistencies without directly mutating production data.

## Required context

Before making code changes, gather:

1. Order ID or payment ID.
2. Environment: local, staging, production.
3. Time window.
4. User-visible symptom.
5. Whether the issue is reproducible.

## References

Read these only when relevant:

- `references/order-state-machine.md`: read when reasoning about order state transitions.
- `references/payment-provider-errors.md`: read when logs include provider error codes.
- `references/database-schema.md`: read before writing SQL or interpreting table joins.

## Available scripts

- `scripts/collect_order_trace.py`: collect logs and related records for one order.
- `scripts/summarize_logs.py`: summarize JSONL logs by trace ID.
- `scripts/validate_report.py`: validate the final report format.

## Workflow

1. Confirm the order identifier and environment.
2. Read the order state machine reference if the task involves state transitions.
3. Collect trace data:

   ```bash
   python scripts/collect_order_trace.py --order-id "$ORDER_ID" --env "$ENV" --window "$WINDOW" --output trace.json
````

4. Summarize logs:

   ```bash
   python scripts/summarize_logs.py trace.json --format markdown > trace-summary.md
   ```

5. Identify the most likely failure point:

   * payment callback
   * idempotency lock
   * message queue publish
   * async consumer
   * fulfillment API
   * database transaction rollback

6. Do not write production data. If data repair is needed, produce a reviewed SQL proposal only.

## Output format

Return:

* Symptom
* Evidence
* Probable root cause
* Impact scope
* Recommended fix
* Verification plan
* Risks and manual checks

````

注意这里的重点不是把所有订单系统知识都塞进 `SKILL.md`，而是把入口流程、资源索引和决策约束写清楚。详细状态机、错误码、数据库结构应该放到 `references/`，由 agent 在需要时读取。

---

## 10. Description 是 skill 的“触发器”，不是广告语

Skill 的 `description` 非常关键，因为 agent 通常只在启动时看到 skill 的 name 和 description；只有任务与 description 匹配时，才会加载完整 `SKILL.md`。Agent Skills 的优化指南明确指出，description 是 skill 触发的主要机制，写得过窄会漏触发，写得过宽会误触发。:contentReference[oaicite:10]{index=10}

一个差的 description：

```yaml
description: Helps with orders.
````

问题是太泛，agent 不知道什么时候必须用它。

一个好的 description：

```yaml
description: Use this skill when investigating order, payment, refund, fulfillment, or webhook state inconsistencies in this codebase. Use it when the user reports that an order is paid but not fulfilled, refunded but still active, webhook callbacks are duplicated, or order state differs across services.
```

它包含：

* 领域关键词：order、payment、refund、fulfillment、webhook。
* 用户意图：investigating state inconsistencies。
* 典型触发场景：paid but not fulfilled、duplicated callbacks。
* 项目限定：in this codebase。

优化 description 的方法是准备正负样本：

```json
[
  {
    "query": "用户反馈订单已经支付成功，但是后台还是 pending，帮我查一下",
    "should_trigger": true
  },
  {
    "query": "帮我给订单详情页加一个 loading skeleton",
    "should_trigger": false
  },
  {
    "query": "refund webhook 收到了两次，为什么订单状态被回滚了？",
    "should_trigger": true
  },
  {
    "query": "重构订单列表组件的样式",
    "should_trigger": false
  }
]
```

Agent Skills 文档建议用真实用户表达来测试触发，包括正式表达、口语化表达、带文件路径的表达、上下文丰富的表达，以及容易误触发的近似任务。([Agent Skills][8])

---

## 11. Skill 与 AGENTS.md 如何分工？

AGENTS.md 是项目级说明，skill 是场景级能力。

AGENTS.md 适合放：

```markdown
# AGENTS.md

## Project overview

This is a TypeScript monorepo using pnpm workspaces.

## Setup commands

- Install dependencies: `pnpm install`
- Run dev server: `pnpm dev`
- Run tests: `pnpm test`

## Code style

- TypeScript strict mode is required.
- Use functional React components.
- Avoid default exports in shared packages.

## Testing instructions

- Run `pnpm test --filter <package>` for package-level changes.
- Run `pnpm lint` before finalizing changes.
```

Skill 适合放：

```text
当排查订单状态不一致时：
- 先读订单状态机。
- 用 trace 脚本收集证据。
- 优先检查 webhook 幂等、MQ 消费、事务回滚。
- 不要直接修改生产数据。
- 输出必须包含证据链和验证计划。
```

可以这样理解：

| 文件                | 粒度    | 生命周期    | 典型内容                |
| ----------------- | ----- | ------- | ------------------- |
| `AGENTS.md`       | 项目级   | 长期稳定    | 构建、测试、代码风格、架构、通用约定  |
| `SKILL.md`        | 任务场景级 | 随业务经验迭代 | 排查流程、业务规则、工具使用、验证标准 |
| `references/*.md` | 专题知识  | 随领域变化更新 | 状态机、表结构、API 说明、错误码  |
| `scripts/*`       | 确定性动作 | 随工具变化更新 | 收集日志、格式转换、校验输出、生成报告 |

不要把所有 skill 内容都塞进 AGENTS.md。AGENTS.md 如果过长，就会变成新的“上下文垃圾场”。更好的做法是：AGENTS.md 保持项目级简洁，skill 负责场景化专业能力。

---

## 12. Skill 如何借由自然语言整合资源？

Skill 的强大之处在于，它用自然语言充当 **控制平面**。

传统程序通常这样写：

```python
if error_code == "PAYMENT_DUPLICATED":
    handle_duplicate_payment()
```

Skill 更像这样写：

```markdown
If the trace shows duplicated payment callbacks:
1. Check idempotency key generation.
2. Confirm whether the provider retries on non-2xx responses.
3. Inspect webhook handler logs before checking fulfillment logs.
4. Do not classify this as payment failure unless provider status is failed.
```

这段自然语言的价值在于：

* 它能覆盖用户表达的多样性。
* 它能连接多个系统资源。
* 它能告诉 agent 哪些线索更重要。
* 它能允许 agent 在不确定时查资料、跑工具、再判断。
* 它能把业务语义和工程动作连接起来。

所以 skill 的核心不是“自然语言替代代码”，而是：

> **自然语言负责组织任务语义、上下文选择和动作策略；脚本负责稳定执行高确定性步骤。**

---

## 13. 什么时候应该写脚本，什么时候只写指令？

Agent Skills 文档建议：当现有命令足够简单时，可以直接在 `SKILL.md` 中引用命令；当命令复杂、易错、需要重复使用时，应写成 `scripts/` 中的测试过的脚本。脚本应避免交互式输入，提供 `--help`，输出清晰错误，并尽量使用 JSON、CSV、TSV 等结构化输出。([Agent Skills][9])

经验规则：

| 场景                             | 做法                              |
| ------------------------------ | ------------------------------- |
| 纯文本总结、格式改写、代码 review checklist | 写在 `SKILL.md`                   |
| 需要查多个文件并做判断                    | `SKILL.md` 指导 agent 用 grep/read |
| 需要稳定解析日志、表格、PDF、JSONL          | 写脚本                             |
| 需要调用内部 API、聚合 trace、生成报告       | 写脚本                             |
| 需要严格校验输出格式                     | 写 validator 脚本                  |
| 有破坏性动作，如发版、删除、数据修复             | plan-validate-execute，必要时要求人工确认 |

好的脚本接口：

```bash
python scripts/collect_order_trace.py \
  --order-id ord_123 \
  --env production \
  --window "2026-05-17T10:00:00Z/2026-05-17T11:00:00Z" \
  --output trace.json
```

好的脚本输出：

```json
{
  "order_id": "ord_123",
  "environment": "production",
  "summary": {
    "payment_status": "succeeded",
    "order_status": "pending",
    "webhook_events": 2,
    "queue_publish": "failed",
    "consumer_errors": []
  },
  "evidence": [
    {
      "timestamp": "2026-05-17T10:22:11Z",
      "component": "payment-webhook",
      "message": "payment succeeded, enqueue fulfillment event failed",
      "trace_id": "trc_abc"
    }
  ],
  "next_hints": [
    "Check message queue publish permissions",
    "Inspect retry policy for payment-webhook"
  ]
}
```

Agent 看到这种结构化输出后，更容易进行下一步判断。

---

## 14. 如何在对话中和 LLM 一起迭代出一套处理逻辑？

最好的 skill 往往不是凭空写出来的，而是从真实任务中提炼出来的。

Agent Skills 最佳实践也强调：有效 skill 应该来自真实专业上下文，可以从一次 hands-on task 中提炼，记录成功步骤、用户纠正、输入输出格式和 agent 原本不知道的项目约定；也可以从内部文档、runbook、schema、code review、issue、历史修复中综合提炼。([Agent Skills][10])

推荐流程如下。

### 第一步：先完成一次真实任务

你可以对 agent 说：

```text
帮我排查这个问题：用户反馈支付成功但订单没生效。
订单号是 ord_123，环境是 staging，时间大概是今天 10:00-10:30。
先不要改代码，先帮我找证据链。
```

在过程中，你不断纠正：

```text
不要先看订单表。我们这个系统里支付 webhook 才是状态流转入口，先看 webhook 日志。
```

```text
这里不能用 /health 判断服务可用，/health 只代表进程活着。要看 /ready。
```

```text
如果 payment_events 里有 succeeded，但 orders 还是 pending，通常是 MQ publish 失败，不是支付失败。
```

这些纠正就是 skill 最有价值的内容。

### 第二步：让 LLM 复盘可复用模式

任务完成后，让 agent 总结：

```text
把我们刚才这次排查过程提炼成一个可复用 skill。
请分成：
1. 触发条件
2. 必要输入
3. 排查顺序
4. 需要读取的参考资料
5. 可脚本化的步骤
6. 常见误判
7. 输出模板
8. 验证标准
```

### 第三步：区分指令、参考资料和脚本

让 agent 继续拆：

```text
请判断哪些内容应该放进 SKILL.md，哪些应该放进 references/，哪些应该做成 scripts/。
原则：
- SKILL.md 只放每次都需要看到的核心流程和 gotchas。
- 详细状态机、表结构、错误码放 references/。
- 重复、易错、可确定执行的部分放 scripts/。
```

### 第四步：生成初版 skill

让 agent 生成目录和文件：

```text
请基于上面的设计生成 order-triage skill 的目录结构和 SKILL.md 初版。
要求：
- description 能覆盖用户不直接说“订单状态不一致”的情况。
- SKILL.md 不超过 500 行。
- references 文件只写目录和摘要，后续我们再补细节。
- scripts 先给出 CLI 接口设计，不要实现。
```

### 第五步：用真实任务回放测试

准备几条历史 issue 或真实工单：

```text
用这个 skill 回放下面 5 个历史问题。
请判断：
1. 是否应该触发 skill
2. 触发后是否加载了正确 reference
3. 是否产生了多余步骤
4. 是否遗漏了关键检查
5. 哪些内容需要更新到 gotchas
```

### 第六步：沉淀为版本化资产

把 skill 放入仓库：

```text
.opencode/
  skills/
    order-triage/
      SKILL.md
      references/
      scripts/
      evals/
      CHANGELOG.md
```

然后像代码一样 review：

* description 是否过宽？
* 有没有泄露内部密钥或敏感信息？
* 是否包含过时命令？
* 脚本是否可重复运行？
* 输出是否可审计？
* destructive action 是否需要人工确认？

---

## 15. 已沉淀的 skill 如何根据新需求迭代？

Skill 的迭代来源通常有六类：

| 现象              | 应该改哪里                                                 |
| --------------- | ----------------------------------------------------- |
| 应该触发但没触发        | 改 `description`，加入真实用户表达                              |
| 不该触发却触发了        | 收窄 `description`，加入排除条件                               |
| 触发后读了太多无关资料     | 拆 `references/`，在 `SKILL.md` 写清加载条件                   |
| agent 重复犯同一个错   | 加到 `Gotchas`                                          |
| agent 反复手写同一段命令 | 做成 `scripts/`                                         |
| 输出格式不稳定         | 加 `assets/template.md` 或 `scripts/validate_output.py` |

迭代时不要只看最终结果，也要看 execution trace：agent 是否走了弯路？是否读取了无关文件？是否运行了不必要命令？是否在缺少证据时过早下结论？Agent Skills 最佳实践也建议阅读 agent 执行 trace，而不是只看最终输出，因为低效步骤常常来自指令过于模糊、不适用或选项太多没有默认路径。([Agent Skills][10])

推荐每次迭代都写 changelog：

```markdown
# CHANGELOG

## 2026-05-17

### Changed
- Narrowed description to avoid triggering on UI-only order page changes.
- Added gotcha: `/health` does not validate database connectivity; use `/ready`.

### Added
- Added `references/webhook-retry-policy.md`.
- Added trigger eval for duplicated payment callbacks.

### Fixed
- Updated trace collection command to require `--window`.
```

---

## 16. Skill 设计最佳实践

### 16.1 从真实任务中提炼，不要从抽象概念开始

差的方式：

```text
帮我写一个支付系统排查 skill。
```

好的方式：

```text
这是我们最近 10 个支付相关故障的 issue、日志摘要、最终修复 PR。
请总结重复出现的排查路径、常见误判、必须验证的状态和应该脚本化的步骤。
```

Skill 的价值来自“模型不知道但你们知道”的部分，而不是通用最佳实践。

### 16.2 `SKILL.md` 保持短，把细节放到 references

`SKILL.md` 是被激活后整体加载的文件。Agent Skills 规范建议将主 `SKILL.md` 保持在 500 行以内，并把详细参考资料拆到单独文件中，只在需要时读取。([Agent Skills][6])

好的写法：

```markdown
Read `references/refund-state-machine.md` only when the issue involves refund status transitions.
```

差的写法：

```markdown
See references/ for more details.
```

前者告诉 agent 什么时候加载；后者只是丢了一个目录。

### 16.3 写 gotchas，而不是泛泛而谈

差的内容：

```markdown
Handle errors carefully.
Follow best practices.
Check logs.
```

好的内容：

```markdown
## Gotchas

- `/health` only checks whether the web process is alive. Use `/ready` to verify database and queue connectivity.
- `payment_status=succeeded` does not mean fulfillment has started. Fulfillment starts only after `OrderFulfillmentRequested` is published.
- The `orders.deleted_at` soft-delete filter is required for all user-facing order queries.
```

Gotchas 是 skill 里单位 token 价值最高的内容之一。

### 16.4 给默认路径，不要给一堆平级选项

差的写法：

```markdown
You can use grep, ripgrep, database query, logs, dashboard, or API to investigate the problem.
```

好的写法：

```markdown
Default investigation path:
1. Use `scripts/collect_order_trace.py` to gather trace data.
2. If trace data is incomplete, use `rg <trace_id> logs/`.
3. Query the database only after confirming the affected order ID.
```

Agent 需要的是“优先级”，不是菜单。

### 16.5 脆弱步骤脚本化，判断步骤自然语言化

* 日志解析、字段映射、格式校验、批量生成、报告检查：脚本化。
* 排查优先级、异常解释、业务风险、是否需要人工确认：自然语言化。

### 16.6 destructive action 必须 plan-validate-execute

例如数据修复 skill 不应该直接执行 SQL，而应该：

1. 生成修复计划。
2. 生成只读验证查询。
3. 生成待审批 SQL。
4. 要求人工确认。
5. 执行后再次验证。
6. 输出回滚方案。

OpenCode 支持对 agent 的工具和权限进行配置，例如 `read`、`edit`、`bash`、`skill` 等权限可设为 allow、ask、deny，也可以按 agent 覆盖权限；这类权限机制应该与 skill 中的安全策略配合使用。([OpenCode][11])

### 16.7 Skill 要有 eval

至少准备两类 eval：

**触发 eval：**

```json
[
  { "query": "订单付款成功但没有发货", "should_trigger": true },
  { "query": "订单列表 UI 字体太小", "should_trigger": false }
]
```

**执行 eval：**

```markdown
## Case: webhook duplicated

Input:
- order_id: ord_123
- logs show duplicated payment callback
- order state: fulfilled

Expected:
- Should not classify as payment failure.
- Should inspect idempotency behavior.
- Should mention provider retry semantics.
- Should not propose direct production mutation.
```

---

## 17. 面向代码研发的常见 skill 类型

### 17.1 代码库理解 skill

用于新成员或 agent 快速理解复杂 repo。

```text
repo-onboarding/
- 项目模块地图
- 构建和测试入口
- 核心抽象说明
- 常见陷阱
- “改某类功能应该看哪些目录”
```

### 17.2 Bug triage skill

用于线上问题、issue、报错日志排查。

```text
bug-triage/
- 输入信息清单
- 复现优先级
- 日志和 trace 收集方式
- 代码定位策略
- 输出证据链模板
```

### 17.3 PR review skill

用于团队代码审查标准化。

```text
pr-review/
- 安全检查
- 性能检查
- 事务和并发检查
- API 兼容性检查
- 测试覆盖要求
```

### 17.4 Migration skill

用于数据库迁移、框架升级、依赖替换。

```text
migration/
- 迁移前检查
- 分阶段修改顺序
- 自动化 codemod
- 回归测试
- 回滚策略
```

### 17.5 Incident report skill

用于故障复盘和报告生成。

```text
incident-report/
- 时间线整理
- 影响面计算
- 根因分类
- 行动项模板
- 证据引用要求
```

### 17.6 Domain-specific coding skill

比如订单、支付、风控、推荐、搜索、权限系统。

```text
payment-domain/
- 状态机
- 错误码
- 幂等规则
- 第三方回调语义
- 数据一致性验证
```

---

## 18. 传统 Web 应用如何把运行过程“塞进智能体”？

如果一个传统 Web 应用想被 agent 有效优化，最重要的不是“让 agent 直接看所有代码”，而是让应用运行过程具备 **agent 可追踪性**。

也就是：当用户说“这个页面点了没反应”“支付成功但订单没更新”“导出报表失败”时，agent 能通过 trace 快速还原：

* 用户做了什么？
* 请求进了哪个接口？
* 经过哪些服务？
* 读写了哪些关键表？
* 调用了哪些外部系统？
* 哪个环节返回异常？
* 代码版本是什么？
* feature flag 是什么？
* 最小复现路径是什么？

### 18.1 为 agent 设计日志，不是只为人类设计日志

差的日志：

```text
Error happened while processing order.
```

好的日志：

```json
{
  "timestamp": "2026-05-17T10:22:11.123Z",
  "level": "error",
  "trace_id": "trc_9f2a",
  "span_id": "spn_webhook_01",
  "parent_span_id": "spn_http_00",
  "service": "payment-webhook",
  "component": "webhook-handler",
  "environment": "staging",
  "git_sha": "a1b2c3d",
  "route": "POST /webhooks/payment",
  "event": "fulfillment_event_publish_failed",
  "order_id_hash": "ord_hash_123",
  "payment_id_hash": "pay_hash_456",
  "provider": "stripe",
  "provider_event_type": "payment_intent.succeeded",
  "idempotency_key_hash": "idem_hash_789",
  "expected_state": "OrderFulfillmentRequested published",
  "actual_state": "message_queue_publish_failed",
  "error": {
    "type": "QueuePermissionError",
    "message": "publish permission denied for topic order.fulfillment"
  },
  "safe_debug_hints": [
    "Check queue IAM policy for payment-webhook service account",
    "Check deployment diff after git_sha a1b2c3d"
  ]
}
```

注意几点：

* 不直接打 PII，使用 hash 或脱敏 ID。
* 必须有 `trace_id`。
* 必须有 `git_sha` 或 release version。
* 必须记录 expected vs actual。
* 错误信息要能指导下一步，而不是只有 stack trace。
* 关键业务语义要结构化，例如 `provider_event_type`、`expected_state`。

### 18.2 给 agent 一个 trace 收集入口

可以在 skill 里提供脚本：

```bash
python scripts/collect_web_trace.py \
  --trace-id trc_9f2a \
  --env staging \
  --include logs,http,db,queue,feature-flags \
  --output trace-bundle.json
```

也可以在内部平台提供只读接口：

```text
GET /internal/agent-traces/{trace_id}
```

返回：

```json
{
  "trace_id": "trc_9f2a",
  "request": {
    "route": "POST /webhooks/payment",
    "status": 500,
    "duration_ms": 412
  },
  "spans": [
    {
      "service": "api-gateway",
      "event": "request_received"
    },
    {
      "service": "payment-webhook",
      "event": "provider_event_validated"
    },
    {
      "service": "payment-webhook",
      "event": "fulfillment_event_publish_failed",
      "error_type": "QueuePermissionError"
    }
  ],
  "related_code": [
    "services/payment-webhook/src/handler.ts",
    "packages/queue/src/publisher.ts"
  ],
  "related_docs": [
    "docs/payment-webhook.md",
    "docs/order-state-machine.md"
  ],
  "suggested_checks": [
    "Verify queue publish permissions",
    "Check deployment diff for payment-webhook",
    "Run webhook retry integration test"
  ]
}
```

这样 agent 不需要盲目 grep 全仓库，而是先通过 trace 定位相关服务、文件、状态和测试。

### 18.3 Skill 如何使用这些 trace？

在 `SKILL.md` 中写：

````markdown
## Runtime trace workflow

When the user provides a trace ID, do not start by searching the entire repo.

1. Run:

   ```bash
   python scripts/collect_web_trace.py --trace-id "$TRACE_ID" --env "$ENV" --output trace-bundle.json
````

2. Inspect `related_code` and `suggested_checks` from the trace bundle.
3. Read only the related files first.
4. If the trace includes `expected_state` and `actual_state`, use them as the primary debugging frame.
5. Only broaden the search if the trace bundle lacks related code or the evidence contradicts the symptom.

````

这就是把传统应用的运行过程“塞进智能体”的关键：不是把运行过程变成一大段自然语言，而是变成 **可查询、可结构化、可引用、可回放的 trace**。

---

## 19. 一套可落地的 skill 设计流程

### 阶段 1：识别候选任务

适合做 skill 的任务通常有这些特征：

- 重复出现。
- 每次都要解释一遍背景。
- agent 容易走错路径。
- 涉及私有业务知识。
- 涉及多个资源：代码、日志、API、数据库、文档。
- 有固定输出格式或验证标准。
- 有安全边界或审批要求。

不适合做 skill 的任务：

- 一次性任务。
- 纯通用知识问答。
- 没有重复价值的临时需求。
- 完全确定性的逻辑，直接写脚本更合适。

### 阶段 2：收集真实材料

收集：

- 历史 issue
- PR diff
- 事故复盘
- runbook
- 日志样例
- API 文档
- 领域状态机
- code review 评论
- 用户纠正 agent 的对话记录

### 阶段 3：提炼核心能力

把材料分成：

```text
触发条件：
- 用户怎么描述这个问题？

输入：
- agent 必须先问清楚什么？

流程：
- 正常路径是什么？

分支：
- 不同反馈下怎么变更策略？

资源：
- 哪些文档需要读？
- 哪些文件不能每次都读？

脚本：
- 哪些动作重复、机械、易错？

验证：
- 怎么知道任务完成？
- 哪些测试必须跑？
- 输出必须包含什么？
````

### 阶段 4：设计目录

```text
my-skill/
├── SKILL.md
├── references/
├── scripts/
├── assets/
├── evals/
└── CHANGELOG.md
```

### 阶段 5：写 description

要求：

* 写用户意图，不只写实现。
* 包含领域关键词。
* 包含隐式触发场景。
* 避免过宽。
* 用正负样本测试。

### 阶段 6：写 `SKILL.md`

建议结构：

```markdown
---
name: my-skill
description: Use this skill when...
---

# Purpose

## Required inputs

## Workflow

## References

## Available scripts

## Gotchas

## Validation

## Output format

## Safety rules
```

### 阶段 7：测试触发

问：

* 应该触发的是否触发？
* 不该触发的是否误触发？
* 用户口语化表达能否触发？
* 更大的任务中嵌套这个需求时能否触发？

### 阶段 8：测试执行

问：

* agent 是否读了正确资料？
* 是否执行了正确脚本？
* 是否遗漏验证步骤？
* 是否过早下结论？
* 输出是否稳定？

### 阶段 9：上线和 review

像 review 代码一样 review skill：

* 是否泄露敏感信息？
* 是否有危险命令？
* 是否有明确权限边界？
* 是否有版本记录？
* 是否有 eval？
* 是否有 owner？

### 阶段 10：持续迭代

每次 agent 失败，都不要只修这一次任务；要问：

> 这个失败是否代表 skill 缺少一个 gotcha、一个 reference、一个脚本、一个 eval，还是 description 触发不准？

---

## 20. 一个完整示例：`frontend-regression-triage` skill

目录：

```text
frontend-regression-triage/
├── SKILL.md
├── references/
│   ├── ui-architecture.md
│   ├── feature-flag-policy.md
│   └── visual-regression-guide.md
├── scripts/
│   ├── collect_browser_trace.py
│   ├── compare_screenshots.py
│   └── validate_report.py
├── assets/
│   └── regression-report-template.md
└── evals/
    └── trigger_queries.json
```

`SKILL.md`：

````markdown
---
name: frontend-regression-triage
description: Use this skill when investigating frontend regressions, broken UI flows, visual diffs, browser console errors, hydration errors, feature flag mismatches, or user reports that a page no longer behaves as expected after a code change.
---

# Frontend regression triage

## Required inputs

Collect as many as available:

- Page URL or route
- Environment
- Browser
- User role
- Feature flags
- Expected behavior
- Actual behavior
- Screenshot or trace ID
- Recent PR or git SHA

## Workflow

1. Do not start by refactoring.
2. Reproduce or inspect evidence first.
3. If a trace ID is available, run:

   ```bash
   python scripts/collect_browser_trace.py --trace-id "$TRACE_ID" --output browser-trace.json
````

4. Check browser console errors before inspecting component code.

5. If the issue is visual, compare screenshots:

   ```bash
   python scripts/compare_screenshots.py --before before.png --after after.png --output visual-diff.json
   ```

6. Read `references/feature-flag-policy.md` if behavior differs by user role, tenant, or environment.

7. Read `references/ui-architecture.md` before changing shared layout components.

8. Make the smallest code change that explains the observed regression.

9. Run focused tests first, then broader checks.

## Gotchas

* Do not assume staging and production have the same feature flags.
* Hydration errors may appear as visual regressions but originate from server/client data mismatch.
* Shared layout components affect multiple product surfaces; inspect dependents before editing.
* A screenshot alone is not proof of root cause; pair it with console logs or trace data.

## Validation

Before finalizing:

* Include reproduction evidence.
* Explain root cause.
* Show changed files.
* Run relevant component or e2e tests.
* Mention any untested browsers or roles.

## Output format

Use:

* Summary
* Evidence
* Root cause
* Fix
* Validation
* Risks
* Follow-up

```

这个 skill 把“前端回归排查”从一次次临时对话，沉淀成了 agent 可复用的工程能力。

---

## 21. 最终心法

设计 skill 时，可以用这五个问题检查质量：

1. **它是否解决了模型原本不知道的东西？**  
   如果只是“写好代码、处理错误、遵循最佳实践”，价值很低。

2. **它是否能在正确场景触发？**  
   如果 description 写不好，skill 再好也不会被用上。

3. **它是否减少了上下文噪声？**  
   好 skill 应该让 agent 少读无关文件，而不是多塞文档。

4. **它是否把易错动作脚本化？**  
   让 LLM 判断，让脚本计算和校验。

5. **它是否能根据执行反馈迭代？**  
   每次失败都应该变成 gotcha、reference、script、eval 或 description 的改进。

最终，skill 的本质不是“把 prompt 保存起来”，而是：

> **把工程师在真实业务场景中的判断路径、资源组织方式、工具使用经验和验证标准，变成 agent 可以按需激活的上下文结构。**

这也是为什么 skill 会成为 agent 应用的重要抽象：它连接了模型内化知识、项目上下文、业务资源和环境反馈，让智能体不只是“会生成代码”，而是能在具体工程环境里持续变得更可靠。
::contentReference[oaicite:17]{index=17}
```

[1]: https://opencode.ai/docs/ "Intro | AI coding agent built for the terminal"
[2]: https://agentskills.io/ "Agent Skills Overview - Agent Skills"
[3]: https://opencode.ai/docs/commands/ "Commands | OpenCode"
[4]: https://agents.md/ "AGENTS.md"
[5]: https://arxiv.org/abs/2210.03629?utm_source=chatgpt.com "ReAct: Synergizing Reasoning and Acting in Language Models"
[6]: https://agentskills.io/specification "Specification - Agent Skills"
[7]: https://opencode.ai/docs/skills/ "Agent Skills | OpenCode"
[8]: https://agentskills.io/skill-creation/optimizing-descriptions "Optimizing skill descriptions - Agent Skills"
[9]: https://agentskills.io/skill-creation/using-scripts "Using scripts in skills - Agent Skills"
[10]: https://agentskills.io/skill-creation/best-practices "Best practices for skill creators - Agent Skills"
[11]: https://opencode.ai/docs/agents/ "Agents | OpenCode"
