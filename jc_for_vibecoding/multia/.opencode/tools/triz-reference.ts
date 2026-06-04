import { tool } from "@opencode-ai/plugin"

interface TrizPrinciple {
  id: number
  name: string
  description: string
  etchExample: string
}

interface TrizParameter {
  id: number
  name: string
  description: string
}

interface MatrixEntry {
  improving: number
  worsening: number
  principles: number[]
}

const PRINCIPLES: TrizPrinciple[] = [
  { id: 1, name: "分割", description: "将物体分成独立部分；使物体可组合/拆卸", etchExample: "将蚀刻工艺拆分为多个步骤，各步骤优化不同性能指标" },
  { id: 2, name: "抽取", description: "从物体中抽出干扰部分或属性", etchExample: "增加中间吹扫步骤去除反应副产物" },
  { id: 3, name: "局部质量", description: "使物体不同部分具有不同功能", etchExample: "边缘区域使用独立气体喷嘴调节均匀性" },
  { id: 4, name: "不对称", description: "用不对称形式代替对称", etchExample: "采用非对称电极设计优化等离子体分布" },
  { id: 5, name: "合并", description: "合并同类或相邻操作", etchExample: "沉积-刻蚀-沉积一体化脉冲工艺" },
  { id: 6, name: "通用性", description: "使物体多功能化", etchExample: "同一气体源通过功率调制实现刻蚀/沉积切换" },
  { id: 7, name: "套装", description: "嵌套或叠放物体", etchExample: "多层掩膜结构实现不同的刻蚀轮廓" },
  { id: 9, name: "预先反作用", description: "预先施加反作用力", etchExample: "预沉积聚合物层再开始主刻蚀" },
  { id: 10, name: "预先作用", description: "预先放置物体，使其在最方便位置立即动作", etchExample: "预调理步骤稳定腔室状态后再刻蚀" },
  { id: 11, name: "预先补偿", description: "预先准备补救措施", etchExample: "刻蚀终点前减速，防止过刻蚀" },
  { id: 14, name: "曲率", description: "用曲线/球面代替直线/平面", etchExample: "曲面电极或气体喷淋头设计改善均匀性" },
  { id: 15, name: "动态性", description: "使物体在操作中自动调整", etchExample: "动态参数调整(功率/气压实时变化)优化刻蚀过程" },
  { id: 18, name: "机械振动", description: "利用振动或共振", etchExample: "兆声波辅助清洗去除刻蚀残留" },
  { id: 19, name: "周期性动作", description: "用周期性动作代替连续动作", etchExample: "脉冲等离子体刻蚀减少电荷损伤" },
  { id: 22, name: "变害为利", description: "利用有害因素获得积极效果", etchExample: "利用聚合物沉积控制侧壁轮廓" },
  { id: 24, name: "中介物", description: "使用中介物传递作用", etchExample: "使用牺牲层或中间层改善刻蚀界面" },
  { id: 26, name: "复制", description: "用廉价复制品代替实物", etchExample: "利用仿真模型预测代替大量试错实验" },
  { id: 27, name: "廉价替代", description: "用廉价物品代替昂贵", etchExample: "使用低成本测试片代替产品晶圆做条件摸索" },
  { id: 28, name: "机械替代", description: "用传感/场作用代替机械作用", etchExample: "OES终点检测替代定时刻蚀" },
  { id: 32, name: "改变颜色", description: "改变物体或其环境的颜色/透明度", etchExample: "利用等离子体光发射谱实时监控工艺状态" },
  { id: 35, name: "参数变化", description: "改变物理/化学状态", etchExample: "改变气体混合物比例实现刻蚀模式切换" },
  { id: 37, name: "热膨胀", description: "利用材料热膨胀特性", etchExample: "静电卡盘温度精确控制影响刻蚀速率均匀性" },
]

