import { tool } from "@opencode-ai/plugin"
import path from "path"

export default tool({
  description: "Run the approved local simple data profile CLI on a CSV file and return a compact manifest. Use for local training datasets or non-production exported measurement files.",
  args: {
    input_path: tool.schema.string().describe("Path to a local CSV file, relative to the project root when possible"),
    value_column: tool.schema.string().describe("Numeric value column to analyze"),
    group_column: tool.schema.string().optional().describe("Optional group column, such as equipment_id"),
    time_column: tool.schema.string().optional().describe("Optional timestamp column used for trend plot"),
    output_dir: tool.schema.string().optional().describe("Output directory for artifacts"),
    z_threshold: tool.schema.number().optional().describe("Absolute z-score threshold used for outlier flagging"),
  },
  async execute(args, context) {
    const script = path.join(context.worktree, "simple_profile_cli.py")
    const outputDir = args.output_dir ?? "artifacts/simple-profile"
    const zThreshold = args.z_threshold ?? 3.0

    const cmd = [
      "python3",
      script,
      "--input",
      args.input_path,
      "--value-column",
      args.value_column,
      "--output-dir",
      outputDir,
      "--z-threshold",
      String(zThreshold),
    ]

    if (args.group_column) {
      cmd.push("--group-column", args.group_column)
    }
    if (args.time_column) {
      cmd.push("--time-column", args.time_column)
    }

    const result = await Bun.$`${cmd}`.text()
    return result.trim()
  },
})
