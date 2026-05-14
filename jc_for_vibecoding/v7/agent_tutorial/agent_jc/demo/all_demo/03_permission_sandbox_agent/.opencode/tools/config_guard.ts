import { tool } from "@opencode-ai/plugin"
import { spawnSync } from "node:child_process"

export default tool({
  description: "Generate, apply, and validate a sandbox-only config change proposal.",
  args: {
    flag: tool.schema.string().describe("Allowed flag name, for example beta_dashboard"),
    value: tool.schema.boolean().describe("Target boolean value"),
    reason: tool.schema.string().describe("Human-readable reason for audit")
  },
  async execute(args) {
    const propose = spawnSync(
      "python3",
      ["scripts/propose_config_patch.py", "--flag", args.flag, "--value", String(args.value), "--reason", args.reason],
      { encoding: "utf-8" }
    )
    if (propose.status !== 0) return propose.stderr || propose.stdout

    const apply = spawnSync("python3", ["scripts/apply_patch_to_sandbox.py"], { encoding: "utf-8" })
    if (apply.status !== 0) return apply.stderr || apply.stdout

    const validate = spawnSync("python3", ["scripts/validate_config_patch.py"], { encoding: "utf-8" })
    if (validate.status !== 0) return [propose.stdout, apply.stdout, validate.stdout, validate.stderr].filter(Boolean).join("\n")
    const viewer = spawnSync("python3", ["../scripts/demo_viewer.py", "--demo", "03_permission_sandbox_agent", "--port", "8763", "--restart"], { encoding: "utf-8" })
    return [propose.stdout, apply.stdout, validate.stdout, viewer.stdout, viewer.stderr].filter(Boolean).join("\n")
  }
})
