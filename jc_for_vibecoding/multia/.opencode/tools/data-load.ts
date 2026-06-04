import { tool } from "@opencode-ai/plugin"

const API_BASE = "http://10.20.52.249:5314"

interface DataLoadResponse {
  status: string
  sample_count?: number
  feature_count?: number
  pca_dimensions?: number
  excluded_features?: string[]
  missing_value_ratio?: number
  data_quality_score?: string
  message?: string
  detail?: string
}

export default tool({
  description: "加载蚀刻历史运行数据，完成特征筛选（排除稀疏列、ME/OEA列名过滤）、缺失值填充（数值列中位数、分类列众数）、标签编码、标准化与PCA降维，输出数据质量报告。",
  args: {
    layerType: tool.schema.enum(["LCH", "MCH"]).describe("层类型：LCH或MCH"),
    filePath: tool.schema.string().optional().describe("可选：指定数据文件路径，不指定则使用默认数据源"),
  },
  async execute(args) {
    const { layerType, filePath } = args

    try {
      const body: Record<string, unknown> = { layer_type: layerType }
      if (filePath) {
        body.file_path = filePath
      }

      const resp = await fetch(`${API_BASE}/data/load`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      })

      if (!resp.ok) {
        return JSON.stringify({
          status: "error",
          message: `数据加载API返回状态 ${resp.status}`,
        })
      }

      const data: DataLoadResponse = await resp.json()

      return JSON.stringify({
        status: "success",
        layerType,
        sampleCount: data.sample_count,
        featureCount: data.feature_count,
        pcaDimensions: data.pca_dimensions,
        excludedFeatures: data.excluded_features,
        missingValueRatio: data.missing_value_ratio,
        dataQualityScore: data.data_quality_score,
        summary: `数据加载完成：${data.sample_count} 样本，${data.feature_count} 特征，PCA降至 ${data.pca_dimensions} 维`,
      })
    } catch (error) {
      return JSON.stringify({
        status: "unavailable",
        message: "数据API当前不可用，请稍后重试",
        detail: error instanceof Error ? error.message : String(error),
        layerType,
        fallback: "无法加载历史数据，请检查API服务状态",
      })
    }
  },
})
