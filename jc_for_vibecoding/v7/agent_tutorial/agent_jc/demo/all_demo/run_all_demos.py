#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

DEMOS = [
    '00_rule_dashboard_agent',
    '01_doc_spec_portability',
    '02_pdf_reproduction_agent',
    '03_permission_sandbox_agent',
]

DEMO_TITLES = {
    '00_rule_dashboard_agent': ('00', '规则看板', '一句话进展 -> dashboard'),
    '01_doc_spec_portability': ('01', 'Gradio -> Flask', 'CSV 分析 App 跨框架迁移'),
    '02_pdf_reproduction_agent': ('02', 'PDF 复现', 'evidence -> project -> validation'),
    '03_permission_sandbox_agent': ('03', '权限沙箱', 'Data Service + protected boundary'),
}


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return {}


def selected_lines(stdout: str) -> list[str]:
    keep = []
    markers = [
        'validation passed',
        'Flask port validation passed',
        'Reproduction project validation passed',
        'Config patch validation passed',
        'Data service validation passed',
        'Demo ',
    ]
    for line in stdout.splitlines():
        if any(marker in line for marker in markers):
            keep.append(line)
    return keep[-5:]


def visual_for(demo: str, service: dict) -> str:
    base = service.get('url', '')
    if demo == '00_rule_dashboard_agent':
        return "<div class='bar'><span style='width:30%'></span></div><small>教学进度与四个 demo 状态</small>"
    if demo == '01_doc_spec_portability':
        return f"<img src='{html.escape(base)}output/framework_migration_map.svg' alt='framework migration map' />"
    if demo == '02_pdf_reproduction_agent':
        return (
            "<svg viewBox='0 0 360 120' role='img' aria-label='reproduction flow'>"
            "<rect width='360' height='120' fill='#ffffff'/>"
            "<text x='28' y='38' font-size='15' font-weight='700' fill='#1f2937'>PDF</text>"
            "<text x='148' y='38' font-size='15' font-weight='700' fill='#1f2937'>Evidence</text>"
            "<text x='278' y='38' font-size='15' font-weight='700' fill='#1f2937'>Tests</text>"
            "<line x1='66' y1='34' x2='132' y2='34' stroke='#64748b'/>"
            "<line x1='218' y1='34' x2='268' y2='34' stroke='#64748b'/>"
            "<rect x='26' y='62' width='308' height='18' rx='8' fill='#0f766e'/>"
            "</svg>"
        )
    if demo == '03_permission_sandbox_agent':
        return f"<img src='{html.escape(base)}output/lot_qtime_chart.svg' alt='lot qtime chart' />"
    return ''


