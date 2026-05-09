import { tool } from "@opencode-ai/plugin"
import { spawnSync } from "node:child_process"

export default tool({
  description: "Render the approved teaching dashboard from a progress JSON file and validate the output.",
  args: {
    input: tool.schema.string().describe("Path to progress JSON, usually data/sample_progress.json"),
    outputDir: tool.schema.string().describe("Output directory, usually output")
  },
  async execute(args) {
    const render = spawnSync("python3", ["scripts/generate_dashboard.py", "--input", args.input, "--output-dir", args.outputDir], { encoding: "utf-8" })
    if (render.status !== 0) return render.stderr || render.stdout
    const validate = spawnSync("python3", ["scripts/validate_dashboard.py", "--output-dir", args.outputDir], { encoding: "utf-8" })
    return [render.stdout, validate.stdout, validate.stderr].filter(Boolean).join("\n")
  }
})
