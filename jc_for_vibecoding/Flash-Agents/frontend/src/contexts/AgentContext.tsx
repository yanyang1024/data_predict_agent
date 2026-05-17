import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { apiFetch } from '../services/api';
import type { Agent } from '../types';
import { useAuth } from './AuthContext';

interface AgentContextValue {
  agents: Agent[];
  reload: () => Promise<void>;
}

const AgentContext = createContext<AgentContextValue | null>(null);

export function AgentProvider({ children }: { children: React.ReactNode }) {
  const { user } = useAuth();
  const [agents, setAgents] = useState<Agent[]>([]);
  const reload = useCallback(async () => {
    if (!user) {
      setAgents([]);
      return;
    }
    setAgents(await apiFetch<Agent[]>('/agents'));
  }, [user]);

  useEffect(() => {
    void reload();
  }, [reload]);

  const value = useMemo(() => ({ agents, reload }), [agents, reload]);
  return <AgentContext.Provider value={value}>{children}</AgentContext.Provider>;
}

export function useAgents() {
  const value = useContext(AgentContext);
  if (!value) throw new Error('useAgents must be used within AgentProvider');
  return value;
}
