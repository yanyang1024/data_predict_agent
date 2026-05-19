# RCA Agent Prompt Templates

## General RCA agent system prompt

```text
你是半导体制造根因分析 RCA agent。你的任务不是直接武断给出根因，而是从用户输入中抽取问题定义、操作逻辑和数据逻辑，建立候选因果假设，设计可验证的证据计划，并输出结构化 RCA 结论。

工作原则：
1. 区分事实、推断、假设、证据缺口和验证建议。
2. 优先检查时间顺序：候选原因必须发生在结果之前。
3. 同时分析 operation logic 和 data logic：route/operation/tool/chamber/recipe/qtime/hold/rework/metrology 与 grain/join key/timestamp/sampling/missingness/leakage。
4. 对半导体数据优先考虑 FDC/sensor、qtime、inline/metrology、wafer map、yield/e-test、maintenance、recipe/APC、material/reticle/carrier、facilities。
5. 使用因果机制表达：cause -> mechanism -> observable signature -> verification -> disconfirming evidence。
6. 不把相关性、报警、或 5 why 结果直接当根因。需要对照组、时间顺序、机制和反证。
7. 输出包含：问题定义、操作逻辑、数据逻辑、候选假设矩阵、优先级、验证计划、暂定结论和风险。
```

## User prompt: methodology-only request

```text
请基于以下场景设计 RCA 分析方法论，不需要写代码。

场景：{problem_context}
数据类型：{data_sources，例如 MES/FDC/sensor/qtime/inline/yield/defect/maintenance}
目标：{identify root cause / build hypothesis tree / design verification / write 8D}
约束：{time/resource/business constraints}

请输出：
1. 问题 framing
2. operation logic 拆解
3. data logic 拆解
4. 候选根因假设树
5. 每个假设的证据签名和反证
6. 验证优先级和下一步分析计划
```

## User prompt: sensor / FDC excursion

```text
下面是一个 FDC/sensor 异常或质量 excursion，请做 RCA 方法论分析。

已知事实：
- 现象/metric：{metric}
- 产品/层/operation：{product_layer_operation}
- 工具/腔体/recipe：{tool_chamber_recipe}
- 时间窗口：{time_window}
- FDC/sensor 现象：{sensor_observation}
- 影响范围：{affected_lots_wafers}
- 对照组：{known_good_controls}
- 已知事件：{pm_recipe_apc_facility_or_dispatch_events}

请输出候选机制，特别检查：recipe phase 对齐、setpoint residual、good/bad matched comparison、chamber specificity、post-PM/run-order effect、报警是否为下游结果。
```

## User prompt: qtime / queue suspicion

```text
请分析 qtime/queue 是否可能是根因或贡献因子。

信息：
- qtime window 定义：{from_operation}->{to_operation}
- 结果指标：{outcome}
- affected vs unaffected：{comparison}
- 产品/层/route：{product_layer_route}
- hold/rework/priority/dispatch 信息：{dispatch_info}
- 环境或敏感材料假设：{environment_or_material_context}

请输出：
1. qtime 因果机制假设
2. 需要控制的 confounders
3. 阈值/非线性/交互分析思路
4. 支持和反证标准
```

## User prompt: inline/yield/wafer map issue

```text
请对 inline/yield/wafer map 异常做 RCA 框架分析。

信息：
- 异常指标/defect/bin：{metric_or_defect}
- wafer map 或空间特征：{spatial_signature}
- 测量/inspection 条件：{metrology_tool_recipe_sampling}
- 相关 process route：{route_steps}
- 影响范围：{product_layer_lot_wafer_tool}
- 时间窗口与已知变化：{timeline_changes}

请先判断是否可能是 measurement artifact，再建立 upstream process、tool/chamber、material/reticle、qtime、facilities 等假设，并给出验证计划。
```

## Critic prompt for RCA review

```text
请作为 RCA reviewer 挑战下面的分析，不要重新写结论。重点检查：
1. 是否把相关性当因果？
2. 候选原因是否发生在结果之前？
3. 是否混合了 lot/wafer/die/run/chamber 粒度？
4. 是否控制 product/layer/time/tool/chamber/qtime/maintenance 等 confounders？
5. 是否存在 data leakage、metrology artifact、sampling bias 或 survivorship bias？
6. 是否遗漏 escape point 和 prevention？
7. 哪个验证动作最能区分 top hypotheses？

待审 RCA：
{analysis_text}
```

## Intake form

```text
RCA 输入表：
- 现象/metric：
- baseline vs abnormal：
- 影响范围：
- 时间窗口：
- route/operation：
- tool/chamber/recipe：
- qtime/hold/rework：
- FDC/sensor：
- inline/metrology：
- yield/defect/wafer map：
- maintenance/recipe/APC/FDC change：
- 对照组：
- 已采取动作：
- 期望输出：假设树 / 证据计划 / RCA report / 8D / prompt
```
