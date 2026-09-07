#!/usr/bin/env bash
set -euo pipefail

mkdir -p "$HOME/.local/bin" "$HOME/.cache/ai-dev-server/logs"
export PATH="$HOME/.local/bin:$PATH"

# Core coding-agent CLIs. Keep multiple independent harnesses so the autonomous router
# can select the strongest working agent and fail over without waiting for a rebuild.
npm install -g opencode-ai @anthropic-ai/claude-code @openai/codex

# Python tooling and sprite post-processing.
python -m pip install --user --upgrade uv pillow rembg
export PATH="$HOME/.local/bin:$PATH"

# Install/update Free Claude Code directly as a uv tool so Codespace creation
# does not stop on the interactive upstream installer.
if command -v fcc-server >/dev/null 2>&1; then
  uv tool upgrade free-claude-code || true
else
  uv tool install git+https://github.com/Alishahryar1/free-claude-code.git
fi

# Warm the web UIs so later startup from a phone is faster.
npx --yes @deepseek-ai/dsh --help >/dev/null 2>&1 || true
npx --yes cdesktop --help >/dev/null 2>&1 || true

# Pollinations/OpenCode integration helper package, if available.
npm install -g opencode-pollinations-plugin >/dev/null 2>&1 || true

# Keep local secrets/config out of git by default.
touch "$HOME/.cache/ai-dev-server/bootstrap-complete"

echo "AI Dev Server bootstrap complete. Services will auto-start."
