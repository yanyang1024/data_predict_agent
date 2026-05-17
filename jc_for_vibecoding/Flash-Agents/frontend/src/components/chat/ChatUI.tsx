import { useMemo, useState } from 'react';
import { useAgents } from '../../contexts/AgentContext';
import { useConversation } from '../../hooks/useConversation';
import { MarkdownMessage } from './MarkdownMessage';
import { QuestionCard } from './QuestionCard';
import { ReasoningBlock } from './ReasoningBlock';
import { TodoDock } from './TodoDock';
import { ToolCard } from './ToolCard';
import { WorkspaceFilePanel } from './WorkspaceFilePanel';

export function ChatUI() {
  const { agents } = useAgents();
  const [agentId, setAgentId] = useState('code');
  const [input, setInput] = useState('');
  const conv = useConversation(agentId);
  const selectedAgent = useMemo(() => agents.find((a) => a.id === agentId), [agents, agentId]);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    const text = input.trim();
    if (!text || conv.state.running) return;
    setInput('');
    await conv.sendMessage(text, agentId);
  }

  return (
    <div className="grid h-[calc(100vh-4rem)] grid-cols-[260px_1fr_320px] gap-4 p-4">
      <aside className="rounded-2xl bg-white p-4 shadow-soft">
        <h2 className="font-semibold">会话</h2>
        <button onClick={() => window.location.reload()} className="mt-3 w-full rounded-xl bg-slate-900 px-3 py-2 text-sm text-white">新建会话</button>
        <div className="mt-4 space-y-2 overflow-auto text-sm">
          {conv.conversations.map((c) => (
            <button key={c.id} onClick={() => void conv.selectConversation(c)} className={`block w-full rounded-xl px-3 py-2 text-left hover:bg-slate-100 ${conv.state.conversationId === c.id ? 'bg-slate-100' : ''}`}>
              <div className="truncate font-medium">{c.title}</div>
              <div className="text-xs text-slate-500">{c.agent_id} · {c.status}</div>
            </button>
          ))}
        </div>
      </aside>

      <main className="flex min-w-0 flex-col rounded-2xl bg-white shadow-soft">
        <header className="border-b border-slate-200 p-4">
          <div className="flex items-center gap-3">
            <select value={agentId} onChange={(e) => setAgentId(e.target.value)} className="rounded-xl border border-slate-300 px-3 py-2">
              {agents.map((a) => <option key={a.id} value={a.id}>{a.name}</option>)}
            </select>
            <div>
              <div className="font-semibold">{selectedAgent?.name || 'Agent'}</div>
              <div className="text-sm text-slate-500">{selectedAgent?.description}</div>
            </div>
            {conv.state.running && <button onClick={() => void conv.abort()} className="ml-auto rounded-xl bg-red-50 px-3 py-2 text-sm text-red-700">中止</button>}
          </div>
        </header>
        <section className="flex-1 space-y-4 overflow-auto p-5">
          {conv.state.messages.length === 0 && <div className="rounded-2xl border border-dashed border-slate-300 p-8 text-center text-slate-500">选择 Agent 并发送任务。OpenCode session 会在首条消息时延迟创建。</div>}
          {conv.state.messages.map((m) => (
            <article key={m.id} className={`rounded-2xl p-4 ${m.role === 'user' ? 'ml-16 bg-blue-50' : 'mr-16 bg-slate-50'}`}>
              <div className="mb-2 text-xs font-semibold uppercase text-slate-400">{m.role}</div>
              <MarkdownMessage content={m.content || (m.status === 'streaming' ? '...' : '')} />
              <ReasoningBlock items={m.reasoning || []} />
              {(m.tools || []).map((tool) => <ToolCard key={tool.id} tool={tool} />)}
              {(m.questions || []).map((q) => <QuestionCard key={q.id} question={q} />)}
            </article>
          ))}
          {conv.state.error && <div className="rounded-xl bg-red-50 p-3 text-sm text-red-700">{conv.state.error}</div>}
        </section>
        <form onSubmit={(e) => void submit(e)} className="border-t border-slate-200 p-4">
          <div className="flex gap-3">
            <textarea value={input} onChange={(e) => setInput(e.target.value)} rows={2} className="flex-1 resize-none rounded-2xl border border-slate-300 p-3 outline-none focus:border-blue-500" placeholder="输入任务，让 Agent 在隔离工作区执行..." />
            <button disabled={conv.state.running || !input.trim()} className="rounded-2xl bg-slate-900 px-6 text-white disabled:cursor-not-allowed disabled:bg-slate-300">发送</button>
          </div>
        </form>
      </main>

      <div className="space-y-4 overflow-auto">
        <TodoDock items={conv.state.todos} />
        <WorkspaceFilePanel conversationId={conv.state.conversationId} />
      </div>
    </div>
  );
}
