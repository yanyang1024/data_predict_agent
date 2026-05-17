import { useState } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export default function LoginPage() {
  const { user, loginDev } = useAuth();
  const [email, setEmail] = useState('admin@example.com');
  const [domain, setDomain] = useState('IT');
  const [employeeNo, setEmployeeNo] = useState('1');
  const [error, setError] = useState('');
  if (user) return <Navigate to="/" replace />;
  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-100 p-6">
      <form
        onSubmit={async (e) => {
          e.preventDefault();
          setError('');
          try {
            await loginDev(email, domain, employeeNo ? Number(employeeNo) : undefined);
          } catch (err) {
            setError((err as Error).message);
          }
        }}
        className="w-full max-w-md rounded-3xl bg-white p-8 shadow-soft"
      >
        <h1 className="text-2xl font-bold">Flash-Agents</h1>
        <p className="mt-2 text-sm text-slate-500">开发模式可使用 whitelist.json 中的账号直接登录；生产环境切换到 SSO code flow。</p>
        <label className="mt-6 block text-sm font-medium">邮箱</label>
        <input value={email} onChange={(e) => setEmail(e.target.value)} className="mt-2 w-full rounded-xl border border-slate-300 px-3 py-2" />
        <label className="mt-4 block text-sm font-medium">域</label>
        <select value={domain} onChange={(e) => setDomain(e.target.value)} className="mt-2 w-full rounded-xl border border-slate-300 px-3 py-2">
          <option>IT</option>
          <option>RD</option>
          <option>MEC</option>
        </select>
        <label className="mt-4 block text-sm font-medium">员工序号（端口 = 20000 + 序号）</label>
        <input value={employeeNo} onChange={(e) => setEmployeeNo(e.target.value)} className="mt-2 w-full rounded-xl border border-slate-300 px-3 py-2" />
        {error && <div className="mt-4 rounded-xl bg-red-50 p-3 text-sm text-red-700">{error}</div>}
        <button className="mt-6 w-full rounded-xl bg-slate-900 px-4 py-3 font-medium text-white">登录</button>
      </form>
    </div>
  );
}
