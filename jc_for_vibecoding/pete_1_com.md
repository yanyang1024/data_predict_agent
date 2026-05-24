下面是一个**初步方案**，专门针对你描述的 PETE 成品测试代码场景：C/C++ 为主、按产品和机台重构测试代码、先删冗余代码、再生成/更新产品测试参数，并且要求每次改动可 trace、关键节点人工检查。

我建议先不要把 Skill 做成“万能代码迁移 Skill”，而是做成一个非常聚焦的：

```text
pete-test-code-migration
```

它的核心目标不是“让 Agent 自动大胆删代码”，而是让 opencode agent 严格执行：

```text
测试项提取
  -> 白名单对齐
  -> 机台语言 pattern 识别
  -> 冗余代码候选分析
  -> 依赖闭包确认
  -> 人工确认
  -> 分阶段删除
  -> 参数更新
  -> 版本 trace
  -> 编译/静态验证/人工检查清单
```

opencode 的 Agent Skills 是通过 `SKILL.md` 定义的可复用行为，opencode 会按需加载 skill；项目级 skill 可以放在 `.opencode/skills/<name>/SKILL.md`，且 `SKILL.md` 需要 `name` 和 `description` frontmatter，名称要和目录名一致并符合 lowercase-hyphen 格式。([OpenCode][1])

---

# 1. 总体落地结构

建议第一版先建立下面这些文件：

```text
repo-root/
  AGENTS.md
  opencode.json

  .opencode/
    skills/
      pete-test-code-migration/
        SKILL.md

    commands/
      pete-migrate.md
      pete-clean-redundant.md
      pete-update-params.md

    agents/
      pete-migration-reviewer.md

  docs/
    agent-rules/
      pete/
        whitelist-format.md
        machine-language-patterns.md
        product-param-schema.md
        redundant-code-deletion-rules.md
        migration-trace-template.md
        known-failure-modes.md
```

这里的职责划分是：

| 文件                                  | 作用                                   |
| ----------------------------------- | ------------------------------------ |
| `AGENTS.md`                         | 放项目长期规则：构建命令、测试命令、代码目录、白名单位置、禁止事项    |
| `SKILL.md`                          | 放 PETE 测试代码迁移的标准流程                   |
| `commands/*.md`                     | 给工程师一个固定入口，比如 `/pete-migrate`        |
| `agents/pete-migration-reviewer.md` | 只读审查 agent，用来复核删代码和参数更新              |
| `docs/agent-rules/pete/*.md`        | 放白名单格式、机台 pattern、产品参数 schema、已知失败模式 |

opencode 支持通过 `AGENTS.md` 提供项目规则，并建议把项目的 `AGENTS.md` 提交到 Git；`/init` 会扫描仓库并帮助创建或更新 `AGENTS.md`，重点包括 build/lint/test 命令、架构结构、项目约定和常见坑。([OpenCode][2])

---

# 2. 从 0 到 1 建立第一版代码迁移 Skill

## 2.1 先定义第一版 Skill 的边界

第一版不要试图覆盖所有 PETE 任务。建议只覆盖这一个闭环：

```text
输入：
- 现有 C/C++ 测试代码
- 测试项白名单
- 机台语言 pattern
- 产品参数来源

输出：
- 测试项 manifest
- 冗余代码删除计划
- 参数更新计划
- 分阶段 patch
- before/after trace
- 人工检查清单
```

第一版 Skill 的核心能力分两步：

```text
Step A：删除冗余代码
- 删除不在白名单上的测试项
- 删除仅被这些测试项调用的函数、变量、类、宏、注册表项
- 保留白名单测试项、机台运行入口、公共基础设施和共享 helper

Step B：产品参数更新
- 按产品生成或更新参数
- 保留参数来源、默认值、覆盖规则
- 输出参数差异表，供人工确认
```

你特别提到的问题是：**Agent 删除冗余代码时会漏匹配：几个类最后生成的代码没有匹配上。目标是把仅被需删除测试项调用的函数、变量和类都删掉。**

所以第一版 Skill 必须把“冗余删除”设计成**依赖图闭包问题**，而不是简单的关键词搜索问题。

