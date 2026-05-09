# 富文本 / PDF 信息抽取规则

## 目标

从 PDF、Word、网页或富文本导出的材料中抽取稳定的中间表示，而不是直接生成最终代码。

## 推荐流程

1. 首选从 PDF/Word 导出结构化文本、HTML 或 Markdown。
2. 保留标题层级、表格、代码块和编号列表。
3. OCR 只作为最后手段，且必须人工抽查。
4. 先抽取为 JSON：pattern_id、intent、native_directive、expected、review_note。
5. 对 native directive 做最小解析，不要猜测不可见语义。
6. 任何不确定阈值、周期、地址、corner，都写入 review packet。

## 字段规范

| 字段 | 说明 |
|---|---|
| pattern_id | 稳定 ID，作为测试函数名的一部分 |
| intent | 验证意图 |
| native_directive | 原生或旧环境指令 |
| expected | 期望结果 |
| review_note | 人工确认点 |

## Stop Rules

- 表格列缺失时停止。
- native directive 无法映射到环境包时停止或标记 unsupported。
- 文档中阈值明显来自示例而非规范时，必须人工确认。
