import type { TodoItem } from '../../types';

export function TodoDock({ items }: { items: TodoItem[] }) {
  return (
    <aside className="rounded-2xl bg-white p-4 shadow-soft">
      <h3 className="font-semibold">任务进度</h3>
      <div className="mt-3 space-y-2">
        {items.length === 0 && <p className="text-sm text-slate-500">等待 Agent 创建 Todo...</p>}
        {items.map((item) => (
          <div key={item.id} className="flex items-center gap-2 text-sm">
            <span className={`h-2 w-2 rounded-full ${item.status === 'done' ? 'bg-emerald-500' : item.status === 'running' ? 'bg-blue-500' : 'bg-slate-300'}`} />
            <span>{item.text}</span>
            <span className="ml-auto text-xs text-slate-400">{item.status}</span>
          </div>
        ))}
      </div>
    </aside>
  );
}
