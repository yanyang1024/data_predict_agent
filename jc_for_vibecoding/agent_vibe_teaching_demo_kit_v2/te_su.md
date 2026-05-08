已按你的要求重做成 **v2 教学版 demo kit**，重点从“具体部门场景实现”调整为“通过样例教学引导 Agent / Vibe Coding 工作流”。
下载： [agent_vibe_teaching_demo_kit_v2.zip](sandbox:/mnt/data/agent_vibe_teaching_demo_kit_v2.zip)

我把原来的 3 个 demo 改成了 4 个循序渐进的教学 demo，并增加了第 0 个入门样例。整体设计仍然承接你前面收集的部门场景：历史文档与样例开发、富文本/规范文档提取后生成验证实现、数据与配置权限约束等需求。

# 新版 demo 结构

```text
agent_vibe_teaching_demo_kit_v2/
  README.md
  TEACHING_GUIDE.md
  AGENTS.md
  opencode.json
  run_all_demos.py

  00_rule_based_report_generation/
  01_doc_spec_portability/
  02_rich_doc_pattern_pipeline/
  03_permission_guarded_execution/
```

可以一键运行：

```bash
python3 run_all_demos.py
```

我已经在当前环境中跑通过一键脚本，4 个 demo 都生成了输出和 validation / manifest 文件。

# 这版主要改了什么

**Demo 0：基于规则的文档生成**
新增。用于课程开头，模拟“根据项目完成情况 + PPT / 汇报模板 + 规则生成项目汇报”。它是最通用、最低风险的 Agent 实践入口，适合介绍 opencode 的 `AGENTS.md`、command、skill、permission 和“Skill Creator + 人协同调试”的工作流。Cline 的 Plan / Act 模式本身也适合这样讲：Plan 先理解规则和模板，不改文件；Act 再执行生成与验证。([Cline][1])

**Demo 1：Doc / Spec 开发规范与可移植实现**
替换了原先偏具体 tester 转平台的实现，改成更抽象的“同一份功能 spec，在 Platform Alpha 和 Platform Beta 上实现”。教学重点是：先读 spec、历史文档、参考样例，再生成 mapping table、目标平台实现、traceability report。它更适合讲“基于历史文档和样例开发”的规范化方法。

**Demo 2：富文本 / PDF 规则提取 + 环境包适配 + Skill 串联验证**
重做为“从 HTML / PDF-like rich document 中提取验证模式和 native instruction，再根据 environment package 生成适配后的验证 flow”。它分成四步：extract → adapt → generate → validate。这个 demo 特意强调：Agent 不只是读和参考，也可以执行脚本生成中间产物和代码；但抽取结果、适配方案、最终逻辑都必须有人介入 review。工具只能验证语法、schema、dry-run，不等于验证逻辑正确。

**Demo 3：权限约束与封装脚本执行空间**
重做为“重要数据和配置不能让 Agent 直接操作，只能通过 wrapper script + 参数约束 + manifest + audit log”。这个 demo 重点展示 `opencode.json` permission、受控查询 contract、禁止直接读写 protected config、配置变更只能生成 change request。OpenCode 的权限模型支持 `allow / ask / deny`，也支持对 bash、edit、read、skill 等工具做细粒度规则，这正好适合这个场景。([OpenCode][2])

# 每个 demo 里都有

每个 demo 都包含：

```text
README.md                  # 教学说明
AGENTS.md                  # 项目规则
opencode.json              # 权限示例
.opencode/commands/*.md    # opencode 命令入口
.opencode/skills/*/SKILL.md # skill 工作流
scripts/*.py               # 可执行教学脚本
output/                    # 已生成示例结果
```

OpenCode 的 Skill 通常放在 `.opencode/skills/<name>/SKILL.md`，并通过 name / description 被发现和按需加载；Command 可以把高频任务变成统一入口。([OpenCode][3]) Cline 侧我也补了 `.clinerules/` 示例，因为 Cline 支持 `.clinerules/`、`AGENTS.md` 等规则文件，也支持按需加载的 Skill。([Cline][4])

# 建议课堂使用顺序

建议你按这个顺序讲：

```text
Demo 0：规则化文档生成
  先让大家理解 opencode 工作流、Skill、Command、Rules、验证脚本。

Demo 1：Doc / Spec 可移植开发
  讲“不要直接生成代码，先 mapping、traceability、validation”。

Demo 2：富文本提取和模块串联
  讲“extract → adapt → generate → validate”，以及人机协同 review gates。

Demo 3：权限约束执行
  讲“重要数据和配置不直接给 Agent，必须通过封装工具和参数合同”。
```

新版 demo kit：
[agent_vibe_teaching_demo_kit_v2.zip](sandbox:/mnt/data/agent_vibe_teaching_demo_kit_v2.zip)

[1]: https://docs.cline.bot/features/plan-and-act "https://docs.cline.bot/features/plan-and-act"
[2]: https://opencode.ai/docs/permissions "https://opencode.ai/docs/permissions"
[3]: https://opencode.ai/docs/skills/ "https://opencode.ai/docs/skills/"
[4]: https://docs.cline.bot/customization/cline-rules "https://docs.cline.bot/customization/cline-rules"
