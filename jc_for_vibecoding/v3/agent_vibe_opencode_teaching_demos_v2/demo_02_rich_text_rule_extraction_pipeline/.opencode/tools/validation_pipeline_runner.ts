import { tool } from "@opencode-ai/plugin"
import { spawnSync } from "node:child_process"

export default tool({
  description: "Run the approved rich-text extraction, adaptation, and syntax validation pipeline.",
  args: {},
  async execute() {
    const result = spawnSync("python3", ["scripts/run_pipeline.py"], { encoding: "utf8" })
    if (result.status !== 0) throw new Error(result.stdout + "\n" + result.stderr)
    return result.stdout
  },
})
