#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import py_compile
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def remove_bytecode_cache(project: Path) -> int:
    removed = 0
    for pyc in project.rglob('*.pyc'):
        pyc.unlink()
        removed += 1
    for cache_dir in sorted(project.rglob('__pycache__'), reverse=True):
        try:
            cache_dir.rmdir()
            removed += 1
        except OSError:
            pass
    return removed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--project-dir', required=True)
    args = ap.parse_args()
    project = Path(args.project_dir)
    target = project / 'src' / 'adaptive_window.py'
    if not target.exists():
        raise SystemExit('missing generated adaptive_window.py')
    py_compile.compile(str(target), doraise=True)
    env = dict(os.environ)
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    proc = subprocess.run(['python3', '-m', 'unittest', 'discover', '-s', 'tests'], cwd=project, text=True, capture_output=True, env=env)
    if proc.returncode != 0:
        print(proc.stdout)
        print(proc.stderr)
        raise SystemExit(proc.returncode)
    removed_cache_entries = remove_bytecode_cache(project)
    manifest = {
        'validated_at': datetime.now(timezone.utc).isoformat(),
        'project_dir': str(project),
        'py_compile': True,
        'unittest_stdout': proc.stdout,
        'unittest_stderr': proc.stderr,
        'removed_cache_entries': removed_cache_entries,
        'limits': ['syntax and sample tests only', 'logic correctness requires human review']
    }
    out = Path('output')
    out.mkdir(exist_ok=True)
    (out / 'validation_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Reproduction project validation passed.')

if __name__ == '__main__':
    main()
