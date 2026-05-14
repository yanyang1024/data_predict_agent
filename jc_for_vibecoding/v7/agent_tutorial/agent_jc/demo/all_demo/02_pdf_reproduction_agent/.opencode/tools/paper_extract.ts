import { tool } from "@opencode-ai/plugin"
import { spawnSync } from "node:child_process"

export const extract = tool({
  description: "Extract structured evidence from the approved paper PDF or fallback text.",
  args: {
    pdf: tool.schema.string().describe("PDF path under papers/"),
    fallback: tool.schema.string().describe("Fallback text path under papers/"),
    outputDir: tool.schema.string().describe("Output directory, usually output")
  },
  async execute(args) {
    const p = spawnSync("python3", ["scripts/extract_pdf_evidence.py", "--pdf", args.pdf, "--fallback", args.fallback, "--output-dir", args.outputDir], { encoding: "utf-8" })
    return p.stdout || p.stderr
  }
})

export const build = tool({
  description: "Build and validate a minimal reproduction project from extracted evidence.",
  args: {
    evidence: tool.schema.string().describe("Evidence JSON path"),
    env: tool.schema.string().describe("Environment package path"),
    outputDir: tool.schema.string().describe("Generated project directory")
  },
  async execute(args) {
    const build = spawnSync("python3", ["scripts/build_repro_project.py", "--evidence", args.evidence, "--env", args.env, "--output-dir", args.outputDir], { encoding: "utf-8" })
    if (build.status !== 0) return build.stderr || build.stdout
    const validate = spawnSync("python3", ["scripts/validate_repro_project.py", "--project-dir", args.outputDir], { encoding: "utf-8" })
    if (validate.status !== 0) return [build.stdout, validate.stdout, validate.stderr].filter(Boolean).join("\n")
    const viewer = spawnSync("python3", ["../scripts/demo_viewer.py", "--demo", "02_pdf_reproduction_agent", "--port", "8762", "--restart"], { encoding: "utf-8" })
    return [build.stdout, validate.stdout, viewer.stdout, viewer.stderr].filter(Boolean).join("\n")
  }
})
