#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path


def extract_pdf_text(pdf: Path) -> tuple[str, str]:
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(pdf))
        text = '\n'.join(page.extract_text() or '' for page in reader.pages)
        if text.strip():
            return text, 'pdf'
    except Exception as exc:
        return f'', f'pdf_failed:{exc}'
    return '', 'pdf_empty'


def section(text: str, heading: str) -> str:
    pattern = rf'## {re.escape(heading)}\s*(.*?)(?=\n## |\Z)'
    m = re.search(pattern, text, re.S | re.I)
    return (m.group(1).strip() if m else '')


def bullets(block: str) -> list[str]:
    items = []
    for line in block.splitlines():
        line = line.strip()
        if line.startswith('- '):
            items.append(line[2:].strip())
    return items


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pdf', required=True)
    ap.add_argument('--fallback', required=True)
    ap.add_argument('--output-dir', default='output')
    args = ap.parse_args()
    pdf = Path(args.pdf)
    fallback = Path(args.fallback)
    text, source = extract_pdf_text(pdf)
    if not text.strip() or '## Objective' not in text:
        text = fallback.read_text(encoding='utf-8')
        source = 'fallback_text'
    objective = section(text, 'Objective')
    env = section(text, 'Environment Requirements')
    alg = section(text, 'Algorithm')
    exp = section(text, 'Experiment Logic')
    native = section(text, 'Native Code Instruction')
    limits = section(text, 'Limitations')
    evidence = {
        'source': source,
        'objective': objective.splitlines()[0] if objective else '',
        'environment_requirements': bullets(env),
        'algorithm_steps': [line.strip() for line in alg.splitlines() if line.strip() and not line.startswith('```')],
        'default_parameters': {'window': 4, 'threshold': 2.5},
        'experiment_logic': [line.strip() for line in exp.splitlines() if line.strip()],
        'native_code_instructions': bullets(native),
        'limitations': [line.strip() for line in limits.splitlines() if line.strip()],
        'human_review_items': ['确认 PDF 抽取是否遗漏公式上下文', '确认样例 anomaly index 是否符合论文意图', '确认算法是否适合真实数据']
    }
    if not evidence['objective'] or not evidence['algorithm_steps']:
        raise SystemExit('evidence extraction incomplete: missing objective or algorithm')
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / 'extracted_text.md').write_text(text, encoding='utf-8')
    (out / 'evidence.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding='utf-8')
    manifest = {'generated_at': datetime.now(timezone.utc).isoformat(), 'pdf': args.pdf, 'fallback': args.fallback, 'source_used': source, 'outputs': ['extracted_text.md', 'evidence.json']}
    (out / 'extract_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Extracted evidence using {source}')

if __name__ == '__main__':
    main()
