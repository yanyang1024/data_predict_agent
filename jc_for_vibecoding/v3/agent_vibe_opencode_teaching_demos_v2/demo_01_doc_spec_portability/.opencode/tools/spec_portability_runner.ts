import { tool } from "@opencode-ai/plugin"
import { spawnSync } from "node:child_process"

export default tool({
  description: "Run the approved spec portability pipeline.",
  args: {},
  async execute() {
    const commands = [
      ["python3", ["scripts/extract_spec_rules.py", "--spec", "docs/order_pricing_spec.md", "--output", "output/normalized_rules.json", "--report", "output/spec_extraction_report.md"]],
      ["python3", ["scripts/generate_implementations.py", "--rules", "output/normalized_rules.json", "--output-dir", "output"]],
      ["python3", ["scripts/validate_portability.py", "--cases", "golden_cases/order_pricing_cases.json", "--python-impl", "output/platform_python/pricer.py", "--node-impl", "output/platform_node/pricer.mjs", "--report", "output/portability_report.md"]],
    ]
    let output = ""
    for (const [cmd, args] of commands) {
      const result = spawnSync(cmd, args as string[], { encoding: "utf8" })
      output += `$ ${cmd} ${(args as string[]).join(" ")}\n${result.stdout}\n${result.stderr}\n`
      if (result.status !== 0) throw new Error(output)
    }
    return output
  },
})