---

## 2.2 第一版 Skill 的核心算法：防漏删的依赖闭包

针对漏删问题，Skill 里要强制 agent 使用下面这个判断逻辑。

```text
1. 提取测试项入口
   - 从 flow.c、efa、机台语言 pattern、注册表、宏、数组、测试 flow 表中识别测试项。
   - 每个测试项都要映射到 entry function / class / handler / parameter block。

2. 建立 keep roots
   - 白名单上的测试项。
   - 白名单测试项依赖的函数、变量、类、宏。
   - 机台运行框架入口。
   - 公共初始化、日志、校准、binning、fail handling、site control 等基础设施。
   - 人工指定保护项。

3. 建立 delete roots
   - 不在白名单上的测试项。
   - 明确判定与保留测试项无关的旧 flow。
   - 明确废弃的 product/machine branch。

4. 建立符号依赖图
   - function -> called function
   - function -> global/static variable
   - class -> method/member
   - test item -> entry function/class
   - registration table -> test item
   - macro/function pointer/table/string dispatch -> 保守标记为 uncertain

5. 计算闭包
   - keep_closure = 从 keep roots 可达的全部符号
   - delete_closure = 从 delete roots 可达的全部符号

6. 生成删除候选
   - candidate = delete_closure - keep_closure - protected_symbols

7. 反向引用复核
   - 每个 candidate 必须确认所有 caller/user 都在 delete_closure 内。
   - 如果被 keep_closure、未知宏、字符串 dispatch、机台脚本引用，则不能自动删，进入人工检查清单。

8. 分阶段删除
   - 先删测试项注册/flow entry
   - 再删仅被删除测试项调用的 helper
   - 再删仅被删除 helper 使用的变量、类、参数块
   - 每一阶段输出 before/after diff
```

这一点非常重要：
**只要一个函数、变量、类还有任何来自保留测试项、未知机台入口、宏展开、函数指针表或字符串 dispatch 的引用，就不能自动删除。**

对于 C/C++，第一版可以先用 `rg`、`ctags/cscope`、编译索引、`clangd` 或 `clang-query/LibTooling` 辅助识别符号；如果仓库已经能生成 `compile_commands.json`，后续可以逐步升级成 Clang AST 级别的识别。Clang 的 LibASTMatchers 官方文档说明它可以匹配 AST 节点并配合 LibTooling 编写代码转换或查询工具；LibTooling 支持基于 compilation database 对源文件运行工具。([clang.llvm.org][3])

如果第一阶段暂时无法做 AST 工具，也可以用 GNU cflow 先辅助生成 C 函数调用图；它支持 direct graph 和 reverse graph，reverse graph 能展示 callee 到 caller 的关系。([gnu.org][4])

---

## 2.3 第一版 Skill 的输入规范

第一版不要让 Agent 自己猜白名单和参数格式。建议固定几个输入文件或章节。

### `docs/agent-rules/pete/whitelist-format.md`

```md
# PETE Test Item Whitelist Format

白名单用于定义必须保留的测试项。

每条记录至少包含：

| field | required | meaning |
|---|---|---|
| test_item_id | yes | 测试项唯一 ID |
| product | optional | 适用产品 |
| machine | optional | 适用机台 |
| flow_file | optional | 例如 flow.c |
| efa_entry | optional | efa 入口或 pattern |
| entry_symbol | optional | C/C++ 入口函数、类、handler |
| reason | yes | 保留原因 |
| owner | optional | 负责人工程师 |

Agent 必须：
- 不删除白名单测试项。
- 不删除白名单测试项依赖的支持代码。
- 白名单字段缺失时，先生成待确认项，不直接删除。
```

---

### `docs/agent-rules/pete/machine-language-patterns.md`

