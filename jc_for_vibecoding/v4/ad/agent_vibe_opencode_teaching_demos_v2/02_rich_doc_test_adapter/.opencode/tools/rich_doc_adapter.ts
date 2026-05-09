import { tool } from "@opencode-ai/plugin"
import { spawnSync } from "node:child_process"

export default tool({
  description: "富文本验证说明抽取与目标环境测试代码适配流水线。",
  args: {
    doc: tool.schema.string().describe("富文本/HTML 文档路径"),
    output: tool.schema.string().describe("输出目录")
  },
  async execute(args) {
    const doc = args.doc || "docs/rich_test_spec_export.html"
    const output = args.output || "output"
    const cmds = [
      ["python3", ["scripts/extract_rich_doc_patterns.py", "--doc", doc, "--rules", "references/extraction_rules.md", "--output", `${output}/extracted_patterns.json`]],
      ["python3", ["scripts/adapt_patterns_to_env.py", "--patterns", `${output}/extracted_patterns.json`, "--env", "env_package/target_env_contract.json", "--output", `${output}/generated_tests.py`, "--review", `${output}/review_packet.md`]],
      ["python3", ["scripts/validate_generated_tests.py", "--tests", `${output}/generated_tests.py`, "--patterns", `${output}/extracted_patterns.json`]]
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
