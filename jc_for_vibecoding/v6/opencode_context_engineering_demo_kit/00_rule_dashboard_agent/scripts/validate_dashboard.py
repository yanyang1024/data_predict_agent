#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output-dir', default='output')
    args = ap.parse_args()
    out = Path(args.output_dir)
    required = ['dashboard.html', 'status_report.md', 'dashboard_manifest.json']
    missing = [name for name in required if not (out / name).exists()]
    if missing:
        raise SystemExit(f'Missing output files: {missing}')
    html = (out / 'dashboard.html').read_text(encoding='utf-8')
    for token in ['教学甘特图', '用户问题', '当前焦点', '00', '01', '02', '03']:
        if token not in html:
            raise SystemExit(f'dashboard.html missing token: {token}')
    manifest = json.loads((out / 'dashboard_manifest.json').read_text(encoding='utf-8'))
    if manifest.get('demo_count') != 4:
        raise SystemExit('manifest demo_count must be 4')
    print('Dashboard validation passed.')

if __name__ == '__main__':
    main()
