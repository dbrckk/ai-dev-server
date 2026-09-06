#!/usr/bin/env bash
set -u
BASE="$HOME/.cache/ai-dev-server"
for name in fcc dsh cdesktop; do
  pidfile="$BASE/$name.pid"
  if [ -s "$pidfile" ]; then
    pid=$(cat "$pidfile" 2>/dev/null || true)
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
      for i in {1..10}; do
        kill -0 "$pid" 2>/dev/null || break
        sleep 0.5
      done
      kill -9 "$pid" 2>/dev/null || true
    fi
    rm -f "$pidfile"
  fi
done
sleep 1
exec bash /workspaces/ai-dev-server/scripts/start-all.sh
