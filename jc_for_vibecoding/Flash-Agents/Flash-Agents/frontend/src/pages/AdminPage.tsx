import { useEffect, useState } from 'react';
import { apiFetch, API_BASE, getToken } from '../services/api';

export default function AdminPage() {
  const [stats, setStats] = useState<any>(null);
  const [users, setUsers] = useState<any[]>([]);
  useEffect(() => {
    void apiFetch('/admin/stats').then(setStats);
    void apiFetch<any[]>('/admin/users').then(setUsers);
  }, []);
  const csvUrl = `${API_BASE}/admin/audit.csv?token=${encodeURIComponent(getToken() || '')}`;
  return (
    <div className="space-y-6 p-6">
      <section className="rounded-2xl bg-white p-6 shadow-soft">
        <h1 className="text-xl font-bold">管理后台</h1>
        <div className="mt-4 grid gap-4 md:grid-cols-4">
          <div className="rounded-xl bg-slate-50 p-4"><div className="text-sm text-slate-500">用户</div><div className="text-2xl font-bold">{stats?.users ?? '-'}</div></div>
          <div className="rounded-xl bg-slate-50 p-4"><div className="text-sm text-slate-500">会话</div><div className="text-2xl font-bold">{stats?.conversations ?? '-'}</div></div>
          <div className="rounded-xl bg-slate-50 p-4"><div className="text-sm text-slate-500">运行实例</div><div className="text-2xl font-bold">{stats?.running_instances ?? '-'}</div></div>
          <a href={csvUrl} className="rounded-xl bg-slate-900 p-4 text-white">导出审计 CSV</a>
        </div>
      </section>
      <section className="rounded-2xl bg-white p-6 shadow-soft">
        <h2 className="font-semibold">组织层级 / 用户</h2>
        <div className="mt-4 overflow-auto">
          <table className="min-w-full text-sm">
            <thead><tr className="text-left text-slate-500"><th>域</th><th>邮箱</th><th>姓名</th><th>员工序号</th><th>管理员</th></tr></thead>
            <tbody>{users.map((u) => <tr key={u.id} className="border-t"><td className="py-2">{u.domain}</td><td>{u.email}</td><td>{u.display_name}</td><td>{u.employee_no}</td><td>{String(u.is_admin)}</td></tr>)}</tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
