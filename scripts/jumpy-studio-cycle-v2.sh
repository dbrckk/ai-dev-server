#!/usr/bin/env bash
set -euo pipefail

: "${GH_TOKEN:?GH_TOKEN required}"
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
for _ in {1..90}; do
  STATE=$(gh codespace view -c "$NAME" --json state --jq .state 2>/dev/null || true)
  [ "$STATE" = Available ] && break
  sleep 5
done
[ "$STATE" = Available ] || { echo 'Codespace unavailable'; exit 1; }

cat > /tmp/jumpy-v2-remote.sh <<'REMOTE'
#!/usr/bin/env bash
set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"
WORK=/workspaces/ai-dev-server/.jumpy-studio-cycle
rm -rf "$WORK"
git clone --depth 1 https://github.com/dbrckk/Jumpy.git "$WORK" >/dev/null 2>&1
cd "$WORK"
BASE_SHA=$(git rev-parse HEAD)

# Keep FCC healthy for strategic review and open-ended fallback.
BASE="$HOME/.cache/ai-dev-server"; mkdir -p "$BASE/logs"
if ! curl -fsS --max-time 3 http://127.0.0.1:8082/health >/dev/null 2>&1; then
  nohup fcc-server >"$BASE/logs/fcc.log" 2>&1 < /dev/null &
  for _ in {1..30}; do curl -fsS --max-time 2 http://127.0.0.1:8082/health >/dev/null 2>&1 && break; sleep 1; done
fi

# 1) Systemic strategic review. It informs priorities but does not get to produce unsafe broad edits.
MODEL=$(grep -E '^MODEL=' "$HOME/.fcc/.env" | tail -n1 | cut -d= -f2-)
CONTEXT=$(python - <<'PY'
from pathlib import Path
names=['docs/AUTONOMOUS_STATE.md','docs/PRODUCTION_ROADMAP.md','docs/GAME_DESIGN.md','SETUP_REQUIRED.txt','scripts/main.gd','scripts/profile.gd','scripts/integrations.gd']
left=65000
for n in names:
 p=Path(n)
 if not p.exists(): continue
 t=p.read_text(errors='replace')[:left]
 print(f'\n===== {n} =====\n{t}')
 left-=len(t)
 if left<=0: break
PY
)
PROMPT='Act as Jumpy senior studio leadership. Audit the CURRENT repository systemically across gameplay feel, UX, accessibility, retention, social/viral, engineering, QA, performance, audio/VFX, analytics and Android release. Identify the highest-impact current bottleneck, root causes, acceptance criteria and next 3-5 priorities. Be concise, evidence-driven, and never claim AAA without proof.'
PAYLOAD=$(python - "$MODEL" "$PROMPT\n\n$CONTEXT" <<'PY'
import json,sys
print(json.dumps({'model':sys.argv[1],'max_tokens':1800,'messages':[{'role':'user','content':sys.argv[2]}],'stream':False}))
PY
)
RESP=$(curl -sS --max-time 75 -H 'Content-Type: application/json' -X POST http://127.0.0.1:8082/v1/messages --data-binary "$PAYLOAD" || true)
python - "$RESP" <<'PY' >/tmp/jumpy-strategy.txt
import json,sys
try:
 d=json.loads(sys.argv[1]); t='\n'.join(str(x.get('text','')) for x in d.get('content',[]) if isinstance(x,dict) and x.get('type')=='text').strip()
except Exception: t=''
print((t or 'Strategic review unavailable; use repository evidence and current living state.')[-5000:])
PY

# 2) Atomic phase resolver. Known high-value foundations are completed deterministically.
PHASE=$(python - <<'PY'
from pathlib import Path
profile=Path('scripts/profile.gd').read_text()
main=Path('scripts/main.gd').read_text()
integ=Path('scripts/integrations.gd').read_text()
if '"reduced_motion"' not in profile or '"high_contrast"' not in profile:
 print('ACCESSIBILITY_PROFILE_FOUNDATION')
elif 'func set_preference(' not in profile:
 print('ACCESSIBILITY_PROFILE_SETTER')
elif 'reduced_motion' not in main:
 print('ACCESSIBILITY_VISUAL_BEHAVIOR')
elif 'SETTINGS' not in main:
 print('ACCESSIBILITY_SETTINGS_UI')
elif 'DAILY BEST %d' not in main:
 print('DAILY_BEST_MENU')
elif 'PERFECT %d  •  COINS %d' not in main:
 print('RUN_STATS_GAMEOVER')
else:
 print('OPEN_ENDED')
PY
)

echo "PHASE=$PHASE"
EXEC_STATUS=completed
NOTE=''

case "$PHASE" in
  ACCESSIBILITY_PROFILE_FOUNDATION)
    python - <<'PY'
