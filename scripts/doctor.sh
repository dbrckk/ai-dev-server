#!/usr/bin/env bash
set -u

cd /workspaces/ai-dev-server 2>/dev/null || true
export PATH="$HOME/.local/bin:$PATH"

echo "=== AI Dev Server doctor ==="
echo "date: $(date -Is)"
echo "user: $(whoami)"
echo "pwd: $(pwd)"
echo "node: $(node --version 2>/dev/null || echo missing)"
echo "npm: $(npm --version 2>/dev/null || echo missing)"
echo "python: $(python --version 2>/dev/null || echo missing)"
echo "gh: $(gh --version 2>/dev/null | head -n1 || echo missing)"
echo

echo "Commands:"
for x in fcc-server fcc-claude fcc-opencode fcc-dsh claude opencode; do
  if command -v "$x" >/dev/null 2>&1; then
    echo "  $x: $(command -v "$x")"
  else
    echo "  $x: missing"
  fi
done

echo
if [ -f scripts/status.sh ]; then
  bash scripts/status.sh || true
fi

echo
echo "HTTP checks:"
check_http() {
  local name="$1" url="$2" code
  code=$(curl -L -sS -o /dev/null -w '%{http_code}' --max-time 8 "$url" 2>/dev/null || echo 000)
  case "$code" in
    2*|3*) echo "  $name: OK ($code)" ;;
    *) echo "  $name: FAIL ($code)" ;;
  esac
}
check_http "FCC health" "http://127.0.0.1:8082/health"
check_http "DSH web" "http://127.0.0.1:3080/"
check_http "cdesktop" "http://127.0.0.1:3000/"

echo
if [ -d "$HOME/.cache/ai-dev-server/logs" ]; then
  echo "Recent logs:"
  for f in "$HOME"/.cache/ai-dev-server/logs/*.log; do
    [ -e "$f" ] || continue
    echo "--- $f ---"
    tail -n 25 "$f" || true
  done
fi
