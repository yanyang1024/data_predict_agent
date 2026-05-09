#!/usr/bin/env python3
import argparse, json
from pathlib import Path


def cond_to_js(cond: str) -> str:
    cond = cond.strip()
    if cond == 'default':
        return 'true'
    cond = cond.replace('AND', '&&')
    cond = cond.replace('outage == true', 'outage === true')
    cond = cond.replace('severity == high', 'severity === "high"')
    cond = cond.replace('customer_tier == enterprise', 'customerTier === "enterprise"')
    cond = cond.replace('age_hours >= 72', 'ageHours >= 72')
    return cond


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--contract', required=True)
    ap.add_argument('--output', required=True)
    args = ap.parse_args()
    contract = json.loads(Path(args.contract).read_text(encoding='utf-8'))
    out = Path(args.output); out.mkdir(parents=True, exist_ok=True)

    lines = [
        '// Auto-generated teaching demo code. Human review required for business semantics.',
        'function classify(ticket) {',
        '  ticket = ticket || {};',
        '  const outage = Boolean(ticket.outage || false);',
        '  const severity = String(ticket.severity || "low").toLowerCase();',
        '  const customerTier = String(ticket.customer_tier || "standard").toLowerCase();',
        '  const ageHours = Number(ticket.age_hours || 0);',
        ''
    ]
    for rule in contract['rules']:
        js_cond = cond_to_js(rule['condition'])
        lines.append(f"  // {rule['rule_id']}: {rule['note']}")
        lines.append(f"  if ({js_cond}) return {{ priority: '{rule['priority']}', route: '{rule['route']}', sla_hours: {rule['sla_hours']} }};")
    lines.extend(['}', '', 'module.exports = { classify };', ''])
    (out / 'rule_engine.js').write_text('\n'.join(lines), encoding='utf-8')

    test = """const assert = require('assert');\nconst { classify } = require('./rule_engine');\nconst cases = require('../../tests/platform_b_cases.json');\nfor (const c of cases) {\n  assert.deepStrictEqual(classify(c.ticket), c.expected, c.name);\n}\nconsole.log('OK platform B cases passed:', cases.length);\n"""
    (out / 'rule_engine.test.js').write_text(test, encoding='utf-8')

    report = '# 可移植性报告\n\n'
    report += '## 自动生成内容\n\n- rule_engine.js\n- rule_engine.test.js\n\n'
    report += '## 自动验证范围\n\n- JavaScript 语法由 Node.js 执行验证。\n- 样例测试验证当前规则表的 happy path 和少量边界。\n\n'
    report += '## 人工确认点\n\n' + ''.join(f"- {x}\n" for x in contract['human_review_required'])
    (out.parent / 'portability_report.md').write_text(report, encoding='utf-8')
    print('generated platform B implementation in', out)

if __name__ == '__main__':
    main()
