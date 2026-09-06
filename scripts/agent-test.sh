#!/usr/bin/env bash
set -u
export PATH="$HOME/.local/bin:$PATH"
BASE="$HOME/.cache/ai-dev-server"
mkdir -p "$BASE/logs"

# Codespaces may wake without postStart services being ready.
if ! curl -fsS --max-time 3 http://127.0.0.1:8082/health >/dev/null 2>&1; then
  echo 'fcc_service: starting'
  nohup fcc-server >"$BASE/logs/fcc.log" 2>&1 &
  echo $! >"$BASE/fcc.pid"
  for i in {1..30}; do
    curl -fsS --max-time 2 http://127.0.0.1:8082/health >/dev/null 2>&1 && break
    sleep 1
  done
fi
if curl -fsS --max-time 3 http://127.0.0.1:8082/health >/dev/null 2>&1; then
  echo 'fcc_service: OK'
else
  echo 'fcc_service: FAILED'
  exit 0
fi

# FCC currently requires OpenCode >= 1.18.18. Keep it current automatically.
CURRENT=$(opencode --version 2>/dev/null | head -n1 || true)
echo "opencode_before: ${CURRENT:-missing}"
npm install -g opencode-ai@latest >/tmp/opencode-update.log 2>&1 || true
hash -r
CURRENT=$(opencode --version 2>/dev/null | head -n1 || true)
echo "opencode_after: ${CURRENT:-missing}"

WORK=/tmp/deadline-zero-agent-test
rm -rf "$WORK"
git clone --depth 1 https://github.com/dbrckk/deadline-zero.git "$WORK" >/dev/null 2>&1 || { echo 'clone: FAILED'; exit 0; }
cd "$WORK"
PROMPT='Inspect this repository in read-only mode. Identify the main technology stack and the primary entry point. Reply in one concise line starting with AGENT_OK:. Do not modify files.'

echo '=== FCC agent smoke test ==='
echo 'repo: dbrckk/deadline-zero'

echo 'claude_code_test: running'
CLAUDE_OUT=$(timeout 150s fcc-claude -p "$PROMPT" 2>&1)
CLAUDE_RC=$?
if [ "$CLAUDE_RC" -eq 0 ] && printf '%s' "$CLAUDE_OUT" | grep -q 'AGENT_OK:'; then
  echo 'claude_code_test: OK'
  printf 'claude_code_response: %s\n' "$(printf '%s' "$CLAUDE_OUT" | grep 'AGENT_OK:' | tail -n1 | head -c 500)"
else
  echo "claude_code_test: FAILED (rc=$CLAUDE_RC)"
  printf 'claude_code_preview: %s\n' "$(printf '%s' "$CLAUDE_OUT" | tail -n 10 | tr '\n' ' ' | head -c 900)"
fi

echo 'opencode_test: running'
OPENCODE_OUT=$(timeout 150s fcc-opencode run "$PROMPT" 2>&1)
OPENCODE_RC=$?
if [ "$OPENCODE_RC" -eq 0 ] && printf '%s' "$OPENCODE_OUT" | grep -q 'AGENT_OK:'; then
  echo 'opencode_test: OK'
  printf 'opencode_response: %s\n' "$(printf '%s' "$OPENCODE_OUT" | grep 'AGENT_OK:' | tail -n1 | head -c 500)"
else
  echo "opencode_test: FAILED (rc=$OPENCODE_RC)"
  printf 'opencode_preview: %s\n' "$(printf '%s' "$OPENCODE_OUT" | tail -n 15 | tr '\n' ' ' | head -c 1200)"
fi
