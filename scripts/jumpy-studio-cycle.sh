#!/usr/bin/env bash
set -euo pipefail

: "${GH_TOKEN:?CODESPACES_PAT/GH_TOKEN is required}"
INFRA_REPO="dbrckk/ai-dev-server"
GAME_REPO="dbrckk/Jumpy"

NAME=$(gh codespace list --json name,repository --jq ".[] | select(.repository == \"$INFRA_REPO\") | .name" | head -n1)
test -n "$NAME" || { echo 'No ai-dev-server Codespace found'; exit 1; }
STATE=$(gh codespace view -c "$NAME" --json state --jq .state 2>/dev/null || true)
if [ "$STATE" != Available ]; then
  curl -fsSL -X POST \
    -H 'Accept: application/vnd.github+json' \
    -H "Authorization: Bearer $GH_TOKEN" \
    -H 'X-GitHub-Api-Version: 2026-03-10' \
    "https://api.github.com/user/codespaces/$NAME/start" >/dev/null || true
fi
for i in {1..120}; do
  STATE=$(gh codespace view -c "$NAME" --json state --jq .state 2>/dev/null || true)
  [ "$STATE" = Available ] && break
  sleep 5
done
[ "$STATE" = Available ] || { echo 'Codespace did not become available'; exit 1; }

cat > /tmp/jumpy-remote-cycle.sh <<'REMOTE'
#!/usr/bin/env bash
set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"
BASE="$HOME/.cache/ai-dev-server"
mkdir -p "$BASE/logs"

if ! curl -fsS --max-time 3 http://127.0.0.1:8082/health >/dev/null 2>&1; then
  nohup fcc-server >"$BASE/logs/fcc.log" 2>&1 < /dev/null &
  for i in {1..30}; do
    curl -fsS --max-time 2 http://127.0.0.1:8082/health >/dev/null 2>&1 && break
    sleep 1
  done
fi
curl -fsS --max-time 3 http://127.0.0.1:8082/health >/dev/null

WORK=/tmp/jumpy-studio-cycle
rm -rf "$WORK"
git clone --depth 1 https://github.com/dbrckk/Jumpy.git "$WORK" >/dev/null 2>&1
cd "$WORK"
BASE_SHA=$(git rev-parse HEAD)

CONTEXT=$(python - <<'PY'
from pathlib import Path
files=[
 'docs/AUTONOMOUS_TEAM.md','docs/AUTONOMOUS_STATE.md','docs/PRODUCTION_ROADMAP.md',
 'docs/GAME_DESIGN.md','docs/EXPERIMENTS.md','SETUP_REQUIRED.txt','README.md','project.godot',
 'scripts/main.gd','scripts/profile.gd','scripts/integrations.gd','assets/ui/theme.tres'
]
budget=105000; used=0
for name in files:
    p=Path(name)
    if not p.exists(): continue
    text=p.read_text(errors='replace')
    remaining=budget-used
    if remaining <= 0: break
    text=text[:remaining]
    print(f'\n===== {name} =====\n{text}')
    used += len(text)
PY
)

python - <<'PY' > /tmp/jumpy-candidates.txt
from pathlib import Path
main=Path('scripts/main.gd').read_text()
items=[]
if 'DAILY BEST %d' not in main and 'DAILY SEED • SAME WORLD FOR EVERYONE' in main:
    items.append(('DAILY_BEST_MENU','Surface the daily best score in daily mode.'))
if 'PERFECT %d  •  COINS %d' not in main and 'ui.gameover.text = "SCORE %d\\nBEST %d\\n%s"' in main:
    items.append(('RUN_STATS_GAMEOVER','Improve post-run feedback with skill/run stats.'))
for ident,desc in items:
    print(f'{ident}: {desc}')
PY

