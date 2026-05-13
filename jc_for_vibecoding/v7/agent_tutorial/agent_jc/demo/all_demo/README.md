# OpenCode 辅助编程与 Context 工程教学包

这个仓库把原来的具体业务 demo 重新定位为 **OpenCode 辅助编程与 context 工程教学包**。它不追求还原某个真实部门系统，而是用四个从 0 到 1 的对话式 agent 项目，演示如何把“业务场景的一句话需求”沉淀成可稳定运行的 Agent 应用。

核心教学目标：

1. 演示 Agent 应用不是单个 prompt，而是 **对话模式 + 项目规则 + Skill + 工具/API + 脚本 + 权限 + 验证闭环**。
2. 让学员理解 context 不是越堆越大的提示词，而是可以分层、外部化、可交接的系统。
3. 通过 OpenCode 项目结构，展示如何把历史文档、样例、开发规范、测试项、权限边界和验证脚本沉淀下来。
4. 训练四个方法论：先设计动作空间，再谈自治；先取证、验证、纠偏，再自动完成；先分层 context，再扩展上下文；先工具和安全边界，再生产落地。

## 四个 demo

| 编号 | 项目 | 教学重点 | 一句话场景 |
|---|---|---|---|
| 00 | `00_rule_dashboard_agent` | 规则、模板、脚本、OpenCode 工作流入门 | 用户一句话更新培训进展，Agent 按模板生成 HTML 看板和进度报告 |
| 01 | `01_doc_spec_portability` | 基于历史文档和样例的开发、跨语言/平台迁移规范 | 根据功能文档和迁移规范，把 Python 规则模块迁移为 JS/TS 风格模块并跑 golden tests |
| 02 | `02_pdf_reproduction_agent` | PDF/论文信息抽取、Skill 串联、环境包适配、验证闭环 | 从 synthetic paper PDF 抽取实验逻辑，结合本地环境库生成可运行复现项目 |
| 03 | `03_permission_sandbox_agent` | 权限约束、动作空间设计、受控脚本/API、保护数据和配置 | 用户提出配置变更或 lot history 查询，Agent 只能通过封装脚本/API 生成 sandbox 输出，不能直接读写 protected 文件 |

## 快速运行

```bash
python3 run_all_demos.py
```

单独运行某个项目：

```bash
cd 00_rule_dashboard_agent && python3 run_demo.py
cd 01_doc_spec_portability && python3 run_demo.py
cd 02_pdf_reproduction_agent && python3 run_demo.py
cd 03_permission_sandbox_agent && python3 run_demo.py
```

每个项目都包含：

```text
AGENTS.md                 # 项目长期规则，说明安全边界、目录结构、验证命令
opencode.json             # OpenCode 权限配置示例
.opencode/commands/       # 对话入口，例如 /dashboard、/port-spec
.opencode/skills/         # 可复用 Skill，含 references/templates/checklists
.opencode/tools/          # OpenCode custom tool 示例，封装脚本/API
scripts/                  # 可执行脚本，Agent 应优先调用这些脚本而不是临时写散乱命令
references/context/       # 历史文档、规范、模板、样例、schema
output/                   # demo 运行后生成的产物
```

## 建议 60 分钟教学节奏

```text
0-8 min   Demo 00：规则驱动文档/看板生成，讲 OpenCode 项目骨架
8-22 min  Demo 01：历史文档 + 样例 + golden test 如何支撑迁移开发
22-40 min Demo 02：PDF 信息抽取 -> Skill 串联 -> 代码生成 -> 验证
40-52 min Demo 03：权限约束、脚本/API 封装、受控动作空间、Data Service 防直连
52-60 min 总结：context 分层、验证闭环、Stop rules、二次开发模板
```

## 教学时要反复强调

- Agent 不是“会调用工具的大模型”，而是带状态的决策循环。
- OpenCode 的项目规则、Skill、Command、Custom Tool 和 Permission 共同构成 Agent 应用的运行上下文。
- 任何自动生成代码或配置的流程，都应有中间产物、验证脚本、manifest 和人工 review 点。
- 不要让 Agent 直接操作高风险数据、数据库或配置；让它调用受控脚本/API，并把可执行动作空间变窄。
