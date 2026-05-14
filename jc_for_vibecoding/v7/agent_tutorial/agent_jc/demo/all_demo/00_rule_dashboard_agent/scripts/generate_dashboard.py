#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
from datetime import datetime, timezone
from pathlib import Path

STATUS_LABEL = {
    'completed': '已完成',
    'in_progress': '进行中',
    'not_started': '未开始',
    'blocked': '阻塞',
}

STATUS_CLASS = {
    'completed': 'done',
    'in_progress': 'doing',
    'not_started': 'todo',
    'blocked': 'blocked',
}


def pct(value: float) -> str:
    return f'{max(0, min(100, value)):.1f}%'


def render_html(data: dict) -> str:
    total = float(data.get('total_minutes', 60))
    current = float(data.get('current_minute', 0))
    demos = data.get('demos', [])
    rows = []
    cards = []
    for d in demos:
        demo_id = html.escape(d['id'])
        left = pct(float(d['planned_start']) / total * 100)
        width = pct(float(d['planned_minutes']) / total * 100)
        cls = STATUS_CLASS.get(d.get('status'), 'todo')
        status = STATUS_LABEL.get(d.get('status'), d.get('status', 'unknown'))
        name = html.escape(d['name'])
        note = html.escape(d.get('actual_note', ''))
        rows.append(f'<div class="gantt-row"><div class="gantt-label">{demo_id} {name}</div><div class="gantt-track"><div class="bar {cls}" style="left:{left};width:{width}">{status}</div></div></div>')
        cards.append(f'<article class="card {cls}"><h3>{demo_id} {name}</h3><p><b>状态：</b>{status}</p><p>{note}</p></article>')
    risks = ''.join(f'<li>{html.escape(x)}</li>' for x in data.get('risks', []))
    actions = ''.join(f'<li>{html.escape(x)}</li>' for x in data.get('next_actions', []))
    current_marker = pct(current / total * 100)
    generated_at = datetime.now(timezone.utc).isoformat()
    title = html.escape(data.get('title', '教学看板'))
    speaker = html.escape(data.get('speaker', ''))
    focus = html.escape(data.get('current_focus', ''))
    question = html.escape(data.get('user_question', ''))
    css = (
        'body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 32px; line-height: 1.55; color: #202124; }'
        'header { border-bottom: 2px solid #ddd; padding-bottom: 12px; margin-bottom: 24px; }'
        '.badge { display:inline-block; padding:4px 10px; border-radius:14px; background:#f1f3f4; margin-right:8px; }'
        '.gantt { margin: 20px 0; position: relative; }'
        '.gantt-row { display:flex; align-items:center; margin: 10px 0; }'
        '.gantt-label { width: 220px; font-weight: 600; }'
        '.gantt-track { position: relative; height: 34px; flex: 1; background: #f1f3f4; border-radius: 6px; overflow: hidden; }'
        '.bar { position: absolute; top: 0; bottom: 0; border-radius: 6px; text-align:center; line-height:34px; font-size: 13px; }'
        '.done { background: #dff3e4; } .doing { background: #fff3cd; } .todo { background: #e8f0fe; } .blocked { background: #fce8e6; }'
        f'.now {{ position:absolute; left:{current_marker}; top:0; bottom:0; border-left:3px solid #444; }}'
        '.cards { display:grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; }'
        '.card { border:1px solid #ddd; border-radius:10px; padding:12px; }'
        'footer { margin-top: 32px; font-size: 12px; color:#666; }'
    )
    parts = [
        '<!doctype html>', '<html lang="zh-CN">', '<head>', '<meta charset="utf-8" />',
        f'<title>{title}</title>', f'<style>{css}</style>', '</head>', '<body>',
        '<header>', f'<h1>{title}</h1>',
        f'<span class="badge">总时长：{total:.0f} min</span>',
        f'<span class="badge">当前：{current:.0f} min</span>',
        f'<span class="badge">讲师：{speaker}</span>', '</header>',
        '<section><h2>教学甘特图</h2>', f'<div class="gantt"><div class="now"></div>{"".join(rows)}</div></section>',
        f'<section class="cards">{"".join(cards)}</section>',
        f'<section><h2>当前焦点</h2><p>{focus}</p></section>',
        f'<section><h2>用户问题</h2><blockquote>{question}</blockquote></section>',
        f'<section><h2>风险</h2><ul>{risks}</ul></section>',
        f'<section><h2>下一步</h2><ol>{actions}</ol></section>',
        f'<footer>Generated at {generated_at}. 本看板为教学演示产物，需要讲师确认内容准确性。</footer>',
        '</body>', '</html>'
    ]
    return '\n'.join(parts)


def render_markdown(data: dict) -> str:
    lines = [f"# {data.get('title', '教学看板')}", '', f"当前进度：{data.get('current_minute', 0)} / {data.get('total_minutes', 60)} 分钟", '', '## Demo 状态']
    for d in data.get('demos', []):
        lines.append(f"- {d['id']} {d['name']}：{STATUS_LABEL.get(d.get('status'), d.get('status'))}。{d.get('actual_note', '')}")
    lines += ['', '## 当前焦点', data.get('current_focus', ''), '', '## 用户问题', data.get('user_question', ''), '', '## 风险']
    lines += [f'- {x}' for x in data.get('risks', [])]
    lines += ['', '## 下一步'] + [f'- {x}' for x in data.get('next_actions', [])]
    lines += ['', '> 注意：本报告只说明教学状态，实际内容需要讲师确认。']
    return '\n'.join(lines) + '\n'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    ap.add_argument('--output-dir', default='output')
    args = ap.parse_args()
    data = json.loads(Path(args.input).read_text(encoding='utf-8'))
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / 'dashboard.html').write_text(render_html(data), encoding='utf-8')
    (out / 'status_report.md').write_text(render_markdown(data), encoding='utf-8')
    manifest = {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'input': args.input,
        'outputs': ['dashboard.html', 'status_report.md'],
        'total_minutes': data.get('total_minutes'),
        'demo_count': len(data.get('demos', [])),
        'validation_hint': 'run scripts/validate_dashboard.py --output-dir output'
    }
    (out / 'dashboard_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Generated dashboard files in {out}')

if __name__ == '__main__':
    main()
