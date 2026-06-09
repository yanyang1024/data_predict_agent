# Phase 2: 维度分解 — 文档构建方案调研

## 综合景观分析

基于Phase 1（Quick Landscape）和Phase 1W（5个探索面的广泛探索），形成以下统一景观图：

**核心矛盾**：Markdown对AI最友好（减少67-90% token消耗、+35% RAG准确率），但对人类编辑图文并茂内容不够友好。富文本平台（飞书/Notion/Word）对人类编辑友好，但对AI处理需要转换管道。

**关键发现**：
1. 文档转换工具生态已成熟（Docling 20K+ stars, Firecrawl API优先, Microsoft MarkItDown 61K+ stars）
2. 多模态RAG从实验性技术进入生产就绪阶段（text-image fusion RAG最优）
3. 结构感知分块（基于标题层级）准确率达87%，远超固定分块的60-65%
4. 企业SOP管理的核心是标准化模板+生命周期管理，非技术选型
5. llms.txt标准快速普及但有效性存争议

## 研究维度（12个）

### Dim 01: Markdown对人类编辑的局限与改进方案
- 角度：人类编辑体验
- 范围：Markdown在SOP场景（图文并茂）的结构性痛点、WYSIWYG编辑器（Typora等）的补偿能力、Markdown扩展语法（GFM/MDX）的增强效果
- 与Dim 02/10有≥30%重叠

### Dim 02: 富文本协作平台的企业SOP适用性
- 角度：人类编辑体验
- 范围：飞书文档、Notion、Confluence、语雀、腾讯文档对SOP编写的支持度对比（图片插入、表格编辑、协作功能、导出能力）
- 与Dim 01/10有≥30%重叠

### Dim 03: 文档格式转换管道与工具链
- 角度：技术桥接
- 范围：从富文本到Markdown的转换工具（Docling/Firecrawl/MarkItDown/飞书导出）的准确率、速度、成本、信息丢失分析
- 与Dim 09/11有≥30%重叠

### Dim 04: RAG分块策略与文档结构要求
- 角度：AI检索技术
- 范围：结构感知分块、语义分块、固定分块的对比；文档标题层级对chunking质量的影响；SOP文档的最优分块策略
- 与Dim 05/08有≥30%重叠

### Dim 05: 多模态RAG与图文并茂文档处理
- 角度：AI检索技术
- 范围：text-image fusion RAG、视觉级整页理解（ColPali/ColQwen）、多模态embedding模型、SOP截图/示意图的处理方案
- 与Dim 04/11有≥30%重叠

### Dim 06: Agent与文档交互模式
- 角度：AI Agent技术
- 范围：MCP协议、function calling、JSON Schema、Agent对结构化vs非结构化文档的处理能力、Agent直接编辑文档的方案
- 与Dim 03/08有≥30%重叠

### Dim 07: 企业SOP文档标准化与生命周期管理
- 角度：企业管理实践
- 范围：SOP模板设计、版本控制、审核工作流、生命周期管理（创建→审核→发布→更新→废弃）、ISO 9001要求
- 与Dim 02/12有≥30%重叠

### Dim 08: 文档元数据与索引策略
- 角度：AI检索优化
- 范围：文档元数据（标题、作者、标签、版本）对RAG检索效果的影响；统一嵌入（unified embedding）；标签体系设计
- 与Dim 04/06有≥30%重叠

### Dim 09: 文档解析工具深度对比
- 角度：技术评估
- 范围：Docling、Marker-PDF、Firecrawl、LlamaParse、Unstructured、MarkItDown的功能矩阵、性能基准、定价、适用场景
- 与Dim 03/11有≥30%重叠

### Dim 10: 权衡分析与混合方案设计
- 角度：综合决策
- 范围：人 vs AI需求的平衡点、双轨制方案（人用富文本→AI用Markdown）、编辑-转换-检索一体化架构、tradeoff分析框架
- 与Dim 01/02/03有≥30%重叠

### Dim 11: 中文场景特殊考量
- 角度：本地化适配
- 范围：中文文档处理的特殊挑战（竖排、古籍、混排）、国内平台生态（飞书/钉钉/企业微信/语雀）、国内RAG/Agent产品（阿里云百炼/火山引擎/百度千帆）
- 与Dim 02/05/09有≥30%重叠

### Dim 12: 实施路径与迁移策略
- 角度：落地实践
- 范围：从现有文档（Word/PDF）到新格式的迁移路径、渐进式改造方案、工具链推荐、成本估算、ROI分析
- 与Dim 07/10有≥30%重叠
