已按你的新要求重构成 **v2 教学版 demo kit**：重点从“贴近具体半导体业务实现”调整为“用相似简化场景讲清楚如何从 0 到 1 沉淀 Agent 应用上下文”。原始部门需求仍作为教学动机来源：测试程序转平台、文档/环境库生成验证内容、数据库 adhoc 拉数与权限边界等。

下载新版：
[agent_vibe_opencode_teaching_demos_v2.zip](sandbox:/mnt/data/agent_vibe_opencode_teaching_demos_v2.zip)

我已经在环境里跑通：

```bash
cd agent_vibe_opencode_teaching_demos_v2
python3 run_all_demos.py
```

结果：四个 demo 全部成功生成输出，并通过各自 validator。

---

## 这版的核心改造

我把原来的 3 个 demo 改成了 **4 个从 0 到 1 的教学 demo**，并统一成 OpenCode 项目结构。设计依据是：OpenCode 的 Skills 通过 `.opencode/skills/<name>/SKILL.md` 按需加载，Commands 放在 `.opencode/commands/`，Custom Tools 可以用 TypeScript / JavaScript 定义并调用 Python 等脚本，Permissions 用 `allow / ask / deny` 控制动作边界，AGENTS.md 用于项目长期规则。([OpenCode][1])

新版结构：

```text
agent_vibe_opencode_teaching_demos_v2/
  README.md
  AGENTS.md
  opencode.json
  run_all_demos.py
  docs/
    one_hour_teaching_plan.md
    context_components_map.md
    skill_creator_workflow.md

  00_rule_based_document_generation/
  01_doc_spec_portability/
  02_rich_doc_test_adapter/
  03_permission_bound_workflow/
```

每个 demo 都包含：

```text
AGENTS.md
opencode.json
README.md
.opencode/
  commands/
  tools/
  skills/
    <skill-name>/
      SKILL.md
      references/
      scripts/
      examples/
      assets/
scripts/
inputs/docs/configs/examples/
output/
```

---

## Demo00：基于规则的文档生成

**定位：实践入口项目。**
用当前这次教学作为场景：讲师准备 1 小时课程，讲四个 demo，用户问了 Skill、Tool、权限、上下文沉淀等问题。用户只说一句话，Agent 把它归一化成结构化课程状态，然后脚本生成：

```text
output/course_update.pptx
output/course_dashboard.xlsx
output/gantt_dashboard.html
output/agent_summary.md
output/context_manifest.json
```

教学重点：

```text
一句话需求
  → Agent 解析为结构化 course_status.json
  → Skill 规定生成流程
  → references/templates 提供模板和口径
  → scripts 生成 PPT/Excel/HTML
  → validator 检查输出
  → 人确认内容是否符合真实课程进度
```

这个 demo 用来开场讲清楚：
**LLM 负责理解和归纳，脚本负责稳定执行，Skill 负责编排流程，人工负责确认内容真实性。**

对应 Skill：

```text
00_rule_based_document_generation/
  .opencode/skills/teaching-document-generator/
    SKILL.md
    references/
    templates/
    scripts/
    examples/
    assets/
```

---

## Demo01：Doc Spec 开发规范与跨平台可移植实现

**对应你的第一个样例建议。**
我把原本“机台 A 到机台 B”的强业务场景改成更通用的 **Doc Spec → 多平台实现** 教学场景：同一份“工单优先级规范”需要在不同平台实现。

流程：

```text
历史规范文档
+ 平台 A 历史 Python 样例
+ 平台 B 目标契约
  → spec_contract.json
  → 平台 B JavaScript 实现
  → Node.js 测试
  → portability_report.md
```

生成输出：

```text
01_doc_spec_portability/output/spec_contract.json
01_doc_spec_portability/output/platform_b/rule_engine.js
01_doc_spec_portability/output/platform_b/rule_engine.test.js
01_doc_spec_portability/output/portability_report.md
```

教学重点：

```text
不要直接从文档生成最终代码。
先抽取中间 contract，再生成代码，再跑测试，再人工确认语义。
```

对应 Skill：

```text
01_doc_spec_portability/
  .opencode/skills/doc-spec-portability/
    SKILL.md
    references/
      spec_authoring_rules.md
      portability_checklist.md
      platform_b_contract.md
    examples/
      sample_prompts.md
    scripts/
    assets/
```

这个 demo 主要讲：

```text
历史文档如何沉淀成 references
历史样例如何帮助 Agent 理解实现风格
平台约束如何变成 contract
中间表示为什么比直接生成代码更可控
自动测试和人工 review 的边界
```

