#!/usr/bin/env bash
set -euo pipefail

# v3 runner: patches the v3 base orchestrator at runtime with stronger scope checks and
# empirical FCC agent selection. FCC launchers own their model catalog/routing; BEST_MODEL
# remains a provider-health signal, not a raw CLI model id.
TMP=/tmp/jumpy-studio-cycle-v3-runtime.sh
cp scripts/jumpy-studio-cycle-v3.sh "$TMP"
python - "$TMP" <<'PY'
from pathlib import Path
import re, sys
p=Path(sys.argv[1]); s=p.read_text()

# Include untracked files in pre/post gates.
s=s.replace("FILES=$(git diff --name-only)", "git add -N --all\nFILES=$(git diff --name-only)", 1)
final_needle = "# Final scope and secret check after patch application.\nFILES=$(git diff --name-only)"
final_replacement = "# Final scope and secret check after patch application. Include untracked files in every gate.\ngit add -N --all\nFILES=$(git diff --name-only)"
if s.count(final_needle) != 1: raise SystemExit('v3 final-scope anchor mismatch')
s=s.replace(final_needle, final_replacement, 1)
count_needle="COUNT=$(printf '%s\\n' \"$FILES\" | grep -v '^docs/AUTONOMOUS_STATE.md$' | sed '/^$/d' | wc -l)"
count_replacement="COUNT=$(printf '%s\\n' \"$FILES\" | awk 'NF && $0 != \"docs/AUTONOMOUS_STATE.md\" {n++} END {print n+0}')"
if s.count(count_needle)!=1: raise SystemExit('v3 source-count anchor mismatch')
s=s.replace(count_needle,count_replacement,1)

