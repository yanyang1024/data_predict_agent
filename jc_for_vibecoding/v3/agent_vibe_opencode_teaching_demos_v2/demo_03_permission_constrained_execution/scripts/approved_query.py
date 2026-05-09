#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = json.loads((ROOT / "configs" / "policy.json").read_text(encoding="utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--window-days", type=int, required=True)
    ap.add_argument("--fields", required=True, help="comma-separated field list")
    ap.add_argument("--output", required=True)
    ap.add_argument("--manifest", required=True)
    args = ap.parse_args()
    if args.dataset not in POLICY["allowed_datasets"]:
        raise SystemExit(f"dataset not allowed: {args.dataset}")
    if args.window_days > POLICY["max_window_days"]:
        raise SystemExit(f"window-days exceeds max: {args.window_days} > {POLICY['max_window_days']}")
    fields = [f.strip() for f in args.fields.split(",") if f.strip()]
    blocked = [f for f in fields if f not in POLICY["allowed_fields"]]
    if blocked:
        raise SystemExit(f"fields not allowed: {blocked}")
    src = ROOT / POLICY["allowed_datasets"][args.dataset]
    rows = list(csv.DictReader(src.open(encoding="utf-8")))
    cutoff = datetime(2026, 5, 9) - timedelta(days=args.window_days)
    filtered = [r for r in rows if datetime.fromisoformat(r["date"]) >= cutoff]
    filtered = filtered[: POLICY["max_rows"]]
    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for r in filtered:
            writer.writerow({f: r[f] for f in fields})
    manifest = {
        "dataset": args.dataset,
        "source": "approved safe export",
        "fields": fields,
        "window_days": args.window_days,
        "row_count": len(filtered),
        "direct_protected_data_access": False,
        "policy_file": "configs/policy.json",
    }
    (ROOT / args.manifest).write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