---

## Demo02：富文本 / PDF 信息抽取到测试实现适配

**对应你的第二个样例建议。**
我用一个 HTML 富文本导出样例模拟 PDF / Word / 网页文档导出后的结构化内容。文档里有验证模式、native directive 和 review note。Agent 不能直接“读完就生成代码”，而是要按规则抽取。

流程：

```text
rich_test_spec_export.html
+ extraction_rules.md
+ target_env_contract.json
  → extracted_patterns.json
  → generated_tests.py
  → validate_generated_tests.py
  → review_packet.md
```

生成输出：

```text
02_rich_doc_test_adapter/output/extracted_patterns.json
02_rich_doc_test_adapter/output/generated_tests.py
02_rich_doc_test_adapter/output/review_packet.md
```

教学重点：

```text
富文本 / PDF 信息抽取要有规则。
抽取结果先进入中间 JSON。
再根据环境包适配成代码。
语法可以自动验证，逻辑正确必须人工确认。
```

这个 demo 特别突出了你要求的几个点：

```text
AI 不只是能读、能给参考，也能调用脚本完成执行动作；
Skill 可以串联抽取、适配、验证、review packet；
中间阶段方案需要人介入；
结果若是代码，可以验证语法；
但业务逻辑、验证意图和阈值仍需人协同确认。
```

对应 Skill：

```text
02_rich_doc_test_adapter/
  .opencode/skills/rich-doc-test-adapter/
    SKILL.md
    references/
      extraction_rules.md
      human_review_checkpoints.md
      target_env_contract.md
    examples/
      sample_prompts.md
    scripts/
    assets/
```

---

## Demo03：权限约束与受控数据 / 配置操作

**对应你的第三个样例建议。**
这个 demo 不再强调具体 lot history，而是抽象成“重要数据和配置的受控访问”教学场景。Agent 不能直接读 protected 配置、不能自己拼查询、不能扩大查询范围，只能调用封装好的脚本。

流程：

```text
用户需求
  → Skill 归一化参数
  → approved_data_api.py 白名单查询
  → analysis_cli.py 分析
  → safe_config_cli.py 受控配置读取
  → audit_log.jsonl 审计
  → validate_guardrails.py 验证非法路径会失败
```

生成输出：

```text
03_permission_bound_workflow/output/query_result.csv
03_permission_bound_workflow/output/analysis_summary.json
03_permission_bound_workflow/output/permission_report.md
03_permission_bound_workflow/output/audit_log.jsonl
```

教学重点：

```text
不要只靠 prompt 提醒 Agent “别误操作”。
要用 opencode.json、AGENTS.md、Skill、脚本参数校验、白名单、审计日志和 validator 多层约束。
```

对应 Skill：

```text
03_permission_bound_workflow/
  .opencode/skills/permission-bound-data-workflow/
    SKILL.md
    references/
      permission_model.md
      safe_api_contract.md
      audit_and_stop_rules.md
    examples/
      sample_prompts.md
    scripts/
    assets/
```

---

## 适合课堂讲解的主线

你可以按这个顺序讲：

```text
Demo00：
先让大家看到一个完整 Agent 应用长什么样：
一句话 → 结构化输入 → Skill → 脚本 → PPT/Excel/Gantt → 验证。

Demo01：
再讲如何把历史文档、历史样例、平台契约沉淀成可移植开发上下文。

Demo02：
接着讲更复杂的文档抽取：PDF/富文本不是直接喂给模型，而是先设计抽取规则和中间表示。

Demo03：
最后讲安全边界：越接近重要数据和配置，越要封装 API/CLI，限制参数，留下审计。
```

根目录里也放了配套讲解文档：

```text
docs/one_hour_teaching_plan.md
docs/context_components_map.md
docs/skill_creator_workflow.md
```

---

## 这版 demo 的 Takeaway

可以直接放到课件里：

```text
Prompt 是一次性输入；
Context 是可复用资产；
Skill 是 Agent 作业指导书；
Tool/API/Script 是受控执行能力；
Validator 只能验证格式、语法、schema 和边界；
Human Review 负责确认业务逻辑、规范语义和最终结论。
```

下载新版 demo kit：
[agent_vibe_opencode_teaching_demos_v2.zip](sandbox:/mnt/data/agent_vibe_opencode_teaching_demos_v2.zip)

[1]: https://opencode.ai/docs/skills/?utm_source=chatgpt.com "Agent Skills | OpenCode"
