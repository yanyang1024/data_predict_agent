#!/usr/bin/env bash
set -euo pipefail
INSTANCE_ID="${1:?missing instance id}"
ENV_FILE="${XDG_CONFIG_HOME:-$HOME/.config}/flash-agents/opencode/${INSTANCE_ID}.env"
if [ -f "$ENV_FILE" ]; then
  # shellcheck disable=SC1090
  source "$ENV_FILE"
fi

: "${OPENCODE_PORT:?OPENCODE_PORT is required}"
: "${OPENCODE_WORKSPACE_ROOT:?OPENCODE_WORKSPACE_ROOT is required}"
: "${OPENCODE_BINARY:=opencode}"
: "${BWRAP_PATH:=bwrap}"

mkdir -p "$OPENCODE_WORKSPACE_ROOT"

# The sandbox keeps host tools read-only and gives the engine a writable /workspace only.
# --share-net is intentional: OpenCode must bind 127.0.0.1:$OPENCODE_PORT for the platform backend.
exec "$BWRAP_PATH" \
  --die-with-parent \
  --new-session \
  --unshare-pid \
  --unshare-ipc \
  --unshare-uts \
  --share-net \
  --ro-bind /usr /usr \
  --ro-bind /bin /bin \
  --ro-bind /lib /lib \
  --ro-bind /lib64 /lib64 \
  --dev /dev \
  --proc /proc \
  --tmpfs /tmp \
  --bind "$OPENCODE_WORKSPACE_ROOT" /workspace \
  --chdir /workspace \
  --setenv HOME /workspace \
  --setenv PORT "$OPENCODE_PORT" \
  --setenv OPENCODE_PORT "$OPENCODE_PORT" \
  "$OPENCODE_BINARY" serve --host 127.0.0.1 --port "$OPENCODE_PORT"