from pathlib import Path
p=Path('scripts/profile.gd'); s=p.read_text()
old='\t"sound": true,\n\t"haptics": true\n}'
new='\t"sound": true,\n\t"haptics": true,\n\t"reduced_motion": false,\n\t"high_contrast": false\n}'
if s.count(old)!=1: raise SystemExit('profile preference anchor mismatch')
p.write_text(s.replace(old,new,1))
PY
    NOTE='Added persistent reduced_motion and high_contrast defaults; load_data already merges only known keys, so older saves migrate safely.'
    ;;
  ACCESSIBILITY_PROFILE_SETTER)
    python - <<'PY'
from pathlib import Path
p=Path('scripts/profile.gd'); s=p.read_text()
anchor='func record_run(score: int, run_coins: int, perfects: int, daily: bool) -> Dictionary:\n'
block='func set_preference(key: String, value: bool) -> void:\n\tif key not in ["sound", "haptics", "reduced_motion", "high_contrast"]:\n\t\tpush_warning("Jumpy: unknown preference %s" % key)\n\t\treturn\n\tdata[key] = value\n\tsave()\n\n'
if s.count(anchor)!=1: raise SystemExit('setter anchor mismatch')
p.write_text(s.replace(anchor,block+anchor,1))
PY
    NOTE='Added one validated preference setter so future UI can persist all four accessibility preferences without duplicating save logic.'
    ;;
  ACCESSIBILITY_VISUAL_BEHAVIOR)
    cat >/tmp/brief.txt <<'EOF'
Modify ONLY scripts/main.gd. Make existing visual feedback respect Profile.data.reduced_motion and Profile.data.high_contrast without adding any settings UI yet. Keep this slice compile-complete: reduced motion should suppress or substantially reduce camera kick/flash/particle intensity; high contrast should increase gameplay readability using existing procedural drawing/colors. Do not add new external dependencies or new files. Do not reference undefined symbols. Keep changes under ~120 lines and finish with a valid diff.
EOF
    setsid bash -lc 'cd /workspaces/ai-dev-server/.jumpy-studio-cycle && fcc-opencode run "$(cat /tmp/brief.txt)"' >/tmp/jumpy-agent.log 2>&1 & PID=$!
    for _ in {1..60}; do ! kill -0 "$PID" 2>/dev/null && { wait "$PID" || true; break; }; sleep 2; done
    if kill -0 "$PID" 2>/dev/null; then EXEC_STATUS=timeout_120s; kill -TERM -- "-$PID" 2>/dev/null || true; sleep 2; kill -KILL -- "-$PID" 2>/dev/null || true; wait "$PID" 2>/dev/null || true; fi
    NOTE=$(python - <<'PY'
from pathlib import Path
p=Path('/tmp/jumpy-agent.log'); print(' '.join(p.read_text(errors='replace').splitlines()[-20:])[-1500:] if p.exists() else '')
PY
)
    ;;
  ACCESSIBILITY_SETTINGS_UI)
    cat >/tmp/brief.txt <<'EOF'
