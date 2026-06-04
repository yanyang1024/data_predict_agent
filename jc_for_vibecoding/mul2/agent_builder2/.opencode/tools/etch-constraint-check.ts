import { tool } from "@opencode-ai/plugin"

interface ParameterBoundary {
  min: number | null
  max: number | null
  unit?: string
}

interface CdConstraint {
  min: number | null
  max: number | null
}

interface ConstraintConfig {
  parameters: Record<string, ParameterBoundary>
  cd_constraints: {
    bias_cd: CdConstraint
    bottom_cd: CdConstraint
    max_cd: CdConstraint
  }
  history_scope: {
    min_runs: number
    parameter_ranges: Record<string, { min: number; max: number }>
  }
}

function checkNumeric(
  value: unknown,
  boundary: ParameterBoundary,
  label: string
): { label: string; status: "PASS" | "FAIL" | "UNKNOWN"; message: string } {
  if (typeof value !== "number") {
    return { label, status: "UNKNOWN", message: `Cannot check ${label}: value is not numeric` }
  }
  if (boundary.min === null && boundary.max === null) {
    return { label, status: "UNKNOWN", message: `Cannot check ${label}: no boundary defined (min/max both null)` }
  }
  if (boundary.min !== null && value < boundary.min) {
    return { label, status: "FAIL", message: `${label} = ${value} is below minimum ${boundary.min} ${boundary.unit || ""}`.trim() }
  }
  if (boundary.max !== null && value > boundary.max) {
    return { label, status: "FAIL", message: `${label} = ${value} exceeds maximum ${boundary.max} ${boundary.unit || ""}`.trim() }
  }
  return { label, status: "PASS", message: `${label} = ${value} is within bounds` }
}

export default tool({
  description: "Check candidate Etch RCP parameters against process constraints, CD boundaries, and historical parameter space. Returns PASS/WARNING/FAIL/UNKNOWN for each constraint category.",
  args: {
    rcpJson: tool.schema.string().describe("Candidate RCP parameters as JSON string"),
    constraintsJson: tool.schema.string().describe("Constraint configuration as JSON string (parameter boundaries, CD constraints, history scope)"),
    cdPredictedJson: tool.schema.string().optional().describe("Predicted CD values (bias_cd, bottom_cd, max_cd) as JSON string"),
  },
  async execute(args) {
    let rcp: Record<string, unknown>
    let config: ConstraintConfig
    let cdPredicted: Record<string, number> | null = null

    try {
      rcp = JSON.parse(args.rcpJson)
    } catch {
      return JSON.stringify({ success: false, error: "Invalid rcpJson" }, null, 2)
    }
    try {
      config = JSON.parse(args.constraintsJson)
    } catch {
      return JSON.stringify({ success: false, error: "Invalid constraintsJson" }, null, 2)
    }
    if (args.cdPredictedJson) {
      try {
        cdPredicted = JSON.parse(args.cdPredictedJson)
      } catch {
        return JSON.stringify({ success: false, error: "Invalid cdPredictedJson" }, null, 2)
      }
    }

    const results: Array<{ label: string; status: string; message: string }> = []
    const details: Record<string, any> = {}

    // 1. Parameter range checks
    const paramResults: any[] = []
    for (const [param, boundary] of Object.entries(config.parameters)) {
      if (param in rcp) {
        paramResults.push(checkNumeric(rcp[param], boundary, param))
      }
    }
    results.push(...paramResults)
    details.parameter_checks = paramResults

    // 2. CD constraint checks
    const cdResults: any[] = []
    if (cdPredicted) {
      for (const [cdKey, constraint] of Object.entries(config.cd_constraints)) {
        if (cdKey in cdPredicted) {
          const val = cdPredicted[cdKey]
          if (constraint.min !== null && val < constraint.min) {
            cdResults.push({ label: cdKey, status: "FAIL", message: `${cdKey} = ${val} is below minimum ${constraint.min}` })
          } else if (constraint.max !== null && val > constraint.max) {
            cdResults.push({ label: cdKey, status: "FAIL", message: `${cdKey} = ${val} exceeds maximum ${constraint.max}` })
          } else {
            cdResults.push({ label: cdKey, status: "PASS", message: `${cdKey} = ${val} is within CD constraints` })
          }
        } else {
          cdResults.push({ label: cdKey, status: "UNKNOWN", message: `${cdKey} not found in predicted CD data` })
        }
      }
    } else {
      for (const cdKey of Object.keys(config.cd_constraints)) {
        cdResults.push({ label: cdKey, status: "UNKNOWN", message: `${cdKey}: no predicted CD data provided` })
      }
    }
    results.push(...cdResults)
    details.cd_checks = cdResults

    // 3. Historical space check
    const historyResults: any[] = []
    const scope = config.history_scope
    for (const [param, range] of Object.entries(scope.parameter_ranges)) {
      if (param in rcp && typeof rcp[param] === "number") {
        const val = rcp[param] as number
        if (val < range.min || val > range.max) {
          historyResults.push({ label: param, status: "WARNING", message: `${param} = ${val} is outside historical range [${range.min}, ${range.max}]` })
        } else {
          historyResults.push({ label: param, status: "PASS", message: `${param} = ${val} is within historical range` })
        }
      }
    }
    if (historyResults.length === 0) {
      historyResults.push({ label: "history_scope", status: "UNKNOWN", message: "No historical parameter ranges defined for comparison" })
    }
    results.push(...historyResults)
    details.history_checks = historyResults

    // 4. Overall status
    const hasFail = results.some(r => r.status === "FAIL")
    const hasWarning = results.some(r => r.status === "WARNING")
    const hasUnknown = results.some(r => r.status === "UNKNOWN")
    let overall: string
    let overallMessage: string
    if (hasFail) {
      overall = "FAIL"
      overallMessage = "One or more explicit violations detected"
    } else if (hasWarning) {
      overall = "WARNING"
      overallMessage = "All checks pass but some parameters are outside historical range"
    } else if (hasUnknown) {
      overall = "UNKNOWN"
      overallMessage = "No violations found but some constraints lack boundary definitions"
    } else {
      overall = "PASS"
      overallMessage = "All checked constraints are satisfied"
    }

    return JSON.stringify({
      success: true,
      overall,
      overall_message: overallMessage,
      details,
    }, null, 2)
  },
})
