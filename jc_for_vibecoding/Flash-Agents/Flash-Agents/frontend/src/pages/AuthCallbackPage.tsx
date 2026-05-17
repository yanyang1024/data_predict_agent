import { useEffect, useState } from 'react';
import { Navigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export default function AuthCallbackPage() {
  const { user, completeSso } = useAuth();
  const [params] = useSearchParams();
  const [error, setError] = useState('');

  useEffect(() => {
    const code = params.get('code') || '';
    const state = params.get('state') || '';
    const expected = sessionStorage.getItem('flash.sso_state') || '';
    if (!code) {
      setError('SSO 回调缺少 code。');
      return;
    }
    if (!state || state !== expected) {
      setError('SSO state 校验失败。');
      return;
    }
    sessionStorage.removeItem('flash.sso_state');
    void completeSso(code, state).catch((err) => setError((err as Error).message));
  }, [completeSso, params]);

  if (user) return <Navigate to="/" replace />;
  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-100 p-6">
      <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-soft">
        <h1 className="text-xl font-bold">SSO 登录</h1>
        <p className="mt-2 text-sm text-slate-500">{error || '正在完成认证...'}</p>
      </div>
    </div>
  );
}
