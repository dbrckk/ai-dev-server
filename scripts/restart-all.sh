#!/usr/bin/env bash
set -u
BASE="$HOME/.cache/ai-dev-server"

# Stop tracked parent processes first.
for name in fcc dsh cdesktop; do
  pidfile="$BASE/$name.pid"
  if [ -s "$pidfile" ]; then
    pid=$(cat "$pidfile" 2>/dev/null || true)
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
    fi
    rm -f "$pidfile"
  fi
done

# npx-based services can leave child processes behind. Kill the actual
# listeners, not only their parent wrappers.
for port in 8082 3080 3000; do
  if command -v fuser >/dev/null 2>&1; then
    fuser -k "${port}/tcp" >/dev/null 2>&1 || true
  fi
done

# Narrow fallbacks for images without fuser.
pkill -f '@deepseek-ai/dsh.*web' 2>/dev/null || true
pkill -f 'cdesktop' 2>/dev/null || true
pkill -f 'fcc-server' 2>/dev/null || true
sleep 2

exec bash /workspaces/ai-dev-server/scripts/start-all.sh
