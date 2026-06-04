import { tool } from "@opencode-ai/plugin"

const API_BASE = "http://10.20.52.249:5314"

interface ModelComparison {
  model_name: string
  r2_score: number
  rmse?: number
  training_time?: number
}

interface AnalyzeResponse {
  status: string
  models?: ModelComparison[]
  best_model?: string
  best_r2?: number
  message?: string
  detail?: string
}

export default tool({
  description: "使用时序交叉验证对比6种回归模型（LightGBM、CatBoost、GPR、SVR、Ridge、LinearRegression），自动选择R²最优模型，提供各模型对比详情。",
  args: {
    layerType: tool.schema.enum(["LCH", "MCH"]).describe("层类型：LCH或MCH"),
  },
  async execute(args) {
    const { layerType } = args

    try {
      const resp = await fetch(`${API_BASE}/data/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ layer_type: layerType }),
      })

      if (!resp.ok) {
        return JSON.stringify({
          status: "error",
          message: `模型分析API返回状态 ${resp.status}`,
        })
      }

      const data: AnalyzeResponse = await resp.json()

      const modelDetails = (data.models || []).map(m => ({
        name: m.model_name,
        r2: m.r2_score,
        rmse: m.rmse,
        rank: "N/A",
      }))

      if (data.best_model) {
        const best = modelDetails.find(m => m.name === data.best_model)
        if (best) best.rank = "1 (BEST)"
      }

      return JSON.stringify({
        status: "success",
        layerType,
        bestModel: data.best_model,
        bestR2: data.best_r2,
        modelDetails,
        summary: `最优模型: ${data.best_model} (R² = ${data.best_r2?.toFixed(4)})`,
        confidenceLevel:
          data.best_r2 !== undefined
            ? data.best_r2 > 0.8 ? "高" : data.best_r2 > 0.6 ? "中" : "低"
            : "未知",
      })
    } catch (error) {
      return JSON.stringify({
        status: "unavailable",
        message: "数据API当前不可用，请稍后重试",
        detail: error instanceof Error ? error.message : String(error),
        layerType,
      })
    }
  },
})
