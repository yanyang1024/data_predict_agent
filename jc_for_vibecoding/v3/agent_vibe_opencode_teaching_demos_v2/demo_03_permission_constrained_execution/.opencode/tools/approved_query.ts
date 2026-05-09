import { tool } from "@opencode-ai/plugin"
import { spawnSync } from "node:child_process"

export default tool({
  description: "Run the approved safe query wrapper. Does not access protected_data directly.",
  args: {
    dataset: tool.schema.string(),
    windowDays: tool.schema.number(),
    fields: tool.schema.string(),
    output: tool.schema.string().default("output/query_result.csv"),
    manifest: tool.schema.string().default("output/query_manifest.json"),
  },
  async execute(args) {
    const result = spawnSync("python3", [
      "scripts/approved_query.py",
      "--dataset", args.dataset,
      "--window-days", String(args.windowDays),
      "--fields", args.fields,
      "--output", args.output,
      "--manifest", args.manifest,
    ], { encoding: "utf8" })
    if (result.status !== 0) throw new Error(result.stdout + "\n" + result.stderr)
    return result.stdout
  },
})
