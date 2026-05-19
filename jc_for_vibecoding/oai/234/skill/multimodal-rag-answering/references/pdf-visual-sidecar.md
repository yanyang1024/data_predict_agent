# PDF Visual Sidecar: 独立 PDF 视觉旁路知识库方法论

## 目标

在不改变原文本 RAG 知识库的前提下，新增一套独立的 PDF 图片管理、解析、索引、检索和返回逻辑，专门服务图文问答里的“图”。

这套逻辑应作为 sidecar 存在：

- 原文本 KB 继续负责文本 chunk、文本 embedding、文本召回和事实回答。
- Visual Sidecar 负责 PDF 页面渲染、图表/表格/图片 crop、caption/上下文绑定、视觉摘要、图片向量或文本索引、asset_uri 管理。
- 回答阶段把两路结果合并：文本 RAG 给事实，视觉旁路给证据图或解释图素材。

## 推荐整体架构

```text
PDF 原文
  |
  |-- 原文本 KB 原有链路：文本解析 -> chunk -> text embedding -> text retriever
  |
  `-- Visual Sidecar 新增链路：
        1. pdf register
        2. page render
        3. visual asset extraction
        4. metadata + caption + nearby text binding
        5. optional VLM visual summary
        6. visual index
        7. visual retrieval API
        8. answer composer
```

## 关键对象抽象

### Document

PDF 文件级元数据。

```json
{
  "doc_id": "原文本 KB 中同一个 doc_id，或稳定映射 id",
  "title": "文件标题",
  "source_uri": "原始 PDF 存储地址",
  "checksum": "PDF 内容 hash",
  "page_count": 28,
  "ingested_at": "2026-05-19T00:00:00Z"
}
```

### Page Render

每页的渲染图，用于版式、整页截图、兜底展示。

```json
{
  "asset_id": "doc/page/0003",
  "asset_kind": "page_render",
  "doc_id": "...",
  "page": 3,
  "image_uri": "visual-kb/assets/doc/page_0003/page.png",
  "width": 1240,
  "height": 1754,
  "dpi": 144
}
```

### Visual Asset

图表、表格、嵌入图片或页面局部 crop。

```json
{
  "asset_id": "...",
  "asset_kind": "figure_crop|table_crop|embedded_image|page_region|page_render",
  "doc_id": "...",
  "page": 3,
  "bbox": [72.0, 120.0, 520.0, 410.0],
  "image_uri": "...",
  "caption": "Figure 2: ...",
  "nearby_text": "...",
  "visual_summary": "图中展示了...",
  "source_text_refs": ["chunk_id_1", "chunk_id_2"],
  "quality": {
    "is_tiny_icon": false,
    "ocr_confidence": null,
    "caption_confidence": 0.7
  }
}
```

## 解析与存储支持

### 1. PDF 注册

需要把原 PDF 的 `doc_id`、文件 hash、页数、源文件地址写入 Visual Sidecar 的 document 表。这里不改原 KB，只建立映射。

最低要求：

- `doc_id` 必须能和文本 RAG 命中的 doc_id 对齐。
- `source_uri` 或本地路径必须能用于重新渲染页面。
- `checksum` 用于增量更新和去重。

### 2. 页面渲染

为每页生成低/中分辨率页面图。

推荐：

- 默认 144 dpi 作为问答展示和 crop 基准。
- 重要文档可保存 72 dpi thumbnail + 144/200 dpi detail image。
- 页面图不一定直接展示，但作为 crop 和兜底证据很重要。

### 3. 视觉资产抽取

至少支持三种资产：

1. `page_render`：整页图，成本最低，能保留版式。
2. `embedded_image` / `image_region`：PDF 内嵌图片或图片块区域。
3. `table_crop` / `figure_crop`：由版面分析、规则或人工标注得到。

最小实现可以先做：页面渲染 + PyMuPDF 图片块 bbox crop + caption 绑定。后续再接入版面模型识别 table/figure。

### 4. Caption 与上下文绑定

每个视觉资产都应绑定文字上下文，否则检索效果会很差。

推荐字段：

- `caption`：图题、表题、Figure/Table 编号。
- `nearby_text`：bbox 上方、下方、左右临近文本。
- `page_text`：整页文本，用于 FTS 兜底。
- `section_title`：可由原文本 KB 或 PDF 目录补齐。
- `source_text_refs`：可选，关联原文本 KB chunk_id。

Caption 绑定优先级：

1. 与 bbox 距离最近、包含 Figure/Fig./Table/图/表/Chart/Diagram 等模式的文本。
2. bbox 下方文本优先于上方文本；很多论文和白皮书图题在图下方。
3. 如果没有 caption，用同页标题/相邻段落作为弱上下文。

### 5. 视觉摘要

可选但强烈建议。对每个图表/页面 crop 调 VLM 生成短摘要：

```json
{
  "visual_summary": "该图比较 A/B/C 三种方案在延迟和吞吐上的表现，A 在低负载下延迟最低。",
  "visible_text": ["Latency", "Throughput", "A", "B", "C"],
  "chart_type": "bar_chart",
  "entities": ["A", "B", "C"]
}
```

视觉摘要不要替代原图，只用于检索和排序。回答中若引用视觉摘要，应说明它来自模型解析，必要时让用户看到原图。

## 索引设计

最小可用索引采用“元数据过滤 + 文本检索”。后续再增强为多模态向量检索。

### A. 元数据索引

支持按以下字段过滤：

- `doc_id`
- `page`
- `asset_kind`
- `section_title`
- `has_caption`
- `quality.is_tiny_icon = false`

### B. 文本索引

把以下字段拼接建全文索引或 embedding：

```text
title + caption + nearby_text + visual_summary + visible_text + section_title + page_text
```

这个索引支持两类查询：

- 直接从用户 query 搜图。
- 根据文本 RAG 的 top chunks 反查同页/相邻页图片。

### C. 图像向量索引，可选增强

当文档里图片多、caption 少、问题高度视觉化时，增加图像向量：

- CLIP / SigLIP：适合通用文本搜图。
- ColPali / late interaction visual document retrieval：适合“把 PDF 页面当图片检索”。
- 专用 chart/table VLM embedding：适合图表密集场景。

### D. 混合排序

推荐综合分数：

```text
score = 0.35 * text_similarity
      + 0.25 * page_proximity
      + 0.20 * caption_match
      + 0.10 * visual_embedding_similarity
      + 0.10 * quality_score
