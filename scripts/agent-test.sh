#!/usr/bin/env bash
set -u
export PATH="$HOME/.local/bin:$PATH"
BASE="$HOME/.cache/ai-dev-server"
mkdir -p "$BASE/logs"

if ! curl -fsS --max-time 3 http://127.0.0.1:8082/health >/dev/null 2>&1; then
  echo 'fcc_service: starting'
  nohup fcc-server >"$BASE/logs/fcc.log" 2>&1 &
  echo $! >"$BASE/fcc.pid"
  for i in {1..30}; do
    curl -fsS --max-time 2 http://127.0.0.1:8082/health >/dev/null 2>&1 && break
    sleep 1
  done
fi
curl -fsS --max-time 3 http://127.0.0.1:8082/health >/dev/null 2>&1 || { echo 'fcc_service: FAILED'; exit 0; }
echo 'fcc_service: OK'

npm install -g opencode-ai@latest >/tmp/opencode-update.log 2>&1 || true
hash -r

WORK=/tmp/jumpy-agent-audit
rm -rf "$WORK"
git clone --depth 1 https://github.com/dbrckk/Jumpy.git "$WORK" >/dev/null 2>&1 || { echo 'clone: FAILED'; exit 0; }
cd "$WORK"
PROMPT='Audit this Godot 4 mobile game repository in read-only mode. Focus on GDScript parse/runtime errors, broken Godot APIs, gameplay blockers, save-data bugs, mobile input issues, and serious architecture risks. Do not modify files. If no blocking issue exists, reply exactly AGENT_OK: followed by one concise assessment. If issues exist, reply AGENT_ISSUES: followed by at most 6 concrete issues with file/function names and fixes.'

echo '=== Jumpy FCC autonomous audit ==='
echo 'repo: dbrckk/Jumpy'

echo 'claude_code_audit: running'
CLAUDE_OUT=$(timeout 210s fcc-claude -p "$PROMPT" 2>&1)
CLAUDE_RC=$?
printf 'claude_code_result: %s\n' "$(printf '%s' "$CLAUDE_OUT" | grep -E 'AGENT_(OK|ISSUES):' -A 8 | tail -n 12 | tr '\n' ' ' | head -c 1800)"
echo "claude_code_rc: $CLAUDE_RC"

echo 'opencode_audit: running'
OPENCODE_OUT=$(timeout 210s fcc-opencode run "$PROMPT" 2>&1)
OPENCODE_RC=$?
printf 'opencode_result: %s\n' "$(printf '%s' "$OPENCODE_OUT" | grep -E 'AGENT_(OK|ISSUES):' -A 8 | tail -n 12 | tr '\n' ' ' | head -c 1800)"
echo "opencode_rc: $OPENCODE_RC"
