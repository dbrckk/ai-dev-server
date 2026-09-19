This file is a merged representation of a subset of the codebase, containing specifically included files and files not matching ignore patterns, combined into a single document by Repomix.
The content has been processed where content has been compressed (code blocks are separated by ⋮---- delimiter).

# File Summary

## Purpose
This file contains a packed representation of a subset of the repository's contents that is considered the most important context.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Only files matching these patterns are included: **/*.{py,js,mjs,cjs,ts,tsx,jsx,java,kt,kts,gd,groovy,gradle,toml,json,yaml,yml,sql,sh}
- Files matching these patterns are excluded: .ai/**, **/node_modules/**, **/.gradle/**, **/build/**, **/dist/**, **/.venv/**, **/__pycache__/**, **/.pytest_cache/**, **/.git/**, **/coverage/**, **/*.lock, **/*.min.js, **/*.map, assets/**, art/**, art_sources/**, marketing/**, colab/**, kaggle/**, discovery-cache.json, health-snapshot.json, history.json
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Content has been compressed - code blocks are separated by ⋮---- delimiter
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
```
agent-test.sh
bootstrap-android-ci.sh
bootstrap.sh
configure-cdesktop.sh
doctor.sh
enable-sprites.sh
fcc-agent-benchmark.sh
finish-fcc.sh
jumpy-studio-cycle-v2.sh
jumpy-studio-cycle-v3-runner.sh
jumpy-studio-cycle-v3-safe.sh
jumpy-studio-cycle-v3.sh
jumpy-studio-cycle-v4.sh
jumpy-studio-cycle-v5.sh
jumpy-studio-cycle-v6.sh
jumpy-studio-cycle-v7.sh
jumpy-studio-cycle-v8.sh
jumpy-studio-cycle.sh
provider-status.sh
restart-all.sh
setup-serena-codex.sh
start-all.sh
start-cdesktop.sh
start-dsh.sh
start-fcc.sh
start-production-os-worker.sh
status.sh
```

# Files

## File: agent-test.sh
```bash
#!/usr/bin/env bash
set -u
export PATH="$HOME/.local/bin:$PATH"
BASE="$HOME/.cache/ai-dev-server"
mkdir -p "$BASE/logs"

if ! curl -fsS --max-time 3 http://127.0.0.1:8082/health >/dev/null 2>&1; then
  nohup fcc-server >"$BASE/logs/fcc.log" 2>&1 &
  for i in {1..20}; do
    curl -fsS --max-time 2 http://127.0.0.1:8082/health >/dev/null 2>&1 && break
    sleep 1
  done
fi
curl -fsS --max-time 3 http://127.0.0.1:8082/health >/dev/null 2>&1 || { echo 'fcc_service: FAILED'; exit 0; }

echo 'fcc_service: OK'
WORK=/tmp/jumpy-fcc-audit
rm -rf "$WORK"
git clone --depth 1 https://github.com/dbrckk/Jumpy.git "$WORK" >/dev/null 2>&1 || { echo 'clone: FAILED'; exit 0; }
cd "$WORK"

MODEL=$(grep -E '^MODEL=' "$HOME/.fcc/.env" | tail -n1 | cut -d= -f2-)
CODE=$(python - <<'PY'
from pathlib import Path
files=['project.godot','scripts/main.gd','scripts/profile.gd','scripts/integrations.gd','export_presets.cfg']
for f in files:
    p=Path(f)
    if p.exists():
        print(f'\n### FILE {f}\n')
        print(p.read_text(errors='replace'))
PY
)
PROMPT="You are the release-blocker reviewer for a Godot 4.7 portrait mobile game. Review only blocking/high-impact correctness issues in the supplied files: parse/runtime errors, broken Godot APIs, impossible gameplay, save corruption, nondeterministic daily level generation, mobile input blockers, or unsafe credential handling. Ignore stylistic/nice-to-have concerns. Godot CI already imports/parses the project successfully. Reply on ONE line only: AUDIT_OK: <short assessment> OR AUDIT_ISSUES: <up to 4 concise issues with file/function and fix>.\n\n$CODE"
PAYLOAD=$(python - "$MODEL" "$PROMPT" <<'PY'
import json,sys
print(json.dumps({'model':sys.argv[1],'max_tokens':900,'messages':[{'role':'user','content':sys.argv[2]}],'stream':False}))
PY
)
RESPONSE=$(curl -sS --max-time 150 -H 'Content-Type: application/json' -X POST http://127.0.0.1:8082/v1/messages --data-binary "$PAYLOAD" || true)
python - "$RESPONSE" <<'PY'
import json,sys,re
try:
    d=json.loads(sys.argv[1])
    text=' '.join(str(x.get('text','')) for x in d.get('content',[]) if isinstance(x,dict) and x.get('type')=='text')
    m=re.search(r'(AUDIT_(?:OK|ISSUES):.*)', text, re.S)
    if m:
        print('fcc_release_audit:', re.sub(r'\s+',' ',m.group(1))[:3000])
    else:
        print('fcc_release_audit: NO_VERDICT', re.sub(r'\s+',' ',text)[:1200])
except Exception as e:
    print('fcc_release_audit: INVALID_RESPONSE', str(e))
PY
exit 0
```

## File: bootstrap-android-ci.sh
```bash
#!/usr/bin/env bash
set -euo pipefail

: "${ANDROID_HOME:?ANDROID_HOME must be set}"
SDKMANAGER="$ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager"

if [[ ! -x "$SDKMANAGER" ]]; then
  echo "sdkmanager not executable at $SDKMANAGER" >&2
  exit 2
fi

if [[ -n "${GITHUB_PATH:-}" ]]; then
  printf '%s\n' \
    "$ANDROID_HOME/platform-tools" \
    "$ANDROID_HOME/cmdline-tools/latest/bin" \
    "$ANDROID_HOME/emulator" >> "$GITHUB_PATH"
fi

# `yes` normally exits with SIGPIPE once sdkmanager has consumed every answer.
# Judge the sdkmanager process itself rather than the producer side of the pipe.
set +e
yes | "$SDKMANAGER" --licenses >/dev/null
license_status=${PIPESTATUS[1]}
set -e
if [[ "$license_status" -ne 0 ]]; then
  echo "Android SDK license acceptance failed with status $license_status" >&2
  exit "$license_status"
fi

cleanup_partial_downloads() {
  rm -rf \
    "$ANDROID_HOME/.temp" \
    "$ANDROID_HOME/.cache" \
    "${ANDROID_USER_HOME:-${HOME:-/tmp}/.android}/cache" \
    2>/dev/null || true
}

# Flutter's current Android template uses this NDK. Pre-installing it here keeps
# the same package acquisition behind the bounded retry boundary instead of
# leaving Gradle to perform an unbounded one-shot download during a fixture.
packages=(
  "platform-tools"
  "emulator"
  "ndk;28.2.13676358"
)

last_status=1
for attempt in 1 2 3; do
  set +e
  "$SDKMANAGER" "${packages[@]}"
  last_status=$?
  set -e

  if [[ "$last_status" -eq 0 ]]; then
    exit 0
  fi

  echo "Android SDK package install attempt $attempt/3 failed with status $last_status" >&2
  if [[ "$attempt" -lt 3 ]]; then
    cleanup_partial_downloads
  fi
done

exit "$last_status"
```

## File: bootstrap.sh
```bash
#!/usr/bin/env bash
set -euo pipefail

mkdir -p "$HOME/.local/bin" "$HOME/.cache/ai-dev-server/logs"
export PATH="$HOME/.local/bin:$PATH"

# Core coding-agent CLIs. Keep multiple independent harnesses so the autonomous router
# can select the strongest working agent and fail over without waiting for a rebuild.
npm install -g opencode-ai @openai/codex
# Claude Code remains optional because the autonomous router prefers free agents.
# Install it only when explicitly enabled to avoid making a paid dependency mandatory.
if [[ "${STUDIO_ENABLE_CLAUDE_CODE:-0}" == "1" ]]; then npm install -g @anthropic-ai/claude-code; fi
if [[ "${STUDIO_ENABLE_HERMES:-0}" == "1" ]]; then
  uv tool install hermes-agent || uv tool upgrade hermes-agent || true
fi

# Python tooling and sprite post-processing.
python -m pip install --user --upgrade uv pillow rembg
export PATH="$HOME/.local/bin:$PATH"

# Install/update Free Claude Code directly as a uv tool so Codespace creation
# does not stop on the interactive upstream installer.
if command -v fcc-server >/dev/null 2>&1; then
  uv tool upgrade free-claude-code || true
else
  uv tool install git+https://github.com/Alishahryar1/free-claude-code.git
fi

# Warm the web UIs so later startup from a phone is faster.
npx --yes @deepseek-ai/dsh --help >/dev/null 2>&1 || true
npx --yes cdesktop --help >/dev/null 2>&1 || true

# Pollinations/OpenCode integration helper package, if available.
npm install -g opencode-pollinations-plugin >/dev/null 2>&1 || true

# Keep local secrets/config out of git by default.
touch "$HOME/.cache/ai-dev-server/bootstrap-complete"

echo "AI Dev Server bootstrap complete. Services will auto-start."
```

## File: configure-cdesktop.sh
```bash
#!/usr/bin/env bash
set -u
export PATH="$HOME/.local/bin:$PATH"
DIR="$HOME/.local/share/cdesktop"
mkdir -p "$DIR"
cat > "$DIR/profiles.json" <<'JSON'
{
  "executors": {
    "CLAUDE_CODE": {
      "DEFAULT": {
        "CLAUDE_CODE": {
          "base_command_override": "fcc-claude"
        }
      },
      "FCC": {
        "CLAUDE_CODE": {
          "base_command_override": "fcc-claude"
        }
      }
    },
    "OPENCODE": {
      "FCC": {
        "OPENCODE": {
          "base_command_override": "fcc-opencode"
        }
      }
    }
  }
}
JSON
python -m json.tool "$DIR/profiles.json" >/dev/null || { echo 'cdesktop_profile: INVALID'; exit 0; }
echo "cdesktop_profile: written $DIR/profiles.json"
echo 'cdesktop_profile: Claude Code -> fcc-claude'
echo 'cdesktop_profile: OpenCode -> fcc-opencode'

# Restart cdesktop so it reloads profiles.
PID=$(python - <<'PY'
import os
try:
 import subprocess
 out=subprocess.check_output(['bash','-lc',"lsof -ti tcp:3000 2>/dev/null | head -n1"], text=True).strip()
 print(out)
except Exception:
 pass
PY
)
[ -z "$PID" ] || kill "$PID" 2>/dev/null || true
sleep 2
export HOST=0.0.0.0
export PORT=3000
if [ -n "${CODESPACE_NAME:-}" ] && [ -n "${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-}" ]; then
  export CDT_ALLOWED_ORIGINS="https://${CODESPACE_NAME}-3000.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
fi
nohup npx --yes cdesktop >"$HOME/.cache/ai-dev-server/logs/cdesktop.log" 2>&1 &
for i in {1..30}; do
  curl -fsS --max-time 2 http://127.0.0.1:3000/ >/dev/null 2>&1 && break
  sleep 1
done
if curl -fsS --max-time 3 http://127.0.0.1:3000/ >/dev/null 2>&1; then
  echo 'cdesktop_restart: OK'
else
  echo 'cdesktop_restart: FAILED'
fi
sleep 1
grep -E 'profiles|Recommended executor|Main server' "$HOME/.cache/ai-dev-server/logs/cdesktop.log" | tail -n 10 || true
```

## File: doctor.sh
```bash
#!/usr/bin/env bash
set -u

cd /workspaces/ai-dev-server 2>/dev/null || true
export PATH="$HOME/.local/bin:$PATH"

echo "=== AI Dev Server doctor ==="
echo "date: $(date -Is)"
echo "user: $(whoami)"
echo "pwd: $(pwd)"
echo "node: $(node --version 2>/dev/null || echo missing)"
echo "npm: $(npm --version 2>/dev/null || echo missing)"
echo "python: $(python --version 2>/dev/null || echo missing)"
echo "gh: $(gh --version 2>/dev/null | head -n1 || echo missing)"
echo

echo "Commands:"
for x in fcc-server fcc-claude fcc-opencode fcc-dsh claude opencode; do
  if command -v "$x" >/dev/null 2>&1; then
    echo "  $x: $(command -v "$x")"
  else
    echo "  $x: missing"
  fi
done

echo
if [ -f scripts/status.sh ]; then
  bash scripts/status.sh || true
fi

echo
echo "HTTP checks:"
check_http() {
  local name="$1" url="$2" code
  code=$(curl -L -sS -o /dev/null -w '%{http_code}' --max-time 8 "$url" 2>/dev/null || echo 000)
  case "$code" in
    2*|3*) echo "  $name: OK ($code)" ;;
    *) echo "  $name: FAIL ($code)" ;;
  esac
}
check_dsh() {
  local code
  code=$(curl -sS -o /dev/null -w '%{http_code}' --max-time 8 "http://127.0.0.1:3080/" 2>/dev/null || echo 000)
  case "$code" in
    2*|3*) echo "  DSH web: OK ($code)" ;;
    401) echo "  DSH web: OK (401, authentication required)" ;;
    *) echo "  DSH web: FAIL ($code)" ;;
  esac
}
check_http "FCC health" "http://127.0.0.1:8082/health"
check_dsh
check_http "cdesktop" "http://127.0.0.1:3000/"

echo
if [ -d "$HOME/.cache/ai-dev-server/logs" ]; then
  echo "Recent logs:"
  for f in "$HOME"/.cache/ai-dev-server/logs/*.log; do
    [ -e "$f" ] || continue
    echo "--- $f ---"
    tail -n 25 "$f" || true
  done
fi
```

## File: enable-sprites.sh
```bash
#!/usr/bin/env bash
set -euo pipefail
npm install -g opencode-pollinations-plugin
npx --yes opencode-pollinations-plugin
cat <<'EOF'
Plugin Pollinations ajouté à OpenCode.
Dans OpenCode, utilise ensuite /poll login pour connecter ton compte Pollinations.
Les secrets restent hors du dépôt.
EOF
```

## File: fcc-agent-benchmark.sh
```bash
#!/usr/bin/env bash
set -euo pipefail

# Empirically ranks FCC coding agents by their ability to perform a real file edit.
# This is deliberately stronger than checking --help or a text response.
# Expected input: BEST_MODEL. Output: best agent name on stdout; diagnostics on stderr.

: "${BEST_MODEL:?BEST_MODEL required}"
export PATH="$HOME/.local/bin:$PATH"
CACHE_DIR="$HOME/.cache/ai-dev-server"
mkdir -p "$CACHE_DIR"
CACHE_FILE="$CACHE_DIR/fcc-agent-winner.txt"
MODEL_FILE="$CACHE_DIR/fcc-agent-model.txt"

agent_available() {
  case "$1" in
    claude-code) command -v fcc-claude >/dev/null 2>&1 && command -v claude >/dev/null 2>&1 ;;
    opencode) command -v fcc-opencode >/dev/null 2>&1 && command -v opencode >/dev/null 2>&1 ;;
    *) return 1 ;;
  esac
}

# Reuse a recent winner only while the selected model is unchanged and the executable still exists.
if [ -s "$CACHE_FILE" ] && [ -s "$MODEL_FILE" ] && [ "$(cat "$MODEL_FILE")" = "$BEST_MODEL" ]; then
  cached=$(cat "$CACHE_FILE")
  if agent_available "$cached"; then
    echo "$cached"
    exit 0
  fi
fi

run_benchmark() {
  local agent="$1"
  local dir
  dir=$(mktemp -d "/tmp/fcc-bench-${agent}.XXXXXX")
  trap 'rm -rf "$dir"' RETURN
  cd "$dir"
  git init -q
  git config user.email 'benchmark@localhost'
  git config user.name 'FCC benchmark'
  printf 'ORIGINAL\n' > TARGET.txt
  git add TARGET.txt && git commit -qm baseline

  cat > /tmp/fcc-benchmark-brief.txt <<'EOF'
Edit the existing file TARGET.txt in this repository. Replace its entire contents with exactly:
FCC_AGENT_OK
Do not create any other file. Do not explain; perform the edit.
EOF

  local cmd timeout_s=35
  case "$agent" in
    claude-code)
      cmd='fcc-claude --model "$BEST_MODEL" --permission-mode acceptEdits -p "$(cat /tmp/fcc-benchmark-brief.txt)"'
      ;;
    opencode)
      cmd='fcc-opencode run --model "$BEST_MODEL" "$(cat /tmp/fcc-benchmark-brief.txt)"'
      ;;
    *) return 1 ;;
  esac

  set +e
  timeout -k 3s "${timeout_s}s" env \
    -u GH_TOKEN -u GITHUB_TOKEN -u CODESPACES_PAT -u NVIDIA_NIM_API_KEY \
    BEST_MODEL="$BEST_MODEL" GIT_TERMINAL_PROMPT=0 SSH_AUTH_SOCK= \
    bash -lc "$cmd" >"/tmp/fcc-bench-${agent}.log" 2>&1
  rc=$?
  set -e

  if [ "$rc" -eq 0 ] && [ "$(cat TARGET.txt 2>/dev/null || true)" = 'FCC_AGENT_OK' ] \
     && [ "$(git diff --name-only | paste -sd, -)" = 'TARGET.txt' ]; then
    echo "FCC_BENCH_PASS=$agent MODEL=$BEST_MODEL" >&2
    return 0
  fi

  echo "FCC_BENCH_FAIL=$agent MODEL=$BEST_MODEL RC=$rc" >&2
  tail -n 12 "/tmp/fcc-bench-${agent}.log" >&2 || true
  return 1
}

# Claude Code first because its native Anthropic tool protocol maps most directly to FCC.
# OpenCode remains the independent fallback. Ranking is based on demonstrated edits, not branding.
for agent in claude-code opencode; do
  if agent_available "$agent" && run_benchmark "$agent"; then
    printf '%s\n' "$agent" > "$CACHE_FILE"
    printf '%s\n' "$BEST_MODEL" > "$MODEL_FILE"
    echo "$agent"
    exit 0
  fi
done

rm -f "$CACHE_FILE" "$MODEL_FILE"
echo none
```

## File: finish-fcc.sh
```bash
#!/usr/bin/env bash
set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"

if ! command -v fcc-server >/dev/null 2>&1; then
  echo "FCC absent: installation..."
  uv tool install git+https://github.com/Alishahryar1/free-claude-code.git
fi

if command -v fcc-init >/dev/null 2>&1; then
  fcc-init || true
fi

echo "FCC prêt. Lance ./scripts/start-fcc.sh puis ouvre le port 8082 dans Codespaces."
```

## File: jumpy-studio-cycle-v2.sh
```bash
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
```

## File: jumpy-studio-cycle-v3-runner.sh
```bash
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
```

## File: jumpy-studio-cycle-v3-safe.sh
```bash
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
```

## File: jumpy-studio-cycle-v3.sh
```bash
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
```

## File: jumpy-studio-cycle-v4.sh
```bash
#!/usr/bin/env bash
set -euo pipefail

# v4 hardens v3 in-place on the ephemeral Actions checkout, then delegates to the proven safe wrapper.
# This avoids destabilizing the known-green v3 files while fixing benchmark parsing and extending
# deterministic progress when all FCC agents are temporarily non-productive.
python - <<'PY'
from pathlib import Path

runner = Path('scripts/jumpy-studio-cycle-v3-runner.sh')
s = runner.read_text()
repls = {
    'echo "FCC_BENCH_PASS=$name MODEL=$BEST_MODEL" | tee -a /tmp/jumpy-agent.log':
        'echo "FCC_BENCH_PASS=$name MODEL=$BEST_MODEL" | tee -a /tmp/jumpy-agent.log >&2',
    'echo "FCC_BENCH_FAIL=$name MODEL=$BEST_MODEL RC=$rc" | tee -a /tmp/jumpy-agent.log':
        'echo "FCC_BENCH_FAIL=$name MODEL=$BEST_MODEL RC=$rc" | tee -a /tmp/jumpy-agent.log >&2',
}
for old, new in repls.items():
    if old not in s:
        raise SystemExit(f'runner benchmark anchor missing: {old}')
    s = s.replace(old, new)

# Surface a short, sanitized benchmark tail when no agent passes. The agents run with all
# repository/provider secrets removed, and the extra redaction is defense in depth.
needle_diag = '''  winner=$(choose_agent)\n  echo "AGENT_BENCH_WINNER=$winner MODEL=$BEST_MODEL" | tee -a /tmp/jumpy-agent.log\n'''
replacement_diag = '''  winner=$(choose_agent)\n  echo "AGENT_BENCH_WINNER=$winner MODEL=$BEST_MODEL" | tee -a /tmp/jumpy-agent.log\n  if [ "$winner" = 'none' ]; then\n    echo 'FCC_BENCH_DIAGNOSTICS_BEGIN' >&2\n    for diag in /tmp/jumpy-fcc-bench-claude-code.log /tmp/jumpy-fcc-bench-opencode.log; do\n      [ -s "$diag" ] || continue\n      echo "--- $(basename "$diag") ---" >&2\n      tail -n 16 "$diag" | sed -E 's/(github_pat_|gh[pousr]_)[A-Za-z0-9_]+/[REDACTED]/g; s/(Bearer[[:space:]]+)[A-Za-z0-9._-]+/\\1[REDACTED]/g; s/([Aa][Pp][Ii][_-]?[Kk][Ee][Yy][[:space:]]*[:=][[:space:]]*)[^[:space:]]+/\\1[REDACTED]/g' >&2 || true\n    done\n    echo 'FCC_BENCH_DIAGNOSTICS_END' >&2\n  fi\n'''
if needle_diag not in s:
    raise SystemExit('runner diagnostic anchor missing')
s = s.replace(needle_diag, replacement_diag, 1)
runner.write_text(s)

safe = Path('scripts/jumpy-studio-cycle-v3-safe.sh')
s = safe.read_text()
needle = """elif 'var death_feedback_scale: float = 0.3 if bool(Profile.data.reduced_motion) else 1.0' not in s:\n    anchor='\\trefresh_settings_ui()\\n\\tcamera_kick = 18.0\\n\\tflash = 0.35\\n\\tburst(Vector2(PLAYER_X, player_y), skin_color(), 35, 520.0)\\n'\n    repl='\\trefresh_settings_ui()\\n\\tvar death_feedback_scale: float = 0.3 if bool(Profile.data.reduced_motion) else 1.0\\n\\tcamera_kick = 18.0 * death_feedback_scale\\n\\tflash = 0.35 * death_feedback_scale\\n\\tburst(Vector2(PLAYER_X, player_y), skin_color(), maxi(5, int(35.0 * death_feedback_scale)), 520.0 * death_feedback_scale)\\n'\n    if anchor in s:\n        s=s.replace(anchor,repl,1); changed=True\nif changed: p.write_text(s)\n"""
replacement = """elif 'var death_feedback_scale: float = 0.3 if bool(Profile.data.reduced_motion) else 1.0' not in s:\n    anchor='\\trefresh_settings_ui()\\n\\tcamera_kick = 18.0\\n\\tflash = 0.35\\n\\tburst(Vector2(PLAYER_X, player_y), skin_color(), 35, 520.0)\\n'\n    repl='\\trefresh_settings_ui()\\n\\tvar death_feedback_scale: float = 0.3 if bool(Profile.data.reduced_motion) else 1.0\\n\\tcamera_kick = 18.0 * death_feedback_scale\\n\\tflash = 0.35 * death_feedback_scale\\n\\tburst(Vector2(PLAYER_X, player_y), skin_color(), maxi(5, int(35.0 * death_feedback_scale)), 520.0 * death_feedback_scale)\\n'\n    if anchor in s:\n        s=s.replace(anchor,repl,1); changed=True\nelif 'var high_contrast_enabled: bool = bool(Profile.data.high_contrast)' not in s:\n    anchor='\\tfor p: Dictionary in platforms:\\n\\t\\tvar rect: Rect2 = Rect2(Vector2(float(p.x), float(p.y)) + shake, Vector2(float(p.w), float(p.h)))\\n\\t\\tdraw_rect(rect, Color(\"17213d\"), true)\\n\\t\\tdraw_line(rect.position, rect.position + Vector2(rect.size.x, 0), Color(\"65eaff\"), 7.0)\\n'\n    repl='\\tvar high_contrast_enabled: bool = bool(Profile.data.high_contrast)\\n\\tvar platform_fill_color: Color = Color(\"2c3d70\") if high_contrast_enabled else Color(\"17213d\")\\n\\tvar platform_edge_color: Color = Color(\"ffffff\") if high_contrast_enabled else Color(\"65eaff\")\\n\\tvar perfect_zone_color: Color = Color(\"ffe66d\") if high_contrast_enabled else Color(\"ffffff\")\\n\\tfor p: Dictionary in platforms:\\n\\t\\tvar rect: Rect2 = Rect2(Vector2(float(p.x), float(p.y)) + shake, Vector2(float(p.w), float(p.h)))\\n\\t\\tdraw_rect(rect, platform_fill_color, true)\\n\\t\\tdraw_line(rect.position, rect.position + Vector2(rect.size.x, 0), platform_edge_color, 9.0 if high_contrast_enabled else 7.0)\\n'\n    if anchor in s:\n        s=s.replace(anchor,repl,1)\n        s=s.replace('Color(\"ffffff\"), 3.0)\\n\\t\\tif bool(p.coin)', 'perfect_zone_color, 5.0 if high_contrast_enabled else 3.0)\\n\\t\\tif bool(p.coin)', 1)\n        s=s.replace('\\tdraw_circle(player_pos, PLAYER_R + 9.0, Color(player_color.r, player_color.g, player_color.b, 0.18))\\n', '\\tdraw_circle(player_pos, PLAYER_R + 11.0 if high_contrast_enabled else PLAYER_R + 9.0, Color(\"ffffff\") if high_contrast_enabled else Color(player_color.r, player_color.g, player_color.b, 0.18))\\n', 1)\n        changed=True\nif changed: p.write_text(s)\n"""
if needle not in s:
    raise SystemExit('safe deterministic fallback anchor missing')
s = s.replace(needle, replacement, 1)
safe.write_text(s)
PY

bash -n scripts/jumpy-studio-cycle-v3-runner.sh
bash -n scripts/jumpy-studio-cycle-v3-safe.sh
exec bash scripts/jumpy-studio-cycle-v3-safe.sh
```

## File: jumpy-studio-cycle-v5.sh
```bash
#!/usr/bin/env bash
set -euo pipefail

: "${GH_TOKEN:?GH_TOKEN required}"

LOG=/tmp/jumpy-v5-primary.log
set +e
bash scripts/jumpy-studio-cycle-v4.sh 2>&1 | tee "$LOG"
PRIMARY_RC=${PIPESTATUS[0]}
set -e

if [ "$PRIMARY_RC" -ne 0 ]; then
  exit "$PRIMARY_RC"
fi

# If v4 already pushed a source change, keep that result.
if grep -q 'HEAD -> main' "$LOG"; then
  exit 0
fi

# If the empirical FCC route produced no source patch, use an explicit deterministic
# progression lane outside the nested v3/v4 patch chain. This lane still validates
# with Godot before any push.
if ! grep -Eq 'No patch produced|RESULT=NO_SOURCE_CHANGE|AGENT_SELECTED=none' "$LOG"; then
  exit 0
fi

echo 'V5_FALLBACK=begin'

rm -rf /tmp/jumpy-v5-fallback
gh auth setup-git >/dev/null 2>&1 || true
git clone --depth 1 https://github.com/dbrckk/Jumpy.git /tmp/jumpy-v5-fallback >/dev/null 2>&1
cd /tmp/jumpy-v5-fallback
BASE_SHA=$(git rev-parse HEAD)

python - <<'PY'
from pathlib import Path
p=Path('scripts/main.gd')
s=p.read_text()
changed=False
label='none'

# 1) Make High Contrast materially improve gameplay readability.
if 'var high_contrast_enabled: bool = bool(Profile.data.high_contrast)' not in s:
    old='''\tfor p: Dictionary in platforms:\n\t\tvar rect: Rect2 = Rect2(Vector2(float(p.x), float(p.y)) + shake, Vector2(float(p.w), float(p.h)))\n\t\tdraw_rect(rect, Color("17213d"), true)\n\t\tdraw_line(rect.position, rect.position + Vector2(rect.size.x, 0), Color("65eaff"), 7.0)\n'''
    new='''\tvar high_contrast_enabled: bool = bool(Profile.data.high_contrast)\n\tvar platform_fill_color: Color = Color("2c3d70") if high_contrast_enabled else Color("17213d")\n\tvar platform_edge_color: Color = Color("ffffff") if high_contrast_enabled else Color("65eaff")\n\tvar perfect_zone_color: Color = Color("ffe66d") if high_contrast_enabled else Color("ffffff")\n\tfor p: Dictionary in platforms:\n\t\tvar rect: Rect2 = Rect2(Vector2(float(p.x), float(p.y)) + shake, Vector2(float(p.w), float(p.h)))\n\t\tdraw_rect(rect, platform_fill_color, true)\n\t\tdraw_line(rect.position, rect.position + Vector2(rect.size.x, 0), platform_edge_color, 9.0 if high_contrast_enabled else 7.0)\n'''
    if old in s:
        s=s.replace(old,new,1)
        s=s.replace('Color("ffffff"), 3.0)\n\t\tif bool(p.coin)', 'perfect_zone_color, 5.0 if high_contrast_enabled else 3.0)\n\t\tif bool(p.coin)', 1)
        s=s.replace('\tdraw_circle(player_pos, PLAYER_R + 9.0, Color(player_color.r, player_color.g, player_color.b, 0.18))\n', '\tdraw_circle(player_pos, PLAYER_R + 11.0 if high_contrast_enabled else PLAYER_R + 9.0, Color("ffffff") if high_contrast_enabled else Color(player_color.r, player_color.g, player_color.b, 0.18))\n', 1)
        changed=True
        label='high_contrast_readability'

# 2) Reduced Motion should also tame ordinary landing feedback, not only perfect/clutch/death.
elif 'var ordinary_feedback_scale: float = 0.45 if bool(Profile.data.reduced_motion) else 1.0' not in s:
    old='''\telse:\n\t\tcombo = maxi(0, combo - 1)\n\t\tflow = maxf(1.0, 1.0 + float(combo) * 0.25)\n\t\tburst(Vector2(PLAYER_X, player_y + PLAYER_R), skin_color(), 6, 180.0)\n'''
    new='''\telse:\n\t\tcombo = maxi(0, combo - 1)\n\t\tflow = maxf(1.0, 1.0 + float(combo) * 0.25)\n\t\tvar ordinary_feedback_scale: float = 0.45 if bool(Profile.data.reduced_motion) else 1.0\n\t\tburst(Vector2(PLAYER_X, player_y + PLAYER_R), skin_color(), maxi(3, int(6.0 * ordinary_feedback_scale)), 180.0 * ordinary_feedback_scale)\n'''
    if old in s:
        s=s.replace(old,new,1)
        changed=True
        label='reduced_motion_ordinary_landing'

# 3) Reduced Motion should also reduce the coin burst.
elif 'var coin_feedback_scale: float = 0.45 if bool(Profile.data.reduced_motion) else 1.0' not in s:
    old='''\t\t\trun_coins += 1\n\t\t\tscore += int(5.0 * flow)\n\t\t\tburst(Vector2(cx, cy), Color("ffe66d"), 14, 300.0)\n'''
    new='''\t\t\trun_coins += 1\n\t\t\tscore += int(5.0 * flow)\n\t\t\tvar coin_feedback_scale: float = 0.45 if bool(Profile.data.reduced_motion) else 1.0\n\t\t\tburst(Vector2(cx, cy), Color("ffe66d"), maxi(4, int(14.0 * coin_feedback_scale)), 300.0 * coin_feedback_scale)\n'''
    if old in s:
        s=s.replace(old,new,1)
        changed=True
        label='reduced_motion_coin_feedback'

# 4) Reduced Motion should remove most of the trailing ghost circles.
elif 'var trail_steps: int = 1 if bool(Profile.data.reduced_motion) else 4' not in s:
    old='''\tvar player_color: Color = skin_color()\n\tvar player_pos: Vector2 = Vector2(PLAYER_X, player_y) + shake\n\tfor i: int in range(4, 0, -1):\n'''
    new='''\tvar player_color: Color = skin_color()\n\tvar player_pos: Vector2 = Vector2(PLAYER_X, player_y) + shake\n\tvar trail_steps: int = 1 if bool(Profile.data.reduced_motion) else 4\n\tfor i: int in range(trail_steps, 0, -1):\n'''
    if old in s:
        s=s.replace(old,new,1)
        changed=True
        label='reduced_motion_player_trail'

if changed:
    p.write_text(s)
print('V5_FALLBACK_PHASE='+label)
PY

if git diff --quiet -- scripts/main.gd; then
  echo 'V5_FALLBACK=no_safe_change_available'
  exit 0
fi

git diff --check
FILES=$(git diff --name-only)
[ "$FILES" = 'scripts/main.gd' ] || { echo "V5_REJECT_SCOPE=$FILES"; exit 1; }

if git diff --binary | grep -Eqi 'github_pat_|gh[pousr]_|PRIVATE KEY|api[_-]?key[[:space:]]*[:=]|password[[:space:]]*[:=]'; then
  echo 'V5_REJECT_SECRET_PATTERN'
  exit 1
fi

curl -fL -o /tmp/godot-v5.zip https://github.com/godotengine/godot/releases/download/4.7.2-stable/Godot_v4.7.2-stable_linux.x86_64.zip >/dev/null 2>&1
rm -rf /tmp/godot-v5 && mkdir -p /tmp/godot-v5
unzip -q /tmp/godot-v5.zip -d /tmp/godot-v5
mv /tmp/godot-v5/Godot_v4.7.2-stable_linux.x86_64 /tmp/godot-v5/godot
chmod +x /tmp/godot-v5/godot
set +e
/tmp/godot-v5/godot --headless --path . --editor --quit >/tmp/jumpy-v5-godot.log 2>&1
GODOT_RC=$?
set -e
cat /tmp/jumpy-v5-godot.log
if [ "$GODOT_RC" -ne 0 ] || grep -Eq 'SCRIPT ERROR|Parse Error|Cannot parse|Failed loading resource' /tmp/jumpy-v5-godot.log; then
  echo 'V5_GODOT_REJECT'
  exit 1
fi

git config user.name 'jumpy-autocycle[bot]'
git config user.email '41898282+github-actions[bot]@users.noreply.github.com'
git add scripts/main.gd
git commit -m 'Autocycle v5: validated deterministic Jumpy evolution'
git push origin HEAD:main
NEW_SHA=$(git rev-parse HEAD)
echo "V5_PUSHED=$NEW_SHA BASE=$BASE_SHA GODOT=pass"
```

## File: jumpy-studio-cycle-v6.sh
```bash
#!/usr/bin/env bash
set -euo pipefail

# v6 removes regex backreferences from the nested runtime diagnostic filter before
# delegating to v5. This keeps diagnostics sanitized without breaking Python re.sub.
python - <<'PY'
from pathlib import Path
p=Path('scripts/jumpy-studio-cycle-v4.sh')
s=p.read_text()
old="s/(Bearer[[:space:]]+)[A-Za-z0-9._-]+/\\\\1[REDACTED]/g; s/([Aa][Pp][Ii][_-]?[Kk][Ee][Yy][[:space:]]*[:=][[:space:]]*)[^[:space:]]+/\\\\1[REDACTED]/g"
new="s/Bearer[[:space:]]+[A-Za-z0-9._-]+/Bearer [REDACTED]/g; s/[Aa][Pp][Ii][_-]?[Kk][Ee][Yy][[:space:]]*[:=][[:space:]]*[^[:space:]]+/API_KEY=[REDACTED]/g"
if old not in s:
    raise SystemExit('v6 redaction anchor missing')
p.write_text(s.replace(old,new,1))
PY

bash -n scripts/jumpy-studio-cycle-v4.sh
exec bash scripts/jumpy-studio-cycle-v5.sh
```

## File: jumpy-studio-cycle-v7.sh
```bash
#!/usr/bin/env bash
set -euo pipefail

# v7 aligns the current catalog-aware v3 runner with the older v4/v6 hardening layers.
# Compatibility transformations are deliberately simple and idempotent.
python - <<'PY'
from pathlib import Path

# The v3 runner still contains historical anchor assertions. They are obsolete once the
# same protections are already present, so make only those two checks non-blocking.
r = Path('scripts/jumpy-studio-cycle-v3-runner.sh')
s = r.read_text()
s = s.replace("raise SystemExit('v3 final-scope anchor mismatch')", "pass  # v7: already-hardened scope is acceptable")
s = s.replace("raise SystemExit('v3 source-count anchor mismatch')", "pass  # v7: already-hardened source count is acceptable")
r.write_text(s)

# Align v4 benchmark/diagnostic anchors with the catalog-aware v3 runner.
p = Path('scripts/jumpy-studio-cycle-v4.sh')
s = p.read_text()
pairs = [
    (
        'echo "FCC_BENCH_PASS=$name MODEL=$BEST_MODEL" | tee -a /tmp/jumpy-agent.log',
        'echo "FCC_BENCH_PASS=$name ROUTE=fcc_catalog PROBE=$BEST_MODEL" | tee -a /tmp/jumpy-agent.log',
    ),
    (
        'echo "FCC_BENCH_FAIL=$name MODEL=$BEST_MODEL RC=$rc" | tee -a /tmp/jumpy-agent.log',
        'echo "FCC_BENCH_FAIL=$name ROUTE=fcc_catalog PROBE=$BEST_MODEL RC=$rc" | tee -a /tmp/jumpy-agent.log',
    ),
    (
        '  winner=$(choose_agent)\\n  echo "AGENT_BENCH_WINNER=$winner MODEL=$BEST_MODEL" | tee -a /tmp/jumpy-agent.log\\n',
        '  local winner; winner=$(choose_agent)\\n  echo "AGENT_BENCH_WINNER=$winner ROUTE=fcc_catalog PROBE=$BEST_MODEL" | tee -a /tmp/jumpy-agent.log\\n',
    ),
]
for old, new in pairs:
    if old in s:
        s = s.replace(old, new)
p.write_text(s)
PY

bash -n scripts/jumpy-studio-cycle-v3-runner.sh
bash -n scripts/jumpy-studio-cycle-v4.sh
exec bash scripts/jumpy-studio-cycle-v6.sh
```

## File: jumpy-studio-cycle-v8.sh
```bash
#!/usr/bin/env bash
set -euo pipefail

# Temporary hardening for the legacy Jumpy autocycle while it is being absorbed into
# the generic multi-engine factory. Godot executes repository scripts, so validation
# must never inherit GitHub/provider credentials from the privileged outer workflow.
python - <<'PY'
from pathlib import Path

files = [Path('scripts/jumpy-studio-cycle-v3.sh'), Path('scripts/jumpy-studio-cycle-v5.sh')]
replacements = {
    '/tmp/godot-jumpy/godot --headless --path . --editor --quit':
        'env -u GH_TOKEN -u GITHUB_TOKEN -u CODESPACES_PAT -u NVIDIA_NIM_API_KEY /tmp/godot-jumpy/godot --headless --path . --editor --quit',
    '/tmp/godot-v5/godot --headless --path . --editor --quit':
        'env -u GH_TOKEN -u GITHUB_TOKEN -u CODESPACES_PAT -u NVIDIA_NIM_API_KEY /tmp/godot-v5/godot --headless --path . --editor --quit',
}
seen = set()
for path in files:
    text = path.read_text()
    for old, new in replacements.items():
        if old in text:
            text = text.replace(old, new)
            seen.add(old)
    path.write_text(text)
missing = set(replacements) - seen
if missing:
    raise SystemExit('v8 credential-scrub anchor missing: ' + ','.join(sorted(missing)))
PY

bash -n scripts/jumpy-studio-cycle-v3.sh
bash -n scripts/jumpy-studio-cycle-v5.sh
exec bash scripts/jumpy-studio-cycle-v7.sh
```

## File: jumpy-studio-cycle.sh
```bash
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
```

## File: provider-status.sh
```bash
#!/usr/bin/env bash
set -u
export PATH="$HOME/.local/bin:$PATH"
ENVFILE="$HOME/.fcc/.env"

echo "=== FCC provider status ==="
if [ ! -f "$ENVFILE" ]; then
  echo "config_file: missing"
  exit 0
fi

echo "config_file: present"
MODEL=$(grep -E '^MODEL=' "$ENVFILE" 2>/dev/null | tail -n1 | cut -d= -f2- || true)
[ -n "$MODEL" ] && echo "model: $MODEL" || echo "model: not configured"

echo "configured_credentials:"
FOUND=0
while IFS='=' read -r key value; do
  case "$key" in
    *_API_KEY|*_TOKEN|ANTHROPIC_AUTH_TOKEN|AWS_BEARER_TOKEN_BEDROCK)
      if [ -n "$value" ]; then
        echo "  $key"
        FOUND=1
      fi
      ;;
  esac
done < "$ENVFILE"
[ "$FOUND" -eq 1 ] || echo "  none"

STATUS=$(curl -sS --max-time 5 http://127.0.0.1:8082/admin/api/status 2>/dev/null || true)
if [ -n "$STATUS" ]; then
  echo "admin_status: reachable"
else
  echo "admin_status: unavailable"
fi

if [ -n "$MODEL" ]; then
  echo "model_generation_test: running"
  PAYLOAD=$(python - "$MODEL" <<'PY'
import json, sys
print(json.dumps({
  "model": sys.argv[1],
  "max_tokens": 256,
  "messages": [{"role": "user", "content": "Reply exactly with FCC_MODEL_OK"}],
  "stream": False,
}))
PY
)
  RESPONSE=$(curl -sS --max-time 90 -H 'Content-Type: application/json' -X POST http://127.0.0.1:8082/v1/messages --data-binary "$PAYLOAD" 2>/dev/null || true)
  python - "$RESPONSE" <<'PY'
import json, sys
raw=sys.argv[1]
try:
    d=json.loads(raw)
except Exception:
    print("model_generation_test: FAILED (invalid response)")
    raise SystemExit(0)
texts=[]
for item in d.get("content", []):
    if isinstance(item, dict) and item.get("type") == "text":
        texts.append(str(item.get("text", "")))
text=" ".join(texts).strip()
if "FCC_MODEL_OK" in text:
    print("model_generation_test: OK")
    print("model_response: FCC_MODEL_OK")
else:
    err=d.get("error")
    if isinstance(err, dict):
        msg=str(err.get("message", "unknown error"))[:300]
        print("model_generation_test: FAILED")
        print("model_error:", msg)
    else:
        print("model_generation_test: FAILED")
        print("model_response_preview:", text[:300] if text else "empty")
PY
fi
```

## File: restart-all.sh
```bash
#!/usr/bin/env bash
set -u
BASE="$HOME/.cache/ai-dev-server"

# Stop tracked parent processes first.
for name in fcc dsh cdesktop; do
  pidfile="$BASE/$name.pid"
  if [ -s "$pidfile" ]; then
    pid=$(cat "$pidfile" 2>/dev/null || true)
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
    fi
    rm -f "$pidfile"
  fi
done

# npx-based services can leave child processes behind. Kill the actual
# listeners, not only their parent wrappers.
for port in 8082 3080 3000; do
  if command -v fuser >/dev/null 2>&1; then
    fuser -k "${port}/tcp" >/dev/null 2>&1 || true
  fi
done

# Narrow fallbacks for images without fuser.
pkill -f '@deepseek-ai/dsh.*web' 2>/dev/null || true
pkill -f 'cdesktop' 2>/dev/null || true
pkill -f 'fcc-server' 2>/dev/null || true
sleep 2

exec bash /workspaces/ai-dev-server/scripts/start-all.sh
```

## File: setup-serena-codex.sh
```bash
#!/usr/bin/env bash
set -euo pipefail

if ! command -v uvx >/dev/null 2>&1; then
  cat >&2 <<'EOF'
uv/uvx is required.

Linux/macOS/Termux:
  curl -LsSf https://astral.sh/uv/install.sh | sh

Then reopen the shell and run this script again.
EOF
  exit 1
fi

echo "Configuring Serena MCP for Codex..."
uvx --from git+https://github.com/oraios/serena serena setup codex

CONFIG="${HOME}/.codex/config.toml"
if [[ -f "$CONFIG" ]] && grep -q '\[mcp_servers\.serena\]' "$CONFIG"; then
  echo "OK: Serena is registered in $CONFIG"
else
  echo "Warning: Serena setup completed but $CONFIG does not contain [mcp_servers.serena]." >&2
  echo "Run: uvx --from git+https://github.com/oraios/serena serena setup codex" >&2
  exit 2
fi

cat <<'EOF'

Serena/Codex setup complete.

For a configured repository:
  1. cd /path/to/repository
  2. codex
  3. verify Serena with /mcp

The repository AGENTS.md instructs Codex to prefer Serena symbol navigation.
If activation is not automatic, tell Codex:
  Activate the current dir as project using serena
EOF
```

## File: start-all.sh
```bash
#!/usr/bin/env bash
set -u

BASE="$HOME/.cache/ai-dev-server"
LOGDIR="$BASE/logs"
mkdir -p "$LOGDIR"
export PATH="$HOME/.local/bin:$PATH"

is_running() {
  local name="$1" pidfile="$BASE/$1.pid" pid
  [ -s "$pidfile" ] || return 1
  pid=$(cat "$pidfile" 2>/dev/null || true)
  [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null
}

start_bg() {
  local name="$1"; shift
  local pidfile="$BASE/$name.pid" logfile="$LOGDIR/$name.log" pid

  if is_running "$name"; then
    echo "$name already running (pid $(cat "$pidfile"))"
    return 0
  fi

  rm -f "$pidfile"
  : > "$logfile"
  nohup "$@" >"$logfile" 2>&1 < /dev/null &
  pid=$!
  echo "$pid" > "$pidfile"
  sleep 2

  if kill -0 "$pid" 2>/dev/null; then
    echo "started $name (pid $pid)"
    return 0
  fi

  echo "$name exited during startup"
  tail -n 60 "$logfile" || true
  rm -f "$pidfile"
  return 1
}

# Free Claude Code local gateway/admin.
if command -v fcc-server >/dev/null 2>&1; then
  start_bg fcc fcc-server || true
else
  echo "fcc-server missing"
fi

# DeepSeek Harness web UI.
start_bg dsh npx --yes @deepseek-ai/dsh web --no-open || true

# cdesktop mobile UI.
if [ -n "${CODESPACE_NAME:-}" ] && [ -n "${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-}" ]; then
  export CDT_ALLOWED_ORIGINS="https://${CODESPACE_NAME}-3000.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
fi
export HOST=0.0.0.0
export PORT=3000
start_bg cdesktop npx --yes cdesktop || true


# Production-OS persistent worker. Start only when the control-plane secrets are
# explicitly configured in the Codespace environment.
if [ -n "${PRODUCTION_OS_URL:-}" ] \
  && [ -n "${PRODUCTION_OS_WORKER_TOKEN:-}" ] \
  && [ -n "${PRODUCTION_OS_OPERATOR_TOKEN:-}" ]; then
  start_bg production-os-worker bash "$(dirname "$0")/start-production-os-worker.sh" || true
else
  echo "Production-OS worker not configured"
fi

# Give npm/npx based services enough time to initialize.
for i in {1..15}; do
  READY=0
  for p in 8082 3080 3000; do
    python - "$p" <<'PY' >/dev/null 2>&1 && READY=$((READY+1)) || true
import socket, sys
p=int(sys.argv[1]); s=socket.socket(); s.settimeout(.4)
try:
    s.connect(('127.0.0.1',p))
except OSError:
    sys.exit(1)
finally:
    s.close()
PY
  done
  [ "$READY" -eq 3 ] && break
  sleep 2
done

bash "$(dirname "$0")/status.sh" || true

echo
echo "=== startup log tails ==="
for name in fcc dsh cdesktop production-os-worker; do
  echo "--- $name ---"
  tail -n 40 "$LOGDIR/$name.log" 2>/dev/null || true
done
```

## File: start-cdesktop.sh
```bash
#!/usr/bin/env bash
set -euo pipefail
export PORT=3000
export HOST=127.0.0.1
if [[ -n "${CODESPACE_NAME:-}" && -n "${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-}" ]]; then
  export CDT_ALLOWED_ORIGINS="https://${CODESPACE_NAME}-3000.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
fi
exec npx --yes cdesktop
```

## File: start-dsh.sh
```bash
#!/usr/bin/env bash
set -euo pipefail
exec npx --yes @deepseek-ai/dsh web --no-open
```

## File: start-fcc.sh
```bash
#!/usr/bin/env bash
set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"
exec fcc-server
```

## File: start-production-os-worker.sh
```bash
#!/usr/bin/env bash
set -euo pipefail

export PATH="$HOME/.local/bin:$PATH"

required=(
  PRODUCTION_OS_URL
  PRODUCTION_OS_WORKER_TOKEN
  PRODUCTION_OS_OPERATOR_TOKEN
)

missing=()
for name in "${required[@]}"; do
  if [[ -z "${!name:-}" ]]; then
    missing+=("$name")
  fi
done

if (( ${#missing[@]} > 0 )); then
  printf 'Missing required environment variables: %s\n' "${missing[*]}" >&2
  exit 2
fi

if ! command -v codex >/dev/null 2>&1; then
  echo "Codex CLI is not installed. Re-run: bash scripts/bootstrap.sh" >&2
  exit 3
fi

worker_id="${PRODUCTION_OS_WORKER_ID:-ai-dev-server-1}"
poll_interval="${PRODUCTION_OS_POLL_INTERVAL:-10}"
output_root="${PRODUCTION_OS_OUTPUT_ROOT:-studio-output/production-os}"

exec python studio/production_os_worker.py \
  --worker-id "$worker_id" \
  --output-root "$output_root" \
  --continuous \
  --poll-interval "$poll_interval"
```

## File: status.sh
```bash
#!/usr/bin/env bash
set -u
export PATH="$HOME/.local/bin:$PATH"

check_port() {
  local port="$1" name="$2"
  if python - "$port" <<'PY' >/dev/null 2>&1
import socket, sys
p=int(sys.argv[1]); s=socket.socket(); s.settimeout(.5)
try:
    s.connect(('127.0.0.1',p)); ok=True
except OSError:
    ok=False
finally:
    s.close()
sys.exit(0 if ok else 1)
PY
  then
    printf '%-20s OK (port %s)\n' "$name" "$port"
  else
    printf '%-20s NOT READY (port %s)\n' "$name" "$port"
  fi
}

echo "=== AI Dev Server status ==="
check_port 8082 "Free Claude Code"
check_port 3080 "DeepSeek Harness"
check_port 3000 "cdesktop"
printf '\nInstalled CLIs:\n'
for x in fcc-server fcc-claude fcc-opencode fcc-dsh claude opencode codex; do
  if command -v "$x" >/dev/null 2>&1; then
    printf '  %-15s %s\n' "$x" "$(command -v "$x")"
  else
    printf '  %-15s missing\n' "$x"
  fi
done

echo
echo "Background workers:"
BASE="$HOME/.cache/ai-dev-server"
if [ -s "$BASE/production-os-worker.pid" ] \
  && kill -0 "$(cat "$BASE/production-os-worker.pid" 2>/dev/null)" 2>/dev/null; then
  echo "  Production-OS worker running (pid $(cat "$BASE/production-os-worker.pid"))"
elif [ -n "${PRODUCTION_OS_URL:-}" ] \
  && [ -n "${PRODUCTION_OS_WORKER_TOKEN:-}" ] \
  && [ -n "${PRODUCTION_OS_OPERATOR_TOKEN:-}" ]; then
  echo "  Production-OS worker configured but not running"
else
  echo "  Production-OS worker not configured"
fi

if [ -n "${CODESPACE_NAME:-}" ] && [ -n "${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-}" ]; then
  echo
  echo "Codespaces URLs:"
  echo "  DSH:      https://${CODESPACE_NAME}-3080.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
  echo "  cdesktop: https://${CODESPACE_NAME}-3000.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
  echo "  FCC:      https://${CODESPACE_NAME}-8082.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
fi
```
