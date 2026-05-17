#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
USER_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
ENV_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/flash-agents/opencode"
mkdir -p "$USER_DIR" "$ENV_DIR"
cp "$ROOT_DIR/systemd/opencode@.service" "$USER_DIR/opencode@.service"
systemctl --user daemon-reload
cat <<EOF
Installed opencode@.service into $USER_DIR.
Set SYSTEMD_ENABLED=true in backend/.env.
The backend writes per-user env files into $ENV_DIR/<user_id>.env before starting each instance.
EOF
