已按你的要求重做成 **v2 教学版 demo kit**，重点转向 OpenCode 辅助编程、从 0 到 1 的 Agent 应用构建、Skill 目录沉淀、规则提取、人工验证介入和权限边界教学。

下载新版：
[agent_vibe_opencode_teaching_demos_v2.zip](sandbox:/mnt/data/agent_vibe_opencode_teaching_demos_v2.zip)

原始部门需求我保留了“场景影子”，但实现上已抽象为更适合教学的通用样例：PETE/Final Testing 的“转平台”被改成 doc spec 可移植开发；IC Design/Logic 的“JEDEC + 环境库”被改成富文本/PDF 规则提取、环境适配和验证流水线；LKG&System 的“数据库 adhoc 拉数”被改成权限约束和 approved script 执行空间示例。

# 新版 demo 结构

```text
agent_vibe_opencode_teaching_demos_v2/
  README.md
  TEACHING_GUIDE_60MIN.md
  AGENTS.md
  opencode.json
  requirements.txt
  run_all_demos.py

  demo_00_rule_based_doc_generation/
  demo_01_doc_spec_portability/
  demo_02_rich_text_rule_extraction_pipeline/
  demo_03_permission_constrained_execution/
```

我参考了 OpenCode 当前文档来组织目录：OpenCode 的 Skills 通过 `SKILL.md` 定义，并可放在 `.opencode/skills/<name>/SKILL.md`；Commands 可放在 `.opencode/commands/`，并支持 `$ARGUMENTS`；Custom Tools 放在 `.opencode/tools/`，虽然工具定义是 TypeScript/JavaScript，但可调用 Python 或 shell 脚本；权限通过 `permission` 配置把动作设为 `allow / ask / deny`；项目长期规则用 `AGENTS.md` 承载。([OpenCode][1])

---

# Demo 00：基于规则的文档生成

**教学定位：** 这是新增的第 0 个样例，用于作为实践开场，讲“如何从一句话开始，协同 AI 做一个稳定运行的 Agent 应用”。

用户一句话：

```text
基于今天 1 小时 OpenCode + Agent 教学安排，
生成当前进度看板、PPT大纲和 Excel 甘特图；
当前已完成开场，Demo0 正在进行，
用户问题：怎么保证 Agent 生成物稳定？
```

生成内容：

```text
output/
  teaching_brief.md
  teaching_progress_deck.pptx
  teaching_dashboard.xlsx
  teaching_gantt.png
  dashboard.html
  generation_manifest.json
```

这个 demo 用来讲：

```text
用户一句话
  -> OpenCode Command
  -> Skill 加载规则
  -> 读取模板和进度数据
  -> 执行稳定脚本
  -> 生成 PPT / Excel / 甘特图 / dashboard
  -> 人工 review
```

对应 Skill 目录：

```text
demo_00_rule_based_doc_generation/
  .opencode/
    commands/
      teach-status.md
    tools/
      training_artifact_generator.ts
    skills/
      rule-based-doc-generator/
        SKILL.md
        references/
          document_rules.md
          template_contract.md
          human_review_checklist.md
        examples/
          sample_request.md
        scripts/
          run_generator.py
```

课堂重点是：**Agent 不是直接“随便生成 PPT”，而是按模板、schema、脚本、manifest 生成可复查产物。** OpenAI 对 Skills 的定位也是可复用、可共享的工作流，可以包含说明、示例和代码，用来让 ChatGPT 更一致地完成特定任务。([OpenAI Help Center][2])

---

# Demo 01：Doc Spec 可移植开发

**对应你的第一个建议：** doc spec 开发规范；基于历史文档和样例的开发；同一文档在不同平台上的可移植实现。

我把它抽象成一个订单计价规范，而不是贴近机台测试语言。这样更适合教学，因为学员能专注理解流程：

```text
Doc Spec + Golden Cases + Historical Samples
  -> normalized_rules.json
  -> Platform Python implementation
  -> Platform Node implementation
  -> portability_report.md
```

核心文件：

```text
demo_01_doc_spec_portability/
  docs/
    order_pricing_spec.md
  examples/
    platform_a_reference.py
    platform_b_style_reference.mjs
  golden_cases/
    order_pricing_cases.json
  scripts/
    extract_spec_rules.py
    generate_implementations.py
    validate_portability.py
```

对应 Skill 目录：

```text
.opencode/
  commands/
    build-portable-spec.md
  tools/
    spec_portability_runner.ts
  skills/
    spec-portability-builder/
      SKILL.md
      references/
        spec_extraction_rules.md
        platform_adapter_contract.md
        review_checklist.md
      examples/
        sample_prompt.md
      scripts/
        run_pipeline.py
```

课堂讲法：

```text
Plan 阶段：
先读 spec、历史样例和 golden cases，不直接改代码。

Act 阶段：
先抽取 normalized_rules.json，再生成 Python / Node 两个平台实现。

Validate 阶段：
用同一组 golden cases 比对两个平台输出。

Human Review：
验证一致性不等于确认业务语义正确。
```

---

# Demo 02：富文本 / PDF 规则提取 + Skill 串联 + 验证

**对应你的第二个建议：** 从 PDF 或其他富文本中提取验证和测试模式、原生代码指令，并根据环境包重新编写适配；重点讲 Skill 串联、中间方案人工介入、语法可验证但逻辑需人协同。