```md
# PETE Machine Language Patterns

记录不同机台语言或测试框架的测试项识别 pattern。

## Pattern Template

| field | meaning |
|---|---|
| pattern_name | 机台 pattern 名称 |
| file_scope | 适用文件，例如 flow.c、efa、*.cpp |
| entry_detection | 如何识别测试项入口 |
| parameter_detection | 如何识别参数 |
| dependency_detection | 如何识别依赖 |
| delete_rule | 删除规则 |
| uncertainty_rule | 何时必须人工检查 |

## Example: flow.c

- 识别 flow table 中的测试项 entry。
- 如果 entry 不在 whitelist，并且其 entry function 只被该测试项引用，则可作为 delete root。
- 如果 entry function 同时被白名单项引用，则保留。
- 如果 entry 通过宏、函数指针、字符串拼接生成，则标记 uncertain。

## Example: efa

- 识别 efa 中的测试项名称、机台 command、parameter block。
- 如果 efa entry 不在 whitelist，需要检查它是否支持白名单测试项。
- 删除前必须输出 efa entry -> C/C++ symbol 映射。
```

---

### `docs/agent-rules/pete/product-param-schema.md`

```md
# Product Parameter Schema

产品参数更新必须输出参数差异。

每个参数至少记录：

| field | meaning |
|---|---|
| product | 产品 |
| machine | 机台 |
| test_item_id | 测试项 |
| parameter_name | 参数名 |
| old_value | 旧值 |
| new_value | 新值 |
| source | 参数来源 |
| rule | 生成规则 |
| confidence | high / medium / low |
| human_check_required | yes / no |

Agent 不允许在没有来源说明的情况下静默修改参数。
```

---

## 2.4 第一版 `SKILL.md` 草案

建议先放在：

```text
.opencode/skills/pete-test-code-migration/SKILL.md
```

内容可以从这个版本开始：

