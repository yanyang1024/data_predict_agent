import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import { useEffect, useRef } from 'react';
import mermaid from 'mermaid';

function MermaidBlock({ code }: { code: string }) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    let mounted = true;
    mermaid.initialize({ startOnLoad: false, theme: 'default', securityLevel: 'strict' });
    const id = `m-${crypto.randomUUID()}`;
    mermaid.render(id, code).then(({ svg }) => {
      if (mounted && ref.current) ref.current.innerHTML = svg;
    }).catch(() => {
      if (mounted && ref.current) ref.current.textContent = code;
    });
    return () => {
      mounted = false;
    };
  }, [code]);
  return <div ref={ref} className="mermaid rounded-xl bg-white p-3" />;
}

export function MarkdownMessage({ content }: { content: string }) {
  return (
    <div className="prose prose-slate max-w-none">
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkMath]}
        rehypePlugins={[rehypeKatex]}
        components={{
          code(props) {
            const { children, className } = props;
            const match = /language-(\w+)/.exec(className || '');
            const code = String(children).replace(/\n$/, '');
            if (match?.[1] === 'mermaid') return <MermaidBlock code={code} />;
            return <code className={className}>{children}</code>;
          }
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
