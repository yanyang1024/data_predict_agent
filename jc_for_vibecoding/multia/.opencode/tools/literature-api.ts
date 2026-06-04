import { tool } from "@opencode-ai/plugin"

interface ConversationResponse {
  conversation_id?: string
  error?: string
}

interface ChatResponse {
  answer?: string
  error?: string
}

interface ReferenceInfo {
  document_name: string
  snippet: string
  download_link: string
}

interface ReferencesResponse {
  references?: ReferenceInfo[]
  error?: string
}

const API_BASE = "http://10.18.220.244:32300"

export default tool({
  description: "检索半导体蚀刻文献知识库。发送问题到远程知识库API，获取回答及引用文档信息。工作流：创建对话 → 获取回答 → 等待5秒 → 获取引用信息。",
  args: {
    query: tool.schema.string().describe("检索问题，例如：高选择比SiO2刻蚀方法"),
    knowledge_base: tool.schema.string().default("半导体蚀刻").describe("知识库名称"),
  },
  async execute(args) {
    const { query, knowledge_base } = args

    try {
      const convResp = await fetch(`${API_BASE}/create_conversation`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          knowledge_base_name: knowledge_base,
          query: query,
        }),
      })

      if (!convResp.ok) {
        return JSON.stringify({
          status: "error",
          message: `API returned status ${convResp.status}`,
          suggestion: "请检查知识库API是否可用",
        })
      }

      const convData: ConversationResponse = await convResp.json()

      if (!convData.conversation_id) {
        return JSON.stringify({
          status: "error",
          message: "未能获取 conversation_id",
          response: convData,
        })
      }

      const conversationId = convData.conversation_id

      const chatResp = await fetch(`${API_BASE}/chat_query_v2_sse`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          conversation_id: conversationId,
          query: query,
        }),
      })

      if (!chatResp.ok) {
        return JSON.stringify({
          status: "error",
          message: `Chat API returned status ${chatResp.status}`,
          conversation_id: conversationId,
        })
      }

      const chatData: ChatResponse = await chatResp.json()
      const answer = chatData.answer || ""

      await new Promise(resolve => setTimeout(resolve, 5000))

      const refResp = await fetch(
        `${API_BASE}/get_message_info?conversation_id=${encodeURIComponent(conversationId)}`,
        { method: "GET" }
      )

      let references: ReferenceInfo[] = []
      if (refResp.ok) {
        const refData: ReferencesResponse = await refResp.json()
        references = refData.references || []
      }

      return JSON.stringify({
        status: "success",
        conversation_id: conversationId,
        answer: answer,
        references: references.map(ref => ({
          document: ref.document_name,
          snippet: ref.snippet,
          link: ref.download_link,
        })),
        summary: `获取到 ${references.length} 份引用文档`,
      })
    } catch (error) {
      return JSON.stringify({
        status: "unavailable",
        message: "知识库API当前不可用，请稍后重试",
        detail: error instanceof Error ? error.message : String(error),
        fallback: "请基于已知知识进行分析",
      })
    }
  },
})
