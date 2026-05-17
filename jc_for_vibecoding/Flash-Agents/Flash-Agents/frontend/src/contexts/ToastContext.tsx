import { createContext, useCallback, useContext, useMemo, useState } from 'react';

type Toast = { id: string; text: string; tone: 'info' | 'error' | 'success' };
const ToastContext = createContext<{ push: (text: string, tone?: Toast['tone']) => void } | null>(null);

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [items, setItems] = useState<Toast[]>([]);
  const push = useCallback((text: string, tone: Toast['tone'] = 'info') => {
    const id = crypto.randomUUID();
    setItems((old) => [...old, { id, text, tone }]);
    window.setTimeout(() => setItems((old) => old.filter((x) => x.id !== id)), 3500);
  }, []);
  const value = useMemo(() => ({ push }), [push]);
  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="fixed right-4 top-4 z-50 space-y-2">
        {items.map((t) => (
          <div key={t.id} className={`rounded-xl px-4 py-3 shadow-soft ${t.tone === 'error' ? 'bg-red-600 text-white' : t.tone === 'success' ? 'bg-emerald-600 text-white' : 'bg-slate-900 text-white'}`}>
            {t.text}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  return useContext(ToastContext) || { push: () => undefined };
}
