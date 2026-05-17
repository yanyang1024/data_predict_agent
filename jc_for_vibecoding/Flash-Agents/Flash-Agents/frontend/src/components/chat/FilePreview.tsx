import { useEffect, useRef, useState } from 'react';
import { API_BASE, getToken } from '../../services/api';

function rawUrl(conversationId: string, path: string) {
  return `${API_BASE}/files/${conversationId}/raw?path=${encodeURIComponent(path)}&token=${encodeURIComponent(getToken() || '')}`;
}

export function FilePreview({ conversationId, path }: { conversationId: string; path: string }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [message, setMessage] = useState('');
  const ext = path.split('.').pop()?.toLowerCase();

  useEffect(() => {
    if (ext !== 'pdf') return;
    let cancelled = false;
    async function renderPdf() {
      setMessage('正在渲染 PDF 首页...');
      const pdfjs = await import('pdfjs-dist');
      pdfjs.GlobalWorkerOptions.workerSrc = new URL('pdfjs-dist/build/pdf.worker.mjs', import.meta.url).toString();
      const doc = await pdfjs.getDocument(rawUrl(conversationId, path)).promise;
      const page = await doc.getPage(1);
      const viewport = page.getViewport({ scale: 1.2 });
      const canvas = canvasRef.current;
      if (!canvas || cancelled) return;
      canvas.width = viewport.width;
      canvas.height = viewport.height;
      const ctx = canvas.getContext('2d');
      if (!ctx) return;
      await page.render({ canvasContext: ctx, viewport }).promise;
      if (!cancelled) setMessage(`PDF · ${doc.numPages} 页`);
    }
    renderPdf().catch((err) => setMessage(`PDF 预览失败：${String(err)}`));
    return () => {
      cancelled = true;
    };
  }, [conversationId, ext, path]);

  if (ext === 'pdf') {
    return (
      <div className="mt-3 rounded-xl border border-slate-200 bg-white p-3">
        <div className="mb-2 text-xs text-slate-500">{message}</div>
        <canvas ref={canvasRef} className="max-h-96 max-w-full rounded-lg border" />
      </div>
    );
  }

  if (ext === 'ppt' || ext === 'pptx') {
    return (
      <div className="mt-3 rounded-xl border border-slate-200 bg-white p-3 text-sm text-slate-600">
        PPT/PPTX 文件已就绪。生产环境可在这里接入 pptxviewjs 或企业文档预览 CDN。
        <a className="ml-2 text-blue-600 underline" href={rawUrl(conversationId, path)} target="_blank" rel="noreferrer">打开原文件</a>
      </div>
    );
  }

  return null;
}
