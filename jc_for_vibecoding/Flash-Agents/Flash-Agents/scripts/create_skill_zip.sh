#!/usr/bin/env bash
set -euo pipefail
SKILL_DIR="${1:?usage: create_skill_zip.sh <skill-dir>}"
OUT="${2:-$(basename "$SKILL_DIR").zip}"
(
  cd "$SKILL_DIR"
  test -f SKILL.md || { echo "SKILL.md is required" >&2; exit 1; }
  zip -r "$OLDPWD/$OUT" .
)
echo "$OUT"