def write_gallery(root: Path, services: dict[str, dict]) -> Path:
    out = root / 'output'
    out.mkdir(exist_ok=True)
    cards = []
    for demo in DEMOS:
        code, title, summary = DEMO_TITLES[demo]
        service = services.get(demo, {})
        url = service.get('url', '#')
        primary = service.get('primary_url', '#')
        ready = 'ready' if service.get('ready') else 'check'
        cards.append(f"""
        <article>
          <div class='top'><b>{html.escape(code)}</b><span>{html.escape(ready)}</span></div>
          <h2>{html.escape(title)}</h2>
          <p>{html.escape(summary)}</p>
          <div class='visual'>{visual_for(demo, service)}</div>
          <p class='links'><a href='{html.escape(url)}'>Viewer</a><a href='{html.escape(primary)}'>Primary</a></p>
        </article>
        """)
    page = f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>OpenCode Demo Gallery</title>
  <style>
    body{{margin:0;background:#f6f8fb;color:#1f2937;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.5}}
    main{{max-width:1180px;margin:0 auto;padding:28px}}
    header{{display:flex;align-items:end;justify-content:space-between;gap:16px;margin-bottom:18px}}
    h1{{margin:0;font-size:30px}} p{{color:#64748b}}
    .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:14px}}
    article{{background:#fff;border:1px solid #d8dee9;border-radius:8px;padding:16px}}
    .top{{display:flex;justify-content:space-between;color:#0f766e;font-weight:700}}
    h2{{margin:10px 0 6px;font-size:20px}}
    .visual{{height:150px;border:1px solid #edf2f7;border-radius:8px;background:#fff;display:flex;align-items:center;justify-content:center;overflow:hidden}}
    .visual img,.visual svg{{width:100%;height:100%;object-fit:contain}}
    .bar{{width:82%;height:18px;background:#e5e7eb;border-radius:8px;overflow:hidden}} .bar span{{display:block;height:18px;background:#0f766e}}
    .links a{{display:inline-block;margin-right:8px;padding:7px 10px;border-radius:8px;background:#0f766e;color:#fff;text-decoration:none;font-weight:700}}
    footer{{margin-top:18px;color:#64748b;font-size:12px}}
  </style>
</head>
<body>
  <main>
    <header>
      <div><h1>OpenCode Demo Gallery</h1><p>四个 demo 的可视化入口，减少长链接堆叠。</p></div>
      <small>{html.escape(datetime.now(timezone.utc).isoformat())}</small>
    </header>
    <section class='grid'>{''.join(cards)}</section>
    <footer>Viewer 服务仍分别运行在 8760-8763；本页只做总览和跳转。</footer>
  </main>
</body>
</html>
"""
    path = out / 'demo_gallery.html'
    path.write_text(page, encoding='utf-8')
    return path


def write_alignment_report(root: Path, services: dict[str, dict]) -> Path:
    out = root / 'output'
    out.mkdir(exist_ok=True)
    demo00 = load_json(root / '00_rule_dashboard_agent/output/dashboard_manifest.json')
    demo01 = load_json(root / '01_doc_spec_portability/output/validation_manifest.json')
    demo02 = load_json(root / '02_pdf_reproduction_agent/output/validation_manifest.json')
    demo03_config = load_json(root / '03_permission_sandbox_agent/output/validation_manifest.json')
    demo03_data = load_json(root / '03_permission_sandbox_agent/output/data_service_manifest.json')
    protected_ok = all(
        item.get('unchanged')
        for item in demo03_data.get('protected_files', {}).values()
    ) if demo03_data else False
    rows = [
        (
            '00',
            '一句话进展 -> 规则化 dashboard、状态报告、manifest、viewer',
            f"{demo00.get('demo_count', 0)} demos, viewer={services.get('00_rule_dashboard_agent', {}).get('ready')}",
            '通过' if demo00.get('demo_count') == 4 and services.get('00_rule_dashboard_agent', {}).get('ready') else '待检查',
        ),
        (
            '01',
            'Gradio CSV 分析 App -> Flask 项目，保持功能和前端风格',
            f"{demo01.get('case_count', 0)} CSV cases, style={all(demo01.get('style_checks', {}).values()) if demo01 else False}",
            '通过' if demo01.get('validated') and demo01.get('case_count', 0) >= 4 else '待检查',
        ),
        (
            '02',
            'PDF evidence -> 设计摘要 -> 复现项目 -> 样例测试',
            f"py_compile={demo02.get('py_compile')}, removed_cache={demo02.get('removed_cache_entries')}",
            '通过' if demo02.get('py_compile') else '待检查',
        ),
        (
            '03',
            '配置和 lot 查询通过受控脚本/API，不暴露 protected 原始数据',
            f"config={demo03_config.get('status')}, data={demo03_data.get('status')}, protected_ok={protected_ok}",
            '通过' if demo03_config.get('status') == 'passed' and demo03_data.get('status') == 'passed' and protected_ok else '待检查',
        ),
    ]
    lines = [
        '# Demo Alignment Report',
        '',
        f'Generated at: {datetime.now(timezone.utc).isoformat()}',
        '',
        '| Demo | 教学文档要求 | 实现证据 | 状态 |',
        '|---|---|---|---|',
    ]
    lines.extend(
        f'| {code} | {requirement} | {evidence} | {status} |'
        for code, requirement, evidence, status in rows
    )
    lines += [
        '',
        '## 未覆盖风险',
        '',
        '- Demo 00：dashboard 内容仍需讲师确认。',
        '- Demo 01：CSV cases 覆盖标准和边界样例，不覆盖生产上传安全、混合编码、超大文件和复杂图表。',
        '- Demo 02：样例测试通过不代表论文科学结论被完整复现。',
        '- Demo 03：字段白名单和 hash 校验通过不代表真实业务口径或审批流程完整。',
        '',
        '## 展示入口',
        '',
        '- Gallery: `output/demo_gallery.html`',
        '- Demo 00: `http://127.0.0.1:8760/`',
        '- Demo 01: `http://127.0.0.1:8761/`',
        '- Demo 02: `http://127.0.0.1:8762/`',
        '- Demo 03: `http://127.0.0.1:8763/`',
        '',
    ]
    path = out / 'demo_alignment_report.md'
    path.write_text('\n'.join(lines), encoding='utf-8')
    return path


root = Path(__file__).resolve().parent
failures = []
services: dict[str, dict] = {}
for demo in DEMOS:
    print(f'\n=== Running {demo} ===', flush=True)
    demo_dir = root / demo
    if not demo_dir.exists():
        print(f'Missing demo directory: {demo_dir}', flush=True)
        failures.append(demo)
        continue
    proc = subprocess.run(['python3', 'run_demo.py'], cwd=demo_dir, text=True, capture_output=True)
    if proc.returncode != 0:
        print(proc.stdout, end='')
        print(proc.stderr, end='')
        failures.append(demo)
    else:
        for line in selected_lines(proc.stdout):
            print(line, flush=True)
        services[demo] = load_json(demo_dir / 'output/service_manifest.json')

print('\n=== Validating OpenCode context files ===', flush=True)
proc = subprocess.run(['python3', 'scripts/validate_opencode_context.py'], cwd=root, text=True)
if proc.returncode != 0:
    failures.append('context-validation')

if failures:
    print('FAILED:', ', '.join(failures))
    raise SystemExit(1)

gallery = write_gallery(root, services)
alignment = write_alignment_report(root, services)
print('\n=== Demo viewer summary ===')
for demo in DEMOS:
    code, title, _ = DEMO_TITLES[demo]
    service = services.get(demo, {})
    print(f'{code} {title}: {service.get("url", "(missing)")}')
print(f'Gallery: {gallery}')
print(f'Alignment report: {alignment}')
print('\nAll demos completed successfully.')
