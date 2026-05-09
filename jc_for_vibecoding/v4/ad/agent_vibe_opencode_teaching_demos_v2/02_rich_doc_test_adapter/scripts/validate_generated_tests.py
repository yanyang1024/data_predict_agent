#!/usr/bin/env python3
import argparse, json, py_compile, re
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tests', required=True)
    ap.add_argument('--patterns', required=True)
    args = ap.parse_args()
    py_compile.compile(args.tests, doraise=True)
    code = Path(args.tests).read_text(encoding='utf-8')
    payload = json.loads(Path(args.patterns).read_text(encoding='utf-8'))
    for p in payload['patterns']:
        fn = 'test_' + re.sub(r'[^A-Za-z0-9_]+', '_', p['pattern_id']).strip('_')
        if f'def {fn}' not in code:
            raise SystemExit(f'missing function {fn}')
    print('OK Demo02 generated tests are syntactically valid and contain all pattern functions.')
    print('NOTE: Logic correctness still requires human/design owner review.')

if __name__ == '__main__':
    main()