const PARAMETERS: TrizParameter[] = [
  { id: 1, name: "运动物体的重量", description: "移动物体的质量" },
  { id: 2, name: "静止物体的重量", description: "静止物体的质量" },
  { id: 9, name: "速度", description: "物体运动速度或速率" },
  { id: 10, name: "力", description: "系统间相互作用的度量" },
  { id: 11, name: "应力/压力", description: "单位面积上的力" },
  { id: 12, name: "形状", description: "物体的外形轮廓" },
  { id: 13, name: "结构的稳定性", description: "系统抵抗变形的能力" },
  { id: 14, name: "强度", description: "抵抗破坏的能力" },
  { id: 15, name: "运动物体耐久性", description: "移动物体能执行功能的时间" },
  { id: 16, name: "静止物体耐久性", description: "静止物体能执行功能的时间" },
  { id: 17, name: "温度", description: "系统的热状态" },
  { id: 18, name: "照度", description: "单位面积的光通量" },
  { id: 19, name: "运动物体消耗能量", description: "移动物体所需的能量" },
  { id: 20, name: "静止物体消耗能量", description: "静止物体所需的能量" },
  { id: 21, name: "功率", description: "单位时间做的功" },
  { id: 22, name: "能量损失", description: "系统能量消耗中无用的部分" },
  { id: 23, name: "物质损失", description: "系统中部分或全部物质的损失" },
  { id: 24, name: "信息损失", description: "系统中部分或全部数据的损失" },
  { id: 25, name: "时间损失", description: "改善功能所需的时间" },
  { id: 26, name: "物质数量", description: "系统中物质的数量" },
  { id: 27, name: "可靠性", description: "系统在指定条件下完成功能的能力" },
  { id: 28, name: "测量精度", description: "系统特性的测量准确度" },
  { id: 29, name: "制造精度", description: "系统制造的一致性" },
  { id: 30, name: "外部有害因素", description: "系统对外部有害影响的敏感度" },
  { id: 31, name: "有害副作用", description: "系统产生的有害效应" },
  { id: 32, name: "可制造性", description: "系统制造的方便程度" },
  { id: 33, name: "操作方便性", description: "系统操作的便利性" },
  { id: 34, name: "可维修性", description: "系统维修的方便程度" },
  { id: 35, name: "适应性", description: "系统适应变化的能力" },
  { id: 36, name: "装置复杂性", description: "系统的复杂程度" },
  { id: 37, name: "控制复杂性", description: "控制系统的复杂程度" },
  { id: 38, name: "自动化程度", description: "系统自动运行的程度" },
  { id: 39, name: "生产率", description: "单位时间的产出" },
]