我做了一个 synthetic validation manual，同时提供 Markdown 和 PDF：

```text
source_docs/
  validation_manual.md
  validation_manual.pdf
```

流水线：

```text
PDF / Markdown Manual
  -> manual-rule-extractor skill
  -> extracted_rules.json
  -> environment-sequence-adapter skill
  -> sequence_ir.json + adapted_sequence.py
  -> syntax-validation-gate skill
  -> validation_manifest.json
  -> human_review_points.md
```

对应 Skill 目录比较完整，专门用于讲模块串联：

```text
.opencode/
  commands/
    extract-adapt-validate.md
  tools/
    validation_pipeline_runner.ts
  skills/
    rich-text-extraction-pipeline/
      SKILL.md
      references/
      examples/
    manual-rule-extractor/
      SKILL.md
      references/
      examples/
    environment-sequence-adapter/
      SKILL.md
      references/
      examples/
    syntax-validation-gate/
      SKILL.md
      references/
      examples/
```

生成输出：

```text
output/
  extracted_rules.json
  sequence_ir.json
  adapted_sequence.py
  validation_manifest.json
  human_review_points.md
```

`validation_manifest.json` 里明确写了：

```json
{
  "syntax_valid": true,
  "dry_run_exit_code": 0,
  "logic_correctness_verified": false,
  "human_review_required": [
    "Human must confirm reset polarity",
    "Human must confirm allowed voltage range",
    "Human must confirm jitter model"
  ]
}
```

这正好用于课堂强调：

```text
Agent 能读文档，也能执行抽取、适配和语法验证；
但 verification intent、测试充分性、业务语义仍然需要人确认。
```

我也渲染检查了 demo PDF，确认没有明显截断或重叠；这个 PDF 是教学用 synthetic material，不包含真实 manual 内容。

---

# Demo 03：权限约束和 approved script 执行空间

**对应你的第三个建议：** 重要数据和配置避免 Agent 直接操作，用封装脚本和参数约束 Agent 的执行空间。

这个 demo 把“数据库 adhoc 拉数”抽象成安全查询：

```text
User request
  -> OpenCode permission boundary
  -> approved_query.py
  -> query_result.csv + query_manifest.json
  -> render_safe_report.py
  -> safe_report.md
```

同时模拟 protected data 和 protected config：

```text
protected_data/
  production_config.yaml
  customer_sensitive_metrics.csv
```

Agent 不应该直接读或改这些文件。它只能使用：

```text
scripts/
  approved_query.py
  render_safe_report.py
  propose_config_change.py
```

对应 Skill 目录：

```text
.opencode/
  commands/
    safe-query.md
    propose-config-change.md
  tools/
    approved_query.ts
    propose_config_change.ts
  skills/
    permission-constrained-analysis/
      SKILL.md
      references/
        policy_design.md
        review_checklist.md
      examples/
        sample_prompt.md
      scripts/
        run_safe_query.py
```

这个 demo 重点讲：

```text
不要只靠 prompt 说“不要读生产数据”；
要用 opencode.json、AGENTS.md、approved CLI、参数白名单、manifest 和 proposal 文件共同约束。
```

OpenCode 文档中，权限配置正是用于控制 read、edit、bash、skill、webfetch 等动作是自动允许、询问还是拒绝；这和该 demo 的教学目标一致。([OpenCode][3])

---

# 已验证的内容

我在本地跑过：

```bash
python3 run_all_demos.py
```

该脚本会生成 Demo 00-02 的完整输出。Demo 03 是权限边界教学，我保留为按 README 分步运行，这样课堂上更容易逐步展示“允许什么、拒绝什么、manifest 记录什么、proposal 为什么不是直接修改”。Demo 03 的以下命令也已单独跑通：

```bash
python3 scripts/approved_query.py ...
python3 scripts/render_safe_report.py ...
python3 scripts/propose_config_change.py ...
python3 tests/test_permission_boundary.py
```

包里已保留生成好的 sample output，便于你直接打开讲解。

---

# 建议你课堂中这样串起来

```text
Demo 00：
从一句话到稳定产物。
讲 OpenCode 项目结构、AGENTS.md、Command、Skill、Tool、脚本、manifest。

Demo 01：
从文档规范到多平台实现。
讲 Plan -> normalized rules -> generated code -> golden case validation。

Demo 02：
从 PDF/富文本到规则提取和环境适配。
讲 Skill 串联、IR、中间结果人工 review、语法验证 vs 逻辑验证。

Demo 03：
从“Agent 能做”到“Agent 被允许做什么”。
讲权限、approved scripts、参数白名单、protected data、proposal 而不是直接修改。
```

下载新版：
[agent_vibe_opencode_teaching_demos_v2.zip](sandbox:/mnt/data/agent_vibe_opencode_teaching_demos_v2.zip)

[1]: https://opencode.ai/docs/skills/ "https://opencode.ai/docs/skills/"
[2]: https://help.openai.com/en/articles/20001066-skills-in-chatgpt "https://help.openai.com/en/articles/20001066-skills-in-chatgpt"
[3]: https://opencode.ai/docs/permissions "https://opencode.ai/docs/permissions"
