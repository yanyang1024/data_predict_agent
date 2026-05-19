# Plan: 构建半导体工程数据根因分析 Skill 模块

## 目标
创建一个面向半导体工程数据（机台数据、传感器数据、FDC、Q-time、Inline等）的根因分析（RCA）Skill，聚焦分析方法论层面，不涉及具体代码实现。

## Stage 1 — 研究与定位
- 加载 `skill-creator-swarm` 技能，了解 Skill 创建规范
- 检索现有类似 RCA / 数据分析 / 半导体相关的 Skill
- 研究半导体工程数据的典型分析方法论：
  - FDC (Fault Detection and Classification) 分析
  - Q-time (Queue Time) 分析
  - Inline 数据分析
  - 机台传感器数据因果分析
  - SPC / APC 相关分析逻辑
  - 常见的 RCA 方法论（5 Whys, Fishbone, 假设检验, 相关性分析, 实验设计等）

## Stage 2 — Skill 设计与撰写
- 基于研究结果，设计 Skill 的核心模块：
  - Skill 定位与适用范围
  - 半导体数据类型与特征定义
  - RCA 分析方法论框架
  - Agent Prompt 模板（用于驱动大模型执行分析）
  - 多维度因果分析逻辑（操作逻辑 vs 数据逻辑）
- 撰写完整的 SKILL.md

## Stage 3 — 验证与交付
- 检查 Skill 的完整性和一致性
- 确保不涉及具体代码，聚焦方法论
- 打包为 .skill 文件交付

## 输出
- `/mnt/agents/output/root-cause-analysis-semiconductor.skill`
