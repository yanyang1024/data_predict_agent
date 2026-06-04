import { tool } from "@opencode-ai/plugin"

const BASE_URL = process.env.ETCH_LITERATURE_API_BASE || "http://10.18.220.244:32300"

async function sleep(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

export default tool({
  description: "Call the Etch literature knowledge-base API. Use this to create a conversation, send a streaming literature query, wait, and retrieve citation metadata. If the API is unavailable, return a structured error.",
  args: {
    query: tool.schema.string().describe("Literature search question for Etch process, mechanism, DOE, or optimization methods"),
    waitMs: tool.schema.number().default(5000).describe("Wait time before retrieving message info"),
  },
  async execute(args) {
    try {
      const convResp = await fetch(`${BASE_URL}/create_conversation`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({})
      })
      if (!convResp.ok) {
        return JSON.stringify({
          success: false,
          stage: "create_conversation",
          status: convResp.status,
          error: await convResp.text(),
          fallback: "Use placeholder literature query plan."
        }, null, 2)
      }
      const conv = await convResp.json()
      const conversationId = conv.conversation_id || conv.id
      const chatResp = await fetch(`${BASE_URL}/chat_query_v2_sse`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          conversation_id: conversationId,
          query: args.query
        })
      })
      if (!chatResp.ok) {
        return JSON.stringify({
          success: false,
          stage: "chat_query_v2_sse",
          status: chatResp.status,
          error: await chatResp.text(),
          conversationId
        }, null, 2)
      }
      await sleep(args.waitMs)
      const infoResp = await fetch(`${BASE_URL}/get_message_info?conversation_id=${encodeURIComponent(conversationId)}`, {
        method: "GET"
      })
      if (!infoResp.ok) {
        return JSON.stringify({
          success: false,
          stage: "get_message_info",
          status: infoResp.status,
          error: await infoResp.text(),
          conversationId
        }, null, 2)
      }
      const info = await infoResp.json()
      return JSON.stringify({
        success: true,
        conversationId,
        messageInfo: info
      }, null, 2)
    } catch (error) {
      return JSON.stringify({
        success: false,
        error: error instanceof Error ? error.message : String(error),
        fallback: "Literature API unavailable. Use query strategy and placeholder citation schema only."
      }, null, 2)
    }
  },
})
