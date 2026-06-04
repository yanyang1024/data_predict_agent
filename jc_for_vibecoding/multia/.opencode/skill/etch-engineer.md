# 半导体蚀刻工艺多智能体技能

加载此技能后，您可以使用 `@etch-orchestrator` 主控来协调蚀刻工艺的全部7个专家子智能体，完成从问题分析到综合决策的全流程。

## 可用 Subagent

| 名称 | 职责 | 调用方式 |
|------|------|---------|
| `@etch-orchestrator` | **主控编排** — 拆解用户问题，协调各专家 | 用户直接调用 |
| `@etch-mechanism` | **机理模型** — 基于物理/化学机理的定性仿真分析 | Orchestrator 自动调用 |
| `@etch-literature` | **文献检索** — 半导体制造文献检索与知识迁移 | Orchestrator 自动调用 |
| `@etch-data` | **数据挖掘** — 历史数据建模与多目标优化 | Orchestrator 自动调用 |
| `@etch-doe` | **实验设计** — 交互式DOE实验设计与统计分析 | Orchestrator 自动调用 |
| `@etch-blue-team` | **蓝军审查** — 对抗性评估与风险识别 | Orchestrator 自动调用 |
| `@etch-triz` | **TRIZ创新** — 系统化创新方法论 | Orchestrator 自动调用 |
| `@etch-summary` | **综合总结** — 多源信息融合与决策建议 | Orchestrator 自动调用 |

## 典型使用方式

### 方式一：完整问题（推荐）
直接调用 Orchestrator 处理完整蚀刻工艺问题：
```
@etch-orchestrator 当前蚀刻工艺Bias CD偏大，层类型LCH，
刻蚀气体为C4F8/CF4/Ar，请分析原因并给出优化建议
```

### 方式二：单独咨询某个专家
```
@etch-literature 请检索高选择比SiO2刻蚀的相关文献
@etch-data 请对LCH层的历史数据进行多目标优化，约束Bias CD < 10nm
@etch-triz 刻蚀速率与选择比的矛盾如何解决？
```

### 方式三：指定部分专家组合
```
@etch-orchestrator 我只想看机理分析和数据优化的结果，
不需要文献和TRIZ。层类型MCH，偏压功率偏高导致损伤。
```

## 工作流说明

### 默认编排流程
```
Phase 1（并行分析）:
  机理模型 + 文献检索 + 数据分析
        │
Phase 2（按需串行）:
  ├─ 数据有推荐 → 蓝军审查
  ├─ 需要实验 → DOE实验设计
  └─ 需突破 → TRIZ创新方法
        │
Phase 3（综合输出）:
  Summary 整合所有结果
```

### 注意事项
- 各 Subagent 支持独立调用
- 文献和数据 API 可能因网络状态不可用，此时 Subagent 会明确提示
- 机理模型当前为定性分析，无定量仿真后端
- DOE 使用通用因子名（A, B, C…），需手动映射为实际 RCP 参数
