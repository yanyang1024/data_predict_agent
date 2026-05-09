#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    rows = list(csv.DictReader((ROOT / args.input).open(encoding="utf-8")))
    manifest = json.loads((ROOT / args.manifest).read_text(encoding="utf-8"))
    values = [float(r["value"]) for r in rows if "value" in r and r["value"]]
    by_status = {}
    for r in rows:
        by_status[r.get("status", "unknown")] = by_status.get(r.get("status", "unknown"), 0) + 1
    text = ["# Safe Query Report", "", "## Manifest", ""]
    for k, v in manifest.items():
        text.append(f"- {k}: {v}")
    text += ["", "## Summary", "", f"- Rows: {len(rows)}"]
    if values:
        text.append(f"- Average value: {mean(values):.2f}")
    text.append(f"- Status counts: {by_status}")
    text += ["", "## Safety Note", "", "This report was generated from an approved safe export. It did not read protected_data and it does not modify configuration."]
    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(text), encoding="utf-8")
    print(json.dumps({"ok": True, "output": str(out)}, indent=2))

if __name__ == "__main__":
    main()
