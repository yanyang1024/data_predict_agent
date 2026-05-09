#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = json.loads((ROOT / "configs" / "policy.json").read_text(encoding="utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parameter", required=True)
    ap.add_argument("--value", required=True)
    ap.add_argument("--reason", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    if args.parameter not in POLICY["config_parameters_allowed_for_proposal"]:
        raise SystemExit(f"parameter cannot be proposed through this tool: {args.parameter}")
    proposal = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "parameter": args.parameter,
        "proposed_value": args.value,
        "reason": args.reason,
        "direct_config_write": False,
        "requires_owner_approval": True,
        "target_config": "protected_data/production_config.yaml",
    }
    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proposal, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(proposal, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
