#!/usr/bin/env bash
set -u
export PATH="$HOME/.local/bin:$PATH"
BASE="$HOME/.cache/ai-dev-server"
mkdir -p "$BASE/logs"

if ! curl -fsS --max-time 3 http://127.0.0.1:8082/health >/dev/null 2>&1; then
  nohup fcc-server >"$BASE/logs/fcc.log" 2>&1 &
  echo $! >"$BASE/fcc.pid"
  for i in {1..20}; do
    curl -fsS --max-time 2 http://127.0.0.1:8082/health >/dev/null 2>&1 && break
    sleep 1
  done
fi
curl -fsS --max-time 3 http://127.0.0.1:8082/health >/dev/null 2>&1 || { echo 'fcc_service: FAILED'; exit 0; }
echo 'fcc_service: OK'

WORK=/tmp/jumpy-agent-audit
rm -rf "$WORK"
git clone --depth 1 https://github.com/dbrckk/Jumpy.git "$WORK" >/dev/null 2>&1 || { echo 'clone: FAILED'; exit 0; }
cd "$WORK"
PROMPT='Audit this Godot 4.7 mobile game read-only. Find only blocking or high-impact issues: GDScript parse/runtime errors, broken Godot APIs, gameplay blockers, daily-seed determinism, save corruption, mobile input problems. Do not modify files. Reply in one line: AGENT_OK: assessment OR AGENT_ISSUES: up to 4 concise issues with file/function and fix.'

echo '=== Jumpy FCC autonomous audit ==='
echo 'repo: dbrckk/Jumpy'

CLAUDE_OUT=$(timeout 110s fcc-claude -p "$PROMPT" 2>&1)
CLAUDE_RC=$?
printf 'claude_code_result: %s\n' "$(printf '%s' "$CLAUDE_OUT" | grep -E 'AGENT_(OK|ISSUES):' | tail -n1 | head -c 1700)"
echo "claude_code_rc: $CLAUDE_RC"

OPENCODE_OUT=$(timeout 110s fcc-opencode run "$PROMPT" 2>&1)
OPENCODE_RC=$?
printf 'opencode_result: %s\n' "$(printf '%s' "$OPENCODE_OUT" | grep -E 'AGENT_(OK|ISSUES):' | tail -n1 | head -c 1700)"
echo "opencode_rc: $OPENCODE_RC"
exit 0
