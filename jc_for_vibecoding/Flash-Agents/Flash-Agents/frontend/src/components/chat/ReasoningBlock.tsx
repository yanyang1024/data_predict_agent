export function ReasoningBlock({ items }: { items: string[] }) {
  if (!items.length) return null;
  return (
    <details className="mt-3 rounded-xl border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">
      <summary className="cursor-pointer font-medium">推理与规划</summary>
      <div className="mt-2 space-y-2">
        {items.map((item, idx) => (
          <p key={idx}>{item}</p>
        ))}
      </div>
    </details>
  );
}
