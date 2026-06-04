import { tool } from "@opencode-ai/plugin"
import path from "path"

export default tool({
  description: "Generate and analyze generic DOE designs for Etch experiments. Supports coded design matrix generation and delegates analysis/reporting to Python.",
  args: {
    action: tool.schema.enum([
      "generate_full_factorial",
      "generate_fractional_factorial",
      "generate_taguchi_placeholder",
      "generate_response_surface_placeholder",
      "analyze_results"
    ]).describe("DOE action"),
    factorCount: tool.schema.number().min(1).max(12).describe("Number of experimental factors"),
    levelsJson: tool.schema.string().default("{}").describe("JSON definition of levels for each factor"),
    resultsCsvPath: tool.schema.string().optional().describe("Path to completed DOE results CSV for analysis"),
    outputDir: tool.schema.string().default("outputs/doe").describe("Output directory"),
  },
  async execute(args, context) {
    const script = path.join(context.worktree, ".opencode/tools/etch_doe.py")
    const cmd = [
      "python3",
      script,
      "--action", args.action,
      "--factor-count", String(args.factorCount),
      "--levels-json", JSON.stringify(args.levelsJson),
      "--output-dir", args.outputDir
    ]
    if (args.resultsCsvPath) {
      cmd.push("--results-csv-path", args.resultsCsvPath)
    }
    try {
      const result = await Bun.$`${cmd}`.text()
      return result.trim()
    } catch (error) {
      return JSON.stringify({
        success: false,
        error: error instanceof Error ? error.message : String(error),
        suggestion: "Check whether Python dependencies are installed and paths are valid."
      }, null, 2)
    }
  },
})
