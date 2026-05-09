# Project Rules for OpenCode Teaching Demos

You are assisting with a teaching repository. Optimize for explainability, small verifiable steps, and safe execution.

## Default workflow

1. Start in Plan mode for any task that reads documents, changes code, or runs scripts.
2. Identify the relevant demo and read its README first.
3. Do not edit generated outputs directly. Regenerate them from scripts.
4. For code changes, run the corresponding validation script.
5. Always produce a short review note that says what was generated, what was verified, and what still needs human review.

## Safety boundaries

- Do not read or edit files under any `protected_data/` directory unless a demo explicitly asks you to explain why this is unsafe.
- Do not modify `opencode.json` to loosen permissions unless the user explicitly asks for a permission design exercise.
- Do not claim generated artifacts are production-ready.
- Do not replace human review for business semantics, verification intent, spec signoff, production data, or configuration decisions.

## Teaching style

When explaining a demo, connect every file to one of these concepts:

- Rule: persistent instruction or convention
- Skill: reusable workflow
- Command: convenient task entrypoint
- Tool/Script: deterministic execution
- Permission: execution boundary
- Manifest: evidence of what happened
- Human review: logic and decision checkpoint
