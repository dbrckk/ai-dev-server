#!/usr/bin/env bash
set -u

BASE="$HOME/.cache/ai-dev-server"
LOGDIR="$BASE/logs"
mkdir -p "$LOGDIR"
export PATH="$HOME/.local/bin:$PATH"

is_running() {
  local name="$1" pidfile="$BASE/$1.pid" pid
  [ -s "$pidfile" ] || return 1
  pid=$(cat "$pidfile" 2>/dev/null || true)
  [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null
}

start_bg() {
  local name="$1"; shift
  local pidfile="$BASE/$name.pid" logfile="$LOGDIR/$name.log" pid

  if is_running "$name"; then
    echo "$name already running (pid $(cat "$pidfile"))"
    return 0
  fi

  rm -f "$pidfile"
  : > "$logfile"
  nohup "$@" >"$logfile" 2>&1 < /dev/null &
  pid=$!
  echo "$pid" > "$pidfile"
  sleep 2

  if kill -0 "$pid" 2>/dev/null; then
    echo "started $name (pid $pid)"
    return 0
  fi

  echo "$name exited during startup"
  tail -n 60 "$logfile" || true
  rm -f "$pidfile"
  return 1
}

# Free Claude Code local gateway/admin.
if command -v fcc-server >/dev/null 2>&1; then
  start_bg fcc fcc-server || true
else
  echo "fcc-server missing"
fi

# DeepSeek Harness web UI.
start_bg dsh npx --yes @deepseek-ai/dsh web --no-open || true

# cdesktop mobile UI.
if [ -n "${CODESPACE_NAME:-}" ] && [ -n "${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-}" ]; then
  export CDT_ALLOWED_ORIGINS="https://${CODESPACE_NAME}-3000.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
fi
export HOST=0.0.0.0
export PORT=3000
start_bg cdesktop npx --yes cdesktop || true

# Give npm/npx based services enough time to initialize.
for i in {1..15}; do
  READY=0
  for p in 8082 3080 3000; do
    python - "$p" <<'PY' >/dev/null 2>&1 && READY=$((READY+1)) || true
import socket, sys
p=int(sys.argv[1]); s=socket.socket(); s.settimeout(.4)
try:
    s.connect(('127.0.0.1',p))
except OSError:
    sys.exit(1)
finally:
    s.close()
PY
  done
  [ "$READY" -eq 3 ] && break
  sleep 2
done

bash "$(dirname "$0")/status.sh" || true

echo
echo "=== startup log tails ==="
for name in fcc dsh cdesktop; do
  echo "--- $name ---"
  tail -n 40 "$LOGDIR/$name.log" 2>/dev/null || true
done
