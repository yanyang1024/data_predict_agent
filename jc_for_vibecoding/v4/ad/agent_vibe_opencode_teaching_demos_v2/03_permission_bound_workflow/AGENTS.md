# Demo03 项目规则

1. 不要直接读取或修改 `protected/` 目录。
2. 查询数据必须通过 `scripts/approved_data_api.py`。
3. 分析必须通过 `scripts/analysis_cli.py`。
4. 配置读取/修改必须通过 `scripts/safe_config_cli.py`。
5. 参数越界、非白名单 metric、超过时间窗口都必须失败。
6. 每次查询必须写 audit log。
7. 不能把 demo 数据分析结论当作生产决策。
