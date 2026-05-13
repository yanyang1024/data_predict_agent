# Dashboard Progress Schema

```json
{
  "title": "课程标题",
  "total_minutes": 60,
  "current_minute": 18,
  "speaker": "讲师",
  "current_focus": "当前讲解重点",
  "user_question": "用户问题",
  "demos": [
    {
      "id": "00",
      "name": "规则驱动看板",
      "planned_start": 0,
      "planned_minutes": 8,
      "status": "completed | in_progress | not_started | blocked",
      "actual_note": "当前状态说明"
    }
  ],
  "risks": ["风险 1"],
  "next_actions": ["下一步 1"]
}
```
