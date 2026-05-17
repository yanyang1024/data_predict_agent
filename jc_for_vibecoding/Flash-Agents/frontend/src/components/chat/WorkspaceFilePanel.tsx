import { useEffect, useState } from 'react';
import { apiFetch } from '../../services/api';
import type { WorkspaceFile } from '../../types';
import { FilePreview } from './FilePreview';

export function WorkspaceFilePanel({ conversationId }: { conversationId?: string }) {
  const [files, setFiles] = useState<WorkspaceFile[]>([]);
  const [selected, setSelected] = useState<{ path: string; content: string; encoding: string } | null>(null);

  useEffect(() => {
    if (!conversationId) return;
    void apiFetch<WorkspaceFile[]>(`/files/${conversationId}`).then(setFiles).catch(() => setFiles([]));
  }, [conversationId]);

  async function open(file: WorkspaceFile) {
    if (file.type === 'dir' || !conversationId) return;
    const ext = file.path.split('.').pop()?.toLowerCase();
    if (ext === 'pdf' || ext === 'ppt' || ext === 'pptx') {
      setSelected({ path: file.path, content: '二进制文件，请使用上方预览或下载原文件。', encoding: 'binary' });
      return;
    }
    const data = await apiFetch<{ path: string; content: string; encoding: string }>(`/files/${conversationId}/read?path=${encodeURIComponent(file.path)}`);
    setSelected(data);
  }

  return (
    <aside className="rounded-2xl bg-white p-4 shadow-soft">
      <h3 className="font-semibold">工作区文件</h3>
      {!conversationId && <p className="mt-3 text-sm text-slate-500">首条消息发送后才会绑定工作区。</p>}
      <div className="mt-3 max-h-52 space-y-1 overflow-auto text-sm">
        {files.map((f) => (
          <button key={f.path} onClick={() => void open(f)} className="block w-full rounded-lg px-2 py-1 text-left hover:bg-slate-100">
            {f.type === 'dir' ? '📁' : '📄'} {f.path}
          </button>
        ))}
      </div>
      {selected && (
        <>
        <FilePreview conversationId={conversationId!} path={selected.path} />
        <div className="mt-3 rounded-xl bg-slate-900 p-3 text-xs text-slate-100">
          <div className="mb-2 text-slate-400">{selected.path} · {selected.encoding}</div>
          <pre className="max-h-64 overflow-auto whitespace-pre-wrap">{selected.content}</pre>
        </div>
        </>
      )}
    </aside>
  );
}
