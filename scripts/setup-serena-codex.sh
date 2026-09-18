#!/usr/bin/env bash
set -euo pipefail

if ! command -v uvx >/dev/null 2>&1; then
  cat >&2 <<'EOF'
uv/uvx is required.

Linux/macOS/Termux:
  curl -LsSf https://astral.sh/uv/install.sh | sh

Then reopen the shell and run this script again.
EOF
  exit 1
fi

echo "Configuring Serena MCP for Codex..."
uvx --from git+https://github.com/oraios/serena serena setup codex

CONFIG="${HOME}/.codex/config.toml"
if [[ -f "$CONFIG" ]] && grep -q '\[mcp_servers\.serena\]' "$CONFIG"; then
  echo "OK: Serena is registered in $CONFIG"
else
  echo "Warning: Serena setup completed but $CONFIG does not contain [mcp_servers.serena]." >&2
  echo "Run: uvx --from git+https://github.com/oraios/serena serena setup codex" >&2
  exit 2
fi

cat <<'EOF'

Serena/Codex setup complete.

For a configured repository:
  1. cd /path/to/repository
  2. codex
  3. verify Serena with /mcp

The repository AGENTS.md instructs Codex to prefer Serena symbol navigation.
If activation is not automatic, tell Codex:
  Activate the current dir as project using serena
EOF
