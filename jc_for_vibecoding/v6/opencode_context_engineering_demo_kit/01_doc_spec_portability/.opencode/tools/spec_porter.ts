import { tool } from "@opencode-ai/plugin"
import { spawnSync } from "node:child_process"

export default tool({
  description: "Run the approved Python-to-JS portability script and golden-case validation.",
  args: {
    source: tool.schema.string().describe("Readonly Python source path"),
    output: tool.schema.string().describe("Generated JS module path under generated/"),
    report: tool.schema.string().describe("Migration report path under output/"),
    cases: tool.schema.string().describe("Golden cases JSON path")
  },
  async execute(args) {
    const gen = spawnSync("python3", ["scripts/port_py_to_js.py", "--source", args.source, "--output", args.output, "--report", args.report], { encoding: "utf-8" })
    if (gen.status !== 0) return gen.stderr || gen.stdout
    const val = spawnSync("python3", ["scripts/validate_port.py", "--module", args.output, "--cases", args.cases], { encoding: "utf-8" })
    return [gen.stdout, val.stdout, val.stderr].filter(Boolean).join("\n")
  }
})
