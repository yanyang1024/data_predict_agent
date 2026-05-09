# 审计与停止规则

每次 approved query 必须记录：action、metric、team、start_date、end_date、rows。

停止规则：参数越界、敏感 key、生产配置、非白名单 metric/team、超过 max_query_days。
