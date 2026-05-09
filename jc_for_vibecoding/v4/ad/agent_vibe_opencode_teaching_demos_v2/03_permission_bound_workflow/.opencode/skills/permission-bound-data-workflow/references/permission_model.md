# 权限模型说明

- AGENTS.md：文字层面的行为规则。
- opencode.json：工具权限和 Skill 权限。
- scripts/approved_data_api.py：参数白名单、时间窗口、行数限制和审计。
- scripts/safe_config_cli.py：配置 key 白名单和值校验。
- validate_guardrails.py：验证合法路径成功、非法路径失败。

多层约束互相补位，不能只靠 prompt 提醒。
