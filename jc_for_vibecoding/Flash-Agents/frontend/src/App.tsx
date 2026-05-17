import { lazy, Suspense } from 'react';
import { BrowserRouter, Link, Navigate, Route, Routes } from 'react-router-dom';
import { AppProviders } from './contexts/AppProviders';
import { useAuth } from './contexts/AuthContext';

const ChatPage = lazy(() => import('./pages/ChatPage'));
const LoginPage = lazy(() => import('./pages/LoginPage'));
const SkillsPage = lazy(() => import('./pages/SkillsPage'));
const AdminPage = lazy(() => import('./pages/AdminPage'));

function Layout({ children }: { children: React.ReactNode }) {
  const { user, logout } = useAuth();
  if (!user) return <Navigate to="/login" replace />;
  return (
    <div>
      <nav className="flex h-16 items-center gap-4 border-b border-slate-200 bg-white px-5">
        <Link to="/" className="text-lg font-bold">Flash-Agents</Link>
        <Link to="/" className="rounded-lg px-3 py-2 text-sm hover:bg-slate-100">对话</Link>
        <Link to="/skills" className="rounded-lg px-3 py-2 text-sm hover:bg-slate-100">技能</Link>
        {user.is_admin && <Link to="/admin" className="rounded-lg px-3 py-2 text-sm hover:bg-slate-100">管理</Link>}
        <div className="ml-auto text-sm text-slate-500">{user.display_name} · {user.domain}</div>
        <button onClick={logout} className="rounded-lg bg-slate-100 px-3 py-2 text-sm">退出</button>
      </nav>
      {children}
    </div>
  );
}

function RoutesView() {
  const { loading } = useAuth();
  if (loading) return <div className="p-8 text-slate-500">加载认证状态...</div>;
  return (
    <Suspense fallback={<div className="p-8 text-slate-500">加载页面...</div>}>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/" element={<Layout><ChatPage /></Layout>} />
        <Route path="/skills" element={<Layout><SkillsPage /></Layout>} />
        <Route path="/admin" element={<Layout><AdminPage /></Layout>} />
      </Routes>
    </Suspense>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppProviders>
        <RoutesView />
      </AppProviders>
    </BrowserRouter>
  );
}
