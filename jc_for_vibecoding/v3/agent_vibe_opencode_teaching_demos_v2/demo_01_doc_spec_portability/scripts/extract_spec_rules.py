#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re
from pathlib import Path
import yaml


def extract_yaml_block(text: str) -> dict:
    match = re.search(r"```yaml\n(.*?)\n```", text, re.S)
    if not match:
        raise ValueError("No YAML rules block found in spec")
    return yaml.safe_load(match.group(1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--report", required=True)
    args = ap.parse_args()
    text = Path(args.spec).read_text(encoding="utf-8")
    raw = extract_yaml_block(text)
    rules = raw["rules"]
    normalized = {
        "schema_version": "pricing-rules-v1",
        "source_spec": args.spec,
        "rules": rules,
        "human_review_required": [
            "Confirm negative quantity behavior.",
            "Confirm whether discounts are additive or sequential.",
            "Confirm whether bankers rounding matches downstream platforms."
        ],
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(normalized, ensure_ascii=False, indent=2), encoding="utf-8")
    report = "# Spec Extraction Report\n\n" + \
        f"- Source spec: `{args.spec}`\n" + \
        "- Extracted normalized schema: `pricing-rules-v1`\n" + \
        "- Human review required for ambiguity log.\n"
    Path(args.report).write_text(report, encoding="utf-8")
    print(json.dumps({"ok": True, "output": args.output, "report": args.report}, indent=2))

if __name__ == "__main__":
    main()