const MATRIX: MatrixEntry[] = [
  { improving: 9, worsening: 14, principles: [28, 35, 10, 19] },
  { improving: 9, worsening: 17, principles: [28, 19, 35, 15] },
  { improving: 9, worsening: 21, principles: [35, 15, 19, 28] },
  { improving: 9, worsening: 30, principles: [1, 24, 35, 10] },
  { improving: 9, worsening: 31, principles: [19, 35, 28, 15] },
  { improving: 10, worsening: 14, principles: [35, 10, 28, 1] },
  { improving: 11, worsening: 9, principles: [35, 14, 3, 19] },
  { improving: 12, worsening: 14, principles: [35, 15, 14, 1] },
  { improving: 13, worsening: 17, principles: [35, 10, 14, 28] },
  { improving: 14, worsening: 9, principles: [1, 28, 35, 14] },
  { improving: 14, worsening: 10, principles: [15, 35, 14, 28] },
  { improving: 14, worsening: 17, principles: [35, 28, 14, 15] },
  { improving: 14, worsening: 19, principles: [35, 28, 14, 10] },
  { improving: 17, worsening: 9, principles: [28, 19, 35, 15] },
  { improving: 17, worsening: 14, principles: [35, 15, 14, 28] },
  { improving: 17, worsening: 21, principles: [28, 35, 10, 19] },
  { improving: 17, worsening: 30, principles: [28, 15, 35, 14] },
  { improving: 17, worsening: 31, principles: [19, 35, 28, 15] },
  { improving: 19, worsening: 9, principles: [35, 28, 10, 19] },
  { improving: 19, worsening: 14, principles: [35, 15, 14, 28] },
  { improving: 21, worsening: 9, principles: [35, 28, 10, 19] },
  { improving: 21, worsening: 14, principles: [35, 15, 14, 28] },
  { improving: 21, worsening: 17, principles: [28, 35, 19, 15] },
  { improving: 21, worsening: 30, principles: [35, 28, 14, 15] },
  { improving: 21, worsening: 31, principles: [35, 19, 28, 15] },
  { improving: 27, worsening: 14, principles: [35, 10, 28, 1] },
  { improving: 27, worsening: 17, principles: [35, 28, 15, 14] },
  { improving: 27, worsening: 30, principles: [35, 28, 1, 15] },
  { improving: 27, worsening: 31, principles: [35, 19, 28, 14] },
  { improving: 30, worsening: 9, principles: [1, 24, 35, 10] },
  { improving: 30, worsening: 14, principles: [35, 14, 28, 1] },
  { improving: 30, worsening: 17, principles: [35, 28, 14, 15] },
  { improving: 30, worsening: 21, principles: [35, 28, 15, 14] },
  { improving: 30, worsening: 31, principles: [19, 35, 28, 14] },
  { improving: 31, worsening: 9, principles: [19, 35, 28, 15] },
  { improving: 31, worsening: 14, principles: [35, 15, 14, 28] },
  { improving: 31, worsening: 17, principles: [19, 35, 28, 15] },
  { improving: 31, worsening: 21, principles: [35, 19, 28, 15] },
  { improving: 31, worsening: 30, principles: [19, 35, 28, 14] },
  { improving: 32, worsening: 14, principles: [1, 35, 28, 14] },
  { improving: 32, worsening: 17, principles: [35, 28, 14, 15] },
  { improving: 33, worsening: 14, principles: [1, 28, 14, 35] },
  { improving: 35, worsening: 14, principles: [14, 35, 28, 15] },
  { improving: 35, worsening: 17, principles: [35, 15, 28, 14] },
  { improving: 35, worsening: 21, principles: [35, 28, 15, 14] },
  { improving: 35, worsening: 30, principles: [35, 15, 1, 28] },
  { improving: 35, worsening: 31, principles: [15, 35, 28, 19] },
  { improving: 38, worsening: 14, principles: [35, 14, 28, 1] },
  { improving: 38, worsening: 17, principles: [35, 15, 14, 28] },
  { improving: 38, worsening: 21, principles: [35, 28, 15, 14] },
  { improving: 38, worsening: 30, principles: [35, 28, 14, 15] },
  { improving: 38, worsening: 31, principles: [35, 19, 28, 14] },
  { improving: 39, worsening: 9, principles: [35, 19, 28, 15] },
  { improving: 39, worsening: 14, principles: [35, 28, 15, 14] },
  { improving: 39, worsening: 17, principles: [28, 35, 19, 15] },
  { improving: 39, worsening: 21, principles: [35, 28, 15, 14] },
  { improving: 39, worsening: 30, principles: [35, 28, 15, 14] },
  { improving: 39, worsening: 31, principles: [35, 19, 28, 15] },
]

