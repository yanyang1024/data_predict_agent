// Teaching-only OpenCode custom tool sketch.
// It illustrates wrapping a Python script instead of letting the agent query data directly.
// This file is not required for the Python demo runner.

import { execFileSync } from "node:child_process"

export async function guardedQuery(args: { asset: string; startDate: string; endDate: string; fields: string }) {
  const output = execFileSync("python3", [
    "scripts/guarded_query.py",
    "--asset", args.asset,
    "--start-date", args.startDate,
    "--end-date", args.endDate,
    "--fields", args.fields,
    "--output-dir", "output"
  ], { encoding: "utf-8" })
  return output
}
