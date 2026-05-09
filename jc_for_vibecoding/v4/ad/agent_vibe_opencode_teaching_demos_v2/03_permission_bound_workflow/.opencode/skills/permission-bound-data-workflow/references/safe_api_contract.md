# Safe API Contract

允许：

- metric: latency_ms, error_rate
- team: alpha, beta
- query window: <= 14 days
- output path: output/*.csv

禁止：

- 生产库连接；
- 任意 SQL；
- 读取 protected/；
- 修改 secret / token / production 配置；
- 跳过 audit log。
