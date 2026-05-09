#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path


def run_python(impl: Path, order: dict) -> dict:
    proc = subprocess.run([sys.executable, str(impl)], input=json.dumps(order), text=True, capture_output=True, check=True)
    return json.loads(proc.stdout)


def run_node(impl: Path, order: dict) -> dict:
    proc = subprocess.run(["node", str(impl)], input=json.dumps(order), text=True, capture_output=True, check=True)
    return json.loads(proc.stdout)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", required=True)
    ap.add_argument("--python-impl", required=True)
    ap.add_argument("--node-impl", required=True)
    ap.add_argument("--report", required=True)
    args = ap.parse_args()
    cases = json.loads(Path(args.cases).read_text(encoding="utf-8"))
    rows = []
    failed = []
    for case in cases:
        py = run_python(Path(args.python_impl), case["order"])
        node = run_node(Path(args.node_impl), case["order"])
        expected = case["expected_final_total"]
        ok = py["final_total"] == node["final_total"] == expected
        rows.append((case["name"], py["final_total"], node["final_total"], expected, ok))
        if not ok:
            failed.append(case["name"])
    lines = ["# Portability Validation Report", "", "| Case | Python | Node | Expected | Pass |", "|---|---:|---:|---:|---|"]
    for name, pyv, nodev, exp, ok in rows:
        lines.append(f"| {name} | {pyv} | {nodev} | {exp} | {'yes' if ok else 'no'} |")
    lines += ["", "## Human Review", "", "Golden cases check cross-platform consistency. Spec owner still needs to confirm business semantics and ambiguity handling."]
    Path(args.report).write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"ok": not failed, "failed": failed, "report": args.report}, indent=2))
    if failed:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