```md
---
name: pete-test-code-migration
description: Use for semiconductor PETE final-test C/C++ code refactoring and migration tasks, especially by-product and by-machine test code cleanup, whitelist-based test item extraction, redundant code deletion, machine-language pattern migration, product parameter generation, traceable before-after code changes, and human review checkpoints.
compatibility: opencode
metadata:
  domain: semiconductor-pete-final-test
  language: c-cpp
---

# PETE Test Code Migration Skill

## Goal

Help migrate and refactor semiconductor PETE final-test code, mainly C/C++, by product and by machine.

The workflow has two main phases:

1. Remove redundant code that is not on the whitelist and is not required to support retained test items.
2. Generate or update test parameters for different products and machines.

Every deletion or modification must be traceable with before/after evidence. Important modification points must be surfaced for human review.

## Required inputs

Before editing code, identify or ask for:

- Target product or product family.
- Target machine or machine language pattern.
- Whitelist source, such as flow.c, efa, CSV, YAML, or manually provided test item list.
- Source code scope to analyze.
- Build or compile command.
- Available static analysis tools.
- Parameter source and product parameter generation rule.
- Whether deletion is allowed or only a deletion plan should be produced.

If the whitelist or machine pattern is ambiguous, do not delete code. Produce a mapping table and ask for human confirmation.

## Mandatory references

Read these project references if present:

- `docs/agent-rules/pete/whitelist-format.md`
- `docs/agent-rules/pete/machine-language-patterns.md`
- `docs/agent-rules/pete/product-param-schema.md`
- `docs/agent-rules/pete/redundant-code-deletion-rules.md`
- `docs/agent-rules/pete/known-failure-modes.md`

## Phase 0: Create trace checkpoint

Before modifying files:

1. Check git status.
2. Refuse to overwrite unrelated user changes.
3. Create a migration trace folder if the project allows it:

   `migration-trace/<task-id>/`

4. Save:
   - baseline git status
   - baseline file list
   - baseline whitelist source
   - initial test item manifest
   - planned commands

If the workspace is dirty, report the changed files and ask before continuing.

## Phase 1: Extract test items

Build a test item manifest.

Each row must include:

| field | meaning |
|---|---|
| test_item_id | normalized test item id |
| source_file | file containing the item |
| machine_pattern | flow.c / efa / table / macro / function pointer / other |
| entry_symbol | function, class, handler, or table entry |
| product_scope | product applicability |
| machine_scope | machine applicability |
| whitelist_status | keep / remove / unknown |
| dependency_symbols | direct dependencies |
| parameter_blocks | related parameter definitions |
| confidence | high / medium / low |
| evidence | file and line references |

Do not proceed to deletion until the manifest is produced.

## Phase 2: Build keep/delete roots

Define keep roots:

- Whitelisted test items.
- All symbols required by whitelisted test items.
- Machine framework entrypoints.
- Common infrastructure: init, calibration, logging, binning, fail handling, site control, communication, error handling.
- Product parameter loading code used by retained items.
- Any symbol manually marked protected.

Define delete roots:

- Test items not in the whitelist.
- Deprecated product or machine branches confirmed out of scope.
- Legacy parameter blocks only used by deleted test items.

Do not treat a symbol as removable just because its name matches a deleted test item. Use reference analysis.

## Phase 3: Dependency closure and redundant-code deletion plan

For each delete root:

1. Find direct callees, used globals, used classes, used macros, used parameter blocks, and registration entries.
2. Build delete closure.
3. Build keep closure from keep roots.
4. Candidate removable symbols are:

   `delete_closure - keep_closure - protected_symbols`

5. For each candidate, run reverse-reference checks.

A candidate can be auto-deleted only if:

- All known callers/users are inside delete_closure.
- It is not referenced from retained test items.
- It is not referenced by machine runtime, flow tables, efa entries, function pointer tables, macros, generated code, string dispatch, or external integration.
- It is not public API or shared infrastructure.
- Compile or static analysis checks can be run after deletion.

If any condition is uncertain, do not auto-delete. Add it to the human review list.

## Phase 4: Delete in small checkpoints

Delete in this order:

1. Test flow entries and registration entries.
2. Test item entry functions/classes.
3. Private helper functions/classes only used by deleted items.
4. Private globals/static variables only used by deleted items.
5. Parameter blocks only used by deleted items.
6. Includes, prototypes, declarations, and dead comments.

After each checkpoint:

- Save diff to `migration-trace/<task-id>/patch-<step>.diff`.
- Report deleted symbols.
- Run the narrowest available compile/static check.
- Stop if new unresolved references appear.

## Phase 5: Product parameter update

For retained test items:

1. Locate old parameters.
2. Locate product-specific parameter sources.
3. Generate a parameter diff table.
4. Update values only when source and rule are explicit.
5. Mark ambiguous values as `human_check_required`.

Output:

| test_item_id | product | machine | parameter | old_value | new_value | source | rule | human_check_required |
|---|---|---|---|---|---|---|---|---|

Do not silently change limits, units, binning, voltage/current ranges, timing, temperature conditions, or fail criteria.

## Phase 6: Verification

Run available checks in this order:

1. Syntax or compile check for touched files.
2. Focused build for affected module.
3. Static reference scan for deleted symbols.
4. Search for stale declarations and includes.
5. Product/machine parameter consistency check.
6. Existing unit/simulation tests if available.
7. Human checklist for machine execution if hardware execution is required.

If hardware or tester execution cannot be run, say so clearly and provide manual validation steps.

## Human review checkpoints

Stop and ask for human review before:

- Deleting a class or global variable.
- Deleting code reachable through macros or function pointers.
- Deleting code referenced by flow.c or efa.
- Deleting code with product-specific preprocessor branches.
- Updating test limits, binning, timing, voltage, current, temperature, or fail criteria.
- Removing compatibility code shared across products or machines.
- Removing code with low-confidence dependency analysis.

## Final response format

Return:

1. Scope analyzed.
2. Whitelist source.
3. Test item manifest summary.
4. Removed test items.
5. Removed functions/classes/variables/macros.
6. Symbols kept because they are shared or uncertain.
7. Product parameter changes.
8. Trace files generated.
9. Commands/checks run.
10. Human review checklist.
11. Known risks and follow-ups.

## Do not

- Do not delete by keyword only.
- Do not delete symbols without reverse-reference checks.
- Do not delete code used by whitelisted test items.
- Do not silently update test parameters.
- Do not modify unrelated formatting.
- Do not collapse multiple migration phases into one large patch.
- Do not proceed when whitelist, product scope, or machine pattern is unclear.
```

