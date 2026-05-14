---
description: 通过受控数据服务查询 lot history 汇总和 QTime 图，不直接读取原始数据
agent: plan
---

Use the `guarded-change-workflow` skill.

用户请求：

$ARGUMENTS

要求：
1. 先识别 lot id 和查询目的；只允许 sandbox 教学查询。
2. 不要读取 `protected/customer_data.csv` 或 `protected/lot_history_raw.csv`。
3. 只能调用 `scripts/query_lot_history_service.py` 获取聚合结果和图。
4. 调用 `scripts/validate_data_service.py` 验证数据输出、审计日志、字段白名单和 protected hash。
5. 调用 `../scripts/demo_viewer.py --demo 03_permission_sandbox_agent --port 8763 --restart` 暴露聚合摘要、QTime 图和验证 manifest。
6. 最终回答要说明数据服务返回了哪些聚合字段、哪些原始字段被隐藏、哪些业务结论需要人工确认，以及浏览器 URL。
