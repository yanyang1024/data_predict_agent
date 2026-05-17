import type { ChatMessage, SseEvent, TodoItem, ToolCall } from '../types';

export interface ConversationUiState {
  conversationId?: string;
  messages: ChatMessage[];
  todos: TodoItem[];
  running: boolean;
  lastEventAt: number;
  error?: string;
}

export type Cache = Map<string, string>;

function assistantDraft(messages: ChatMessage[]): ChatMessage[] {
  const last = messages[messages.length - 1];
  if (last?.role === 'assistant' && last.status === 'streaming') return messages;
  return [...messages, { id: crypto.randomUUID(), role: 'assistant', content: '', createdAt: Date.now(), status: 'streaming', reasoning: [], tools: [] }];
}

function updateLastAssistant(messages: ChatMessage[], updater: (msg: ChatMessage) => ChatMessage): ChatMessage[] {
  const next = assistantDraft(messages);
  const idx = next.length - 1;
  return next.map((msg, i) => (i === idx ? updater(msg) : msg));
}

export function reduceSseEvent(state: ConversationUiState, event: SseEvent, cache: Cache): ConversationUiState {
  const now = Date.now();
  switch (event.event) {
    case 'conversation.bound': {
      const data = event.data as { conversation_id?: string };
      if (data.conversation_id) cache.set('conversation_id', data.conversation_id);
      return { ...state, conversationId: data.conversation_id || state.conversationId, running: true, lastEventAt: now };
    }
    case 'assistant.delta': {
      const text = String((event.data as any).text ?? '');
      return { ...state, messages: updateLastAssistant(state.messages, (m) => ({ ...m, content: m.content + text })), running: true, lastEventAt: now };
    }
    case 'reasoning': {
      const text = String((event.data as any).text ?? '');
      return { ...state, messages: updateLastAssistant(state.messages, (m) => ({ ...m, reasoning: [...(m.reasoning || []), text] })), lastEventAt: now };
    }
    case 'todo.update': {
      const items = ((event.data as any).items || []) as TodoItem[];
      return { ...state, todos: items, lastEventAt: now };
    }
    case 'tool.start':
    case 'tool.end': {
      const data = event.data as any;
      const tool: ToolCall = {
        id: data.id || data.name || crypto.randomUUID(),
        name: data.name || 'tool',
        status: event.event === 'tool.end' ? 'done' : 'running',
        input: data.input,
        output: data.output
      };
      return {
        ...state,
        messages: updateLastAssistant(state.messages, (m) => {
          const tools = [...(m.tools || [])];
          const idx = tools.findIndex((t) => t.id === tool.id);
          if (idx >= 0) tools[idx] = { ...tools[idx], ...tool };
          else tools.push(tool);
          return { ...m, tools };
        }),
        lastEventAt: now
      };
    }
    case 'question': {
      const q = event.data as any;
      return { ...state, messages: updateLastAssistant(state.messages, (m) => ({ ...m, questions: [...(m.questions || []), { id: q.id || crypto.randomUUID(), text: q.text || '', options: q.options || [] }] })), lastEventAt: now };
    }
    case 'done':
      return { ...state, messages: state.messages.map((m, i) => (i === state.messages.length - 1 && m.role === 'assistant' ? { ...m, status: 'done' } : m)), running: false, lastEventAt: now };
    case 'aborted':
      return { ...state, running: false, lastEventAt: now };
    case 'error':
      return { ...state, error: String((event.data as any).message || event.data || '未知错误'), running: false, lastEventAt: now };
    default:
      return { ...state, lastEventAt: now };
  }
}
