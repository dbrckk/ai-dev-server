#!/usr/bin/env bash
set -euo pipefail

: "${GH_TOKEN:?CODESPACES_PAT/GH_TOKEN is required}"
INFRA_REPO="dbrckk/ai-dev-server"
GAME_REPO="dbrckk/Jumpy"

NAME=$(gh codespace list --json name,repository --jq ".[] | select(.repository == \"$INFRA_REPO\") | .name" | head -n1)
test -n "$NAME" || { echo 'No ai-dev-server Codespace found'; exit 1; }
STATE=$(gh codespace view -c "$NAME" --json state --jq .state)
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

CONTEXT=$(python - <<'PY'
from pathlib import Path
files=[
 'docs/AUTONOMOUS_TEAM.md','docs/AUTONOMOUS_STATE.md','docs/PRODUCTION_ROADMAP.md',
 'docs/GAME_DESIGN.md','SETUP_REQUIRED.txt','README.md','project.godot',
 'scripts/main.gd','scripts/profile.gd','scripts/integrations.gd','assets/ui/theme.tres'
]
budget=100000; used=0
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

# High-confidence executable shortcuts. They are options, never mandatory priorities.
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
Act as the complete senior game-development studio defined in docs/AUTONOMOUS_TEAM.md. Audit the CURRENT Jumpy repository systemically and adversarially.

Evaluate creative direction, one-touch game feel, mastery/difficulty, engineering, architecture, UX/UI, visual feedback, audio/haptics, accessibility, retention/progression, social/viral loops, performance, QA/testability, analytics/experimentation, Android/release and compliance. Find root causes and second-order effects. If a path is blocked, open alternative paths instead of stopping.

Produce a concise but concrete cycle plan:
- weakest domains and strongest evidence;
- ONE highest-value safe implementation feasible now without a new external account/API/paid service;
- acceptance criteria;
- next 3–7 actions in priority order;
- blockers and alternative routes;
- roadmap changes if needed.

The following deterministic shortcuts MAY be selected only if one truly is the highest-value immediate action. If so, write its exact ID on a separate line as `SHORTCUT: ID`. Otherwise write `SHORTCUT: NONE` and the open-ended executor will implement your actual priority.

Do not lower the quality bar to claim completion. Preserve the one-touch core while increasing depth, polish and evidence.
PROMPT
)
PAYLOAD=$(python - "$MODEL" "$STRATEGY_PROMPT\n\nSHORTCUTS:\n$CANDIDATES\n\nCURRENT REPOSITORY:\n$CONTEXT" <<'PY'
import json,sys
print(json.dumps({'model':sys.argv[1],'max_tokens':4800,'messages':[{'role':'user','content':sys.argv[2]}],'stream':False}))
PY
)
RESPONSE=$(curl -sS --max-time 180 -H 'Content-Type: application/json' -X POST http://127.0.0.1:8082/v1/messages --data-binary "$PAYLOAD" || true)
python - "$RESPONSE" <<'PY' > /tmp/jumpy-strategy.txt
import json,sys
try:
    d=json.loads(sys.argv[1])
    text='\n'.join(str(x.get('text','')) for x in d.get('content',[]) if isinstance(x,dict) and x.get('type')=='text')
except Exception:
    text='Strategic model response unavailable. Re-audit using repository evidence and choose a safe local improvement.'
print(text.strip()[-12000:])
PY

CHOICE=$(python - /tmp/jumpy-strategy.txt /tmp/jumpy-candidates.txt <<'PY'
import re,sys
text=open(sys.argv[1],errors='replace').read()
ids=[line.split(':',1)[0].strip() for line in open(sys.argv[2],errors='replace') if ':' in line]
m=re.search(r'(?im)^\s*SHORTCUT\s*:\s*([A-Z0-9_]+)\s*$',text)
print(m.group(1) if m and m.group(1) in ids else '')
PY
)

IMPLEMENTATION_NOTE=''
if [ -n "$CHOICE" ]; then
  echo "EXECUTION_LANE=deterministic:$CHOICE"
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
else:
    raise SystemExit('unknown shortcut')
if s.count(old) != 1:
    raise SystemExit('shortcut anchor mismatch: '+task)
p.write_text(s.replace(old,new,1))
PY
else
  echo 'EXECUTION_LANE=open-ended'
  STRATEGY=$(cat /tmp/jumpy-strategy.txt)
  IMPLEMENT_PROMPT=$(cat <<'PROMPT'
Work as Jumpy's senior implementation pair. Implement the SINGLE immediate priority from the strategic review in this isolated clone. Do not merely discuss it.

Rules:
- Godot 4.7 compatible; preserve deterministic daily behavior and one-touch simplicity.
- Prefer systemic, maintainable changes over hacks.
- Modify at most 4 EXISTING text files and roughly 350 changed lines this cycle.
- Do not commit or push.
- Do not touch .github/, secrets, signing, keystores, external credentials, paid services or binary assets.
- Do not add a new external dependency.
- If the proposed route is blocked, implement the best independent local alternative that advances the same objective.
- Inspect your own diff and correct obvious errors before exiting.
PROMPT
)
  timeout -k 5s 420s fcc-opencode run "$IMPLEMENT_PROMPT\n\nSTRATEGIC REVIEW:\n$STRATEGY" >/tmp/jumpy-implement.log 2>&1 || true
  if [ -s /tmp/jumpy-implement.log ]; then
    IMPLEMENTATION_NOTE=$(tail -n 20 /tmp/jumpy-implement.log | tr '\n' ' ' | head -c 1800)
  fi
fi

# Reject unsafe or excessively broad source edits. If rejected, keep only the strategic state update.
python - <<'PY'
import subprocess
changed=subprocess.check_output(['git','diff','--name-only'],text=True).splitlines()
forbidden=[p for p in changed if p.startswith('.github/') or any(x in p.lower() for x in ['secret','keystore','.jks','.p12'])]
if forbidden or len(changed)>4:
    print('Rejecting unsafe/broad implementation:',changed)
    subprocess.run(['git','reset','--hard','HEAD'],check=False,stdout=subprocess.DEVNULL)
PY

python - "$CHOICE" "$IMPLEMENTATION_NOTE" <<'PY'
from pathlib import Path
import datetime,re,sys
p=Path('docs/AUTONOMOUS_STATE.md'); s=p.read_text()
strategy=Path('/tmp/jumpy-strategy.txt').read_text(errors='replace').strip()[-10000:]
remaining=Path('/tmp/jumpy-candidates.txt').read_text(errors='replace').strip()
focus=sys.argv[1] or 'OPEN_ENDED_STRATEGIC_TASK'
note=sys.argv[2].strip()
now=datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
block=f'''<!-- AUTO_CYCLE_START -->
## Latest autonomous strategic cycle
**Time:** {now}  
**Execution focus:** `{focus}`

### Multidisciplinary review and immediate plan
{strategy}

### Executor evidence
{note if note else 'Implementation lane completed without a diagnostic note. Source diff and Godot validation determine whether code is accepted.'}

### Remaining deterministic shortcuts
{remaining if remaining else 'None. Strategy is not constrained by a fixed feature catalog; use the open-ended implementation lane.'}

### Operating instruction
Re-audit the whole product next cycle. Treat failed approaches as evidence, choose alternate paths, and change priorities whenever current evidence makes another action higher-value.
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
timeout -k 5s 840s gh codespace ssh -c "$NAME" "printf '%s' '$DATA' | base64 -d | bash" > /tmp/jumpy-cycle.out
sed -E 's/(PATCH_B64=).*/\1[REDACTED]/' /tmp/jumpy-cycle.out
RESULT=$(grep '^RESULT=' /tmp/jumpy-cycle.out | tail -n1 | cut -d= -f2- || true)
[ "$RESULT" = PATCH ] || exit 0
grep '^PATCH_B64=' /tmp/jumpy-cycle.out | tail -n1 | cut -d= -f2- | base64 -d > /tmp/jumpy.patch

rm -rf /tmp/jumpy-validated
gh auth setup-git >/dev/null 2>&1 || true
git clone --depth 1 https://github.com/dbrckk/Jumpy.git /tmp/jumpy-validated >/dev/null 2>&1
cd /tmp/jumpy-validated
git apply --check /tmp/jumpy.patch
git apply /tmp/jumpy.patch

curl -fL -o /tmp/godot.zip https://github.com/godotengine/godot/releases/download/4.7.2-stable/Godot_v4.7.2-stable_linux.x86_64.zip >/dev/null 2>&1
rm -rf /tmp/godot-jumpy
mkdir -p /tmp/godot-jumpy
unzip -q /tmp/godot.zip -d /tmp/godot-jumpy
mv /tmp/godot-jumpy/Godot_v4.7.2-stable_linux.x86_64 /tmp/godot-jumpy/godot
chmod +x /tmp/godot-jumpy/godot
/tmp/godot-jumpy/godot --headless --path . --editor --quit 2>&1 | tee /tmp/jumpy-godot.log
if grep -E 'SCRIPT ERROR|Parse Error|Cannot parse|Failed loading resource' /tmp/jumpy-godot.log; then
  echo 'Blocking Godot error detected; candidate not committed.'
  exit 1
fi

test -f docs/AUTONOMOUS_TEAM.md
test -f docs/AUTONOMOUS_STATE.md
test -f docs/PRODUCTION_ROADMAP.md
test -f SETUP_REQUIRED.txt

git config user.name 'jumpy-autocycle[bot]'
git config user.email '41898282+github-actions[bot]@users.noreply.github.com'
git diff --name-only -z | xargs -0 -r git add --
git diff --cached --quiet && { echo 'No effective validated change'; exit 0; }
git commit -m 'Autocycle: adaptive studio evolution'
git push origin HEAD:main
