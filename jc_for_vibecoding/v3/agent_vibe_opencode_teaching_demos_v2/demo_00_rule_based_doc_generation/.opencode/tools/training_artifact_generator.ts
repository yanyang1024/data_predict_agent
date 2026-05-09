import { tool } from "@opencode-ai/plugin"
import { spawnSync } from "node:child_process"

export default tool({
  description: "Generate the teaching status artifacts through the approved local script.",
  args: {
    requestFile: tool.schema.string().default("sample_request.txt"),
    progressFile: tool.schema.string().default("data/course_progress.json"),
    templateFile: tool.schema.string().default("configs/course_template.yaml"),
    outputDir: tool.schema.string().default("output"),
  },
  async execute(args) {
    const result = spawnSync("python3", [
      "scripts/generate_training_artifacts.py",
      "--request", args.requestFile,
      "--progress", args.progressFile,
      "--template", args.templateFile,
      "--output-dir", args.outputDir,
    ], { encoding: "utf8" })
    if (result.status !== 0) {
      throw new Error(result.stderr || result.stdout)
    }
    return result.stdout
  },
})
