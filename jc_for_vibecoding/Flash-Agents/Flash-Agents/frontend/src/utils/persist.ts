type Entry<T> = { value: T; ts: number };

const memory = new Map<string, Entry<unknown>>();
const PREFIX = 'flash.';
const MAX_KEYS = 80;

function key(name: string) {
  return `${PREFIX}${name}`;
}

function evictIfNeeded() {
  const keys = Object.keys(localStorage).filter((k) => k.startsWith(PREFIX));
  if (keys.length <= MAX_KEYS) return;
  const scored = keys
    .map((k) => {
      try {
        const raw = JSON.parse(localStorage.getItem(k) || '{}') as Entry<unknown>;
        return [k, raw.ts || 0] as const;
      } catch {
        return [k, 0] as const;
      }
    })
    .sort((a, b) => a[1] - b[1]);
  for (const [k] of scored.slice(0, keys.length - MAX_KEYS)) localStorage.removeItem(k);
}

export const persist = {
  get<T>(name: string, fallback: T): T {
    const k = key(name);
    const cached = memory.get(k) as Entry<T> | undefined;
    if (cached) return cached.value;
    try {
      const raw = localStorage.getItem(k);
      if (!raw) return fallback;
      const parsed = JSON.parse(raw) as Entry<T>;
      memory.set(k, parsed);
      return parsed.value ?? fallback;
    } catch {
      return fallback;
    }
  },
  set<T>(name: string, value: T) {
    const k = key(name);
    const entry: Entry<T> = { value, ts: Date.now() };
    memory.set(k, entry);
    try {
      localStorage.setItem(k, JSON.stringify(entry));
    } catch {
      evictIfNeeded();
      try {
        localStorage.setItem(k, JSON.stringify(entry));
      } catch {
        // memory cache remains available for the current tab.
      }
    }
  },
  remove(name: string) {
    const k = key(name);
    memory.delete(k);
    localStorage.removeItem(k);
  }
};
