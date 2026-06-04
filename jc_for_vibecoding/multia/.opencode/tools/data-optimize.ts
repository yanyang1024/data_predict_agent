import { tool } from "@opencode-ai/plugin"

const API_BASE = "http://10.20.52.249:5314"

interface Constraint {
  min?: number
  max?: number
}

interface OptimizationTrial {
  params: Record<string, number | string>
  row1_striation?: number
  row7_striation?: number
  row7_distortion?: number
  distortion_ratio?: number
  constraints_satisfied?: boolean
}

interface OptimizationResponse {
  status: string
  recommended_params?: Record<string, number | string>
  top_n_candidates?: OptimizationTrial[]
  historical_best?: Record<string, number | string>
  constraint_violations?: string[]
  all_trials_count?: number
  message?: string
}

export default tool({
  description: "基于Optuna NSGA-II算法在历史参数空间内进行多目标约束优化。最小化Row1/Row7条纹度、最大化Row7畸变率和畸变率比值，同时满足Bias CD、Bottom CD、Max CD工艺约束。输出推荐参数组合及Top N可行候选方案。",
  args: {
    layerType: tool.schema.enum(["LCH", "MCH"]).describe("层类型：LCH或MCH"),
    constraints: tool.schema.string().describe("JSON格式约束条件，例如：{\"biasCD\":{\"max\":10},\"bottomCD\":{\"min\":90,\"max\":110},\"maxCD\":{\"max\":120}}"),
    topN: tool.schema.number().default(5).describe("返回的Top N候选方案数量"),
  },
  async execute(args) {
    const { layerType, topN } = args

    let constraints: Record<string, Constraint> = {}
    try {
      constraints = JSON.parse(args.constraints)
    } catch {
      return JSON.stringify({
        status: "error",
        message: "约束条件JSON解析失败，请检查格式",
      })
    }

    try {
      const resp = await fetch(`${API_BASE}/data/optimize`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          layer_type: layerType,
          constraints,
          top_n: topN,
        }),
      })

      if (!resp.ok) {
        return JSON.stringify({
          status: "error",
          message: `优化API返回状态 ${resp.status}`,
        })
      }

      const data: OptimizationResponse = await resp.json()

      const candidates = (data.top_n_candidates || []).map((t, i) => ({
        rank: i + 1,
        params: t.params,
        performance: {
          row1Striation: t.row1_striation,
          row7Striation: t.row7_striation,
          row7Distortion: t.row7_distortion,
          distortionRatio: t.distortion_ratio,
        },
        feasible: t.constraints_satisfied,
      }))

      const recParams = data.recommended_params || {}
      const histBest = data.historical_best || {}

      const comparisons = Object.keys(recParams).map(key => {
        const rec = recParams[key]
        const hist = histBest[key]
        if (hist === undefined) return { param: key, recommended: rec, historical: "N/A", verdict: "NEW" }
        const recNum = typeof rec === "number" ? rec : parseFloat(String(rec))
        const histNum = typeof hist === "number" ? hist : parseFloat(String(hist))
        if (isNaN(recNum) || isNaN(histNum)) return { param: key, recommended: rec, historical: hist, verdict: "N/A" }
        return {
          param: key,
          recommended: rec,
          historical: hist,
          verdict: recNum > histNum ? "BETTER" : recNum < histNum ? "WORSE" : "PASS",
        }
      })

      return JSON.stringify({
        status: "success",
        layerType,
        recommendedParams: recParams,
        comparisons,
        topCandidates: candidates,
        feasibleCount: candidates.filter(c => c.feasible).length,
        totalTrials: data.all_trials_count,
        hasFeasibleSolution: candidates.some(c => c.feasible),
        summary: data.constraint_violations?.length
          ? `无完全可行解，违反约束: ${data.constraint_violations.join(", ")}`
          : `找到 ${candidates.filter(c => c.feasible).length} 个可行候选方案`,
      })
    } catch (error) {
      return JSON.stringify({
        status: "unavailable",
        message: "优化API当前不可用，请稍后重试",
        detail: error instanceof Error ? error.message : String(error),
        layerType,
      })
    }
  },
})
