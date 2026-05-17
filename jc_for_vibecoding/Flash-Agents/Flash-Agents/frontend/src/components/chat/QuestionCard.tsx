import { apiFetch } from '../../services/api';

export function QuestionCard({ conversationId, question }: { conversationId?: string; question: { id: string; text: string; options?: string[] } }) {
  async function answer(value: string) {
    if (!conversationId) return;
    await apiFetch(`/conversations/${conversationId}/questions/${encodeURIComponent(question.id)}/answer`, {
      method: 'POST',
      body: JSON.stringify({ answer: value })
    });
  }

  return (
    <div className="mt-2 rounded-xl border border-blue-200 bg-blue-50 p-3 text-sm text-blue-950">
      <div className="font-medium">Agent 需要确认</div>
      <p className="mt-1">{question.text}</p>
      {!!question.options?.length && <div className="mt-2 flex flex-wrap gap-2">{question.options.map((o) => <button key={o} onClick={() => void answer(o)} className="rounded-full bg-white px-3 py-1 text-xs shadow">{o}</button>)}</div>}
    </div>
  );
}
