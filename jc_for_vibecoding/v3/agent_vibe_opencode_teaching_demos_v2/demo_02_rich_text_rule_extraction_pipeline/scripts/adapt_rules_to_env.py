#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re
from pathlib import Path


def adapt_pattern(pattern: str, env: dict):
    steps = []
    if "RESET_N=0" in pattern:
        steps.append({"op": "set_signal", "name": env["signals"]["RESET_N"], "value": 0})
    if "WAIT 10ns" in pattern:
        steps.append({"op": "wait_ns", "value": 10})
    if "RESET_N=1" in pattern:
        steps.append({"op": "set_signal", "name": env["signals"]["RESET_N"], "value": 1})
    if "WAIT 20ns" in pattern:
        steps.append({"op": "wait_ns", "value": 20})
    if "CHECK READY==1" in pattern:
        steps.append({"op": "check_equal", "name": env["signals"]["READY"], "value": 1})
    if "FOR VDD" in pattern:
        for v in [0.9, 1.0, 1.1]:
            steps.append({"op": "set_param", "name": env["parameters"]["VDD"], "value": v})
            steps.append({"op": env["macros"]["BASIC_OP"]})
            steps.append({"op": "check_equal", "name": env["signals"]["PASS"], "value": 1})
    if "CLK_JITTER=50ps" in pattern:
        steps.append({"op": "set_param", "name": env["parameters"]["CLK_JITTER"], "value": 50})
        steps.append({"op": env["macros"]["BASIC_OP"]})
        steps.append({"op": "check_equal", "name": env["signals"]["ERROR_COUNT"], "value": 0})
    return steps


def render_sequence(ir: dict) -> str:
    lines = [
        "# Auto-generated teaching sequence. Syntax-validated only; logic requires human review.",
        "import sys",
        "from pathlib import Path",
        "sys.path.insert(0, str(Path(__file__).resolve().parents[1]))",
        "from env_package.tiny_validation_env import TinyValidationEnv",
        "",
        "def run(env=None):",
        "    env = env or TinyValidationEnv()",
    ]
    for rule in ir["rules"]:
        lines.append(f"    # Rule: {rule['id']} - {rule['intent']}")
        for s in rule["steps"]:
            if s["op"] == "set_signal": lines.append(f"    env.set_signal({s['name']!r}, {s['value']!r})")
            elif s["op"] == "set_param": lines.append(f"    env.set_param({s['name']!r}, {s['value']!r})")
            elif s["op"] == "wait_ns": lines.append(f"    env.wait_ns({s['value']!r})")
            elif s["op"] == "check_equal": lines.append(f"    env.check_equal({s['name']!r}, {s['value']!r})")
            elif s["op"] == "basic_transaction": lines.append("    env.basic_transaction()")
            else: lines.append(f"    # UNKNOWN OP: {s}")
    lines += ["    return env", "", "if __name__ == '__main__':", "    run()", "    print('sequence syntax and dry run passed')"]
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rules", required=True)
    ap.add_argument("--env", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--ir", required=True)
    args = ap.parse_args()
    rules_doc = json.loads(Path(args.rules).read_text(encoding="utf-8"))
    env = json.loads(Path(args.env).read_text(encoding="utf-8"))
    ir = {"environment": env["environment_name"], "rules": []}
    for r in rules_doc["rules"]:
        ir["rules"].append({"id": r["id"], "intent": r["intent"], "steps": adapt_pattern(r["native_pattern"], env), "review": r["review"]})
    Path(args.ir).write_text(json.dumps(ir, ensure_ascii=False, indent=2), encoding="utf-8")
    Path(args.output).write_text(render_sequence(ir), encoding="utf-8")
    print(json.dumps({"ok": True, "rules": len(ir["rules"]), "output": args.output}, indent=2))

if __name__ == "__main__":
    main()
