#!/usr/bin/env python3
import argparse, json
from pathlib import Path

REQUIRED = ['course_dashboard.xlsx', 'gantt_dashboard.html', 'agent_summary.md', 'context_manifest.json']

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', required=True)
    args = ap.parse_args()
    out = Path(args.output)
    missing = [f for f in REQUIRED if not (out / f).exists()]
    ppt_exists = (out / 'course_update.pptx').exists() or (out / 'course_update.pptx.md').exists()
    if not ppt_exists:
        missing.append('course_update.pptx or course_update.pptx.md')
    if missing:
        raise SystemExit('missing outputs: ' + ', '.join(missing))
    manifest = json.loads((out / 'context_manifest.json').read_text(encoding='utf-8'))
    assert 'requires_human_review' in manifest and manifest['requires_human_review']
    print('OK Demo00 outputs validated. Human review is still required for content correctness.')

if __name__ == '__main__':
    main()
