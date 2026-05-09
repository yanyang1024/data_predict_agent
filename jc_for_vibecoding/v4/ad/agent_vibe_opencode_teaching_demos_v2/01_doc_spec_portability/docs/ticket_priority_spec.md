# 工单优先级规范 v1.0

## 输入字段

| 字段 | 类型 | 说明 |
|---|---|---|
| outage | boolean | 是否为线上中断 |
| severity | string | low / medium / high |
| customer_tier | string | standard / enterprise |
| age_hours | number | 工单创建到当前的小时数 |

## 输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| priority | string | P0 / P1 / P2 / P3 |
| route | string | 分派队列 |
| sla_hours | number | 目标响应时长 |

## 规则表

| rule_id | condition | priority | route | sla_hours | note |
|---|---|---|---|---:|---|
| R1 | outage == true | P0 | incident-war-room | 1 | 中断优先级最高 |
| R2 | severity == high AND customer_tier == enterprise | P1 | senior-support | 4 | 企业客户高严重度 |
| R3 | severity == high | P2 | support | 8 | 一般高严重度 |
| R4 | age_hours >= 72 | P2 | support | 8 | 长时间未处理升级 |
| R5 | default | P3 | support | 24 | 默认规则 |

## 可移植性要求

1. 所有平台必须遵循相同规则顺序。
2. 目标平台不得依赖本地时区。
3. 未识别字段应使用默认值，不得抛出未捕获异常。
4. 实现必须导出 `classify(ticket)` 函数。

## 人工确认点

- `severity` 大小写是否需要归一化；
- 多个规则同时命中时是否始终采用第一条；
- `age_hours` 缺失时是否按 0 处理。
