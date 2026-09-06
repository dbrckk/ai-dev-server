#!/usr/bin/env bash
set -u
export PATH="$HOME/.local/bin:$PATH"

check_port() {
  local port="$1" name="$2"
  if python - "$port" <<'PY' >/dev/null 2>&1
import socket, sys
p=int(sys.argv[1]); s=socket.socket(); s.settimeout(.5)
try:
    s.connect(('127.0.0.1',p)); ok=True
except OSError:
    ok=False
finally:
    s.close()
sys.exit(0 if ok else 1)
PY
  then
    printf '%-20s OK (port %s)\n' "$name" "$port"
  else
    printf '%-20s NOT READY (port %s)\n' "$name" "$port"
  fi
}

echo "=== AI Dev Server status ==="
check_port 8082 "Free Claude Code"
check_port 3080 "DeepSeek Harness"
check_port 3000 "cdesktop"
printf '\nInstalled CLIs:\n'
for x in fcc-server fcc-claude fcc-opencode fcc-dsh claude opencode; do
  if command -v "$x" >/dev/null 2>&1; then
    printf '  %-15s %s\n' "$x" "$(command -v "$x")"
  else
    printf '  %-15s missing\n' "$x"
  fi
done

if [ -n "${CODESPACE_NAME:-}" ] && [ -n "${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-}" ]; then
  echo
  echo "Codespaces URLs:"
  echo "  DSH:      https://${CODESPACE_NAME}-3080.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
  echo "  cdesktop: https://${CODESPACE_NAME}-3000.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
  echo "  FCC:      https://${CODESPACE_NAME}-8082.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
fi