Modify ONLY scripts/main.gd. Add a minimal, compile-complete SETTINGS UI to the existing programmatic main menu for the four existing Profile preferences: sound, haptics, reduced_motion, high_contrast. Use Profile.set_preference for persistence. Prefer simple buttons/toggles and existing UI patterns. Do not create dangling callbacks or new files. Keep changes under ~150 lines. If the full four-toggle panel cannot be completed safely, implement a smaller complete settings surface that still exposes at least reduced_motion and high_contrast, with every referenced function defined before exit.
EOF
    setsid bash -lc 'cd /workspaces/ai-dev-server/.jumpy-studio-cycle && fcc-opencode run "$(cat /tmp/brief.txt)"' >/tmp/jumpy-agent.log 2>&1 & PID=$!
    for _ in {1..70}; do ! kill -0 "$PID" 2>/dev/null && { wait "$PID" || true; break; }; sleep 2; done
    if kill -0 "$PID" 2>/dev/null; then EXEC_STATUS=timeout_140s; kill -TERM -- "-$PID" 2>/dev/null || true; sleep 2; kill -KILL -- "-$PID" 2>/dev/null || true; wait "$PID" 2>/dev/null || true; fi
    NOTE=$(python - <<'PY'
from pathlib import Path
p=Path('/tmp/jumpy-agent.log'); print(' '.join(p.read_text(errors='replace').splitlines()[-20:])[-1500:] if p.exists() else '')
PY
)
    ;;
  DAILY_BEST_MENU)
    python - <<'PY'
from pathlib import Path
p=Path('scripts/main.gd'); s=p.read_text(); old='\tui.subtitle.text = "DAILY SEED • SAME WORLD FOR EVERYONE" if value else "TAP • LAND • FLOW"'; new='\tui.subtitle.text = "DAILY SEED • DAILY BEST %d" % int(Profile.data.daily_best) if value else "TAP • LAND • FLOW"'
if s.count(old)!=1: raise SystemExit('daily best anchor mismatch')
p.write_text(s.replace(old,new,1))
PY
    NOTE='Surfaced daily best in deterministic daily mode.'
    ;;
  RUN_STATS_GAMEOVER)
    python - <<'PY'
from pathlib import Path
p=Path('scripts/main.gd'); s=p.read_text(); old='\tui.gameover.text = "SCORE %d\\nBEST %d\\n%s" % [score, int(Profile.data.best_score), "NEW BEST" if score >= int(Profile.data.best_score) and score > 0 else "FLOW BROKEN"]'; new='\tui.gameover.text = "SCORE %d\\nBEST %d\\nPERFECT %d  •  COINS %d\\n%s" % [score, int(Profile.data.best_score), perfects, run_coins, "NEW BEST" if score >= int(Profile.data.best_score) and score > 0 else "FLOW BROKEN"]'
if s.count(old)!=1: raise SystemExit('run stats anchor mismatch')
p.write_text(s.replace(old,new,1))
PY
    NOTE='Added post-run skill/resource summary.'
    ;;
  OPEN_ENDED)
    cat >/tmp/brief.txt <<EOF
Using the strategic review below, implement ONE smallest complete safe improvement in Jumpy. Modify at most 2 existing text files and ~120 changed lines. Produce useful file edits early; no external APIs, credentials, .github changes, binary assets or dependencies. Every referenced symbol must exist before exit. If blocked, choose a smaller local improvement.\n\n$(cat /tmp/jumpy-strategy.txt)
EOF
    setsid bash -lc 'cd /workspaces/ai-dev-server/.jumpy-studio-cycle && fcc-opencode run "$(cat /tmp/brief.txt)"' >/tmp/jumpy-agent.log 2>&1 & PID=$!
    for _ in {1..60}; do ! kill -0 "$PID" 2>/dev/null && { wait "$PID" || true; break; }; sleep 2; done
    if kill -0 "$PID" 2>/dev/null; then EXEC_STATUS=timeout_120s; kill -TERM -- "-$PID" 2>/dev/null || true; sleep 2; kill -KILL -- "-$PID" 2>/dev/null || true; wait "$PID" 2>/dev/null || true; fi
    NOTE=$(python - <<'PY'
from pathlib import Path
p=Path('/tmp/jumpy-agent.log'); print(' '.join(p.read_text(errors='replace').splitlines()[-20:])[-1500:] if p.exists() else '')
PY
)
    ;;
esac

# Safety: max 2 source files, never automation/secrets.
python - <<'PY'
import subprocess
changed=subprocess.check_output(['git','diff','--name-only'],text=True).splitlines()
forbidden=[x for x in changed if x.startswith('.github/') or any(k in x.lower() for k in ['secret','keystore','.jks','.p12'])]
source=[x for x in changed if x!='docs/AUTONOMOUS_STATE.md']
if forbidden or len(source)>2:
 print('REJECTING='+','.join(changed)); subprocess.run(['git','reset','--hard','HEAD'],check=False,stdout=subprocess.DEVNULL)
