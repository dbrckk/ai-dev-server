#!/usr/bin/env bash
set -u
export PATH="$HOME/.local/bin:$PATH"
WORK=/tmp/deadline-zero-agent-test
rm -rf "$WORK"
git clone --depth 1 https://github.com/dbrckk/deadline-zero.git "$WORK" >/dev/null 2>&1 || { echo 'clone: FAILED'; exit 0; }
cd "$WORK"
PROMPT='Inspect this repository in read-only mode. Identify the main technology stack and the primary entry point. Reply in one concise line starting with AGENT_OK:. Do not modify files.'

echo '=== FCC agent smoke test ==='
echo 'repo: dbrckk/deadline-zero'

echo 'claude_code_test: running'
CLAUDE_OUT=$(timeout 120s fcc-claude -p "$PROMPT" 2>&1)
CLAUDE_RC=$?
if [ "$CLAUDE_RC" -eq 0 ] && printf '%s' "$CLAUDE_OUT" | grep -q 'AGENT_OK:'; then
  echo 'claude_code_test: OK'
  printf 'claude_code_response: %s\n' "$(printf '%s' "$CLAUDE_OUT" | grep 'AGENT_OK:' | tail -n1 | head -c 500)"
else
  echo "claude_code_test: FAILED (rc=$CLAUDE_RC)"
  printf 'claude_code_preview: %s\n' "$(printf '%s' "$CLAUDE_OUT" | tail -n 8 | tr '\n' ' ' | head -c 700)"
fi

echo 'opencode_test: running'
OPENCODE_OUT=$(timeout 120s fcc-opencode run "$PROMPT" 2>&1)
OPENCODE_RC=$?
if [ "$OPENCODE_RC" -eq 0 ] && printf '%s' "$OPENCODE_OUT" | grep -q 'AGENT_OK:'; then
  echo 'opencode_test: OK'
  printf 'opencode_response: %s\n' "$(printf '%s' "$OPENCODE_OUT" | grep 'AGENT_OK:' | tail -n1 | head -c 500)"
else
  echo "opencode_test: FAILED (rc=$OPENCODE_RC)"
  printf 'opencode_preview: %s\n' "$(printf '%s' "$OPENCODE_OUT" | tail -n 12 | tr '\n' ' ' | head -c 900)"
fi