---

# 3. opencode command 设计

opencode 支持 custom commands，用 `.opencode/commands/*.md` 或配置文件定义。命令文件的 frontmatter 定义属性，正文作为 prompt 模板；执行时可以通过 `/command-name` 调用。([OpenCode][5])

建议先做 3 个 command。

---

## 3.1 `/pete-migrate`

```text
.opencode/commands/pete-migrate.md
```

```md
---
description: Run PETE test code migration workflow
agent: plan
---

Load and use the `pete-test-code-migration` skill.

Migration request:

$ARGUMENTS

Start in planning mode.

Do not edit files yet.

First produce:
1. Input assumptions.
2. Whitelist source.
3. Machine pattern source.
4. Initial test item extraction plan.
5. Redundant-code deletion strategy.
6. Product parameter update strategy.
7. Human review checkpoints.
```

这个命令用于完整迁移。

---

## 3.2 `/pete-clean-redundant`

```text
.opencode/commands/pete-clean-redundant.md
```

```md
---
description: Analyze and remove redundant PETE test code using whitelist and dependency closure
agent: plan
---

Load and use the `pete-test-code-migration` skill.

Focus only on redundant-code cleanup.

Request:

$ARGUMENTS

Do not edit files until you produce:

1. Test item manifest.
2. Keep roots.
3. Delete roots.
4. Dependency closure.
5. Delete candidate list.
6. Symbols that must be manually checked.
7. Proposed checkpoint sequence.
```

这个命令专门解决你现在最痛的“删冗余代码漏匹配”问题。

---

## 3.3 `/pete-update-params`

```text
.opencode/commands/pete-update-params.md
```

```md
---
description: Update PETE product and machine test parameters with traceable parameter diff
agent: plan
---

Load and use the `pete-test-code-migration` skill.

Focus only on product and machine parameter generation or update.

Request:

$ARGUMENTS

Do not edit files until you produce:

1. Product scope.
2. Machine scope.
3. Retained test item list.
4. Parameter source.
5. Parameter diff table.
6. Human review items.
```

---

# 4. 权限与人工检查设计

代码删除任务必须控制权限。opencode 的 permission 配置可以把动作设为 `allow`、`ask`、`deny`，并支持按 bash/edit 等工具做粒度化规则；规则是 pattern match，常见做法是先放 `"*": "ask"`，再放更具体的规则。([OpenCode][6])

建议第一版 `opencode.json` 偏保守：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "skill": {
      "*": "allow",
      "experimental-*": "ask"
    },
    "read": {
      "*": "allow",
      "*.env": "deny",
      "*.env.*": "deny"
    },
    "edit": "ask",
    "bash": {
      "*": "ask",
      "git status*": "allow",
      "git diff*": "allow",
      "git show*": "allow",
      "rg *": "allow",
      "grep *": "allow",
      "find *": "allow",
      "ctags *": "ask",
      "cscope *": "ask",
      "cflow *": "ask",
      "clang*": "ask",
      "make *": "ask",
      "cmake *": "ask",
      "ninja *": "ask",
      "rm *": "deny",
      "git clean*": "deny",
      "git reset*": "deny",
      "git push*": "deny",
      "git commit*": "ask"
    }
  }
}
```

重点是：
**允许读和分析，编辑要 ask，危险删除命令 deny。**
让 Agent 通过 patch 修改文件，而不是直接 `rm` 一堆文件。

---

# 5. 专门增加一个只读 reviewer agent

opencode 里 Plan agent 适合在不实际修改代码的情况下分析和计划；Build agent 适合需要文件操作和命令执行的开发任务。官方文档也说明，Plan 是受限 agent，适合分析代码、建议变更或创建计划，不做实际修改。([OpenCode][7])

建议增加一个只读 reviewer：

```text
.opencode/agents/pete-migration-reviewer.md
```

```md
---
description: Review PETE test code migration for whitelist correctness, redundant-code deletion safety, dependency closure, parameter changes, and human traceability.
mode: subagent
temperature: 0.1
permission:
  edit: deny
  bash:
    "*": "ask"
    "git diff*": "allow"
    "git status*": "allow"
    "rg *": "allow"
    "grep *": "allow"
