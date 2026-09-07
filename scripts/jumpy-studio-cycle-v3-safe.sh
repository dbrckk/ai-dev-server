#!/usr/bin/env bash
set -euo pipefail

python - <<'PY'
from pathlib import Path
import re
p = Path('scripts/jumpy-studio-cycle-v3.sh')
s = p.read_text()

old = 'Implement ONE smallest complete safe improvement from the strategic review below. Modify at most 2 existing text files and about 100 changed lines. No external downloads, package installs, dependencies, network calls, credentials, .github edits, binary assets or release configuration. Produce useful edits early and leave no undefined symbols. If the main idea is too large, choose a smaller local improvement.'
new = 'EDIT FIRST. Modify ONLY scripts/main.gd with one small compile-complete improvement. Use TABS ONLY for GDScript indentation. Do not redo completed work. Priority: reduced-motion perfect/clutch feedback, then reduced-motion death feedback, then high-contrast readability, then the next smallest gameplay/UX improvement. Do not spend the cycle only reading. Keep the diff under about 100 changed lines. No downloads, installs, dependencies, network calls, credentials, .github edits, binary assets or release config. Leave no undefined symbols.'
if old not in s:
    raise SystemExit('open-ended prompt anchor mismatch')
s = s.replace(old, new, 1)

# Probe current FCC models through the exact Anthropic-compatible gateway.
# A plain text response is not enough for an autonomous coding agent: the winning
# model must demonstrate structured tool use before it can be selected.
health = 'curl -fsS --max-time 3 http://127.0.0.1:8082/health >/dev/null\n\nMODEL=$(grep -E \'^MODEL=\' "$HOME/.fcc/.env" | tail -n1 | cut -d= -f2-)'
probe = r'''curl -fsS --max-time 3 http://127.0.0.1:8082/health >/dev/null

BEST_MODEL=$(python - <<'PYMODEL'
import json, urllib.request
# Prefer current coding/agentic families exposed by FCC/NVIDIA. Eligibility requires
# a live structured tool call, not merely successful text generation.
candidates = [
    'nvidia_nim/z-ai/glm5.1',
    'nvidia_nim/moonshotai/kimi-k2.5',
    'nvidia_nim/minimaxai/minimax-m2.5',
    'nvidia_nim/nvidia/nemotron-3-ultra-550b-a55b',
    'nvidia_nim/nvidia/nemotron-3.5-lightning-30b-a3b',
    'nvidia_nim/nvidia/nemotron-3-super-120b-a12b',
]
tool={'name':'read_probe','description':'Return a probe value','input_schema':{'type':'object','properties':{'value':{'type':'string'}},'required':['value']}}
for model in candidates:
    body=json.dumps({'model':model,'max_tokens':96,'messages':[{'role':'user','content':'Use the read_probe tool exactly once with value OK. Do not answer with plain text.'}],'tools':[tool],'tool_choice':{'type':'tool','name':'read_probe'},'stream':False}).encode()
    req=urllib.request.Request('http://127.0.0.1:8082/v1/messages',data=body,headers={'Content-Type':'application/json'},method='POST')
    try:
        with urllib.request.urlopen(req,timeout=15) as r:
            data=json.loads(r.read().decode('utf-8','replace'))
            blocks=data.get('content',[])
            if r.status == 200 and any(isinstance(x,dict) and x.get('type')=='tool_use' and x.get('name')=='read_probe' for x in blocks):
                print(model)
                break
    except Exception:
        pass
PYMODEL
)
[ -n "$BEST_MODEL" ] || BEST_MODEL=$(grep -E '^MODEL=' "$HOME/.fcc/.env" | tail -n1 | cut -d= -f2- | tr -d '"')
export BEST_MODEL
echo "BEST_MODEL=$BEST_MODEL"
MODEL="$BEST_MODEL"'''
if health not in s:
    raise SystemExit('model probe anchor mismatch')
s = s.replace(health, probe, 1)

