#!/usr/bin/env bash
set -euo pipefail

# Harden and specialize the base v3 orchestrator at runtime. Keep the base script small while
# allowing the safety wrapper to evolve agent routing without exposing repository credentials.
python - <<'PY'
from pathlib import Path
import re
p = Path('scripts/jumpy-studio-cycle-v3.sh')
s = p.read_text()

old = 'Implement ONE smallest complete safe improvement from the strategic review below. Modify at most 2 existing text files and about 100 changed lines. No external downloads, package installs, dependencies, network calls, credentials, .github edits, binary assets or release configuration. Produce useful edits early and leave no undefined symbols. If the main idea is too large, choose a smaller local improvement.'
new = 'EDIT FIRST. Within the first concrete action, modify ONLY scripts/main.gd with one small compile-complete improvement. Use TABS ONLY for GDScript indentation; never introduce leading spaces in indented GDScript lines. Do not redo pulse if it already respects reduced_motion. Priority order: (1) make perfect/clutch landing camera kick, flash and burst materially smaller or disabled under reduced_motion; (2) make death feedback materially smaller or disabled under reduced_motion; (3) make high_contrast visibly improve player/platform/perfect-zone readability using existing procedural drawing only. If all three are already complete, choose the next smallest local gameplay/UX improvement. Do not spend the cycle only reading. Keep the diff under about 100 changed lines. No external downloads, package installs, dependencies, network calls, credentials, .github edits, binary assets or release configuration. Leave no undefined symbols.'
if old not in s:
    raise SystemExit('open-ended prompt anchor mismatch')
s = s.replace(old, new, 1)

# Dynamic agent router. For repository implementation work Claude Code is the primary agent,
# OpenCode is the automatic fallback. A deterministic phase remains preferred when one exists.
# The fallback is attempted only when the primary produced no source edit.
pattern = r'''run_agent\(\) \{\n.*?\n\}\n\ncase \"\$PHASE\" in'''
replacement = r'''run_agent() {
  local seconds="$1"
  local primary_budget=$((seconds * 2 / 3))
  local fallback_budget=$((seconds - primary_budget))
  local agent=""
  local cmd=""
  EXEC_STATUS="no_agent"
  : >/tmp/jumpy-agent.log

  run_one_agent() {
    local name="$1" budget="$2" command="$3"
    echo "AGENT_ATTEMPT=$name" | tee -a /tmp/jumpy-agent.log
    setsid env -u GH_TOKEN -u GITHUB_TOKEN -u CODESPACES_PAT -u NVIDIA_NIM_API_KEY \
      GIT_TERMINAL_PROMPT=0 SSH_AUTH_SOCK= GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null \
      bash -lc "cd /workspaces/ai-dev-server/.jumpy-studio-cycle && git config --local credential.helper '' && $command" \
      >>/tmp/jumpy-agent.log 2>&1 &
    local pid=$!
    local loops=$((budget / 2))
    local timed_out=1
    for _ in $(seq 1 "$loops"); do
      if ! kill -0 "$pid" 2>/dev/null; then
        wait "$pid" || true
        timed_out=0
        break
      fi
      sleep 2
    done
    if [ "$timed_out" -eq 1 ]; then
      kill -TERM -- "-$pid" 2>/dev/null || true
      sleep 2
      kill -KILL -- "-$pid" 2>/dev/null || true
      wait "$pid" 2>/dev/null || true
      EXEC_STATUS="${name}_timeout_${budget}s"
    else
      EXEC_STATUS="${name}_completed"
    fi
    if git diff --name-only | awk '$0 != "docs/AUTONOMOUS_STATE.md" {found=1} END {exit !found}'; then
      echo "AGENT_SELECTED=$name" | tee -a /tmp/jumpy-agent.log
      return 0
    fi
    return 1
  }

  # Best-capability order for code editing in this stack. Skip unavailable launchers cleanly.
  if command -v fcc-claude >/dev/null 2>&1 && command -v claude >/dev/null 2>&1; then
    agent="claude-code"
    cmd='fcc-claude -p "$(cat /tmp/brief.txt)"'
    run_one_agent "$agent" "$primary_budget" "$cmd" && return 0
  fi

  if command -v fcc-opencode >/dev/null 2>&1 && command -v opencode >/dev/null 2>&1; then
    agent="opencode"
    cmd='fcc-opencode run "$(cat /tmp/brief.txt)"'
    run_one_agent "$agent" "$fallback_budget" "$cmd" && return 0
  fi

  echo 'AGENT_SELECTED=none' | tee -a /tmp/jumpy-agent.log
  return 0
}

case "$PHASE" in'''
s2, n = re.subn(pattern, replacement, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f'agent router anchor mismatch ({n})')
s = s2

# Repair recurring model indentation mistakes before strict diff checks and Godot validation.
# Canonicalize any mixed leading whitespace in main.gd by visual columns (tab width 4).
anchor = "if [ -s /tmp/jumpy-agent.log ]; then"
repair = r'''python - <<'PY2'
from pathlib import Path
p=Path('scripts/main.gd')
if p.exists():
    out=[]
    for line in p.read_text().splitlines(keepends=True):
        body=line.rstrip('\r\n')
        ending=line[len(body):]
        i=0
        cols=0
        while i < len(body) and body[i] in (' ', '\t'):
            if body[i] == '\t':
                cols += 4 - (cols % 4)
            else:
                cols += 1
            i += 1
        if i:
            # GDScript in this project is tab-indented. Preserve only whole indentation levels.
            # Any residual spaces are kept only when the original prefix had a non-multiple-of-4 column.
            body = ('\t' * (cols // 4)) + (' ' * (cols % 4)) + body[i:]
        out.append(body + ending)
    p.write_text(''.join(out))
PY2

'''
if anchor not in s:
    raise SystemExit('agent-log anchor mismatch')
s = s.replace(anchor, repair + anchor, 1)
p.write_text(s)
PY

LOG=/tmp/jumpy-v3-safe.log
set +e
bash scripts/jumpy-studio-cycle-v3-runner.sh 2>&1 | tee "$LOG"
RC=${PIPESTATUS[0]}
set -e

if [ "$RC" -eq 0 ]; then
  exit 0
fi

# OPEN_ENDED may legitimately end without producing a source change. Treat only the exact,
# validated documentation-only outcome as a clean no-op; all safety/parse failures remain red.
if grep -q '^PHASE=OPEN_ENDED$' "$LOG" \
  && grep -q '^FILES=docs/AUTONOMOUS_STATE.md$' "$LOG" \
  && grep -q 'Godot Engine v4.7.2' "$LOG" \
  && ! grep -Eq 'Godot rejected candidate|REJECTING_|Secret-like material detected|Final scope too broad|Parse Error|SCRIPT ERROR' "$LOG"; then
  echo 'RESULT=NO_SOURCE_CHANGE'
  echo 'Open-ended executor produced documentation only; preserving green workflow without pushing noise.'
  exit 0
fi

exit "$RC"
