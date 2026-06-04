import { tool } from "@opencode-ai/plugin"

const API_BASE = "http://10.20.52.249:5314"

interface PredictResponse {
  status: string
  predicted_params?: Record<string, number | string>
  predicted_performance?: Record<string, number>
  confidence_score?: number
  message?: string
}

export default tool({
  description: "交互式参数探索工具。用户只需指定想修改的部分参数（数值或分类原始字符串均可），其余参数自动填充后返回预测结果。支持按层类型探索不同的参数组合效果。",
  args: {
    layerType: tool.schema.enum(["LCH", "MCH"]).describe("层类型：LCH或MCH"),
    partialParams: tool.schema.string().describe("JSON格式的部分参数，例如：{\"gas_flow_C4F8\": 80, \"source_power\": 600}"),
  },
  async execute(args) {
    const { layerType } = args

    let partialParams: Record<string, unknown> = {}
    try {
      partialParams = JSON.parse(args.partialParams)
    } catch {
      return JSON.stringify({
        status: "error",
        message: "参数JSON解析失败，请检查格式",
      })
    }

    if (Object.keys(partialParams).length === 0) {
      return JSON.stringify({
        status: "error",
        message: "请至少指定一个参数进行预测",
      })
    }

    try {
      const resp = await fetch(`${API_BASE}/data/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          layer_type: layerType,
          partial_params: partialParams,
        }),
      })

      if (!resp.ok) {
        return JSON.stringify({
          status: "error",
          message: `预测API返回状态 ${resp.status}`,
        })
      }

      const data: PredictResponse = await resp.json()

      return JSON.stringify({
        status: "success",
        layerType,
        inputParams: partialParams,
        predictedFullParams: data.predicted_params,
        predictedPerformance: data.predicted_performance,
        confidenceScore: data.confidence_score,
        summary: `预测完成，置信度: ${((data.confidence_score || 0) * 100).toFixed(1)}%`,
      })
    } catch (error) {
      return JSON.stringify({
        status: "unavailable",
        message: "预测API当前不可用，请稍后重试",
        detail: error instanceof Error ? error.message : String(error),
        layerType,
      })
    }
  },
})
