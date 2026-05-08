#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(cmd):
    print('>', ' '.join(cmd))
    subprocess.run(cmd, cwd=ROOT, check=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default='docs/verification_guide.html')
    args = parser.parse_args()
    run([sys.executable, 'scripts/01_extract_patterns.py', '--input', args.input])
    run([sys.executable, 'scripts/02_adapt_patterns.py'])
    run([sys.executable, 'scripts/03_generate_code.py'])
    run([sys.executable, 'scripts/04_validate_syntax.py'])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
