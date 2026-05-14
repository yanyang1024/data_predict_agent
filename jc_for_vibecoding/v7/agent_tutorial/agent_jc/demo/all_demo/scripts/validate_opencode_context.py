#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEMOS = [p for p in ROOT.iterdir() if p.is_dir() and re.match(r'^\d\d_', p.name)]
NAME_RE = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')
errors: list[str] = []

if not (ROOT / 'scripts' / 'demo_viewer.py').exists():
    errors.append('root: missing scripts/demo_viewer.py')

for demo in DEMOS:
    for required in ['README.md', 'AGENTS.md', 'opencode.json', 'run_demo.py']:
        if not (demo / required).exists():
            errors.append(f'{demo.name}: missing {required}')
    try:
        json.loads((demo / 'opencode.json').read_text(encoding='utf-8'))
    except Exception as exc:
        errors.append(f'{demo.name}: invalid opencode.json: {exc}')
    run_demo_text = (demo / 'run_demo.py').read_text(encoding='utf-8') if (demo / 'run_demo.py').exists() else ''
    if 'demo_viewer.py' not in run_demo_text:
        errors.append(f'{demo.name}: run_demo.py does not start demo viewer')
    opencode_text = (demo / 'opencode.json').read_text(encoding='utf-8') if (demo / 'opencode.json').exists() else ''
    if 'demo_viewer.py' not in opencode_text:
        errors.append(f'{demo.name}: opencode.json does not allow demo viewer script')
    skill_root = demo / '.opencode' / 'skills'
    if not skill_root.exists():
        errors.append(f'{demo.name}: missing .opencode/skills')
        continue
    skills = [p for p in skill_root.iterdir() if p.is_dir()]
    if not skills:
        errors.append(f'{demo.name}: no skill directories')
    for skill in skills:
        skill_md = skill / 'SKILL.md'
        if not skill_md.exists():
            errors.append(f'{demo.name}: {skill.name} missing SKILL.md')
            continue
        text = skill_md.read_text(encoding='utf-8')
        if not text.startswith('---'):
            errors.append(f'{demo.name}: {skill.name} SKILL.md missing frontmatter')
            continue
        fm = text.split('---', 2)[1]
        fields = {}
        for line in fm.splitlines():
            if ':' in line:
                k, v = line.split(':', 1)
                fields[k.strip()] = v.strip().strip('"')
        name = fields.get('name')
        desc = fields.get('description')
        if name != skill.name:
            errors.append(f'{demo.name}: skill name {name!r} does not match directory {skill.name!r}')
        if not name or not NAME_RE.match(name):
            errors.append(f'{demo.name}: invalid skill name {name!r}')
        if not desc or len(desc) > 1024:
            errors.append(f'{demo.name}: invalid description for {skill.name}')
    command_root = demo / '.opencode' / 'commands'
    if not command_root.exists() or not list(command_root.glob('*.md')):
        errors.append(f'{demo.name}: missing command markdown')
    tool_root = demo / '.opencode' / 'tools'
    if not tool_root.exists() or not list(tool_root.glob('*.ts')):
        errors.append(f'{demo.name}: missing custom tool examples')

if errors:
    print('Context validation failed:')
    for e in errors:
        print('-', e)
    raise SystemExit(1)
print(f'Context validation passed for {len(DEMOS)} demos.')
