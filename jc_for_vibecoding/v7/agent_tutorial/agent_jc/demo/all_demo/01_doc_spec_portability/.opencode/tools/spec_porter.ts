import { tool } from "@opencode-ai/plugin"
import { spawnSync } from "node:child_process"

export default tool({
  description: "Run the approved Gradio-to-Flask portability script and sample CSV/style validation.",
  args: {
    source: tool.schema.string().describe("Readonly Gradio source path"),
    request: tool.schema.string().describe("User migration request markdown path"),
    styleSpec: tool.schema.string().describe("Frontend style spec markdown path"),
    outputDir: tool.schema.string().describe("Generated Flask project directory under generated/"),
    report: tool.schema.string().describe("Migration report path under output/"),
    cases: tool.schema.string().describe("Analysis cases JSON path")
  },
  async execute(args) {
    const gen = spawnSync("python3", [
      "scripts/port_gradio_to_flask.py",
      "--source", args.source,
      "--request", args.request,
      "--style-spec", args.styleSpec,
      "--output-dir", args.outputDir,
      "--report", args.report
    ], { encoding: "utf-8" })
    if (gen.status !== 0) return gen.stderr || gen.stdout
    const val = spawnSync("python3", ["scripts/validate_flask_port.py", "--project-dir", args.outputDir, "--cases", args.cases], { encoding: "utf-8" })
    if (val.status !== 0) return [gen.stdout, val.stdout, val.stderr].filter(Boolean).join("\n")
    const viewer = spawnSync("python3", ["../scripts/demo_viewer.py", "--demo", "01_doc_spec_portability", "--port", "8761", "--restart"], { encoding: "utf-8" })
    return [gen.stdout, val.stdout, viewer.stdout, viewer.stderr].filter(Boolean).join("\n")
  }
})
