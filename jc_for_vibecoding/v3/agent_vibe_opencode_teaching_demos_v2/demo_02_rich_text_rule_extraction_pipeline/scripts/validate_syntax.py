#!/usr/bin/env python3
from __future__ import annotations
import argparse, ast, json, py_compile, subprocess, sys
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sequence", required=True)
    ap.add_argument("--ir", required=True)
    ap.add_argument("--manifest", required=True)
    args = ap.parse_args()
    seq = Path(args.sequence)
    ir = json.loads(Path(args.ir).read_text(encoding="utf-8"))
    ast.parse(seq.read_text(encoding="utf-8"))
    py_compile.compile(str(seq), doraise=True)
    proc = subprocess.run([sys.executable, str(seq)], cwd=str(seq.parents[1]), text=True, capture_output=True)
    manifest = {
        "syntax_valid": True,
        "dry_run_exit_code": proc.returncode,
        "dry_run_stdout": proc.stdout.strip(),
        "dry_run_stderr": proc.stderr.strip(),
        "rules_checked": [r["id"] for r in ir["rules"]],
        "logic_correctness_verified": False,
        "human_review_required": [r.get("review") for r in ir["rules"]],
    }
    Path(args.manifest).write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    if proc.returncode != 0:
        raise SystemExit(proc.returncode)

if __name__ == "__main__":
    main()
