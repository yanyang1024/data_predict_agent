import { tool } from "@opencode-ai/plugin"
import { spawnSync } from "node:child_process"

export default tool({
  description: "生成课程进度 PPT、Excel 看板和 Gantt HTML。只允许读取 inputs/course_status.json 和 inputs/one_sentence_request.txt，并写入 output/。",
  args: {
    status: tool.schema.string().describe("课程状态 JSON 路径，默认 inputs/course_status.json"),
    request: tool.schema.string().describe("用户一句话需求文件，默认 inputs/one_sentence_request.txt"),
    output: tool.schema.string().describe("输出目录，默认 output")
  },
  async execute(args) {
    const result = spawnSync("python3", [
      "scripts/build_course_assets.py",
      "--status", args.status || "inputs/course_status.json",
      "--request", args.request || "inputs/one_sentence_request.txt",
      "--output", args.output || "output"
    ], { encoding: "utf-8" })
    if (result.status !== 0) throw new Error(result.stderr || result.stdout)
    return result.stdout
  }
})
