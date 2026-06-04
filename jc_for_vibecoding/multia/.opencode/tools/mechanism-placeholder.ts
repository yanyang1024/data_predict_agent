import { tool } from "@opencode-ai/plugin"

interface RcpParams {
  [key: string]: number | string
}

interface MechanismResult {
  status: string
  inputSummary: Record<string, unknown>
  analysis: {
    parameterEffects: Array<{
      parameter: string
      value: number | string
      expectedImpact: string
      confidence: string
    }>
    processWindowNotes: string[]
    potentialRootCauses: string[]
  }
  disclaimer: string
}

export default tool({
  description: "蚀刻机理仿真（定性分析版）。基于蚀刻物理/化学机理知识，对RCP参数进行定性分析 - 评估各参数对刻蚀速率、选择比、均匀性、剖面轮廓的影响，分析工艺窗口边界与偏差根因。当前无定量仿真后端，仅提供理论分析。",
  args: {
    rcpParams: tool.schema.string().describe("RCP参数JSON，例如：{\"CF4_flow\": 100, \"CHF3_flow\": 20, \"Ar_flow\": 200, \"source_power\": 500, \"bias_power\": 100, \"pressure\": 30, \"temperature\": 20}"),
    etchIssue: tool.schema.string().optional().describe("当前遇到的蚀刻问题描述，例如：Bias CD偏大、选择比不够、刻蚀速率慢"),
  },
  async execute(args) {
    let params: RcpParams = {}
    try {
      params = JSON.parse(args.rcpParams)
    } catch {
      return JSON.stringify({
        status: "error",
        message: "RCP参数JSON解析失败，请检查格式",
      } as MechanismResult)
    }

    const effects: MechanismResult["analysis"]["parameterEffects"] = []
    const windowNotes: string[] = []
    const rootCauses: string[] = []

    for (const [key, value] of Object.entries(params)) {
      const keyLower = key.toLowerCase()
      const numVal = typeof value === "number" ? value : parseFloat(String(value))

      if (keyLower.includes("power") || keyLower.includes("source") || keyLower.includes("bias")) {
        if (!isNaN(numVal)) {
          if (numVal > 800) {
            effects.push({ parameter: key, value, expectedImpact: "高功率可能导致选择比下降和衬底损伤", confidence: "高" })
            windowNotes.push(`${key} 偏高（${numVal}），需关注选择比和离子损伤`)
          } else if (numVal < 200) {
            effects.push({ parameter: key, value, expectedImpact: "低功率可能刻蚀速率不足", confidence: "高" })
            windowNotes.push(`${key} 偏低（${numVal}），需关注刻蚀速率`)
          } else {
            effects.push({ parameter: key, value, expectedImpact: "功率在典型工艺窗口内", confidence: "高" })
          }
        }
      }

      if (keyLower.includes("flow") || keyLower.includes("gas")) {
        if (!isNaN(numVal) && numVal > 200) {
          effects.push({ parameter: key, value, expectedImpact: "高流量可能增加气体消耗和均匀性挑战", confidence: "中" })
        }
      }

      if (keyLower.includes("press")) {
        if (!isNaN(numVal)) {
          if (numVal > 80) {
            effects.push({ parameter: key, value, expectedImpact: "高气压降低离子方向性，可能导致剖面倾斜", confidence: "高" })
            windowNotes.push(`气压 ${numVal}mTorr 偏高，可能导致各向同性刻蚀`)
          } else if (numVal < 10) {
            effects.push({ parameter: key, value, expectedImpact: "低气压提高方向性但降低刻蚀速率", confidence: "高" })
          } else {
            effects.push({ parameter: key, value, expectedImpact: "气压在典型工艺窗口内", confidence: "高" })
          }
        }
      }

      if (keyLower.includes("temp")) {
        if (!isNaN(numVal)) {
          if (numVal > 60) {
            effects.push({ parameter: key, value, expectedImpact: "高温可能影响聚合物沉积和侧壁保护", confidence: "中" })
          } else if (numVal < -10) {
            effects.push({ parameter: key, value, expectedImpact: "低温可能影响反应速率和副产物挥发", confidence: "中" })
          }
        }
      }
    }

    if (!effects.length) {
      effects.push({ parameter: "(全部)", value: "N/A", expectedImpact: "基于提供的参数无法进行具体分析，请提供更标准的RCP参数", confidence: "低" })
    }

    if (args.etchIssue) {
      const issue = args.etchIssue.toLowerCase()
      if (issue.includes("bias cd") || issue.includes("cd偏")) {
        rootCauses.push("偏压功率与气压比例可能不合适，影响离子方向性")
        rootCauses.push("聚合物生成与刻蚀速率平衡可能失调")
        rootCauses.push("掩膜侧壁沉积不足可能导致CD偏大")
      }
      if (issue.includes("selectiv") || issue.includes("选择比")) {
        rootCauses.push("含氟碳气体(C4F8/CHF3)比例可能偏低")
        rootCauses.push("偏压功率过高导致物理溅射增强，降低选择比")
        rootCauses.push("氧气添加量可能过大，加速了掩膜消耗")
      }
      if (issue.includes("rate") || issue.includes("速率") || issue.includes("慢")) {
        rootCauses.push("源功率或偏压功率可能偏低")
        rootCauses.push("刻蚀气体总流量可能不足")
        rootCauses.push("气压可能偏离最佳反应条件")
      }
      if (issue.includes("uniform") || issue.includes("均匀")) {
        rootCauses.push("气体分布均匀性可能需要优化")
        rootCauses.push("电极间距或温度分布可能不均匀")
        rootCauses.push("腔室压力梯度可能导致中心与边缘速率差异")
      }
      if (rootCauses.length === 0) {
        rootCauses.push(`"${args.etchIssue}" 问题需要结合更多工艺参数进行详细分析`)
      }
    }

    const result: MechanismResult = {
      status: "success",
      inputSummary: params,
      analysis: {
        parameterEffects: effects,
        processWindowNotes: windowNotes.length > 0 ? windowNotes : ["所有参数在典型工艺窗口范围内"],
        potentialRootCauses: rootCauses.length > 0 ? rootCauses : ["未识别到明确问题，可进一步调节参数优化性能"],
      },
      disclaimer: "分析基于蚀刻机理理论知识，为定性分析结果。定量仿真后端尚未接入，具体数值需通过实验或仿真验证。建议结合数据分析和实验设计(DOE)获得更精确的结论。",
    }

    return JSON.stringify(result, null, 2)
  },
})