---

You are a PETE test code migration reviewer.

Review only. Do not edit files.

Check:

1. Whether all whitelisted test items are preserved.
2. Whether deleted test items are truly outside the whitelist.
3. Whether every deleted function/class/global is only used by deleted test items.
4. Whether any deleted symbol has remaining references.
5. Whether macro, function pointer, table-driven, flow.c, or efa references were considered.
6. Whether parameter changes have old value, new value, source, and rule.
7. Whether trace files and before/after diffs exist.
8. Whether human review checkpoints are sufficient.

Return:

- Blocking issues.
- Possible missed deletions.
- Possible unsafe deletions.
- Parameter risks.
- Required human checks.
- Suggested skill updates.
```

这个 reviewer agent 对后续迭代非常关键，因为它会把“Agent 做错了什么”结构化输出，方便你更新 Skill。

---

# 6. 第一次真实使用时的推荐流程

第一版 Skill 建好后，不要直接让它改整个代码库。建议按下面方式跑。

## 6.1 选一个小范围试点

选择一个小范围任务：

```text
产品：Product_A
机台：Tester_X
范围：某一个 flow.c + 相关 efa + 2~5 个测试项
目标：删除 1~2 个不在白名单的测试项，以及仅被它们调用的 helper
```

不要一开始就全量迁移。

---

## 6.2 第一次对话示例

在 opencode 中输入：

```text
/pete-clean-redundant

产品：Product_A
机台：Tester_X
白名单来源：docs/whitelist/Product_A_Tester_X.csv
入口文件：src/flow.c
efa 文件：config/tester_x.efa
代码范围：src/tests/, src/common/
目标：
1. 提取测试项 manifest。
2. 删除不在白名单上的测试项。
3. 删除仅被这些测试项调用的函数、变量、类。
4. 所有删除前先给我删除计划，不要直接改文件。
5. 每个删除 checkpoint 都要保留 before/after diff。
```

期待 Agent 第一轮输出的是计划，而不是直接删代码。

---

## 6.3 第一轮 Agent 必须产出的中间物

要求它先产出这些表。

### 测试项 manifest

| test_item_id | source | entry_symbol | whitelist_status | dependencies | confidence |
| ------------ | ------ | ------------ | ---------------- | ------------ | ---------- |

### 删除候选表

| symbol | type | reason | callers/users | safe_to_delete | confidence | human_check |
| ------ | ---- | ------ | ------------- | -------------- | ---------- | ----------- |

### 保留原因表

| symbol           | reason                        |
| ---------------- | ----------------------------- |
| `InitSite()`     | shared machine infrastructure |
| `ReadEfaParam()` | used by retained test item    |
| `LimitTable_A`   | referenced by whitelist item  |

### 不确定项表

| symbol       | uncertainty                               | required human decision      |
| ------------ | ----------------------------------------- | ---------------------------- |
| `TestClassX` | referenced through function pointer table | confirm runtime registration |
| `VrefLimit`  | product-specific macro branch             | confirm Product_A only       |

只有这几张表清楚了，才允许进入 Build agent 修改代码。

---

# 7. 后续如何修改和优化这个 Skill

后续迭代的核心不是“再写长一点”，而是用真实失败案例更新 Skill。

建议每次使用后记录：

```text
skill-feedback/<date>-<task-id>.md
```

模板如下：

```md
# Skill Feedback

## Task

- Product:
- Machine:
- Code scope:
- Whitelist:
- Command used:
- Agent used:

## Result

- Completed:
- Compile passed:
- Human review passed:
- Hardware/simulator checked:

## Problems

### Missed deletion

| symbol | type | why it should be deleted | why agent missed it |
|---|---|---|---|

### Unsafe deletion

| symbol | type | why deletion was unsafe | how it was detected |
|---|---|---|---|

### Missed test item

| test_item_id | source | pattern missed |
|---|---|---|

### Wrong parameter update