MODEL=$(grep -E '^MODEL=' "$HOME/.fcc/.env" | tail -n1 | cut -d= -f2-)
CANDIDATES=$(cat /tmp/jumpy-candidates.txt 2>/dev/null || true)
STRATEGY_PROMPT=$(cat <<'PROMPT'
Act as Jumpy's complete senior game-development studio. Audit the CURRENT repository systemically and adversarially.

Evaluate creative direction, one-touch game feel, mastery/difficulty, engineering, architecture, UX/UI, visual feedback, audio/haptics, accessibility, retention/progression, social/viral loops, performance, QA/testability, analytics/experimentation, Android/release and compliance. Find root causes, dependencies and second-order effects. If a path is blocked, open alternate routes rather than stopping.

For this cycle produce:
1. weakest domains with concrete repository evidence;
2. ONE highest-value safe objective feasible without a new external account/API/paid service;
3. measurable acceptance criteria;
4. next 3-7 actions in priority order;
5. blockers plus alternate routes;
6. roadmap changes if warranted.

The deterministic shortcuts below are only accelerators. Select one only if it truly is the highest-value action, using exactly `SHORTCUT: ID`. Otherwise use `SHORTCUT: NONE`.

Never inflate quality scores or claim AAA completion without evidence. Preserve one-touch simplicity while increasing depth, polish, robustness and test evidence.
PROMPT
)
PAYLOAD=$(python - "$MODEL" "$STRATEGY_PROMPT\n\nSHORTCUTS:\n$CANDIDATES\n\nCURRENT REPOSITORY:\n$CONTEXT" <<'PY'
import json,sys
print(json.dumps({'model':sys.argv[1],'max_tokens':3600,'messages':[{'role':'user','content':sys.argv[2]}],'stream':False}))
PY
)
RESPONSE=$(curl -sS --max-time 110 -H 'Content-Type: application/json' -X POST http://127.0.0.1:8082/v1/messages --data-binary "$PAYLOAD" || true)
python - "$RESPONSE" <<'PY' > /tmp/jumpy-strategy.txt
import json,sys
fallback='Strategic model response unavailable. Preserve current roadmap, inspect the repository directly, and implement the safest highest-impact local improvement.'
try:
    d=json.loads(sys.argv[1]); text='\n'.join(str(x.get('text','')) for x in d.get('content',[]) if isinstance(x,dict) and x.get('type')=='text').strip()
except Exception: text=''
print((text or fallback)[-10000:])
PY

CHOICE=$(python - /tmp/jumpy-strategy.txt /tmp/jumpy-candidates.txt <<'PY'
import re,sys
text=open(sys.argv[1],errors='replace').read()
ids=[line.split(':',1)[0].strip() for line in open(sys.argv[2],errors='replace') if ':' in line]
m=re.search(r'(?im)^\s*SHORTCUT\s*:\s*([A-Z0-9_]+)\s*$',text)
print(m.group(1) if m and m.group(1) in ids else '')
PY
)

EXECUTION_LANE='open-ended'
EXECUTION_STATUS='not_started'
IMPLEMENTATION_NOTE=''
MICRO_BRIEF=''

if [ -n "$CHOICE" ]; then
  EXECUTION_LANE="deterministic:$CHOICE"
  EXECUTION_STATUS='completed'
  python - "$CHOICE" <<'PY'
from pathlib import Path
import sys
p=Path('scripts/main.gd'); s=p.read_text(); task=sys.argv[1]
if task == 'DAILY_BEST_MENU':
    old='\tui.subtitle.text = "DAILY SEED • SAME WORLD FOR EVERYONE" if value else "TAP • LAND • FLOW"'
    new='\tui.subtitle.text = "DAILY SEED • DAILY BEST %d" % int(Profile.data.daily_best) if value else "TAP • LAND • FLOW"'
elif task == 'RUN_STATS_GAMEOVER':
    old='\tui.gameover.text = "SCORE %d\\nBEST %d\\n%s" % [score, int(Profile.data.best_score), "NEW BEST" if score >= int(Profile.data.best_score) and score > 0 else "FLOW BROKEN"]'
    new='\tui.gameover.text = "SCORE %d\\nBEST %d\\nPERFECT %d  •  COINS %d\\n%s" % [score, int(Profile.data.best_score), perfects, run_coins, "NEW BEST" if score >= int(Profile.data.best_score) and score > 0 else "FLOW BROKEN"]'
else: raise SystemExit('unknown shortcut')
if s.count(old) != 1: raise SystemExit('shortcut anchor mismatch: '+task)
p.write_text(s.replace(old,new,1))
PY
else
  STRATEGY=$(cat /tmp/jumpy-strategy.txt)
  MICRO_PROMPT=$(cat <<'PROMPT'
Turn the strategic objective below into ONE atomic implementation slice for the current cycle.

The slice must be independently useful and complete, fit in at most 2 existing text files and about 160 changed lines, compile by itself, and create no dangling references to functions/UI/data that are planned for later. If the objective is larger, choose the best Phase 1 foundation that can ship safely now. Prefer foundations that unlock the next phase. Explicitly state what NOT to implement this cycle.

Return a concise implementation brief only: target files, exact behavior, completion conditions, and deferred follow-up. Do not write code.
PROMPT
)
  MPAYLOAD=$(python - "$MODEL" "$MICRO_PROMPT\n\nSTRATEGIC REVIEW:\n$STRATEGY\n\nCURRENT SOURCE SUMMARY:\n$CONTEXT" <<'PY'
import json,sys
print(json.dumps({'model':sys.argv[1],'max_tokens':900,'messages':[{'role':'user','content':sys.argv[2]}],'stream':False}))
PY
  )
  MRESP=$(curl -sS --max-time 45 -H 'Content-Type: application/json' -X POST http://127.0.0.1:8082/v1/messages --data-binary "$MPAYLOAD" || true)
  MICRO_BRIEF=$(python - "$MRESP" <<'PY'
import json,sys
try:
    d=json.loads(sys.argv[1]); t='\n'.join(str(x.get('text','')) for x in d.get('content',[]) if isinstance(x,dict) and x.get('type')=='text').strip()
except Exception: t=''
print(t[-3500:] if t else 'Implement the smallest complete, independently compiling foundation of the strategic objective. Limit to two files; create no dangling references; defer UI or secondary behavior if needed.')
PY
  )

  cat > /tmp/jumpy-brief.txt <<EOF
Work as Jumpy's senior implementation pair. Implement the atomic micro-deliverable below in this isolated clone. Do not broaden scope.

MICRO-DELIVERABLE:
$MICRO_BRIEF

Rules:
- Godot 4.7 compatible; preserve deterministic daily behavior and one-touch simplicity.
- Modify at most 2 existing text files and about 160 changed lines.
- Finish a coherent compiling slice before polishing it.
- Never add a call, button, field or symbol unless its required implementation also exists in this same cycle.
- If time becomes tight, remove incomplete work and leave a smaller valid slice.
- Do not commit or push; do not touch .github/, secrets, signing, keystores, external credentials, paid services or binary assets.
- Do not add a new external dependency.
- Inspect the final diff for dangling references before exiting.

STRATEGIC CONTEXT:
$STRATEGY
EOF

  setsid bash -lc 'fcc-opencode run "$(cat /tmp/jumpy-brief.txt)"' >/tmp/jumpy-implement.log 2>&1 &
  AGENT_PID=$!
  EXECUTION_STATUS='running'
  for _ in {1..75}; do
    if ! kill -0 "$AGENT_PID" 2>/dev/null; then
      wait "$AGENT_PID" || true
      EXECUTION_STATUS='completed'
      break
    fi
    sleep 2
  done
  if kill -0 "$AGENT_PID" 2>/dev/null; then
    EXECUTION_STATUS='timeout_150s'
    kill -TERM -- "-$AGENT_PID" 2>/dev/null || true
    sleep 3
    kill -KILL -- "-$AGENT_PID" 2>/dev/null || true
    wait "$AGENT_PID" 2>/dev/null || true
  fi
  if [ -s /tmp/jumpy-implement.log ]; then
    IMPLEMENTATION_NOTE=$(python - <<'PY'
from pathlib import Path
text=Path('/tmp/jumpy-implement.log').read_text(errors='replace')
print(' '.join(text.splitlines()[-30:])[-2200:])
PY
    )
  fi
fi

echo "EXECUTION_LANE=$EXECUTION_LANE"
echo "EXECUTION_STATUS=$EXECUTION_STATUS"

python - <<'PY' > /tmp/jumpy-safety.txt
import subprocess
changed=subprocess.check_output(['git','diff','--name-only'],text=True).splitlines()
forbidden=[p for p in changed if p.startswith('.github/') or any(x in p.lower() for x in ['secret','keystore','.jks','.p12'])]
source=[p for p in changed if p != 'docs/AUTONOMOUS_STATE.md']
if forbidden or len(source)>2:
    print('REJECTED: '+(','.join(changed) or 'none'))
    subprocess.run(['git','reset','--hard','HEAD'],check=False,stdout=subprocess.DEVNULL)
else:
    print('ACCEPTABLE: '+(','.join(changed) or 'none'))
PY
SAFETY_NOTE=$(cat /tmp/jumpy-safety.txt)

python - "$CHOICE" "$EXECUTION_LANE" "$EXECUTION_STATUS" "$SAFETY_NOTE" "$IMPLEMENTATION_NOTE" "$BASE_SHA" "$MICRO_BRIEF" <<'PY'
from pathlib import Path
import datetime,re,sys
p=Path('docs/AUTONOMOUS_STATE.md'); s=p.read_text() if p.exists() else '# Jumpy — Autonomous Living State\n'
strategy=Path('/tmp/jumpy-strategy.txt').read_text(errors='replace').strip()[-9000:]
remaining=Path('/tmp/jumpy-candidates.txt').read_text(errors='replace').strip()
choice,lane,status,safety,note,base,micro=sys.argv[1:8]
focus=choice or 'OPEN_ENDED_STRATEGIC_TASK'; now=datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
block=f'''<!-- AUTO_CYCLE_START -->
## Latest autonomous strategic cycle
**Time:** {now}  
**Base commit:** `{base[:12]}`  
**Execution focus:** `{focus}`  
**Lane:** `{lane}`  
**Executor status:** `{status}`

### Multidisciplinary review and immediate plan
{strategy}

### Atomic implementation slice
{micro if micro else 'Deterministic shortcut selected; no separate micro-planning required.'}

### Executor evidence
Safety gate: {safety}

{note if note else 'No useful executor transcript was produced. Treat this as execution evidence and choose an alternate implementation route next cycle if no source change survives.'}

### Remaining deterministic shortcuts
{remaining if remaining else 'None. Strategy is not constrained by a fixed feature catalog; continue through open-ended implementation.'}

### Operating instruction
Re-audit next cycle. Failed approaches are evidence: split scope further, change architecture or choose an alternate route. Never repeat the same failed implementation shape unchanged.
<!-- AUTO_CYCLE_END -->'''
pattern=r'<!-- AUTO_CYCLE_START -->.*?<!-- AUTO_CYCLE_END -->'
s=re.sub(pattern,block,s,flags=re.S) if re.search(pattern,s,re.S) else s.rstrip()+'\n\n'+block+'\n'
p.write_text(s)
PY

CHANGED=$(git diff --name-only)
[ -n "$CHANGED" ] || { echo 'RESULT=NO_CHANGE'; exit 0; }
echo 'RESULT=PATCH'
echo "TASK=${CHOICE:-OPEN_ENDED_STRATEGIC_TASK}"
echo "FILES=$(printf '%s\n' "$CHANGED" | paste -sd, -)"
echo "PATCH_B64=$(git diff --binary | base64 -w0)"
REMOTE

DATA=$(base64 -w0 /tmp/jumpy-remote-cycle.sh)
set +e
timeout -k 5s 420s gh codespace ssh -c "$NAME" "printf '%s' '$DATA' | base64 -d | bash" > /tmp/jumpy-cycle.out
REMOTE_RC=$?
set -e
sed -E 's/(PATCH_B64=).*/\1[REDACTED]/' /tmp/jumpy-cycle.out || true
if [ "$REMOTE_RC" -ne 0 ]; then echo "Remote cycle failed with rc=$REMOTE_RC"; exit 1; fi
RESULT=$(grep '^RESULT=' /tmp/jumpy-cycle.out | tail -n1 | cut -d= -f2- || true)
[ "$RESULT" = PATCH ] || { echo "Cycle result: ${RESULT:-UNKNOWN}"; exit 0; }
grep '^PATCH_B64=' /tmp/jumpy-cycle.out | tail -n1 | cut -d= -f2- | base64 -d > /tmp/jumpy.patch

rm -rf /tmp/jumpy-validated
gh auth setup-git >/dev/null 2>&1 || true
git clone --depth 1 https://github.com/dbrckk/Jumpy.git /tmp/jumpy-validated >/dev/null 2>&1
cd /tmp/jumpy-validated
git apply --check /tmp/jumpy.patch
git apply /tmp/jumpy.patch

curl -fL -o /tmp/godot.zip https://github.com/godotengine/godot/releases/download/4.7.2-stable/Godot_v4.7.2-stable_linux.x86_64.zip >/dev/null 2>&1
rm -rf /tmp/godot-jumpy && mkdir -p /tmp/godot-jumpy
unzip -q /tmp/godot.zip -d /tmp/godot-jumpy
mv /tmp/godot-jumpy/Godot_v4.7.2-stable_linux.x86_64 /tmp/godot-jumpy/godot
chmod +x /tmp/godot-jumpy/godot
set +e
/tmp/godot-jumpy/godot --headless --path . --editor --quit > /tmp/jumpy-godot.log 2>&1
GODOT_RC=$?
set -e
cat /tmp/jumpy-godot.log
if [ "$GODOT_RC" -ne 0 ] || grep -E 'SCRIPT ERROR|Parse Error|Cannot parse|Failed loading resource' /tmp/jumpy-godot.log; then
  echo 'Godot rejected implementation; preserving only diagnostic state.'
  git diff --name-only | while read -r f; do [ "$f" = 'docs/AUTONOMOUS_STATE.md' ] || git checkout HEAD -- "$f"; done
  python - <<'PY'
from pathlib import Path
p=Path('docs/AUTONOMOUS_STATE.md'); s=p.read_text(); marker='\n### Validation outcome\nGodot 4.7.2 rejected the implementation candidate. Source changes were discarded. Next cycle must split scope further or choose a different route.\n'; pos=s.find('<!-- AUTO_CYCLE_END -->')
if pos >= 0: s=s[:pos]+marker+s[pos:]
p.write_text(s)
PY
fi

test -f docs/AUTONOMOUS_TEAM.md
test -f docs/AUTONOMOUS_STATE.md
test -f docs/PRODUCTION_ROADMAP.md
test -f SETUP_REQUIRED.txt

git config user.name 'jumpy-autocycle[bot]'
git config user.email '41898282+github-actions[bot]@users.noreply.github.com'
git diff --name-only -z | xargs -0 -r git add --
git diff --cached --quiet && { echo 'No effective validated or diagnostic change'; exit 0; }
git commit -m 'Autocycle: adaptive studio evolution'
git push origin HEAD:main
