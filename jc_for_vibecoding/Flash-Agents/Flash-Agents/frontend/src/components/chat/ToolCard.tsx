import type { ToolCall } from '../../types';

export function ToolCard({ tool }: { tool: ToolCall }) {
  return (
    <div className="mt-2 rounded-xl border border-slate-200 bg-slate-50 p-3 text-sm">
      <div className="flex items-center justify-between">
        <span className="font-medium">工具：{tool.name}</span>
        <span className="text-xs text-slate-500">{tool.status}</span>
      </div>
      {tool.input !== undefined && <pre className="mt-2 overflow-auto rounded-lg bg-white p-2 text-xs">{JSON.stringify(tool.input, null, 2)}</pre>}
      {tool.output !== undefined && <pre className="mt-2 overflow-auto rounded-lg bg-white p-2 text-xs">{JSON.stringify(tool.output, null, 2)}</pre>}
    </div>
  );
}
