# 蚀刻多智能体系统 Subagent 能力规划 — 执行计划

## 目标
基于半导体蚀刻工艺场景，规划8个subagent的能力矩阵、信息贡献、交互关系，产出完整的技术架构设计文档。

## Stage 1 — 深度调研（并行）
- **技能**: `deep-research-swarm`
- **任务**: 
  - Agent_1: 调研半导体蚀刻工艺全流程、关键参数、常见问题（过刻蚀/undercut/残留/负载效应等）
  - Agent_2: 调研OpenCode Agent架构设计模式、subagent协作范式
  - Agent_3: 调研TRIZ方法论在半导体工艺优化中的应用案例
  - Agent_4: 调研DOE（实验设计）和贝叶斯优化在蚀刻工艺中的应用
- **输出**: 各领域调研摘要

## Stage 2 — 架构设计（基于调研结果）
- **技能**: 自主设计（Orchestrator主导）
- **任务**: 
  - 设计8个subagent的能力边界、输入输出规范
  - 设计agent间信息流转机制
  - 设计主agent调度逻辑
- **输出**: 详细架构设计文档

## Stage 3 — 报告撰写
- **技能**: `report-writing`
- **任务**: 将Stage 1和Stage 2成果整合为完整的技术文档
- **输出**: `.md` 格式报告

## Stage 4 — 文档转换
- **技能**: `docx`
- **任务**: 将markdown报告转换为Word文档
- **输出**: `.docx` 格式最终交付物
