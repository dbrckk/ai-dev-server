#!/usr/bin/env bash
set -u

mkdir -p "$HOME/.cache/ai-dev-server/logs"
export PATH="$HOME/.local/bin:$PATH"
LOGDIR="$HOME/.cache/ai-dev-server/logs"

start_bg() {
  local name="$1"; shift
  if pgrep -f "$*" >/dev/null 2>&1; then
    echo "$name already running"
    return 0
  fi
  nohup "$@" >"$LOGDIR/$name.log" 2>&1 &
  echo $! >"$HOME/.cache/ai-dev-server/$name.pid"
  echo "started $name"
}

# FCC local gateway/admin.
if command -v fcc-server >/dev/null 2>&1; then
  start_bg fcc fcc-server
fi

# DeepSeek Harness web UI.
start_bg dsh npx --yes @deepseek-ai/dsh web --no-open

# cdesktop mobile UI. Build the Codespaces forwarded origin dynamically.
if [ -n "${CODESPACE_NAME:-}" ] && [ -n "${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-}" ]; then
  export CDT_ALLOWED_ORIGINS="https://${CODESPACE_NAME}-3000.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
fi
export HOST=0.0.0.0
export PORT=3000
start_bg cdesktop npx --yes cdesktop

# Show a concise status after services have had a moment to bind.
sleep 3
bash "$(dirname "$0")/status.sh" || true
