# AGENTS.md — 半导体蚀刻多智能体系统

## 仓库结构

```
ref/                                # 参考文档 — OpenCode Tool/Subagent 教程
.opencode/
├── agent/                          # 8个 Subagent 定义 (.md)
│   ├── etch-orchestrator.md        # 主控编排 (Supervisor Pattern)
│   ├── etch-mechanism.md           # 机理模型 (理论驱动，无仿真后端)
│   ├── etch-literature.md          # 文献检索 (API: 10.18.220.244:32300)
│   ├── etch-data.md                # 数据挖掘 (API: 10.20.52.249:5314/5315)
│   ├── etch-doe.md                 # 实验设计 (Skill封装)
│   ├── etch-blue-team.md           # 蓝军审查 (纯LLM对抗性评估)
│   ├── etch-triz.md                # TRIZ创新方法 (搭配本地工具)
│   └── etch-summary.md             # 综合总结 (信息整合+报告)
├── tools/                          # 7个自定义工具 (.ts)
│   ├── literature-api.ts           # 文献API调用的完整工作流
│   ├── data-load.ts                # 数据加载与预处理
│   ├── data-analyze.ts             # 6模型对比分析
│   ├── data-optimize.ts            # NSGA-II多目标优化
│   ├── data-predict.ts             # 交互式参数探索
│   ├── mechanism-placeholder.ts    # 机理占位 (理论分析)
│   └── triz-reference.ts           # TRIZ矛盾矩阵查询
└── skill/
    └── etch-engineer.md            # 蚀刻技能 — 统一入口
opencode.json                       # 主配置 (8 subagent hidden)
```

## 架构: Supervisor Pattern

```
Orchestrator → 并行: 机理 + 文献 + 数据
             → 按需串行: 蓝军Review → DOE → TRIZ
             → 最终: Summary整合
```

Orchestrator 通过 `task()` 调用各 Subagent，权限由 `permission.task` 严格控制（仅 allow `etch-*` 模式）。

## 各 Subagent 实现状态

| Subagent | 后端 | 说明 |
|----------|------|------|
| orchestrator | 无 | 纯编排指令 |
| mechanism | **占位** | 理论分析，无定量仿真 |
| literature | **API** | 10.18.220.244:32300 (当前离线) |
| data | **API** | 10.20.52.249:5314/5315 (当前离线) |
| doe | **Skill** | 复用已有 DOE Skill |
| blue-team | 无 | 纯 LLM Review |
| triz | 本地工具 | `triz-reference.ts` 含矛盾矩阵 |
| summary | 无 | 纯信息整合 |

API 不可用时工具返回 `status: "unavailable"`，Subagent 处理 fallback。

## 入口

用户调用: `@etch-orchestrator <蚀刻问题>`

加载 Skill: skill 工具加载 `etch-engineer.md`

## 定制工具约定

- 使用 `@opencode-ai/plugin` 的 `tool()` 辅助函数
- 参数使用 Zod schema 做类型校验
- 返回 JSON string，含 `status` (`success|error|unavailable`)
- 外部 API 调用含 try/catch + fallback 信息
