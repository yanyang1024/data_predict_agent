import { useEffect, useState } from 'react';
import { apiFetch } from '../services/api';
import type { Skill } from '../types';

export default function SkillsPage() {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [file, setFile] = useState<File | null>(null);
  async function load() {
    setSkills(await apiFetch<Skill[]>('/skills'));
  }
  useEffect(() => {
    void load();
  }, []);
  async function upload() {
    if (!file) return;
    const form = new FormData();
    form.append('upload', file);
    await apiFetch('/skills/upload', { method: 'POST', body: form });
    setFile(null);
    await load();
  }
  return (
    <div className="p-6">
      <div className="rounded-2xl bg-white p-6 shadow-soft">
        <h1 className="text-xl font-bold">文件系统技能</h1>
        <p className="mt-2 text-sm text-slate-500">上传 ZIP，后端会安全解压到当前用户所在域的技能目录，天然兼容 Git 分发。</p>
        <div className="mt-4 flex gap-3">
          <input type="file" accept=".zip" onChange={(e) => setFile(e.target.files?.[0] || null)} />
          <button onClick={() => void upload()} className="rounded-xl bg-slate-900 px-4 py-2 text-white">上传</button>
        </div>
        <div className="mt-6 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {skills.map((s) => (
            <div key={s.id} className="rounded-2xl border border-slate-200 p-4">
              <div className="font-semibold">{s.name}</div>
              <div className="mt-1 text-sm text-slate-500">{s.source} · {s.domain} · v{s.version}</div>
              <pre className="mt-3 max-h-40 overflow-auto rounded-xl bg-slate-50 p-3 text-xs">{JSON.stringify(s.manifest, null, 2)}</pre>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
