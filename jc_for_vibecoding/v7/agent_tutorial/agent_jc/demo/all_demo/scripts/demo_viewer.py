#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import mimetypes
import os
import socket
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote
from urllib.request import urlopen


HOST = '127.0.0.1'

DEMO_CONFIGS = {
    '00_rule_dashboard_agent': {
        'title': 'Demo 00 规则看板 Agent',
        'port': 8760,
        'primary': 'output/dashboard.html',
        'mounts': ['output'],
        'summary': '一句话教学进展 -> 结构化 progress -> HTML dashboard / 讲师报告 / manifest。',
        'steps': [
            '读取 progress 输入和 dashboard schema',
            '调用 generate_dashboard.py 渲染 HTML 与 Markdown',
            '调用 validate_dashboard.py 检查必要区块',
            '启动本地 viewer 服务，暴露 dashboard 链接',
        ],
        'artifacts': [
            ('教学看板', 'output/dashboard.html'),
            ('讲师口播摘要', 'output/status_report.md'),
            ('生成 manifest', 'output/dashboard_manifest.json'),
            ('服务 manifest', 'output/service_manifest.json'),
        ],
        'previews': ['output/dashboard.html', 'output/status_report.md', 'output/dashboard_manifest.json'],
    },
    '01_doc_spec_portability': {
        'title': 'Demo 01 Web App 跨框架迁移 Agent',
        'port': 8761,
        'primary': 'output/migration_report.md',
        'mounts': ['output', 'generated'],
        'summary': 'Gradio CSV 分析应用 + 用户迁移要求 + 前端风格规范 -> Flask 项目 -> 标准/边界 CSV 与静态风格验证。',
        'steps': [
            '读取用户迁移要求、功能文档、迁移规范、前端风格规范和 Gradio 源实现',
            '调用 port_gradio_to_flask.py 生成 generated/flask_app/',
            '调用 validate_flask_port.py 运行标准路径、边界 CSV 行为验证和静态风格验证',
            '启动本地 viewer 服务，暴露迁移报告、Flask 项目代码、可视化迁移图和验证 manifest',
        ],
        'artifacts': [
            ('迁移报告', 'output/migration_report.md'),
            ('迁移图', 'output/framework_migration_map.svg'),
            ('Flask app', 'generated/flask_app/app.py'),
            ('Jinja 模板', 'generated/flask_app/templates/index.html'),
            ('样式文件', 'generated/flask_app/static/styles.css'),
            ('项目 README', 'generated/flask_app/README.md'),
            ('验证 manifest', 'output/validation_manifest.json'),
            ('服务 manifest', 'output/service_manifest.json'),
        ],
        'previews': ['output/framework_migration_map.svg', 'output/migration_report.md', 'output/validation_manifest.json', 'generated/flask_app/app.py'],
    },
    '02_pdf_reproduction_agent': {
        'title': 'Demo 02 PDF 证据抽取与复现 Agent',
        'port': 8762,
        'primary': 'output/design_brief.md',
        'mounts': ['output', 'repro_project'],
        'summary': 'PDF / fallback text -> evidence.json -> design brief -> 最小复现项目 -> unittest 验证。',
        'steps': [
            '调用 extract_pdf_evidence.py 抽取结构化证据',
            '调用 build_repro_project.py 生成最小复现项目',
            '调用 validate_repro_project.py 编译并运行样例测试',
            '启动本地 viewer 服务，暴露 evidence、设计摘要、生成项目和验证结果',
        ],
        'artifacts': [
            ('证据 JSON', 'output/evidence.json'),
            ('设计摘要', 'output/design_brief.md'),
            ('抽取 manifest', 'output/extract_manifest.json'),
            ('验证 manifest', 'output/validation_manifest.json'),
            ('复现项目 README', 'repro_project/README.md'),
            ('生成代码', 'repro_project/src/adaptive_window.py'),
            ('服务 manifest', 'output/service_manifest.json'),
        ],
        'previews': ['output/design_brief.md', 'output/evidence.json', 'output/validation_manifest.json', 'repro_project/src/adaptive_window.py'],
    },
    '03_permission_sandbox_agent': {
        'title': 'Demo 03 权限沙箱与受控数据服务 Agent',
        'port': 8763,
        'primary': 'output/lot_qtime_chart.svg',
        'mounts': ['output'],
        'summary': '配置变更和 lot history 查询都通过受控脚本/API 输出，不暴露 protected 原始数据。',
        'steps': [
            '调用 propose_config_patch.py 生成 sandbox proposal',
            '调用 apply_patch_to_sandbox.py 写入 sandbox 输出',
            '调用 query_lot_history_service.py 返回聚合 QTime / UT 摘要和 SVG 图',
            '调用验证脚本检查字段白名单、审计日志和 protected hash',
            '启动本地 viewer 服务，只暴露 output 目录中的审计产物',
        ],
        'artifacts': [
            ('QTime / UT 图', 'output/lot_qtime_chart.svg'),
            ('lot history 聚合摘要', 'output/lot_history_summary.json'),
            ('配置 proposal', 'output/proposal_001.json'),
            ('sandbox 配置结果', 'output/sandbox_config_after.json'),
            ('配置验证 manifest', 'output/validation_manifest.json'),
            ('数据服务验证 manifest', 'output/data_service_manifest.json'),
            ('审计日志', 'output/audit_log.jsonl'),
            ('服务 manifest', 'output/service_manifest.json'),
        ],
        'previews': ['output/lot_qtime_chart.svg', 'output/lot_history_summary.json', 'output/data_service_manifest.json', 'output/proposal_001.json'],
    },
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def infer_demo(root: Path, explicit: str | None) -> str:
    if explicit:
        return explicit
    name = root.resolve().name
    if name not in DEMO_CONFIGS:
        raise SystemExit(f'Cannot infer demo from {root}; pass --demo explicitly.')
    return name


def read_text_if_exists(root: Path, relative: str, limit: int = 12000) -> str:
    path = root / relative
    if not path.exists() or not path.is_file():
        return ''
    text = path.read_text(encoding='utf-8', errors='replace')
    if len(text) > limit:
        return text[:limit] + '\n... truncated for viewer ...\n'
    return text


def load_json_if_exists(root: Path, relative: str) -> dict:
    path = root / relative
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return {}


def status_cards(root: Path, demo: str) -> list[tuple[str, str, str]]:
    cards: list[tuple[str, str, str]] = []
    if demo == '00_rule_dashboard_agent':
        manifest = load_json_if_exists(root, 'output/dashboard_manifest.json')
        cards.append(('Dashboard', 'passed' if (root / 'output/dashboard.html').exists() else 'missing', f"{manifest.get('demo_count', 0)} demos"))
        cards.append(('Report', 'ready' if (root / 'output/status_report.md').exists() else 'missing', '讲师口播摘要'))
    elif demo == '01_doc_spec_portability':
        manifest = load_json_if_exists(root, 'output/validation_manifest.json')
        state = 'passed' if manifest.get('validated') else 'missing'
        style_ok = all(manifest.get('style_checks', {}).values()) if manifest else False
        cards.append(('CSV cases', state, f"{manifest.get('case_count', 0)} case(s)"))
        cards.append(('UI style', 'passed' if style_ok else 'missing', 'style spec checks'))
        cards.append(('Flask project', 'ready' if (root / 'generated/flask_app/app.py').exists() else 'missing', 'generated/flask_app'))
    elif demo == '02_pdf_reproduction_agent':
        extract = load_json_if_exists(root, 'output/extract_manifest.json')
        validation = load_json_if_exists(root, 'output/validation_manifest.json')
        cards.append(('Evidence source', extract.get('source_used', 'unknown'), 'PDF fallback allowed'))
        cards.append(('Unittest', 'passed' if validation.get('py_compile') else 'missing', 'syntax + sample tests'))
    elif demo == '03_permission_sandbox_agent':
        config = load_json_if_exists(root, 'output/validation_manifest.json')
        data = load_json_if_exists(root, 'output/data_service_manifest.json')
        cards.append(('Config patch', config.get('status', 'missing'), 'sandbox only'))
        cards.append(('Data service', data.get('status', 'missing'), 'field allowlist'))
    return cards


def url_path(relative: str) -> str:
    return '/' + relative.replace(os.sep, '/')


def display_path(relative: str) -> str:
    parts = Path(relative).parts
    if len(parts) <= 2:
        return relative
    return '/'.join(parts[-2:])


def primary_for(root: Path, demo: str) -> str:
    configured = DEMO_CONFIGS[demo]['primary']
    if (root / configured).exists():
        return configured
    return 'output/viewer.html'


def render_preview(root: Path, relative: str) -> str:
    path = root / relative
    if not path.exists():
        return f'<section class="preview missing"><h3>{html.escape(relative)}</h3><p>文件尚未生成。</p></section>'
    escaped = html.escape(relative)
    if path.suffix.lower() in {'.html', '.svg'}:
        return (
            f'<section class="preview"><h3>{escaped}</h3>'
            f'<iframe src="{html.escape(url_path(relative))}" title="{escaped}"></iframe></section>'
        )
    text = read_text_if_exists(root, relative)
    return f'<section class="preview"><h3>{escaped}</h3><pre>{html.escape(text)}</pre></section>'


def render_result_visual(root: Path, demo: str) -> str:
    if demo == '00_rule_dashboard_agent':
        data = load_json_if_exists(root, 'data/sample_progress.json')
        total = int(data.get('total_minutes', 60) or 60)
        current = int(data.get('current_minute', 0) or 0)
        demos = data.get('demos', [])
        status_color = {
            'completed': '#137333',
            'in_progress': '#b45309',
            'not_started': '#94a3b8',
            'blocked': '#a50e0e',
        }
        bars = []
        for index, item in enumerate(demos):
            start = int(item.get('planned_start', 0) or 0)
            minutes = int(item.get('planned_minutes', 1) or 1)
            x = 72 + (start / total) * 760
            width = max(24, (minutes / total) * 760)
            color = status_color.get(item.get('status'), '#64748b')
            label = html.escape(f"{item.get('id', '')} {item.get('name', '')}")
            bars.append(
                f"<rect x='{x:.1f}' y='{56 + index * 38}' width='{width:.1f}' height='22' rx='6' fill='{color}'/>"
                f"<text x='24' y='{72 + index * 38}' fill='#1f2937' font-size='12'>{label}</text>"
            )
        current_x = 72 + (current / total) * 760
        svg = (
            "<svg viewBox='0 0 900 230' class='mini-viz' role='img' aria-label='demo timeline'>"
            "<rect width='900' height='230' fill='#ffffff'/>"
            "<text x='24' y='30' font-size='18' font-weight='700' fill='#1f2937'>60 分钟教学进度</text>"
            "<line x1='72' y1='196' x2='832' y2='196' stroke='#d8dee9'/>"
            f"<line x1='{current_x:.1f}' y1='42' x2='{current_x:.1f}' y2='202' stroke='#0f766e' stroke-width='2'/>"
            f"<text x='{current_x + 6:.1f}' y='52' fill='#0f766e' font-size='12'>当前 {current} min</text>"
            + ''.join(bars) +
            "</svg>"
        )
        return f"<section class='visual-panel'><h2>可视化结果</h2>{svg}</section>"

    if demo == '01_doc_spec_portability':
        manifest = load_json_if_exists(root, 'output/validation_manifest.json')
        runtime = 'Flask runtime checked' if manifest.get('flask_runtime_checked') else 'Static + helper checks'
        visual = 'output/framework_migration_map.svg'
        if (root / visual).exists():
            graphic = f"<iframe class='mini-viz-frame' src='{html.escape(url_path(visual))}' title='framework migration map'></iframe>"
        else:
            graphic = (
                "<svg viewBox='0 0 900 180' class='mini-viz'><rect width='900' height='180' fill='#fff'/>"
                "<text x='32' y='92' font-size='18' fill='#1f2937'>Gradio -> Flask migration map will appear after generation.</text></svg>"
            )
        chips = (
            "<div class='visual-chips'>"
            f"<span>{html.escape(str(manifest.get('case_count', 0)))} CSV cases</span>"
            f"<span>{html.escape(runtime)}</span>"
            "<span>same CSV workflow</span><span>same UI style spec</span>"
            "</div>"
        )
        return f"<section class='visual-panel'><h2>可视化结果</h2>{graphic}{chips}</section>"

    if demo == '02_pdf_reproduction_agent':
        evidence = load_json_if_exists(root, 'output/evidence.json')
        validation = load_json_if_exists(root, 'output/validation_manifest.json')
        window = evidence.get('default_parameters', {}).get('window', 4)
        threshold = evidence.get('default_parameters', {}).get('threshold', 2.5)
        test_state = 'passed' if validation.get('py_compile') else 'pending'
        svg = f"""
<svg viewBox='0 0 900 220' class='mini-viz' role='img' aria-label='paper reproduction flow'>
  <rect width='900' height='220' fill='#ffffff'/>
  <defs><marker id='arrow02' markerWidth='10' markerHeight='10' refX='8' refY='3' orient='auto'><path d='M0,0 L0,6 L9,3 z' fill='#64748b'/></marker></defs>
  <g font-family='-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif'>
    <rect x='36' y='58' width='170' height='92' rx='8' fill='#f8fafc' stroke='#d8dee9'/>
    <text x='58' y='92' font-size='16' font-weight='700' fill='#1f2937'>PDF Text</text>
    <text x='58' y='120' font-size='12' fill='#64748b'>fallback evidence</text>
    <line x1='216' y1='104' x2='300' y2='104' stroke='#64748b' stroke-width='2' marker-end='url(#arrow02)'/>
    <rect x='312' y='58' width='170' height='92' rx='8' fill='#f8fafc' stroke='#d8dee9'/>
    <text x='334' y='92' font-size='16' font-weight='700' fill='#1f2937'>Evidence</text>
    <text x='334' y='120' font-size='12' fill='#64748b'>window {html.escape(str(window))}, threshold {html.escape(str(threshold))}</text>
    <line x1='492' y1='104' x2='576' y2='104' stroke='#64748b' stroke-width='2' marker-end='url(#arrow02)'/>
    <rect x='588' y='58' width='170' height='92' rx='8' fill='#f8fafc' stroke='#d8dee9'/>
    <text x='610' y='92' font-size='16' font-weight='700' fill='#1f2937'>Repro Project</text>
    <text x='610' y='120' font-size='12' fill='#64748b'>unittest {html.escape(test_state)}</text>
    <rect x='318' y='176' width='264' height='24' rx='8' fill='#0f766e'/>
    <text x='450' y='193' text-anchor='middle' font-size='12' font-weight='700' fill='#ffffff'>证据抽取 -> 代码生成 -> 样例验证</text>
  </g>
</svg>
"""
        return f"<section class='visual-panel'><h2>可视化结果</h2>{svg}</section>"

    if demo == '03_permission_sandbox_agent':
        summary = load_json_if_exists(root, 'output/lot_history_summary.json')
        data = load_json_if_exists(root, 'output/data_service_manifest.json')
        protected_ok = all(item.get('unchanged') for item in data.get('protected_files', {}).values()) if data else False
        chart = 'output/lot_qtime_chart.svg'
        chart_html = ''
        if (root / chart).exists():
            chart_html = f"<iframe class='mini-viz-frame short' src='{html.escape(url_path(chart))}' title='lot qtime chart'></iframe>"
        svg = f"""
<svg viewBox='0 0 900 210' class='mini-viz' role='img' aria-label='permission boundary'>
  <rect width='900' height='210' fill='#ffffff'/>
  <g font-family='-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif'>
    <rect x='38' y='54' width='220' height='102' rx='8' fill='#fef2f2' stroke='#fecaca'/>
    <text x='62' y='90' font-size='16' font-weight='700' fill='#7f1d1d'>Protected</text>
    <text x='62' y='118' font-size='12' fill='#7f1d1d'>raw data and prod config</text>
    <rect x='340' y='54' width='220' height='102' rx='8' fill='#ecfeff' stroke='#a5f3fc'/>
    <text x='364' y='90' font-size='16' font-weight='700' fill='#155e75'>Data Service</text>
    <text x='364' y='118' font-size='12' fill='#155e75'>allowlist + audit log</text>
    <rect x='642' y='54' width='220' height='102' rx='8' fill='#f0fdf4' stroke='#bbf7d0'/>
    <text x='666' y='90' font-size='16' font-weight='700' fill='#14532d'>Safe Output</text>
    <text x='666' y='118' font-size='12' fill='#14532d'>LOT {html.escape(str(summary.get('lot_id', 'unknown')))} / UT {html.escape(str(summary.get('utilization', '')))}</text>
    <line x1='258' y1='105' x2='340' y2='105' stroke='#64748b' stroke-width='2' stroke-dasharray='6 6'/>
    <line x1='560' y1='105' x2='642' y2='105' stroke='#64748b' stroke-width='2'/>
    <text x='450' y='184' text-anchor='middle' font-size='13' font-weight='700' fill='#0f766e'>protected unchanged: {html.escape(str(protected_ok).lower())}</text>
  </g>
</svg>
"""
        return f"<section class='visual-panel'><h2>可视化结果</h2>{svg}{chart_html}</section>"
    return ''


def write_viewer(root: Path, demo: str, port: int | None = None) -> Path:
    cfg = DEMO_CONFIGS[demo]
    out = root / 'output'
    out.mkdir(parents=True, exist_ok=True)
    primary = primary_for(root, demo)
    cards = ''.join(
        f'<article><b>{html.escape(title)}</b><span>{html.escape(state)}</span><small>{html.escape(detail)}</small></article>'
        for title, state, detail in status_cards(root, demo)
    )
    steps = ''.join(f'<li>{html.escape(step)}</li>' for step in cfg['steps'])
    artifact_links = []
    for label, relative in cfg['artifacts']:
        path = root / relative
        state = 'ready' if path.exists() else 'missing'
        short = display_path(relative)
        artifact_links.append(
            f'<li><a href="{html.escape(url_path(relative))}">{html.escape(label)}</a>'
            f'<code title="{html.escape(relative)}">{html.escape(short)}</code><span class="{state}">{state}</span></li>'
        )
    visual = render_result_visual(root, demo)
    previews = ''.join(render_preview(root, relative) for relative in cfg['previews'])
    link_hint = ''
    if port:
        link_hint = (
            f'<p class="links"><a href="http://{HOST}:{port}/">Viewer</a>'
            f'<a href="http://{HOST}:{port}{html.escape(url_path(primary))}">Primary artifact</a></p>'
        )
    css = '''
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;margin:0;color:#202124;background:#f8fafc;line-height:1.55}
header{background:#111827;color:white;padding:24px 32px}
main{padding:24px 32px;max-width:1180px;margin:auto}
h1{margin:0 0 8px;font-size:28px}
h2{margin-top:28px}
.summary{max-width:900px;color:#d1d5db}
.links a{display:inline-block;margin-right:12px;color:white;font-weight:700}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin:18px 0}
.cards article{background:white;border:1px solid #e5e7eb;border-radius:8px;padding:14px}
.cards b,.cards span,.cards small{display:block}
.cards span{font-size:22px;font-weight:700;margin:6px 0}
.visual-panel{background:white;border:1px solid #e5e7eb;border-radius:8px;margin:20px 0;padding:16px}
.visual-panel h2{margin:0 0 12px}
.mini-viz{width:100%;height:auto;display:block;border:1px solid #eef2f7;border-radius:8px}
.mini-viz-frame{width:100%;height:290px;border:1px solid #eef2f7;border-radius:8px;background:white}
.mini-viz-frame.short{height:260px;margin-top:12px}
.visual-chips{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}
.visual-chips span{background:#ecfeff;color:#155e75;border:1px solid #a5f3fc;border-radius:8px;padding:6px 9px;font-size:12px;font-weight:700}
ol{background:white;border:1px solid #e5e7eb;border-radius:8px;padding:18px 18px 18px 42px}
.artifacts{background:white;border:1px solid #e5e7eb;border-radius:8px;padding:8px 18px}
.artifacts li{display:grid;grid-template-columns:minmax(140px,180px) minmax(120px,1fr) 80px;gap:12px;padding:8px 0;border-bottom:1px solid #f1f5f9}
.artifacts li:last-child{border-bottom:0}
code{font-family:"SFMono-Regular",Consolas,monospace;font-size:12px;color:#475569}
.ready,.passed{color:#137333;font-weight:700}.missing{color:#a50e0e;font-weight:700}
.preview{background:white;border:1px solid #e5e7eb;border-radius:8px;margin:16px 0;overflow:hidden}
.preview h3{font-size:15px;margin:0;padding:10px 14px;background:#eef2ff;border-bottom:1px solid #e5e7eb}
iframe{width:100%;height:520px;border:0;background:white}
pre{margin:0;padding:14px;white-space:pre-wrap;overflow:auto;max-height:520px;font-size:13px;background:#0f172a;color:#e5e7eb}
footer{padding:20px 32px;color:#64748b}
'''
    body = f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{html.escape(cfg['title'])}</title>
  <style>{css}</style>
</head>
<body>
  <header>
    <h1>{html.escape(cfg['title'])}</h1>
    <p class="summary">{html.escape(cfg['summary'])}</p>
    {link_hint}
  </header>
  <main>
    <h2>执行状态</h2>
    <section class="cards">{cards}</section>
    {visual}
    <h2>执行过程</h2>
    <ol>{steps}</ol>
    <h2>产物链接</h2>
    <ul class="artifacts">{''.join(artifact_links)}</ul>
    <h2>效果预览</h2>
    {previews}
  </main>
  <footer>Generated at {html.escape(utc_now())}. Viewer 只暴露演示产物目录，不暴露 protected 原始材料。</footer>
</body>
</html>
'''
    path = out / 'viewer.html'
    path.write_text(body, encoding='utf-8')
    return path


def pid_cmdline(pid: int) -> str:
    proc = Path('/proc') / str(pid) / 'cmdline'
    if not proc.exists():
        return ''
    return proc.read_text(encoding='utf-8', errors='ignore').replace('\x00', ' ')


def stop_previous(root: Path) -> None:
    manifest = root / 'output/service_manifest.json'
    if not manifest.exists():
        return
    try:
        data = json.loads(manifest.read_text(encoding='utf-8'))
        pid = int(data.get('pid', 0))
    except Exception:
        return
    if pid <= 0:
        return
    cmdline = pid_cmdline(pid)
    if 'demo_viewer.py' not in cmdline:
        return
    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    for _ in range(20):
        time.sleep(0.05)
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return


def port_is_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        return sock.connect_ex((HOST, port)) != 0


def choose_port(preferred: int) -> int:
    for port in range(preferred, preferred + 50):
        if port_is_free(port):
            return port
    raise SystemExit(f'No free port found near {preferred}.')


def wait_until_ready(port: int) -> bool:
    url = f'http://{HOST}:{port}/healthz'
    for _ in range(30):
        try:
            with urlopen(url, timeout=0.2) as resp:
                return resp.status == 200
        except Exception:
            time.sleep(0.1)
    return False


def write_service_manifest(root: Path, demo: str, port: int, pid: int, ready: bool) -> dict:
    cfg = DEMO_CONFIGS[demo]
    primary = primary_for(root, demo)
    manifest = {
        'demo': demo,
        'title': cfg['title'],
        'host': HOST,
        'port': port,
        'pid': pid,
        'ready': ready,
        'url': f'http://{HOST}:{port}/',
        'primary_url': f'http://{HOST}:{port}{url_path(primary)}',
        'viewer_path': 'output/viewer.html',
        'allowed_mounts': cfg['mounts'],
        'started_at': utc_now(),
        'note': 'Viewer only serves generated demo artifacts. protected/ and policy/ are not mounted.',
    }
    path = root / 'output/service_manifest.json'
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    write_viewer(root, demo, port)
    return manifest


def start_server(root: Path, demo: str, preferred_port: int, restart: bool) -> dict:
    if restart:
        stop_previous(root)
    port = choose_port(preferred_port)
    write_viewer(root, demo, port)
    log = root / 'output/viewer_server.log'
    log_fh = log.open('a', encoding='utf-8')
    script = Path(__file__).resolve()
    proc = subprocess.Popen(
        [sys.executable, str(script), '--serve', '--root', str(root), '--demo', demo, '--port', str(port)],
        stdout=log_fh,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    ready = wait_until_ready(port)
    manifest = write_service_manifest(root, demo, port, proc.pid, ready)
    print(f'Viewer URL: {manifest["url"]}')
    print(f'Primary URL: {manifest["primary_url"]}')
    print(f'Service manifest: {root / "output/service_manifest.json"}')
    return manifest


def is_allowed(relative: str, mounts: list[str]) -> bool:
    parts = Path(relative).parts
    if not parts:
        return False
    if any(part.startswith('.') for part in parts):
        return False
    if parts[0] in {'protected', 'policy', 'schemas', 'papers', 'env_pkg', 'data', 'references'}:
        return False
    return parts[0] in mounts


class DemoHandler(BaseHTTPRequestHandler):
    root: Path
    demo: str

    def log_message(self, fmt: str, *args: object) -> None:
        print(f'{self.address_string()} - {fmt % args}')

    def send_text(self, status: int, body: str, content_type: str = 'text/plain; charset=utf-8') -> None:
        data = body.encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        cfg = DEMO_CONFIGS[self.demo]
        raw_path = unquote(self.path.split('?', 1)[0])
        if raw_path == '/healthz':
            self.send_text(200, 'ok')
            return
        if raw_path in {'/', ''}:
            relative = 'output/viewer.html'
        else:
            relative = raw_path.lstrip('/')
        relative = os.path.normpath(relative).replace('\\', '/')
        if relative.startswith('../') or relative == '..' or not is_allowed(relative, cfg['mounts']):
            self.send_text(403, 'Forbidden')
            return
        target = (self.root / relative).resolve()
        try:
            target.relative_to(self.root.resolve())
        except ValueError:
            self.send_text(403, 'Forbidden')
            return
        if not target.exists() or not target.is_file():
            self.send_text(404, 'Not found')
            return
        content_type = mimetypes.guess_type(str(target))[0] or 'application/octet-stream'
        if target.suffix.lower() in {'.md', '.py', '.mjs', '.json', '.jsonl', '.txt'}:
            content_type = 'text/plain; charset=utf-8'
        if relative.startswith('generated/') and target.suffix.lower() in {'.html', '.css'}:
            content_type = 'text/plain; charset=utf-8'
        data = target.read_bytes()
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def serve(root: Path, demo: str, port: int) -> None:
    write_viewer(root, demo, port)
    handler = type('ConfiguredDemoHandler', (DemoHandler,), {'root': root.resolve(), 'demo': demo})
    server = ThreadingHTTPServer((HOST, port), handler)
    print(f'Serving {demo} at http://{HOST}:{port}/ from {root}', flush=True)
    server.serve_forever()


def main() -> None:
    parser = argparse.ArgumentParser(description='Create and serve a browser viewer for demo artifacts.')
    parser.add_argument('--root', default='.')
    parser.add_argument('--demo')
    parser.add_argument('--port', type=int)
    parser.add_argument('--restart', action='store_true')
    parser.add_argument('--write-only', action='store_true')
    parser.add_argument('--serve', action='store_true')
    args = parser.parse_args()

    root = Path(args.root).resolve()
    demo = infer_demo(root, args.demo)
    cfg = DEMO_CONFIGS[demo]
    port = args.port or int(cfg['port'])

    if args.serve:
        serve(root, demo, port)
        return
    if args.write_only:
        path = write_viewer(root, demo, port)
        print(f'Wrote {path}')
        return
    start_server(root, demo, port, restart=args.restart)


if __name__ == '__main__':
    main()
