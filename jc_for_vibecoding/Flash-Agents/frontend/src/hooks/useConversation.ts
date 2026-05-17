import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { apiFetch, streamSse } from '../services/api';
import { reduceSseEvent, type ConversationUiState } from '../services/sseEventHandler';
import type { ChatMessage, Conversation } from '../types';

const initialState: ConversationUiState = { messages: [], todos: [], running: false, lastEventAt: 0 };

export function useConversation(initialAgent = 'code') {
  const [state, setState] = useState<ConversationUiState>(initialState);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const cacheRef = useRef(new Map<string, string>());
  const abortRef = useRef<AbortController | null>(null);

  const loadConversations = useCallback(async () => {
    setConversations(await apiFetch<Conversation[]>('/conversations'));
  }, []);

  useEffect(() => {
    void loadConversations();
  }, [loadConversations]);

  useEffect(() => {
    const timer = window.setInterval(() => {
      setState((current) => {
        if (!current.running || !current.lastEventAt) return current;
        if (Date.now() - current.lastEventAt > 45_000) return { ...current, error: '流式响应超过 45 秒没有事件，可能已卡住。', running: false };
        return current;
      });
    }, 5000);
    return () => window.clearInterval(timer);
  }, []);

  useEffect(() => () => abortRef.current?.abort(), []);

  const sendMessage = useCallback(
    async (content: string, agentId = initialAgent) => {
      const userMessage: ChatMessage = { id: crypto.randomUUID(), role: 'user', content, createdAt: Date.now(), status: 'done' };
      setState((s) => ({ ...s, messages: [...s.messages, userMessage], running: true, error: undefined, lastEventAt: Date.now() }));
      abortRef.current?.abort();
      const controller = new AbortController();
      abortRef.current = controller;
      const conversationId = state.conversationId || cacheRef.current.get('conversation_id');
      try {
        await streamSse('/conversations/messages/stream', { content, conversation_id: conversationId, agent_id: agentId, client_message_id: userMessage.id }, (event) => {
          setState((prev) => reduceSseEvent(prev, event, cacheRef.current));
        }, controller.signal);
        await loadConversations();
      } catch (err) {
        if ((err as Error).name === 'AbortError') return;
        setState((s) => ({ ...s, running: false, error: (err as Error).message }));
      }
    },
    [initialAgent, loadConversations, state.conversationId]
  );

  const selectConversation = useCallback(async (conversation: Conversation) => {
    cacheRef.current.set('conversation_id', conversation.id);
    setState({ ...initialState, conversationId: conversation.id });
    try {
      const orphan = await apiFetch<{ lost: boolean; todos: any[] }>(`/conversations/${conversation.id}/orphan-check`);
      if (orphan.lost) setState((s) => ({ ...s, error: '检测到刷新后 OpenCode 内存状态丢失，已进入只读恢复状态。' }));
      else setState((s) => ({ ...s, todos: orphan.todos || [] }));
    } catch {
      // Orphan check should not block chat loading.
    }
  }, []);

  const abort = useCallback(async () => {
    const id = state.conversationId || cacheRef.current.get('conversation_id');
    abortRef.current?.abort();
    if (id) await apiFetch(`/conversations/${id}/abort`, { method: 'POST' });
    setState((s) => ({ ...s, running: false }));
  }, [state.conversationId]);

  return useMemo(() => ({ state, conversations, sendMessage, selectConversation, abort, reload: loadConversations }), [state, conversations, sendMessage, selectConversation, abort, loadConversations]);
}
