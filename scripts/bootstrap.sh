#!/usr/bin/env bash
set -euo pipefail

mkdir -p "$HOME/.local/bin"
export PATH="$HOME/.local/bin:$PATH"

# Core CLIs used by the agents.
npm install -g opencode-ai @anthropic-ai/claude-code

# uv is used to install Free Claude Code without forcing its interactive installer
# during Codespace creation.
python -m pip install --user --upgrade uv
export PATH="$HOME/.local/bin:$PATH"

if ! command -v fcc-server >/dev/null 2>&1; then
  uv tool install git+https://github.com/Alishahryar1/free-claude-code.git || true
fi

# Warm npm packages so first mobile launch is faster. Failures are non-fatal.
npx --yes @deepseek-ai/dsh --help >/dev/null 2>&1 || true
npx --yes cdesktop --help >/dev/null 2>&1 || true

# Sprite preparation dependencies (generation itself uses an external image provider).
python -m pip install --user --upgrade pillow rembg || true

cat <<'EOF'

AI Dev Server bootstrap completed.
Next commands:
  ./scripts/finish-fcc.sh
  ./scripts/start-fcc.sh
  ./scripts/start-dsh.sh
  ./scripts/start-cdesktop.sh

EOF
