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

cat >/tmp/jumpy-v3-remote.sh <<'REMOTE'
#!/usr/bin/env bash
set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"
WORK=/workspaces/ai-dev-server/.jumpy-studio-cycle
rm -rf "$WORK"
git clone --depth 1 https://github.com/dbrckk/Jumpy.git "$WORK" >/dev/null 2>&1
cd "$WORK"
BASE_SHA=$(git rev-parse HEAD)

BASE="$HOME/.cache/ai-dev-server"; mkdir -p "$BASE/logs"
if ! curl -fsS --max-time 3 http://127.0.0.1:8082/health >/dev/null 2>&1; then
  nohup fcc-server >"$BASE/logs/fcc.log" 2>&1 < /dev/null &
  for _ in {1..30}; do curl -fsS --max-time 2 http://127.0.0.1:8082/health >/dev/null 2>&1 && break; sleep 1; done
fi
curl -fsS --max-time 3 http://127.0.0.1:8082/health >/dev/null

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
PROMPT='Act as Jumpy senior studio leadership. Audit the CURRENT repository across gameplay feel, UX, accessibility, retention, social/viral loops, engineering, QA, performance, audio/VFX, analytics and Android release. Identify the highest-impact current bottleneck, root cause, measurable acceptance criteria and next 3-5 priorities. Prefer small validated improvements. Never claim AAA without real evidence. External tools may be recommended only when clearly licensed, maintained and reputable; do not install anything in this cycle.'
PAYLOAD=$(python - "$MODEL" "$PROMPT\n\n$CONTEXT" <<'PY'
import json,sys
print(json.dumps({'model':sys.argv[1],'max_tokens':1600,'messages':[{'role':'user','content':sys.argv[2]}],'stream':False}))
PY
)
RESP=$(curl -sS --max-time 70 -H 'Content-Type: application/json' -X POST http://127.0.0.1:8082/v1/messages --data-binary "$PAYLOAD" || true)
python - "$RESP" <<'PY' >/tmp/jumpy-strategy.txt
import json,sys
try:
    d=json.loads(sys.argv[1]); t='\n'.join(str(x.get('text','')) for x in d.get('content',[]) if isinstance(x,dict) and x.get('type')=='text').strip()
except Exception: t=''
print((t or 'Strategic review unavailable; use repository evidence and living state.')[-4500:])
PY

PHASE=$(python - <<'PY'
from pathlib import Path
main=Path('scripts/main.gd').read_text()
profile=Path('scripts/profile.gd').read_text()
if '"reduced_motion"' not in profile or '"high_contrast"' not in profile: print('ACCESSIBILITY_PROFILE_FOUNDATION')
elif 'func set_preference(' not in profile: print('ACCESSIBILITY_PROFILE_SETTER')
elif 'reduced_motion' not in main: print('ACCESSIBILITY_VISUAL_BEHAVIOR')
elif 'SETTINGS' not in main: print('ACCESSIBILITY_SETTINGS_UI')
elif 'DAILY BEST %d' not in main: print('DAILY_BEST_MENU')
elif 'PERFECT %d  •  COINS %d' not in main: print('RUN_STATS_GAMEOVER')
else: print('OPEN_ENDED')
PY
)

echo "PHASE=$PHASE"
EXEC_STATUS=completed
NOTE=''

run_agent() {
  local seconds="$1"
  # Agent receives no repository/Codespaces/provider secrets. It only talks to the already-running loopback FCC service.
  setsid env -u GH_TOKEN -u GITHUB_TOKEN -u CODESPACES_PAT -u NVIDIA_NIM_API_KEY \
    bash -lc 'cd /workspaces/ai-dev-server/.jumpy-studio-cycle && fcc-opencode run "$(cat /tmp/brief.txt)"' \
    >/tmp/jumpy-agent.log 2>&1 &
  local pid=$!
  local loops=$((seconds / 2))
  for _ in $(seq 1 "$loops"); do
    if ! kill -0 "$pid" 2>/dev/null; then wait "$pid" || true; return 0; fi
    sleep 2
  done
  EXEC_STATUS="timeout_${seconds}s"
  kill -TERM -- "-$pid" 2>/dev/null || true
  sleep 2
  kill -KILL -- "-$pid" 2>/dev/null || true
  wait "$pid" 2>/dev/null || true
}

case "$PHASE" in
  ACCESSIBILITY_PROFILE_FOUNDATION)
    python - <<'PY'
from pathlib import Path
p=Path('scripts/profile.gd'); s=p.read_text(); old='\t"sound": true,\n\t"haptics": true\n}'; new='\t"sound": true,\n\t"haptics": true,\n\t"reduced_motion": false,\n\t"high_contrast": false\n}'
if s.count(old)!=1: raise SystemExit('profile anchor mismatch')
p.write_text(s.replace(old,new,1))
PY
    NOTE='Added persistent accessibility defaults.' ;;
  ACCESSIBILITY_PROFILE_SETTER)
    python - <<'PY'
