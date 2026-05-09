import { tool } from "@opencode-ai/plugin"
import { spawnSync } from "node:child_process"

export const propose = tool({
  description: "Create a sandbox-only config change proposal for an allowed flag.",
  args: {
    flag: tool.schema.string().describe("Allowed flag name"),
    value: tool.schema.boolean().describe("Boolean value"),
    reason: tool.schema.string().describe("Human-readable reason"),
    output: tool.schema.string().describe("Proposal output path under output/")
  },
  async execute(args) {
    const p = spawnSync("python3", ["scripts/propose_config_patch.py", "--flag", args.flag, "--value", String(args.value), "--reason", args.reason, "--output", args.output], { encoding: "utf-8" })
    return p.stdout || p.stderr
  }
})

export const applyAndValidate = tool({
  description: "Apply an approved proposal to sandbox output and validate protected files are untouched.",
  args: {
    proposal: tool.schema.string().describe("Proposal path under output/"),
    sandbox: tool.schema.string().describe("Sandbox source config path"),
    output: tool.schema.string().describe("Sandbox output path under output/"),
    audit: tool.schema.string().describe("Audit log path under output/")
  },
  async execute(args) {
    const apply = spawnSync("python3", ["scripts/apply_patch_to_sandbox.py", "--proposal", args.proposal, "--sandbox", args.sandbox, "--output", args.output, "--audit", args.audit], { encoding: "utf-8" })
    if (apply.status !== 0) return apply.stderr || apply.stdout
    const validate = spawnSync("python3", ["scripts/validate_config_patch.py", "--proposal", args.proposal, "--sandbox-output", args.output, "--audit", args.audit], { encoding: "utf-8" })
    return [apply.stdout, validate.stdout, validate.stderr].filter(Boolean).join("\n")
  }
})
