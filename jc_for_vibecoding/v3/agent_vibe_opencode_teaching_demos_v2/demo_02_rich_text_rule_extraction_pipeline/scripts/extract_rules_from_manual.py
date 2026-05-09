#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re
from pathlib import Path
from pypdf import PdfReader

RULE_IDS = ["RESET_STABILITY", "VOLTAGE_SWEEP", "JITTER_TOLERANCE"]

FALLBACK = {
    "RESET_STABILITY": {
        "intent": "Verify reset release stability",
        "native_pattern": "SET RESET_N=0; WAIT 10ns; SET RESET_N=1; WAIT 20ns; CHECK READY==1",
        "expected_evidence": "READY becomes 1 after reset release",
        "review": "Human must confirm reset polarity",
    },
    "VOLTAGE_SWEEP": {
        "intent": "Validate operation across voltage range",
        "native_pattern": "FOR VDD IN [0.9, 1.0, 1.1]: SET VDD; RUN BASIC_OP; CHECK PASS==1",
        "expected_evidence": "PASS remains 1",
        "review": "Human must confirm allowed voltage range",
    },
    "JITTER_TOLERANCE": {
        "intent": "Validate clock jitter tolerance",
        "native_pattern": "SET CLK_JITTER=50ps; RUN BASIC_OP; CHECK ERROR_COUNT==0",
        "expected_evidence": "ERROR_COUNT remains zero",
        "review": "Human must confirm jitter model",
    },
}


def read_text(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    return path.read_text(encoding="utf-8")


def extract_rules(text: str):
    # This extractor is intentionally conservative for teaching.
    # It confirms the rule IDs exist in the text, then uses a deterministic pattern library.
    rules = []
    missing = []
    for rid in RULE_IDS:
        if rid in text:
            rules.append({"id": rid, **FALLBACK[rid]})
        else:
            missing.append(rid)
    return rules, missing


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--review", required=True)
    args = ap.parse_args()
    text = read_text(Path(args.input))
    rules, missing = extract_rules(text)
    out = {"source": args.input, "rules": rules, "missing_rule_ids": missing, "human_review_required": True}
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    review_lines = ["# Human Review Points", ""]
    for r in rules:
        review_lines.append(f"- {r['id']}: {r['review']}")
    for m in missing:
        review_lines.append(f"- Missing rule ID: {m}")
    Path(args.review).write_text("\n".join(review_lines), encoding="utf-8")
    print(json.dumps({"ok": True, "rules": len(rules), "missing": missing}, indent=2))

if __name__ == "__main__":
    main()