PY

# Concise living state: no raw chain-of-thought accumulation.
python - "$PHASE" "$EXEC_STATUS" "$BASE_SHA" "$NOTE" <<'PY'
from pathlib import Path
import datetime,re,sys
p=Path('docs/AUTONOMOUS_STATE.md'); s=p.read_text()
phase,status,base,note=sys.argv[1:5]
strategy=Path('/tmp/jumpy-strategy.txt').read_text(errors='replace').strip()
strategy=' '.join(strategy.split())[:2200]
now=datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
block=f'''<!-- AUTO_CYCLE_START -->
## Latest autonomous cycle
- Time: {now}
- Base: `{base[:12]}`
- Atomic phase: `{phase}`
- Executor: `{status}`

### Strategic snapshot
{strategy}

### Execution evidence
{note[:1800] if note else 'No executor note. Validation outcome determines acceptance.'}

### Next-cycle rule
Re-read current source and resolve the next atomic phase from evidence. Do not repeat a failed phase unchanged; reduce scope or change route.
<!-- AUTO_CYCLE_END -->'''
pat=r'<!-- AUTO_CYCLE_START -->.*?<!-- AUTO_CYCLE_END -->'
s=re.sub(pat,block,s,flags=re.S) if re.search(pat,s,re.S) else s.rstrip()+'\n\n'+block+'\n'
p.write_text(s)
PY

CHANGED=$(git diff --name-only)
[ -n "$CHANGED" ] || { echo 'RESULT=NO_CHANGE'; exit 0; }
echo "PHASE=$PHASE"
echo "EXEC_STATUS=$EXEC_STATUS"
echo "FILES=$(printf '%s\n' "$CHANGED" | paste -sd, -)"
echo "PATCH_B64=$(git diff --binary | base64 -w0)"
REMOTE

DATA=$(base64 -w0 /tmp/jumpy-v2-remote.sh)
set +e
timeout -k 5s 390s gh codespace ssh -c "$NAME" "printf '%s' '$DATA' | base64 -d | bash" >/tmp/jumpy-v2.out
RC=$?
set -e
sed -E 's/(PATCH_B64=).*/\1[REDACTED]/' /tmp/jumpy-v2.out || true
[ "$RC" -eq 0 ] || { echo "remote rc=$RC"; exit 1; }
grep '^PATCH_B64=' /tmp/jumpy-v2.out | tail -n1 | cut -d= -f2- | base64 -d >/tmp/jumpy.patch
[ -s /tmp/jumpy.patch ] || exit 0

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
/tmp/godot-jumpy/godot --headless --path . --editor --quit >/tmp/jumpy-godot.log 2>&1
GRC=$?
set -e
cat /tmp/jumpy-godot.log
if [ "$GRC" -ne 0 ] || grep -E 'SCRIPT ERROR|Parse Error|Cannot parse|Failed loading resource' /tmp/jumpy-godot.log; then
  echo 'Godot rejected source; preserve diagnostic state only.'
  git diff --name-only | while read -r f; do [ "$f" = 'docs/AUTONOMOUS_STATE.md' ] || git checkout HEAD -- "$f"; done
  python - <<'PY'
from pathlib import Path
p=Path('docs/AUTONOMOUS_STATE.md'); s=p.read_text(); pos=s.find('<!-- AUTO_CYCLE_END -->'); msg='\n### Validation\nGodot 4.7.2 rejected this source candidate. Source edits were discarded; next cycle must use a smaller or different route.\n'; p.write_text(s[:pos]+msg+s[pos:] if pos>=0 else s+msg)
PY
fi

git config user.name 'jumpy-autocycle[bot]'
git config user.email '41898282+github-actions[bot]@users.noreply.github.com'
git diff --name-only -z | xargs -0 -r git add --
git diff --cached --quiet && exit 0
git commit -m 'Autocycle v2: atomic Jumpy evolution'
git push origin HEAD:main
