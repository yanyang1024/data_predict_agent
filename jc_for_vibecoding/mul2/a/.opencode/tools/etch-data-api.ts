import { tool } from "@opencode-ai/plugin"

const BASE_URL_1 = process.env.ETCH_DATA_API_BASE || "http://10.20.52.249:5314"
const BASE_URL_2 = process.env.ETCH_DATA_API_BASE_ALT || "http://10.20.52.249:5315"

export default tool({
  description: "Call the Etch data prediction and multi-objective optimization API. Use this for historical data quality report, model comparison, NSGA-II optimization, and user parameter override prediction.",
  args: {
    action: tool.schema.enum([
      "health_check",
      "data_quality",
      "model_compare",
      "optimize",
      "predict_override",
      "export_files"
    ]).describe("API action to perform"),
    layerType: tool.schema.enum(["LCH", "MCH"]).describe("Etch layer type"),
    payloadJson: tool.schema.string().default("{}").describe("Action-specific JSON payload"),
    base: tool.schema.enum(["primary", "secondary"]).default("primary").describe("Which API base URL to use"),
  },
  async execute(args) {
    const baseUrl = args.base === "primary" ? BASE_URL_1 : BASE_URL_2
    let payload: any
    try {
      payload = JSON.parse(args.payloadJson)
    } catch {
      return JSON.stringify({
        success: false,
        error: "Invalid payloadJson. Please provide valid JSON."
      }, null, 2)
    }
    try {
      const response = await fetch(`${baseUrl}/${args.action}`, {
        method: args.action === "health_check" ? "GET" : "POST",
        headers: { "Content-Type": "application/json" },
        body: args.action === "health_check"
          ? undefined
          : JSON.stringify({
              layer_type: args.layerType,
              ...payload
            })
      })
      if (!response.ok) {
        return JSON.stringify({
          success: false,
          baseUrl,
          action: args.action,
          status: response.status,
          error: await response.text(),
          fallback: "Data API unavailable. Return schema-level plan only."
        }, null, 2)
      }
      const data = await response.json()
      return JSON.stringify({
        success: true,
        baseUrl,
        action: args.action,
        result: data
      }, null, 2)
    } catch (error) {
      return JSON.stringify({
        success: false,
        baseUrl,
        action: args.action,
        error: error instanceof Error ? error.message : String(error),
        fallback: "Data API unavailable. Use fallback data plan and do not fabricate metrics."
      }, null, 2)
    }
  },
})