```

其中 `page_proximity` 来自文本 RAG 命中页：同页最高，相邻页次之，同文档其他页再次之。

## 检索策略

### 策略 1：文本命中页反查图片，默认首选

适合已有文本 RAG 很可靠的场景。

输入：用户 query + 文本 RAG top chunks。

步骤：

1. 取 top chunks 的 `doc_id/page/chunk_text`。
2. 在视觉索引中过滤同 doc_id、page ± 1。
3. 用 query + chunk keywords 在 caption/nearby_text/visual_summary 上检索。
4. 返回 1-3 张最相关图片。

优点：不改变原 RAG，准确率高，工程成本低。

### 策略 2：视觉索引直接检索

适合用户问“哪张图展示了架构/流程/性能曲线”。

输入：用户 query。

步骤：

1. 对 caption/nearby_text/visual_summary 做文本检索。
2. 如果有图像向量，对 query 做跨模态检索。
3. 按 doc/page/asset_kind/quality 重排。

### 策略 3：页面级视觉检索

适合图文混排复杂、传统解析损失严重的 PDF。

做法：把每页渲染图作为检索单位，用视觉文档检索模型或页面摘要索引。召回页面后再裁剪局部区域。

### 策略 4：生成渲染图兜底

当视觉旁路没有找到源图，但文本 RAG 已经有足够结构化事实时，生成解释图。必须标注为 generated visual。

## API 建议

### Ingest API

```http
POST /visual-kb/ingest
```

```json
{
  "doc_id": "kb_doc_123",
  "title": "产品白皮书.pdf",
  "pdf_uri": "s3://bucket/path/file.pdf",
  "options": {
    "render_dpi": 144,
    "extract_images": true,
    "extract_tables": false,
    "generate_visual_summary": true
  }
}
```

### Search API

```http
POST /visual-kb/search
```

```json
{
  "query": "A 方案和 B 方案的性能差异",
  "text_hits": [
    {"doc_id": "kb_doc_123", "page": 8, "chunk_text": "A 方案在吞吐上..."}
  ],
  "filters": {"asset_kind": ["figure_crop", "table_crop", "page_render"]},
  "top_k": 3
}
```

### Fetch API

```http
GET /visual-kb/assets/{asset_id}
```

返回图片二进制或带签名的 `image_uri`。

### Explain API，可选

```http
POST /visual-kb/explain-hit
```

用于返回为什么这张图被选中：query 命中词、caption、同页文本证据、排序分数。

## 工程落地优先级

### MVP

- 独立 PDF registry。
- 每页渲染 page image。
- 抽取图片块 bbox 并 crop。
- 绑定 caption/nearby_text/page_text。
- SQLite/Postgres FTS 或 Elasticsearch 文本索引。
- Search API 支持 query + doc_id/page 过滤。
- 回答层支持 source visual 卡片。

### V1

- 接入版面分析，区分 figure/table/formula/image/logo。
- VLM 生成 visual_summary、visible_text、chart_type。
- 建立 source_text_refs，把视觉 asset 与原文本 chunk_id 松耦合关联。
- 支持 page ± N 反查和多图重排。

### V2

- 增加 CLIP/SigLIP/ColPali 等视觉向量。
- 支持页面级视觉检索 + region grounding。
- 支持人工审核/标注高价值图片。
- 支持缓存签名 URL、权限控制和多租户隔离。

## 不建议做的事

- 不要把图片 OCR 文本直接塞回原文本 KB，除非明确需要；否则会污染原 RAG 的召回语义。
- 不要只保存图片文件而不保存 caption、page、bbox、doc_id；这样无法可靠追溯。
- 不要用生成图冒充源图。
- 不要一次返回大量图片；图文问答应重视“最相关的少量证据”。
- 不要把 VLM 视觉摘要当作绝对事实；摘要是检索辅助，原图和原文仍是证据。

## 最小参考实现

`../scripts/visual_pdf_kb.py` 是一个单文件参考实现，适合验证 MVP：

- `ingest`：解析 PDF，保存页面图、图片区域 crop、元数据和 SQLite FTS 索引。
- `search`：根据 query、doc_id、page 过滤召回图片候选。
- `show`：按 asset_id 输出完整元数据。

它不是生产级服务，但可作为后端 API 的原型。
