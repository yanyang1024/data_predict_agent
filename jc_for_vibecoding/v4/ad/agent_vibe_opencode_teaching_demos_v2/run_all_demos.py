#!/usr/bin/env python3
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def run(demo, cmd):
    print('\n===', demo, '===')
    r = subprocess.run(cmd, cwd=ROOT / demo, text=True, capture_output=True)
    print(r.stdout)
    if r.returncode != 0:
        print(r.stderr)
        raise SystemExit(r.returncode)

run('00_rule_based_document_generation', ['python3','scripts/build_course_assets.py','--status','inputs/course_status.json','--request','inputs/one_sentence_request.txt','--output','output'])
run('00_rule_based_document_generation', ['python3','scripts/validate_outputs.py','--output','output'])

run('01_doc_spec_portability', ['python3','scripts/extract_spec_contract.py','--spec','docs/ticket_priority_spec.md','--output','output/spec_contract.json'])
run('01_doc_spec_portability', ['python3','scripts/port_to_platform_b.py','--contract','output/spec_contract.json','--output','output/platform_b'])
run('01_doc_spec_portability', ['python3','scripts/validate_port.py','--impl','output/platform_b/rule_engine.js','--cases','tests/platform_b_cases.json'])

run('02_rich_doc_test_adapter', ['python3','scripts/extract_rich_doc_patterns.py','--doc','docs/rich_test_spec_export.html','--rules','references/extraction_rules.md','--output','output/extracted_patterns.json'])
run('02_rich_doc_test_adapter', ['python3','scripts/adapt_patterns_to_env.py','--patterns','output/extracted_patterns.json','--env','env_package/target_env_contract.json','--output','output/generated_tests.py','--review','output/review_packet.md'])
run('02_rich_doc_test_adapter', ['python3','scripts/validate_generated_tests.py','--tests','output/generated_tests.py','--patterns','output/extracted_patterns.json'])

run('03_permission_bound_workflow', ['python3','scripts/validate_guardrails.py'])

print('\nAll teaching demos completed successfully.')
