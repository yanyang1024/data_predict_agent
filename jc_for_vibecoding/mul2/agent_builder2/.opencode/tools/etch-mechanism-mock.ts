import { tool } from "@opencode-ai/plugin"

export default tool({
  description: "Mock Etch mechanism evaluator. Use only as a placeholder before the real simulator is integrated. It returns qualitative mechanism hints, not validated simulation results.",
  args: {
    rcpJson: tool.schema.string().describe("RCP parameters as a JSON string"),
    objective: tool.schema.string().describe("Etch objective or issue description"),
  },
  async execute(args) {
    let parsed: any
    try {
      parsed = JSON.parse(args.rcpJson)
    } catch {
      return JSON.stringify({
        success: false,
        error: "Invalid rcpJson. Please provide valid JSON.",
      }, null, 2)
    }
    return JSON.stringify({
      success: true,
      mode: "placeholder_only",
      objective: args.objective,
      input_keys: Object.keys(parsed),
      qualitative_hints: [
        "Check whether bias-related parameters may affect ion energy and CD/profile risk.",
        "Check whether pressure or gas-ratio changes may affect etch uniformity and selectivity.",
        "Use historical data or DOE validation before treating these hints as recommendations."
      ],
      limitations: [
        "No real simulator is connected.",
        "No numerical prediction is generated.",
        "This output is not process-validated."
      ]
    }, null, 2)
  },
})
