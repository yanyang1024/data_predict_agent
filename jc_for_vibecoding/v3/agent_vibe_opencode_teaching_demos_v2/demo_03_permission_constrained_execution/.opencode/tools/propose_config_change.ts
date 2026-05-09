import { tool } from "@opencode-ai/plugin"
import { spawnSync } from "node:child_process"

export default tool({
  description: "Create a protected config change proposal without editing protected config files.",
  args: {
    parameter: tool.schema.string(),
    value: tool.schema.string(),
    reason: tool.schema.string(),
    output: tool.schema.string().default("output/config_change_proposal.json"),
  },
  async execute(args) {
    const result = spawnSync("python3", [
      "scripts/propose_config_change.py",
      "--parameter", args.parameter,
      "--value", args.value,
      "--reason", args.reason,
      "--output", args.output,
    ], { encoding: "utf8" })
    if (result.status !== 0) throw new Error(result.stdout + "\n" + result.stderr)
    return result.stdout
  },
})