| parameter | old | generated | expected | reason |
|---|---|---|---|---|

## Skill updates needed

- Update SKILL.md:
- Update machine pattern docs:
- Update whitelist format:
- Update product parameter schema:
- Add known failure mode:
- Add benchmark case:
```

---

## 7.1 按错误类型决定改哪里

| 发现的问题                        | 应该修改哪里                                                    |
| ---------------------------- | --------------------------------------------------------- |
| Agent 没有触发 PETE skill        | 改 `SKILL.md` 的 `description`                              |
| Agent 不知道 flow.c/efa 怎么提取测试项 | 改 `machine-language-patterns.md`                          |
| Agent 漏删仅被删除测试项调用的类          | 改 `redundant-code-deletion-rules.md` 和 `SKILL.md` 的依赖闭包规则 |
| Agent 误删共享 helper            | 增加 protected symbol 规则和 reviewer 检查                       |
| Agent 参数更新缺少来源               | 改 `product-param-schema.md`                               |
| Agent 忘记保存 before/after      | 改 `SKILL.md` 的 checkpoint 规则                              |
| Agent 修改太大，难 review          | 改 command，让它必须分阶段 patch                                   |
| Agent 直接删代码没有人工确认            | 改 `opencode.json` 权限和 Skill 的 stop 条件                     |

---

## 7.2 针对“漏匹配”的专项迭代机制

你现在最明确的问题是：
**仅被需删除测试项调用的函数、变量、类没有全部删掉。**

建议把这类问题专门沉淀成一个 failure mode。

在：

```text
docs/agent-rules/pete/known-failure-modes.md
```

增加：

```md
# Known Failure Mode: Missed Transitive Dead Code

## Symptom

After deleting non-whitelisted test items, some functions, variables, classes, or parameter blocks remain even though they are only used by deleted test items.

## Required fix in future runs

Agent must not stop after deleting test item entrypoints.

Agent must run iterative dependency cleanup until fixed point:

1. Delete selected test entries.
2. Re-scan references.
3. Identify newly orphaned private helpers.
4. Identify globals/classes/parameter blocks only used by those helpers.
5. Delete safe candidates.
6. Re-scan again.
7. Stop only when no more safe candidates remain.

## Required candidate rule

A symbol can be deleted if:

- It is reachable from delete roots.
- It is not reachable from keep roots.
- All reverse references are deleted or scheduled for deletion.
- It is not in protected infrastructure.
- It is not referenced by macro/function pointer/string dispatch with unresolved target.

## Required report

For every missed candidate found by reviewer, add:

- symbol name
- type
- file
- old caller
- why previous rule missed it
- new rule to prevent recurrence
```

同时在 `SKILL.md` 的 Phase 3 增加一句硬规则：

```md
Do not perform only one deletion pass. After each deletion checkpoint, re-run reference analysis and continue until the removable-symbol candidate set reaches a fixed point.
```

这个 fixed point 规则很关键。很多漏删发生在第一层删掉后，第二层 helper 才变成 dead code；如果 Agent 只做一轮，很容易漏。

---

# 8. 建议建立一个小型 benchmark 集合

为了让 Skill 越用越好，建议准备 5~8 个小型 case，不需要真实完整项目，可以是脱敏后的最小代码片段。

```text
tests/agent-benchmarks/pete-migration/
  case-01-simple-test-delete/
  case-02-shared-helper-must-keep/
  case-03-class-only-used-by-deleted-test/
  case-04-global-variable-only-used-by-deleted-test/
  case-05-flow-table-function-pointer/
  case-06-efa-entry-mapping/
  case-07-product-param-ifdef/
  case-08-macro-generated-test-name/
```

每个 case 放：

```text
input/
expected/
README.md
```

`README.md` 写清楚：

```md
# Case 03: class only used by deleted test

## Whitelist

Keep:
- TEST_A

Remove:
- TEST_B

## Expected deletion

- TEST_B flow entry
- TestBEntry()
- ClassB
- ClassB::Run()
- ClassBParam

## Must keep

