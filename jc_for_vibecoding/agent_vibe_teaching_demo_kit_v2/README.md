# Agent + Vibe Coding Teaching Demo Kit v2

This kit is intentionally small and synthetic. It is designed for teaching how to guide coding agents with rules, skills, commands, validation scripts, and permissions. The examples are inspired by the department scenarios in the course request, but they avoid real production data, proprietary manuals, real tester APIs, and real verification IP.

## Demo sequence

| Demo | Teaching focus | Main message |
|---|---|---|
| 00_rule_based_report_generation | Rule-based document generation and first opencode workflow | Start with a stable, low-risk workflow: fill a report from structured status data using rules and a template. |
| 01_doc_spec_portability | Doc/spec-driven development standards and portability | Same functional spec, different platform implementation. Use historical docs and reference examples to build traceable adapters. |
| 02_rich_doc_pattern_pipeline | Rich document extraction, skill chaining, and human-in-the-loop validation | Extract rules from PDF/HTML-like docs, adapt to an environment package, generate code, validate syntax, and leave logic review to humans. |
| 03_permission_guarded_execution | Permission boundaries and wrapper scripts | Important data/config must not be edited directly by an agent. Use approved wrappers, contracts, manifests, and audit logs. |

## Quick run

```bash
python3 run_all_demos.py
```

`run_all_demos.py` uses `/usr/bin/python3` when available to avoid environment-specific virtualenv side effects. To force a different interpreter, run `PYTHON=/path/to/python python3 run_all_demos.py`.

Each demo can also be run independently from its own directory. Generated outputs are committed in each `output/` directory after the scripts are run.

## Optional dependencies

Most scripts use Python standard library. For the full demo experience:

```bash
pip install -r requirements.txt
```

- `python-pptx` is used by Demo 0 to create a simple PPTX report.
- `beautifulsoup4` and `pypdf` are used by Demo 2 for rich-text/PDF extraction.
- `reportlab` is only used to regenerate the synthetic sample PDF.

## Suggested classroom rhythm

1. Read `TEACHING_GUIDE.md`.
2. Open the demo README.
3. Start in Plan mode: ask the agent to inspect rules, inputs, and stop rules without editing.
4. Switch to Act mode: run the approved script only.
5. Review the manifest and validation output.
6. Ask: what did the tool prove, and what still needs human validation?
