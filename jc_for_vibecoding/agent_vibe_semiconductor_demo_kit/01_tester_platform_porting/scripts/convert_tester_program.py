#!/usr/bin/env python3
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src/A_program/main.cpp'
PAT = ROOT / 'src/A_program/pattern_a.pat'
MAP = ROOT / 'configs/platform_mapping.json'
OUT_DIR = ROOT / 'output'
CAND = OUT_DIR / 'B_program_candidate'

CALL_RE = re.compile(r'(?P<prefix>\s*)(?P<lhs>(?:AResult\s+\w+\s*=\s*)?)(?P<fn>a_[a-zA-Z0-9_]+)\((?P<args>.*)\);')


def split_args(args):
    # Good enough for this synthetic demo: no nested commas.
    return [a.strip() for a in args.split(',')] if args.strip() else []


def convert_cpp():
    mapping = json.loads(MAP.read_text(encoding='utf-8'))['api_map']
    lines = SRC.read_text(encoding='utf-8').splitlines()
    out = ['#include "tester_b.hpp"', '', 'void basic_function_check(BSession& b) {']
    report = []
    unsupported = []

    for line in lines:
        m = CALL_RE.match(line)
        if not m:
            if line.strip().startswith('#include') or line.strip().startswith('void basic_function_check') or line.strip() == '}':
                continue
            if line.strip().startswith('//') or line.strip() == '':
                out.append(line)
            continue
        fn = m.group('fn')
        args = m.group('args')
        info = mapping.get(fn, {'status': 'unsupported', 'review_reason': 'No mapping entry'})
        status = info['status']
        if status == 'unsupported':
            out.append(f'    // TODO HUMAN REVIEW: unsupported source call: {line.strip()}')
            unsupported.append([fn, info.get('review_reason', 'unsupported'), line.strip()])
            report.append(f'- UNSUPPORTED `{fn}`: {info.get("review_reason", "unsupported")}.')
            continue

        expr = info['b_expr']
        if fn == 'a_wait_us':
            arg0 = split_args(args)[0]
            converted = expr.replace('{arg0}', arg0)
        else:
            converted = expr.replace('{args}', args)

        if fn == 'a_load_pattern':
            converted = converted.replace('pattern_a.pat', 'pattern_b_generated.pat')
        if fn == 'a_run_pattern':
            converted = 'BRunResult result = ' + converted
        if fn == 'a_log_value':
            converted = converted.replace('result.pass_count', 'result.passed')

        review_note = ''
        if status == 'needs_review':
            review_note = ' // NEEDS REVIEW: confirm platform B voltage semantics'
            report.append(f'- NEEDS REVIEW `{fn}` -> `{converted}`. {info.get("review_reason", "")}'.strip())
        else:
            report.append(f'- {status.upper()} `{fn}` -> `{converted}` using {info.get("manual_source", "mapping file")}.')
        out.append('    ' + converted + ';' + review_note)

    out.append('}')
    CAND.mkdir(parents=True, exist_ok=True)
    (CAND / 'main.cpp').write_text('\n'.join(out) + '\n', encoding='utf-8')

    with (OUT_DIR / 'unsupported_functions.csv').open('w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['source_function', 'reason', 'source_line'])
        w.writerows(unsupported)

    report_text = '# Conversion Report\n\n' + '\n'.join(report) + '\n\n## Human Validation Checklist\n\n'
    report_text += '- Confirm voltage limits and power rail naming.\n'
    report_text += '- Confirm timing set equivalence.\n'
    report_text += '- Confirm binning configuration in platform B flow setup.\n'
    report_text += '- Compile candidate code against platform B SDK.\n'
    report_text += '- Run generated pattern in offline parser before tester execution.\n'
    (OUT_DIR / 'conversion_report.md').write_text(report_text, encoding='utf-8')


def convert_pattern():
    cfg = json.loads(MAP.read_text(encoding='utf-8'))['pattern_map']
    text = PAT.read_text(encoding='utf-8')
    for src, dst in cfg.items():
        text = re.sub(r'\b' + re.escape(src) + r'\b', dst, text)
    (CAND / 'pattern_b_generated.pat').write_text(text, encoding='utf-8')


def main():
    OUT_DIR.mkdir(exist_ok=True)
    convert_cpp()
    convert_pattern()
    print(f'Wrote {CAND / "main.cpp"}')
    print(f'Wrote {CAND / "pattern_b_generated.pat"}')
    print(f'Wrote {OUT_DIR / "conversion_report.md"}')


if __name__ == '__main__':
    main()