agent_pattern=r'''run_agent\(\) \{\n.*?\n\}\n\ncase \"\$PHASE\" in'''
agent_replacement=r'''run_agent() {
  local seconds="$1"
  local primary_budget=$((seconds * 3 / 4))
  local fallback_budget=$((seconds - primary_budget))
  EXEC_STATUS="no_agent"
  : >/tmp/jumpy-agent.log

  ensure_fcc() {
    if curl -fsS --max-time 3 http://127.0.0.1:8082/health >/dev/null 2>&1; then return 0; fi
    nohup fcc-server >"$BASE/logs/fcc.log" 2>&1 < /dev/null &
    for _ in {1..30}; do curl -fsS --max-time 2 http://127.0.0.1:8082/health >/dev/null 2>&1 && return 0; sleep 1; done
    return 1
  }
  agent_available() {
    case "$1" in
      claude-code) command -v fcc-claude >/dev/null 2>&1 && command -v claude >/dev/null 2>&1 ;;
      opencode) command -v fcc-opencode >/dev/null 2>&1 && command -v opencode >/dev/null 2>&1 ;;
      *) return 1 ;;
    esac
  }
  agent_command() {
    # Do not pass provider/model ids directly. FCC launchers expose their own compatible
    # model catalog and routing; raw NVIDIA ids can be rejected by the client itself.
    case "$1" in
      claude-code) printf '%s' 'fcc-claude --permission-mode acceptEdits -p "$(cat /tmp/jumpy-fcc-bench-brief.txt)"' ;;
      opencode) printf '%s' 'fcc-opencode run "$(cat /tmp/jumpy-fcc-bench-brief.txt)"' ;;
    esac
  }
  benchmark_agent() {
    local name="$1" dir cmd rc
    dir=$(mktemp -d "/tmp/jumpy-fcc-bench-${name}.XXXXXX")
    pushd "$dir" >/dev/null
    git init -q; git config user.email benchmark@localhost; git config user.name 'FCC benchmark'
    printf 'ORIGINAL\n' > TARGET.txt; git add TARGET.txt && git commit -qm baseline
    printf '%s\n' 'Edit TARGET.txt. Replace its entire contents with exactly FCC_AGENT_OK. Do not create other files. Perform the edit; do not merely explain.' >/tmp/jumpy-fcc-bench-brief.txt
    cmd=$(agent_command "$name")
    set +e
    timeout -k 3s 40s env -u GH_TOKEN -u GITHUB_TOKEN -u CODESPACES_PAT -u NVIDIA_NIM_API_KEY GIT_TERMINAL_PROMPT=0 SSH_AUTH_SOCK= bash -lc "$cmd" >"/tmp/jumpy-fcc-bench-${name}.log" 2>&1
    rc=$?; set -e
    local ok=1
    if [ "$rc" -eq 0 ] && [ "$(cat TARGET.txt 2>/dev/null || true)" = 'FCC_AGENT_OK' ] && [ "$(git diff --name-only | paste -sd, -)" = 'TARGET.txt' ]; then ok=0; fi
    popd >/dev/null; rm -rf "$dir"
    if [ "$ok" -eq 0 ]; then echo "FCC_BENCH_PASS=$name ROUTE=fcc_catalog PROBE=$BEST_MODEL" | tee -a /tmp/jumpy-agent.log; return 0; fi
    echo "FCC_BENCH_FAIL=$name ROUTE=fcc_catalog PROBE=$BEST_MODEL RC=$rc" | tee -a /tmp/jumpy-agent.log
    tail -n 10 "/tmp/jumpy-fcc-bench-${name}.log" >>/tmp/jumpy-agent.log 2>/dev/null || true
    return 1
  }
  choose_agent() {
    local cache="$HOME/.cache/ai-dev-server/fcc-agent-winner.txt"
    mkdir -p "$HOME/.cache/ai-dev-server"
    local cached=''
    [ -s "$cache" ] && cached=$(cat "$cache")
    if [ -n "$cached" ] && agent_available "$cached" && benchmark_agent "$cached"; then echo "$cached"; return 0; fi
    local candidate
    for candidate in claude-code opencode; do
      [ "$candidate" = "$cached" ] && continue
      if agent_available "$candidate" && benchmark_agent "$candidate"; then printf '%s\n' "$candidate" > "$cache"; echo "$candidate"; return 0; fi
    done
    rm -f "$cache"; echo none
  }
  run_one_agent() {
    local name="$1" budget="$2" command
    ensure_fcc || return 1
    echo "AGENT_ATTEMPT=$name ROUTE=fcc_catalog PROBE=$BEST_MODEL" | tee -a /tmp/jumpy-agent.log
    case "$name" in
      claude-code) command='fcc-claude --permission-mode acceptEdits -p "$(cat /tmp/brief.txt)"' ;;
      opencode) command='fcc-opencode run "$(cat /tmp/brief.txt)"' ;;
      *) return 1 ;;
    esac
    setsid env -u GH_TOKEN -u GITHUB_TOKEN -u CODESPACES_PAT -u NVIDIA_NIM_API_KEY GIT_TERMINAL_PROMPT=0 SSH_AUTH_SOCK= GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null bash -lc "cd /workspaces/ai-dev-server/.jumpy-studio-cycle && git config --local credential.helper '' && $command" >>/tmp/jumpy-agent.log 2>&1 &
    local pid=$! loops=$((budget / 2)) timed_out=1
    for _ in $(seq 1 "$loops"); do if ! kill -0 "$pid" 2>/dev/null; then wait "$pid" || true; timed_out=0; break; fi; sleep 2; done
    if [ "$timed_out" -eq 1 ]; then kill -TERM -- "-$pid" 2>/dev/null || true; sleep 2; kill -KILL -- "-$pid" 2>/dev/null || true; wait "$pid" 2>/dev/null || true; EXEC_STATUS="${name}_timeout_${budget}s"; else EXEC_STATUS="${name}_completed"; fi
    if git diff --name-only | awk '$0 != "docs/AUTONOMOUS_STATE.md" {found=1} END {exit !found}'; then echo "AGENT_SELECTED=$name ROUTE=fcc_catalog PROBE=$BEST_MODEL" | tee -a /tmp/jumpy-agent.log; return 0; fi
    rm -f "$HOME/.cache/ai-dev-server/fcc-agent-winner.txt"; return 1
  }

  ensure_fcc || { echo 'AGENT_SELECTED=none FCC_UNAVAILABLE=1' | tee -a /tmp/jumpy-agent.log; return 0; }
  local winner; winner=$(choose_agent)
  echo "AGENT_BENCH_WINNER=$winner ROUTE=fcc_catalog PROBE=$BEST_MODEL" | tee -a /tmp/jumpy-agent.log
  if [ "$winner" != 'none' ]; then run_one_agent "$winner" "$primary_budget" && return 0; fi
  echo 'AGENT_SELECTED=none' | tee -a /tmp/jumpy-agent.log; return 0
}

case "$PHASE" in'''
s2,n=re.subn(agent_pattern,agent_replacement,s,count=1,flags=re.S)
if n!=1: raise SystemExit(f'v3 empirical-agent anchor mismatch ({n})')
p.write_text(s2)
PY
bash -n "$TMP"
exec bash "$TMP"
