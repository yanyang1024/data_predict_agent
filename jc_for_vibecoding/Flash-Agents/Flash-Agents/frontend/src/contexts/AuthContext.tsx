import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { apiFetch, setToken } from '../services/api';
import type { TokenOut, User } from '../types';

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  loginDev: (email: string, domain: string, employeeNo?: number) => Promise<void>;
  completeSso: (code: string, state: string) => Promise<void>;
  logout: () => void;
  refresh: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    try {
      const me = await apiFetch<User>('/auth/me');
      setUser(me);
    } catch {
      setUser(null);
      setToken(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const loginDev = useCallback(async (email: string, domain: string, employeeNo?: number) => {
    const token = await apiFetch<TokenOut>('/auth/dev-login', {
      method: 'POST',
      body: JSON.stringify({ email, domain, employee_no: employeeNo })
    });
    setToken(token.access_token);
    setUser(token.user);
  }, []);

  const completeSso = useCallback(async (code: string, state: string) => {
    const token = await apiFetch<TokenOut>('/auth/callback', {
      method: 'POST',
      body: JSON.stringify({ code, state })
    });
    setToken(token.access_token);
    setUser(token.user);
  }, []);

  const logout = useCallback(() => {
    setToken(null);
    setUser(null);
  }, []);

  const value = useMemo(() => ({ user, loading, loginDev, completeSso, logout, refresh }), [user, loading, loginDev, completeSso, logout, refresh]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) throw new Error('useAuth must be used within AuthProvider');
  return value;
}
