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
if [ -d "$HOME/.cache/ai-dev-server/logs" ]; then
  echo "Recent logs:"
  for f in "$HOME"/.cache/ai-dev-server/logs/*.log; do
    [ -e "$f" ] || continue
    echo "--- $f ---"
    tail -n 40 "$f" || true
  done
fi