from pathlib import Path
p=Path('scripts/profile.gd'); s=p.read_text(); a='func record_run(score: int, run_coins: int, perfects: int, daily: bool) -> Dictionary:\n'; b='func set_preference(key: String, value: bool) -> void:\n\tif key not in ["sound", "haptics", "reduced_motion", "high_contrast"]:\n\t\tpush_warning("Jumpy: unknown preference %s" % key)\n\t\treturn\n\tdata[key] = value\n\tsave()\n\n'
if s.count(a)!=1: raise SystemExit('setter anchor mismatch')
p.write_text(s.replace(a,b+a,1))
PY
    NOTE='Added centralized persistent preference setter.' ;;
  ACCESSIBILITY_VISUAL_BEHAVIOR)
    cat >/tmp/brief.txt <<'EOF'
Modify ONLY scripts/main.gd. Make existing visual feedback respect Profile.data.reduced_motion and Profile.data.high_contrast. No settings UI yet. Reduced motion should materially reduce camera kick/flash/particle intensity. High contrast should improve gameplay readability using existing procedural colors/drawing. No undefined symbols, dependencies or new files. Keep under ~100 changed lines and leave compiling code early.
EOF
    run_agent 110 ;;
  ACCESSIBILITY_SETTINGS_UI)
    cat >/tmp/brief.txt <<'EOF'
Modify ONLY scripts/main.gd. Add a small compile-complete SETTINGS surface using the existing Profile preferences and Profile.set_preference. Expose sound, haptics, reduced_motion and high_contrast, or a smaller complete subset if needed. Follow existing programmatic UI patterns. No new files, dependencies or undefined callbacks. Keep under ~130 changed lines.
EOF
    run_agent 120 ;;
  DAILY_BEST_MENU)
    python - <<'PY'
from pathlib import Path
p=Path('scripts/main.gd'); s=p.read_text(); old='\tui.subtitle.text = "DAILY SEED • SAME WORLD FOR EVERYONE" if value else "TAP • LAND • FLOW"'; new='\tui.subtitle.text = "DAILY SEED • DAILY BEST %d" % int(Profile.data.daily_best) if value else "TAP • LAND • FLOW"'
if s.count(old)!=1: raise SystemExit('daily anchor mismatch')
p.write_text(s.replace(old,new,1))
PY
    NOTE='Surfaced daily best.' ;;
  RUN_STATS_GAMEOVER)
    python - <<'PY'
from pathlib import Path
p=Path('scripts/main.gd'); s=p.read_text(); old='\tui.gameover.text = "SCORE %d\\nBEST %d\\n%s" % [score, int(Profile.data.best_score), "NEW BEST" if score >= int(Profile.data.best_score) and score > 0 else "FLOW BROKEN"]'; new='\tui.gameover.text = "SCORE %d\\nBEST %d\\nPERFECT %d  •  COINS %d\\n%s" % [score, int(Profile.data.best_score), perfects, run_coins, "NEW BEST" if score >= int(Profile.data.best_score) and score > 0 else "FLOW BROKEN"]'
if s.count(old)!=1: raise SystemExit('run stats anchor mismatch')
p.write_text(s.replace(old,new,1))
PY
    NOTE='Added post-run skill/resource summary.' ;;
  OPEN_ENDED)
    cat >/tmp/brief.txt <<EOF
Implement ONE smallest complete safe improvement from the strategic review below. Modify at most 2 existing text files and about 100 changed lines. No external downloads, package installs, dependencies, network calls, credentials, .github edits, binary assets or release configuration. Produce useful edits early and leave no undefined symbols. If the main idea is too large, choose a smaller local improvement.\n\n$(cat /tmp/jumpy-strategy.txt)
EOF
    run_agent 105 ;;
esac

if [ -s /tmp/jumpy-agent.log ]; then
  NOTE=$(python - <<'PY'
from pathlib import Path
p=Path('/tmp/jumpy-agent.log'); print(' '.join(p.read_text(errors='replace').splitlines()[-18:])[-1400:])
PY
)
fi

python - <<'PY'
import subprocess,sys,re
changed=subprocess.check_output(['git','diff','--name-only'],text=True).splitlines()
forbidden=[]
for x in changed:
    low=x.lower()
    if x.startswith('.github/') or x in {'project.godot','export_presets.cfg'} or any(k in low for k in ['secret','keystore','.jks','.p12','package-lock','package.json','requirements','pyproject','cargo.lock','cargo.toml']): forbidden.append(x)
