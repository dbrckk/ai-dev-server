#!/usr/bin/env bash
set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"

if ! command -v fcc-server >/dev/null 2>&1; then
  echo "FCC absent: installation..."
  uv tool install git+https://github.com/Alishahryar1/free-claude-code.git
fi

if command -v fcc-init >/dev/null 2>&1; then
  fcc-init || true
fi

echo "FCC prêt. Lance ./scripts/start-fcc.sh puis ouvre le port 8082 dans Codespaces."
