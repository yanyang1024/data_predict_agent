#!/usr/bin/env python3
import argparse, subprocess
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--impl', required=True)
    ap.add_argument('--cases', required=True)
    args = ap.parse_args()
    impl = Path(args.impl)
    test = impl.with_name('rule_engine.test.js')
    if not impl.exists():
        raise SystemExit(f'missing {impl}')
    if not test.exists():
        raise SystemExit(f'missing {test}')
    result = subprocess.run(['node', str(test)], text=True, capture_output=True)
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)
        raise SystemExit(result.returncode)
    print(result.stdout.strip())
    print('OK Demo01 validation passed. Business semantics still require human review.')

if __name__ == '__main__':
    main()