source=[x for x in changed if x!='docs/AUTONOMOUS_STATE.md']
if forbidden or len(source)>2:
    print('REJECTING_UNSAFE_SCOPE='+','.join(changed)); subprocess.run(['git','reset','--hard','HEAD'],check=False,stdout=subprocess.DEVNULL); sys.exit(0)
# Reject obvious credential material from candidate diff.
diff=subprocess.check_output(['git','diff','--binary'],text=True,errors='replace')
patterns=[r'github_pat_[A-Za-z0-9_]+',r'gh[pousr]_[A-Za-z0-9_]+',r'BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY',r'(?i)(api[_-]?key|token|password)\s*[:=]\s*["\'][A-Za-z0-9_\-]{16,}']
if any(re.search(p,diff) for p in patterns):
    print('REJECTING_SECRET_PATTERN'); subprocess.run(['git','reset','--hard','HEAD'],check=False,stdout=subprocess.DEVNULL); sys.exit(0)
subprocess.run(['git','diff','--check'],check=True)
PY

python - "$PHASE" "$EXEC_STATUS" "$BASE_SHA" "$NOTE" <<'PY'
from pathlib import Path
import datetime,re,sys
p=Path('docs/AUTONOMOUS_STATE.md'); s=p.read_text(); phase,status,base,note=sys.argv[1:5]
strategy=' '.join(Path('/tmp/jumpy-strategy.txt').read_text(errors='replace').split())[:1800]
now=datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
block=f'''<!-- AUTO_CYCLE_START -->\n## Latest autonomous cycle\n- Time: {now}\n- Base: `{base[:12]}`\n- Atomic phase: `{phase}`\n- Executor: `{status}`\n\n### Strategic snapshot\n{strategy}\n\n### Execution evidence\n{note[:1400] if note else 'Validation determines acceptance.'}\n\n### Next-cycle rule\nRe-read current source. Never repeat a failed approach unchanged; reduce scope or choose another route.\n<!-- AUTO_CYCLE_END -->'''
pat=r'<!-- AUTO_CYCLE_START -->.*?<!-- AUTO_CYCLE_END -->'; s=re.sub(pat,block,s,flags=re.S) if re.search(pat,s,re.S) else s.rstrip()+'\n\n'+block+'\n'; p.write_text(s)
PY

CHANGED=$(git diff --name-only)
[ -n "$CHANGED" ] || { echo 'RESULT=NO_CHANGE'; exit 0; }
echo "PHASE=$PHASE"
echo "EXEC_STATUS=$EXEC_STATUS"
echo "FILES=$(printf '%s\n' "$CHANGED" | paste -sd, -)"
echo "PATCH_B64=$(git diff --binary | base64 -w0)"
REMOTE

DATA=$(base64 -w0 /tmp/jumpy-v3-remote.sh)
set +e
timeout -k 5s 360s gh codespace ssh -c "$NAME" "printf '%s' '$DATA' | base64 -d | bash" >/tmp/jumpy-v3.out
RC=$?
set -e
sed -E 's/(PATCH_B64=).*/\1[REDACTED]/' /tmp/jumpy-v3.out || true
[ "$RC" -eq 0 ] || { echo "remote rc=$RC"; exit 1; }
PATCH=$(grep '^PATCH_B64=' /tmp/jumpy-v3.out | tail -n1 | cut -d= -f2- || true)
[ -n "$PATCH" ] || { echo 'No patch produced'; exit 0; }
printf '%s' "$PATCH" | base64 -d >/tmp/jumpy.patch

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
GODOT_RC=$?
set -e
cat /tmp/jumpy-godot.log
if [ "$GODOT_RC" -ne 0 ] || grep -Eq 'SCRIPT ERROR|Parse Error|Cannot parse|Failed loading resource' /tmp/jumpy-godot.log; then
  echo 'Godot rejected candidate; source changes will not be pushed.'
  exit 0
fi

# Final scope and secret check after patch application.
FILES=$(git diff --name-only)
COUNT=$(printf '%s\n' "$FILES" | grep -v '^docs/AUTONOMOUS_STATE.md$' | sed '/^$/d' | wc -l)
[ "$COUNT" -le 2 ] || { echo 'Final scope too broad'; exit 1; }
if git diff | grep -Eiq 'github_pat_|gh[pousr]_[A-Za-z0-9_]+|BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY'; then echo 'Secret-like material detected'; exit 1; fi

git config user.name 'jumpy-autocycle[bot]'
git config user.email '41898282+github-actions[bot]@users.noreply.github.com'
git add -A
git diff --cached --quiet && { echo 'No effective change'; exit 0; }
git commit -m 'Autocycle v3: hardened atomic Jumpy evolution'
git push origin HEAD:main
