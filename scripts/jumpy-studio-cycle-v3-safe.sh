#!/usr/bin/env bash
set -euo pipefail

python - <<'PY'
from pathlib import Path
import re
p = Path('scripts/jumpy-studio-cycle-v3.sh')
s = p.read_text()

old = 'Implement ONE smallest complete safe improvement from the strategic review below. Modify at most 2 existing text files and about 100 changed lines. No external downloads, package installs, dependencies, network calls, credentials, .github edits, binary assets or release configuration. Produce useful edits early and leave no undefined symbols. If the main idea is too large, choose a smaller local improvement.'
new = 'EDIT FIRST. Within the first concrete action, modify ONLY scripts/main.gd with one small compile-complete improvement. Use TABS ONLY for GDScript indentation. Do not redo pulse if it already respects reduced_motion. Priority order: (1) reduced-motion perfect/clutch feedback; (2) reduced-motion death feedback; (3) high-contrast gameplay readability; then the next smallest local gameplay/UX improvement. Do not spend the cycle only reading. Keep the diff under about 100 changed lines. No external downloads, package installs, dependencies, network calls, credentials, .github edits, binary assets or release configuration. Leave no undefined symbols.'
if old not in s:
    raise SystemExit('open-ended prompt anchor mismatch')
s = s.replace(old, new, 1)

health = 'curl -fsS --max-time 3 http://127.0.0.1:8082/health >/dev/null\n\nMODEL=$(grep -E \'^MODEL=\' "$HOME/.fcc/.env" | tail -n1 | cut -d= -f2-)'
probe = r'''curl -fsS --max-time 3 http://127.0.0.1:8082/health >/dev/null

BEST_MODEL=$(python - <<'PYMODEL'
import json, urllib.request
candidates = [
    'nvidia_nim/deepseek-ai/deepseek-v4-pro-0813',
    'nvidia_nim/nvidia/nemotron-3-ultra-550b-a55b',
    'nvidia_nim/moonshotai/kimi-k2.6',
    'nvidia_nim/nvidia/nemotron-3.5-lightning-30b-a3b',
    'nvidia_nim/nvidia/nemotron-3-super-120b-a12b',
]
for model in candidates:
    body=json.dumps({'model':model,'max_tokens':12,'messages':[{'role':'user','content':'Reply OK'}],'stream':False}).encode()
    req=urllib.request.Request('http://127.0.0.1:8082/v1/messages',data=body,headers={'Content-Type':'application/json'},method='POST')
    try:
        with urllib.request.urlopen(req,timeout=18) as r:
            data=json.loads(r.read().decode('utf-8','replace'))
            text=' '.join(str(x.get('text','')) for x in data.get('content',[]) if isinstance(x,dict))
            if r.status == 200 and text.strip():
                print(model)
                break
    except Exception:
        pass
PYMODEL
)
[ -n "$BEST_MODEL" ] || { echo 'MODEL_PROBE_FAILED'; exit 2; }
export BEST_MODEL
echo "BEST_MODEL=$BEST_MODEL"

# Persist the good route for future sessions. Running agents use --model directly, so the
# healthy FCC process does not need to be restarted just to apply this file update.
python - "$HOME/.fcc/.env" "$BEST_MODEL" <<'PYMODELENV'
from pathlib import Path
import re,sys
p=Path(sys.argv[1]); model=sys.argv[2]; s=p.read_text()
for key in ['MODEL','MODEL_OPUS','MODEL_SONNET','MODEL_HAIKU']:
    line=f'{key}="{model}"'
    if re.search(rf'(?m)^{key}=.*$',s): s=re.sub(rf'(?m)^{key}=.*$',line,s)
    else: s += '\n'+line
p.write_text(s)
PYMODELENV

MODEL="$BEST_MODEL"'''
if health not in s:
    raise SystemExit('model probe anchor mismatch')
s = s.replace(health, probe, 1)

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
    for _ in {1..30}; do
      curl -fsS --max-time 2 http://127.0.0.1:8082/health >/dev/null 2>&1 && return 0
      sleep 1
    done
    echo 'FCC_UNAVAILABLE' | tee -a /tmp/jumpy-agent.log
    return 1
  }

  run_one_agent() {
    local name="$1" budget="$2" command="$3"
    ensure_fcc || return 1
    echo "AGENT_ATTEMPT=$name" | tee -a /tmp/jumpy-agent.log
    setsid env -u GH_TOKEN -u GITHUB_TOKEN -u CODESPACES_PAT -u NVIDIA_NIM_API_KEY \
      GIT_TERMINAL_PROMPT=0 SSH_AUTH_SOCK= GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null BEST_MODEL="$BEST_MODEL" \
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
      echo "AGENT_SELECTED=$name" | tee -a /tmp/jumpy-agent.log
      return 0
    fi
    return 1
  }

  if command -v fcc-claude >/dev/null 2>&1 && command -v claude >/dev/null 2>&1; then
    run_one_agent "claude-code" "$primary_budget" 'fcc-claude --model "$BEST_MODEL" -p "$(cat /tmp/brief.txt)"' && return 0
  fi
  if command -v fcc-codex >/dev/null 2>&1 && command -v codex >/dev/null 2>&1; then
    run_one_agent "codex" "$fallback_budget" 'fcc-codex exec --model "$BEST_MODEL" "$(cat /tmp/brief.txt)"' && return 0
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

anchor = "if [ -s /tmp/jumpy-agent.log ]; then"
repair = r'''python - <<'PY2'
from pathlib import Path
p=Path('scripts/main.gd')
if p.exists():
    out=[]
    for line in p.read_text().splitlines(keepends=True):
        body=line.rstrip('\r\n'); ending=line[len(body):]; i=0; cols=0
        while i < len(body) and body[i] in (' ', '\t'):
            cols += (4 - cols % 4) if body[i]=='\t' else 1; i += 1
        if i: body=('\t'*(cols//4))+(' '*(cols%4))+body[i:]
        out.append(body+ending)
    p.write_text(''.join(out))
PY2

'''
if anchor not in s:
    raise SystemExit('agent-log anchor mismatch')
s = s.replace(anchor, repair + anchor, 1)

changed_anchor = 'CHANGED=$(git diff --name-only)\n[ -n "$CHANGED" ] || { echo \'RESULT=NO_CHANGE\'; exit 0; }'
changed_replacement = '''CHANGED=$(git diff --name-only)
[ -n "$CHANGED" ] || { echo 'RESULT=NO_CHANGE'; exit 0; }
if [ "$PHASE" = "OPEN_ENDED" ] && ! printf '%s\n' "$CHANGED" | awk '$0 != "docs/AUTONOMOUS_STATE.md" {found=1} END {exit !found}'; then
  echo '=== AGENT DIAGNOSTIC ==='
  tail -n 40 /tmp/jumpy-agent.log 2>/dev/null || true
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
