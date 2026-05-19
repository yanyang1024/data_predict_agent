# RCA Output Templates

## Compact RCA answer

Use when the user asks for analysis from limited text.

```markdown
# RCA 初步分析

## 1. 问题定义
- 现象：
- 影响范围：
- 时间窗口：
- 当前已知事实：
- 关键缺口：

## 2. 操作逻辑
[按 route / operation / tool / chamber / recipe / qtime / hold / metrology 顺序重建]

## 3. 数据逻辑
[说明粒度、join key、时间戳、采样、lag/lead、潜在偏差]

## 4. 候选根因假设
| 优先级 | 假设 | 因果机制 | 支持证据 | 反证/缺口 | 下一步验证 |
|---|---|---|---|---|---|

## 5. 推荐验证计划
| 步骤 | 数据/比较 | 目的 | 预期支持信号 | 若未观察到则 |
|---|---|---|---|---|

## 6. 暂定结论
[概率化表达，避免过度确认]
```

## Hypothesis matrix

Use when comparing many possible causes.

| Hypothesis | Mechanism | Required temporal order | Expected bad-vs-good signature | Current evidence | Disconfirming evidence | Priority |
|---|---|---|---|---|---|---|

Priority guidance:

- **P1**: high plausibility, high impact, easy/urgent to verify.
- **P2**: plausible but needs more data or has moderate coverage.
- **P3**: weak, broad, or low actionability.

## Evidence plan

| Question | Data needed | Grain | Control group | Method | Decision criterion |
|---|---|---|---|---|---|
| Did chamber B cause the shift? | chamber path, metric, time, product/layer | wafer/run | sister chambers same product/time | stratified bad-good comparison | bad enrichment remains after product/time control |
| Did qtime matter? | qtime start/end, outcome, product/layer | wafer/lot | non-violating lots same product/layer | threshold/segmented comparison | outcome increases after defined qtime boundary |
| Is it a metrology artifact? | repeat metrology, tool/recipe, gauge data | wafer/site | alternate metrology tool/recipe | repeatability/tool matching | shift disappears on independent measurement |

## 8D-style RCA report

```markdown
# 8D / RCA Report

## D0. Preparation and containment
- Problem owner:
- Immediate containment:
- Material disposition:

## D1. Team / expertise needed
- Process:
- Equipment:
- Yield / defect / metrology:
- Data / automation:

## D2. Problem description
- What / where / when / how many / how severe:
- Baseline and excursion definition:

## D3. Interim containment
- Actions taken:
- Effectiveness check:

## D4. Root cause and escape point analysis
| Cause type | Candidate | Evidence | Status |
|---|---|---|---|
| occurrence cause |  |  |  |
| escape cause |  |  |  |
| systemic cause |  |  |  |

## D5. Permanent corrective action
- Action:
- Owner:
- Risk:
- Validation plan:

## D6. Implementation and validation
- Before/after metric:
- Monitoring window:

## D7. Prevention
- FMEA/control plan/FDC/APC/qtime rule update:
- Standardization:

## D8. Closure
- Lessons learned:
- Remaining risks:
```

## Text fishbone template for semiconductor RCA

```markdown
Effect: [symptom / metric / affected scope]

1. Product / process / design
   - [potential cause] -> [mechanism] -> [evidence to check]
2. Tool / chamber / module
   -
3. Recipe / APC / FDC / control logic
   -
4. Time / qtime / dispatch / queue
   -
5. Material / reticle / carrier / consumables
   -
6. Measurement / metrology / inspection / yield test
   -
7. People / procedure / change management
   -
8. Environment / facilities / utilities
   -
```

## Causal graph text template

```markdown
Outcome: [Y]
Candidate causes: [X1, X2, X3]
Confounders: [C1, C2]
Mediators: [M1]
Controls to avoid: [post-outcome variables or downstream alarms]

Proposed DAG text:
C1 -> X1
C1 -> Y
X1 -> M1 -> Y
X2 -> Y
Y -> downstream alarm  [do not control for this]

Identification logic:
- Compare X1 exposed vs unexposed within same C1 strata.
- Do not treat downstream alarm as a cause unless it occurred before Y.
- Seek negative controls that should not be affected by X1.
```

## Minimum data request template

Use this only when the input is too thin for useful analysis.

```markdown
为形成可验证 RCA，请补充以下最小信息：
1. 问题指标：metric、单位、规格/目标、baseline、异常值。
2. 影响范围：product/layer/route/op/tool/chamber/recipe/lot/wafer。
3. 时间窗口：last known good、first bad、恢复时间。
4. 对照组：同期正常 lot/wafer/tool/chamber。
5. 可用数据：MES、FDC、sensor trace、qtime、inline、yield、defect map、maintenance、recipe change。
6. 已采取动作：hold、tool down、recipe rollback、PM、retest。
```
