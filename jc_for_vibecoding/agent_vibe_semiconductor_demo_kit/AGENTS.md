# Project Rules for Agentic Coding Demos

These scenarios are synthetic training examples.

General rules:

- Start complex tasks in planning mode. Read relevant docs and code before editing.
- Do not claim any generated tester program, vector, or engineering report is production-ready.
- Do not connect to production databases, tester systems, EDA tools, or lab equipment.
- Treat all manuals, standards, and specs as sources that can be ambiguous.
- When a mapping is uncertain, write it to an unsupported or needs-review list.
- Keep deterministic transformations in scripts and make them easy to test.
- Prefer small changes and explicit validation artifacts.

Stop rules:

- Stop before modifying recipe, spec, timing, voltage limits, tester setup, or production data.
- Stop before giving lot hold/release, ship, or customer-impact decisions.
- Stop when data coverage or document semantics are insufficient.