const ETCH_KEYWORD_MAP: Record<string, [number, number][]> = {
  "etch rate": [[9, 14], [9, 21], [39, 14]],
  "selectivity": [[27, 30], [27, 31], [14, 30]],
  "uniformity": [[33, 14], [32, 14], [38, 14]],
  "profile": [[12, 14], [12, 30], [35, 14]],
  "cd": [[29, 14], [29, 17], [28, 14]],
  "damage": [[31, 14], [31, 17], [30, 31]],
  "pressure": [[11, 9], [11, 14], [17, 30]],
  "power": [[21, 9], [21, 17], [21, 31]],
  "temperature": [[17, 9], [17, 14], [17, 30]],
  "polymer": [[23, 14], [26, 14], [31, 14]],
  "bias": [[10, 14], [10, 31], [21, 31]],
  "rate slow": [[9, 21], [19, 21], [39, 21]],
  "bias cd": [[29, 14], [29, 17], [28, 17]],
  "bottom cd": [[29, 14], [29, 12], [28, 12]],
}

function findBestMatch(input: string): [number, number][] {
  const lower = input.toLowerCase()
  const matches: [number, number][] = []

  for (const [keyword, pairs] of Object.entries(ETCH_KEYWORD_MAP)) {
    if (lower.includes(keyword)) {
      matches.push(...pairs)
    }
  }

  if (!matches.length) {
    if (lower.includes("improve") || lower.includes("increase") || lower.includes("want")) {
      return [[39, 14], [35, 14], [39, 31]]
    }
    if (lower.includes("reduce") || lower.includes("decrease") || lower.includes("problem")) {
      return [[31, 9], [30, 14], [27, 31]]
    }
    return [[35, 14], [28, 14], [15, 14]]
  }

  return matches
}

function lookupMatrix(improving: number, worsening: number): number[] {
  for (const entry of MATRIX) {
    if (entry.improving === improving && entry.worsening === worsening) {
      return entry.principles
    }
  }
  return [35, 28, 15, 14]
}

export default tool({
  description: "TRIZ矛盾矩阵查询工具。输入蚀刻工艺中的技术矛盾描述，返回推荐的TRIZ发明原理及其在半导体蚀刻场景的应用建议。内置40条发明原理和关键矛盾矩阵映射。",
  args: {
    contradiction: tool.schema.string().describe("技术矛盾描述，例如：需要提高刻蚀速率但选择比下降；或需要提高偏压功率但晶圆损伤增加"),
    improvingAspect: tool.schema.string().optional().describe("可选：直接指定要改善的方面，例如：刻蚀速率、选择比、均匀性"),
    worseningAspect: tool.schema.string().optional().describe("可选：直接指定恶化的方面，例如：选择比、损伤、轮廓"),
  },
  async execute(args) {
    const { contradiction, improvingAspect, worseningAspect } = args

    let pairs: [number, number][]

    if (improvingAspect && worseningAspect) {
      pairs = findBestMatch(`${improvingAspect} ${worseningAspect}`)
    } else {
      pairs = findBestMatch(contradiction)
    }

    pairs = pairs.slice(0, 3)

    const results = pairs.map(([improving, worsening]) => {
      const principles = lookupMatrix(improving, worsening)
      const improvingParam = PARAMETERS.find(p => p.id === improving)
      const worseningParam = PARAMETERS.find(p => p.id === worsening)

      return {
        contradiction: {
          improving: improvingParam ? `${improvingParam.name}(${improving})` : `${improving}`,
          worsening: worseningParam ? `${worseningParam.name}(${worsening})` : `${worsening}`,
        },
        recommendedPrinciples: principles.map(id => {
          const principle = PRINCIPLES.find(p => p.id === id)
          return principle
            ? { id: principle.id, name: principle.name, description: principle.description, etchApplication: principle.etchExample }
            : { id, name: `原理${id}`, description: "请查阅TRIZ参考手册", etchApplication: "请结合实际场景分析" }
        }),
      }
    })

    return JSON.stringify({
      status: "success",
      inputContradiction: contradiction,
      extractedContradictions: results.map(r => `${r.contradiction.improving} ↔ ${r.contradiction.worsening}`),
      results,
      allPrinciples: PRINCIPLES.map(p => ({ id: p.id, name: p.name, description: p.description, etchExample: p.etchExample })),
    }, null, 2)
  },
})
