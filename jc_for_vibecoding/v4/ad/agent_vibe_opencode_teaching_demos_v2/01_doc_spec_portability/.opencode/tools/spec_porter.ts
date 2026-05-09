import { tool } from "@opencode-ai/plugin"
import { spawnSync } from "node:child_process"

export default tool({
  description: "执行 Doc Spec 可移植实现流水线：抽取 contract、生成平台 B 代码、运行样例验证。",
  args: {
    spec: tool.schema.string().describe("规范文档路径"),
    output: tool.schema.string().describe("输出目录")
  },
  async execute(args) {
    const spec = args.spec || "docs/ticket_priority_spec.md"
    const output = args.output || "output"
    const cmds = [
      ["python3", ["scripts/extract_spec_contract.py", "--spec", spec, "--output", `${output}/spec_contract.json`]],
      ["python3", ["scripts/port_to_platform_b.py", "--contract", `${output}/spec_contract.json`, "--output", `${output}/platform_b`]],
      ["python3", ["scripts/validate_port.py", "--impl", `${output}/platform_b/rule_engine.js`, "--cases", "tests/platform_b_cases.json"]]
    ]
    let log = ""
    for (const [cmd, argv] of cmds) {
      const r = spawnSync(cmd as string, argv as string[], { encoding: "utf-8" })
      log += `$ ${cmd} ${argv.join(" ")}\n${r.stdout}${r.stderr}\n`
      if (r.status !== 0) throw new Error(log)
    }
    return log
  }
})