- SharedLimitCheck()
- TEST_A
- TestAEntry()
```

每次改 Skill 后，用这些 case 跑一遍。
目标不是完全自动化，而是形成“可回归验证”的标准样例。

---

# 9. 迭代节奏建议

## v0.1：人工监督版

目标：能稳定产出分析表和删除计划。

能力范围：

* 提取测试项 manifest。
* 对齐白名单。
* 生成 keep roots / delete roots。
* 生成删除候选。
* 强制人工确认。
* 只做小范围 patch。

不追求全自动删除。

---

## v0.2：闭包删除版

目标：解决漏删问题。

增加：

* 依赖闭包规则。
* reverse reference 检查。
* fixed point 多轮清理。
* 类、全局变量、参数块专项规则。
* reviewer agent 复核。

---

## v0.3：机台 pattern 增强版

目标：提升 flow.c、efa、机台语言 pattern 识别能力。

增加：

* 每种机台 pattern 的识别模板。
* 宏展开、函数指针、table-driven flow 的保守规则。
* uncertain 项必须人工检查。

---

## v0.4：产品参数生成版

目标：稳定更新产品参数。

增加：

* 产品参数 schema。
* 参数来源追踪。
* old/new diff 表。
* limit/binning/timing/temperature 等高风险参数的人工检查规则。

---

## v0.5：准自动化迁移版

目标：可以处理更大范围迁移。

增加：

* golden benchmark。
* 常见失败模式库。
* 按产品/机台维度的回归清单。
* 自动生成 trace report。

---

# 10. 最关键的 Skill 优化原则

这个场景的 Skill 需要遵守 6 个原则：

1. **先建 manifest，再改代码**
   没有测试项 manifest，Agent 不允许删除代码。

2. **先做 keep closure，再做 delete closure**
   不能只看要删什么，还要先明确什么绝对不能删。

3. **删除候选必须经过反向引用检查**
   特别是函数、变量、类、宏、参数块。

4. **分阶段 patch，不做大爆炸式改动**
   每一步都有 before/after diff。

5. **低置信度不自动删**
   宏、函数指针、字符串 dispatch、机台脚本引用都进入人工检查。

6. **每次失败都变成 Skill 更新项**
   漏删、误删、参数错误、缺少 trace，都要沉淀到规则或 benchmark。

---

# 11. 你这个场景的第一版交付清单

建议第一版先交付这些内容：

```text
1. .opencode/skills/pete-test-code-migration/SKILL.md
2. .opencode/commands/pete-clean-redundant.md
3. .opencode/commands/pete-update-params.md
4. .opencode/commands/pete-migrate.md
5. .opencode/agents/pete-migration-reviewer.md
6. docs/agent-rules/pete/whitelist-format.md
7. docs/agent-rules/pete/machine-language-patterns.md
8. docs/agent-rules/pete/product-param-schema.md
9. docs/agent-rules/pete/redundant-code-deletion-rules.md
10. docs/agent-rules/pete/known-failure-modes.md
11. opencode.json 权限配置
12. 3~5 个小型 benchmark case
```

第一版的成功标准不是“Agent 已经能全自动迁移所有代码”，而是：

```text
给定一个产品 + 一个机台 + 一个白名单，
Agent 能稳定输出：
- 测试项 manifest
- keep/delete roots
- 删除候选表
- 不确定项表
- 分阶段删除计划
- 参数更新计划
- 人工检查点
- before/after trace
```

等这个流程跑通后，再逐步增强自动删除能力。

[1]: https://opencode.ai/docs/skills/ "Agent Skills | OpenCode"
[2]: https://opencode.ai/docs/rules/ "Rules | OpenCode"
[3]: https://clang.llvm.org/docs/LibASTMatchers.html "Matching the Clang AST — Clang 23.0.0git documentation"
[4]: https://www.gnu.org/software/cflow/manual/cflow.html "GNU cflow"
[5]: https://opencode.ai/docs/commands/ "Commands | OpenCode"
[6]: https://opencode.ai/docs/permissions/ "Permissions | OpenCode"
[7]: https://opencode.ai/docs/agents/ "Agents | OpenCode"
