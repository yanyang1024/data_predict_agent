# Teaching guide

## Goal

Use the demos to teach a repeatable agentic coding pattern:

```text
rules + inputs + examples -> plan -> approved script/tool -> manifest -> validation -> human review -> skill iteration
```

The emphasis is not on domain-specific implementation. The emphasis is on how to design stable agent workflows.

## Demo 0: Start with rule-based document generation

This is the safest first exercise because it does not touch production data or complex code. The agent reads structured status data, a report template, and report rules, then calls a script to generate a markdown report and a small PPTX.

Plan prompt:

```text
Use the rule-based-project-report skill. Do not edit files yet.
Read README.md, rules/report_rules.json, templates/project_status_template.md, and inputs/progress_update.json.
Explain the workflow, required sections, forbidden claims, and validation plan.
```

Act prompt:

```text
Run the approved report generation script and validator. Only write to output/. Then summarize what the validator proved and what still needs human review.
```

Teaching point: a stable agent app comes from skill design plus human debugging. A human provides examples, checks the first output, tightens rules, and reruns validation.

## Demo 1: Doc/spec portability

Teach how to develop from specs and historical samples. The agent should not invent behavior from thin air. It should build a mapping, generate an implementation, and provide traceability.

Plan prompt:

```text
Use the doc-spec-portability skill. Do not write code yet.
Read docs/widget_feature_spec.md, platform guides, examples, and configs/portability_rules.json.
Produce a mapping table, portability risks, and a minimal implementation plan.
```

Act prompt:

```text
Run scripts/build_portable_impl.py and scripts/validate_portable_impl.py. Only write to output/. Report the traceability from spec requirements to generated implementation.
```

Teaching point: same functional spec can be implemented on multiple platforms if the contract, mapping, and examples are explicit.

## Demo 2: Rich document pattern pipeline

Teach extraction rules and modular skill chaining. The agent can read documents and execute pipeline steps, but the human must review extraction assumptions, intermediate plan, and final logic.

Plan prompt:

```text
Use the rich-doc-verification-pipeline skill. Do not generate code yet.
Read docs/verification_guide.html, rules/extraction_rules.json, and env_package/env_config.json.
Explain the four stages: extract, adapt, generate, validate. Identify human review gates.
```

Act prompt:

```text
Run the pipeline on docs/verification_guide.html. Then explain which parts were syntax/tool validated and which parts still need human logic review.
```

Teaching point: syntax correctness is not logic correctness. A generated verification flow can compile and still be semantically wrong.

## Demo 3: Permission-guarded execution

Teach that important data and config are not agent playgrounds. Agents should operate through wrappers with parameter constraints, not direct file/database access.

Plan prompt:

```text
Use the permission-guarded-ops skill. Do not read protected files.
Read README.md, configs/approved_query_contract.json, scripts/guarded_query.py, and opencode.json.
Explain the allowed parameter space and forbidden actions.
```

Act prompt:

```text
Run the approved query wrapper for PILOT_A from 2026-04-01 to 2026-04-07. Then create a config change request, not a direct config edit. Run the guardrail validator.
```

Teaching point: combine opencode permissions with script-level validation. Text rules are not enough.
