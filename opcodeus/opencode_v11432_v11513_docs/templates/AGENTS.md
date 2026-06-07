# Project Agent Rules

## Project overview

- This is a `<language/framework>` project.
- Package manager: `<pnpm/npm/bun/yarn/pip/cargo/go>`.
- Project root is the git worktree root.
- Main app/module: `<path>`.
- Shared libraries: `<path>`.

## Path rules

- Treat the git worktree root as the default project root.
- When referencing project files, use paths relative to the git worktree root.
- Do not assume the current shell directory is the same as `.opencode/tools` or `.opencode/skills`.
- If a script is under `scripts/`, invoke it with an explicit interpreter, e.g. `python3 scripts/foo.py`.
- If a command fails because a file is not found, run `pwd`, `git rev-parse --show-toplevel`, and `ls` before retrying.

## Required workflow

1. For non-trivial tasks, start in Plan mode.
2. Before editing, list files you plan to modify and why.
3. Prefer minimal patches. Do not rewrite large files unless explicitly asked.
4. After editing, run the smallest relevant test first.
5. Always summarize changed files, tests run, and remaining risks.

## Commands

- Install: `<install command>`
- Test: `<test command>`
- Related test: `<test command with file/path>`
- Typecheck: `<typecheck command>`
- Lint: `<lint command>`

## Safety rules

- Do not run `git push`.
- Do not run `git reset --hard` or `git clean -fd`.
- Do not run `rm -rf`.
- Do not run broad process-kill commands such as `pkill -f`, `killall`, or `taskkill /IM node.exe`.
- Do not start long-running dev servers inside the agent unless explicitly approved.
- If a command may affect running processes, ask first and explain the exact PID / port / process name.
- Do not read `.env`, `.env.*`, `*.pem`, `*.key`, or secret files.

## Git workflow

- Human owns commits.
- Agent may inspect `git status`, `git diff`, and `git log`.
- Agent must not commit unless explicitly asked.

## Testing policy

- Add or update regression tests when fixing bugs.
- If tests cannot be run, explain why and give the exact command for humans to run.

## Review policy

When reviewing code, check:

1. Correctness.
2. Edge cases.
3. Security risks.
4. Concurrency / idempotency / transaction risks.
5. Test coverage.
6. Unrelated changes.
