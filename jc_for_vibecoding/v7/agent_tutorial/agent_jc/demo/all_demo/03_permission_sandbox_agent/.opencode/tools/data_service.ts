import { tool } from "@opencode-ai/plugin"
import { spawnSync } from "node:child_process"

export default tool({
  description: "Query lot history through the controlled sandbox data service and validate outputs.",
  args: {
    lot: tool.schema.string().describe("Allowed lot id, for example LOT-A12")
  },
  async execute(args) {
    const query = spawnSync("python3", ["scripts/query_lot_history_service.py", "--lot", args.lot], { encoding: "utf-8" })
    if (query.status !== 0) return query.stderr || query.stdout

    const validate = spawnSync("python3", ["scripts/validate_data_service.py"], { encoding: "utf-8" })
    return [query.stdout, validate.stdout, validate.stderr].filter(Boolean).join("\n")
  }
})
