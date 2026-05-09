import { tool } from "@opencode-ai/plugin"
import { spawnSync } from "node:child_process"

export default tool({
  description: "受控 mock 数据查询 API。只允许白名单 metric/team 和最大 14 天窗口。",
  args: {
    metric: tool.schema.string().describe("latency_ms 或 error_rate"),
    team: tool.schema.string().describe("alpha 或 beta"),
    startDate: tool.schema.string().describe("YYYY-MM-DD"),
    endDate: tool.schema.string().describe("YYYY-MM-DD"),
    output: tool.schema.string().describe("输出 CSV 路径")
  },
  async execute(args) {
    const r = spawnSync("python3", [
      "scripts/approved_data_api.py",
      "--metric", args.metric,
      "--team", args.team,
      "--start-date", args.startDate,
      "--end-date", args.endDate,
      "--output", args.output || "output/query_result.csv"
    ], { encoding: "utf-8" })
    if (r.status !== 0) throw new Error(r.stderr || r.stdout)
    return r.stdout
  }
})