# Claude Code is the primary autonomous editor when available because FCC natively
# preserves its Anthropic tool protocol. acceptEdits removes the non-interactive
# permission deadlock without granting unrestricted shell bypass. OpenCode remains
# an independent fallback. Both run without repository/provider credentials.
pattern = r'''run_agent\(\) \{\n.*?\n\}\n\ncase \"\$PHASE\" in'''
replacement = r'''run_agent() {
  local seconds="$1"
  local primary_budget=$((seconds * 2 / 3))
  local fallback_budget=$((seconds - primary_budget))
  EXEC_STATUS="no_agent"
  : >/tmp/jumpy-agent.log

  ensure_fcc() {
    if curl -fsS --max-time 3 http://127.0.0.1:8082/health >/dev/null 2>&1; then return 0; fi
    nohup fcc-server >"$BASE/logs/fcc.log" 2>&1 < /dev/null &
    for _ in {1..30}; do curl -fsS --max-time 2 http://127.0.0.1:8082/health >/dev/null 2>&1 && return 0; sleep 1; done
    return 1
  }

  run_one_agent() {
    local name="$1" budget="$2" command="$3"
    ensure_fcc || return 1
    echo "AGENT_ATTEMPT=$name MODEL=$BEST_MODEL" | tee -a /tmp/jumpy-agent.log
    setsid env -u GH_TOKEN -u GITHUB_TOKEN -u CODESPACES_PAT -u NVIDIA_NIM_API_KEY \
      BEST_MODEL="$BEST_MODEL" GIT_TERMINAL_PROMPT=0 SSH_AUTH_SOCK= GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null \
      bash -lc "cd /workspaces/ai-dev-server/.jumpy-studio-cycle && git config --local credential.helper '' && $command" \
      >>/tmp/jumpy-agent.log 2>&1 &
    local pid=$! loops=$((budget / 2)) timed_out=1
    for _ in $(seq 1 "$loops"); do
      if ! kill -0 "$pid" 2>/dev/null; then wait "$pid" || true; timed_out=0; break; fi
      sleep 2
    done
    if [ "$timed_out" -eq 1 ]; then
      kill -TERM -- "-$pid" 2>/dev/null || true; sleep 2; kill -KILL -- "-$pid" 2>/dev/null || true; wait "$pid" 2>/dev/null || true
      EXEC_STATUS="${name}_timeout_${budget}s"
    else
      EXEC_STATUS="${name}_completed"
    fi
    if git diff --name-only | awk '$0 != "docs/AUTONOMOUS_STATE.md" {found=1} END {exit !found}'; then
      echo "AGENT_SELECTED=$name MODEL=$BEST_MODEL" | tee -a /tmp/jumpy-agent.log
      return 0
    fi
    return 1
  }

  if command -v fcc-claude >/dev/null 2>&1 && command -v claude >/dev/null 2>&1; then
    run_one_agent "claude-code" "$primary_budget" 'fcc-claude --model "$BEST_MODEL" --permission-mode acceptEdits -p "$(cat /tmp/brief.txt)"' && return 0
  fi
  if command -v fcc-opencode >/dev/null 2>&1 && command -v opencode >/dev/null 2>&1; then
    run_one_agent "opencode" "$fallback_budget" 'fcc-opencode run --model "$BEST_MODEL" "$(cat /tmp/brief.txt)"' && return 0
  fi
  echo 'AGENT_SELECTED=none' | tee -a /tmp/jumpy-agent.log
  return 0
}

case "$PHASE" in'''
s2, n = re.subn(pattern, replacement, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f'agent router anchor mismatch ({n})')
s = s2

