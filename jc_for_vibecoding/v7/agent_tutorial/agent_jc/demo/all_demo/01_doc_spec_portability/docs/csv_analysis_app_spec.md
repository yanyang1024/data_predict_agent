# CSV Table Analysis App Functional Spec

## 输入

用户上传一个 CSV 文件。首行必须是字段名，后续每一行是业务数据。

演示数据使用 `tests/sample_sales.csv`，字段包括：

- `day`
- `product`
- `units`
- `revenue`
- `defect_rate`

## 功能要求

1. 读取上传的 CSV，不把原始文件持久化到磁盘。
2. 展示数据总览：行数、列数、数值列数量、推荐绘图列。
3. 自动识别所有完整数值列。
4. 对每个数值列计算 `count`、`mean`、`min`、`max`。
5. 对每个字段统计缺失值数量。
6. 为推荐数值列生成一个柱状 SVG 图，方便浏览器直接展示。
7. 当 CSV 缺少表头、没有数据行或没有数值列时，页面给出清晰错误或空状态。

## 非目标

- 不使用 pandas、matplotlib 或外部数据分析库。
- 不实现用户登录、文件持久化、数据库写入或异步任务。
- 不声称覆盖生产级 CSV 编码、超大文件和安全扫描。

