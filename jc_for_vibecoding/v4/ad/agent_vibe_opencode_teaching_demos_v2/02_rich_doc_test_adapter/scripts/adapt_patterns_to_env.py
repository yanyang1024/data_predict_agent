#!/usr/bin/env python3
import argparse, json, re
from pathlib import Path


def adapt_directive(directive: str):
    steps = []
    unsupported = []
    for part in [p.strip() for p in directive.split(';') if p.strip()]:
        if part.startswith('legacy_reset'):
            steps.append('env.reset(cycles=1)')
        elif part.startswith('wait_cycles'):
            m = re.search(r'\((\d+)\)', part); cycles = m.group(1) if m else '1'
            steps.append(f'env.wait_cycles({cycles})')
        elif part.startswith('assert_ready'):
            steps.append("env.expect_signal('ready', 1)")
        elif part.startswith('write_reg'):
            m = re.search(r'\(([^,]+),\s*([^\)]+)\)', part)
            if m: steps.append(f'env.write_reg({m.group(1)}, {m.group(2)})')
            else: unsupported.append(part)
        elif part.startswith('read_reg'):
            m = re.search(r'\(([^\)]+)\)', part)
            if m: steps.append(f'actual = env.read_reg({m.group(1)})')
            else: unsupported.append(part)
        elif part.startswith('assert_eq'):
            m = re.search(r'\(([^\)]+)\)', part)
            if m: steps.append(f'env.assert_equal(actual, {m.group(1)})')
            else: unsupported.append(part)
        elif part.startswith('inject_clock_jitter'):
            m = re.search(r'\((\d+)\)', part); ppm = m.group(1) if m else '0'
            steps.append(f'env.clock_jitter({ppm})')
        elif part.startswith('assert_no_error'):
            steps.append("env.expect_signal('error', 0)")
        else:
            unsupported.append(part)
    return steps, unsupported


def safe_name(x: str) -> str:
    return re.sub(r'[^A-Za-z0-9_]+', '_', x).strip('_')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--patterns', required=True)
    ap.add_argument('--env', required=True)
    ap.add_argument('--output', required=True)
    ap.add_argument('--review', required=True)
    args = ap.parse_args()
    payload = json.loads(Path(args.patterns).read_text(encoding='utf-8'))
    env_contract = json.loads(Path(args.env).read_text(encoding='utf-8'))
    lines = [
        '# Auto-generated teaching demo tests. Human review required for verification semantics.',
        'class DemoEnvProtocol:',
        '    pass',
        ''
    ]
    review = ['# Review Packet\n', '## 自动生成说明\n', '以下代码通过文档抽取和环境包适配生成。语法可自动检查，验证逻辑必须人工确认。\n', '## 人工确认点\n']
    all_unsupported = []
    for p in payload['patterns']:
        steps, unsupported = adapt_directive(p['native_directive'])
        all_unsupported.extend(unsupported)
        fn = 'test_' + safe_name(p['pattern_id'])
        lines.append(f'def {fn}(env):')
        lines.append(f'    """{p["intent"]} Expected: {p["expected"]}"""')
        if not steps:
            lines.append('    raise NotImplementedError("no mapped steps")')
        else:
            for st in steps:
                lines.append('    ' + st)
        lines.append('')
        review.append(f"- {p['pattern_id']}: {p['review_note']}")
    if all_unsupported:
        review.append('\n## Unsupported Directives')
        review.extend(f'- {x}' for x in all_unsupported)
    review.append('\n## 自动验证不覆盖')
    review.append('- 时序逻辑是否符合真实设计。')
    review.append('- 阈值是否来自正式规范。')
    review.append('- 环境包 API 的语义是否与旧指令完全一致。')

    out = Path(args.output); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text('\n'.join(lines), encoding='utf-8')
    Path(args.review).write_text('\n'.join(review) + '\n', encoding='utf-8')
    print('generated tests ->', out)
    print('review packet ->', args.review)

if __name__ == '__main__':
    main()