# If agents produce no source change, continue with the next known-safe atomic improvement.
agent_log_anchor = "if [ -s /tmp/jumpy-agent.log ]; then"
fallback = r'''if [ "$PHASE" = "OPEN_ENDED" ] && ! git diff --name-only | awk '$0 != "docs/AUTONOMOUS_STATE.md" {found=1} END {exit !found}'; then
  python - <<'PYFALLBACK'
from pathlib import Path
p=Path('scripts/main.gd'); s=p.read_text()
changed=False
if 'var feedback_scale: float = 0.35 if bool(Profile.data.reduced_motion) else 1.0' not in s:
    anchor='\tvar clutch: bool = not perfect and edge_distance <= PLAYER_R * 0.72\n'
    if anchor in s:
        s=s.replace(anchor, anchor+'\tvar feedback_scale: float = 0.35 if bool(Profile.data.reduced_motion) else 1.0\n',1)
        s=s.replace('\t\tcamera_kick = 9.0\n\t\tflash = 0.24\n\t\tburst(Vector2(PLAYER_X, player_y + PLAYER_R), Color("ffffff"), 22, 420.0)\n', '\t\tcamera_kick = 9.0 * feedback_scale\n\t\tflash = 0.24 * feedback_scale\n\t\tburst(Vector2(PLAYER_X, player_y + PLAYER_R), Color("ffffff"), maxi(4, int(22.0 * feedback_scale)), 420.0 * feedback_scale)\n',1)
        s=s.replace('\t\tcamera_kick = 12.0\n\t\tburst(Vector2(PLAYER_X, player_y + PLAYER_R), Color("ffe66d"), 18, 360.0)\n', '\t\tcamera_kick = 12.0 * feedback_scale\n\t\tburst(Vector2(PLAYER_X, player_y + PLAYER_R), Color("ffe66d"), maxi(4, int(18.0 * feedback_scale)), 360.0 * feedback_scale)\n',1)
        changed=True
elif 'var death_feedback_scale: float = 0.3 if bool(Profile.data.reduced_motion) else 1.0' not in s:
    anchor='\trefresh_settings_ui()\n\tcamera_kick = 18.0\n\tflash = 0.35\n\tburst(Vector2(PLAYER_X, player_y), skin_color(), 35, 520.0)\n'
    repl='\trefresh_settings_ui()\n\tvar death_feedback_scale: float = 0.3 if bool(Profile.data.reduced_motion) else 1.0\n\tcamera_kick = 18.0 * death_feedback_scale\n\tflash = 0.35 * death_feedback_scale\n\tburst(Vector2(PLAYER_X, player_y), skin_color(), maxi(5, int(35.0 * death_feedback_scale)), 520.0 * death_feedback_scale)\n'
    if anchor in s:
        s=s.replace(anchor,repl,1); changed=True
if changed: p.write_text(s)
PYFALLBACK
  if git diff --name-only | grep -q '^scripts/main.gd$'; then
    EXEC_STATUS="${EXEC_STATUS}+deterministic_fallback"
    NOTE='Agent fallback applied the next compile-checkable Reduced Motion feedback improvement.'
  fi
fi

# Canonicalize mixed GDScript indentation before strict validation.
python - <<'PYINDENT'
from pathlib import Path
p=Path('scripts/main.gd')
if p.exists():
    out=[]
    for line in p.read_text().splitlines(keepends=True):
        body=line.rstrip('\r\n'); ending=line[len(body):]; i=0; cols=0
        while i < len(body) and body[i] in (' ', '\t'):
            cols += (4-cols%4) if body[i]=='\t' else 1; i+=1
        if i: body=('\t'*(cols//4))+(' '*(cols%4))+body[i:]
        out.append(body+ending)
    p.write_text(''.join(out))
PYINDENT

'''
if agent_log_anchor not in s:
    raise SystemExit('agent-log anchor mismatch')
s = s.replace(agent_log_anchor, fallback + agent_log_anchor, 1)

# No documentation-only fake progress.
changed_anchor = 'CHANGED=$(git diff --name-only)\n[ -n "$CHANGED" ] || { echo \'RESULT=NO_CHANGE\'; exit 0; }'
changed_replacement = '''CHANGED=$(git diff --name-only)
[ -n "$CHANGED" ] || { echo 'RESULT=NO_CHANGE'; exit 0; }
if [ "$PHASE" = "OPEN_ENDED" ] && ! printf '%s\n' "$CHANGED" | awk '$0 != "docs/AUTONOMOUS_STATE.md" {found=1} END {exit !found}'; then
  git checkout -- docs/AUTONOMOUS_STATE.md
  echo 'RESULT=NO_SOURCE_CHANGE'
  exit 0
fi'''
if changed_anchor not in s:
    raise SystemExit('no-source anchor mismatch')
s = s.replace(changed_anchor, changed_replacement, 1)

p.write_text(s)
PY

LOG=/tmp/jumpy-v3-safe.log
set +e
bash scripts/jumpy-studio-cycle-v3-runner.sh 2>&1 | tee "$LOG"
RC=${PIPESTATUS[0]}
set -e
if [ "$RC" -eq 0 ]; then exit 0; fi
exit "$RC"
