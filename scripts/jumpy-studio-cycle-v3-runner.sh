#!/usr/bin/env bash
set -euo pipefail

SRC="scripts/jumpy-studio-cycle-v3.sh"
TMP="/tmp/jumpy-studio-cycle-v3-runtime.sh"
cp "$SRC" "$TMP"

python - "$TMP" <<'PY'
from pathlib import Path
import re, sys
p = Path(sys.argv[1])
s = p.read_text()

# 0) Strategy is advisory. A provider stall must never consume most of a 20-minute cycle.
# Repository-derived deterministic phases continue even when the strategy endpoint is unavailable.
s = s.replace("curl -sS --max-time 70 -H 'Content-Type: application/json'", "curl -sS --max-time 20 -H 'Content-Type: application/json'", 1)

# 1) Harmless formatting defects from an interrupted agent should not waste a cycle.
needle = "subprocess.run(['git','diff','--check'],check=True)"
replacement = r'''# Normalize harmless trailing spaces/tabs in changed text files before strict diff validation.
for x in source:
    try:
        data=open(x,'r',encoding='utf-8').read()
    except (OSError, UnicodeDecodeError):
        continue
    had_nl=data.endswith('\n')
    cleaned='\n'.join(line.rstrip(' \t') for line in data.splitlines())
    if had_nl:
        cleaned += '\n'
    if cleaned != data:
        open(x,'w',encoding='utf-8',newline='').write(cleaned)
subprocess.run(['git','diff','--check'],check=True)'''
if s.count(needle) != 1:
    raise SystemExit('v3 diff-check anchor mismatch')
s = s.replace(needle, replacement, 1)

# 2) Known settings phase is deterministic: no long model call, no partial callbacks.
pattern = r"  ACCESSIBILITY_SETTINGS_UI\)\n.*?\n    run_agent 120 ;;\n"
phase = r"""  ACCESSIBILITY_SETTINGS_UI)
    python - <<'PY2'
from pathlib import Path
p=Path('scripts/main.gd')
s=p.read_text()

def once(old: str, new: str, label: str) -> None:
    global s
    if new in s:
        return
    if s.count(old) != 1:
        raise SystemExit(f'{label} anchor mismatch')
    s=s.replace(old,new,1)

once('var ui: Dictionary = {}\n', 'var ui: Dictionary = {}\nvar settings_open: bool = false\n', 'settings state')

old='\tui.skin = make_button(root, "SKIN", Vector2(375, 1240), Vector2(330, 82), cycle_skin)\n'
new=old + '''\tui.settings = make_button(root, "SETTINGS", Vector2(375, 1340), Vector2(330, 82), settings_pressed)\n\tui.setting_sound = make_button(root, "", Vector2(120, 1450), Vector2(390, 82), func() -> void: toggle_preference("sound"))\n\tui.setting_haptics = make_button(root, "", Vector2(570, 1450), Vector2(390, 82), func() -> void: toggle_preference("haptics"))\n\tui.setting_motion = make_button(root, "", Vector2(120, 1550), Vector2(390, 82), func() -> void: toggle_preference("reduced_motion"))\n\tui.setting_contrast = make_button(root, "", Vector2(570, 1550), Vector2(390, 82), func() -> void: toggle_preference("high_contrast"))\n'''
once(old,new,'settings buttons')

anchor='func reset_run(use_daily: bool) -> void:\n'
functions='''func settings_pressed() -> void:\n\tif state != "READY":\n\t\treturn\n\tsettings_open = not settings_open\n\tshow_menu(true)\n\nfunc toggle_preference(key: String) -> void:\n\tif state != "READY":\n\t\treturn\n\tProfile.set_preference(key, not bool(Profile.data.get(key, false)))\n\trefresh_settings_ui()\n\tqueue_redraw()\n\nfunc refresh_settings_ui() -> void:\n\tif not ui.has("settings"):\n\t\treturn\n\tui.settings.text = "BACK" if settings_open else "SETTINGS"\n\tvar show_settings: bool = state == "READY" and settings_open\n\tui.setting_sound.visible = show_settings\n\tui.setting_haptics.visible = show_settings\n\tui.setting_motion.visible = show_settings\n\tui.setting_contrast.visible = show_settings\n\tui.setting_sound.text = "SOUND  %s" % ("ON" if bool(Profile.data.sound) else "OFF")\n\tui.setting_haptics.text = "HAPTICS  %s" % ("ON" if bool(Profile.data.haptics) else "OFF")\n\tui.setting_motion.text = "REDUCED MOTION  %s" % ("ON" if bool(Profile.data.reduced_motion) else "OFF")\n\tui.setting_contrast.text = "HIGH CONTRAST  %s" % ("ON" if bool(Profile.data.high_contrast) else "OFF")\n\n'''
once(anchor,functions+anchor,'settings functions')

old_show='''func show_menu(value: bool) -> void:\n\tui.title.visible = value\n\tui.subtitle.visible = value\n\tui.hint.visible = value\n\tui.mission.visible = value\n\tui.daily.visible = value\n\tui.normal.visible = value\n\tui.skin.visible = value\n\tui.gameover.visible = false\n'''
new_show='''func show_menu(value: bool) -> void:\n\tif not value:\n\t\tsettings_open = false\n\tvar show_main: bool = value and not settings_open\n\tui.title.visible = show_main\n\tui.subtitle.visible = show_main\n\tui.hint.visible = show_main\n\tui.mission.visible = show_main\n\tui.daily.visible = show_main\n\tui.normal.visible = show_main\n\tui.skin.visible = show_main\n\tui.settings.visible = value\n\trefresh_settings_ui()\n\tui.gameover.visible = false\n'''
once(old_show,new_show,'show_menu settings integration')

once('\tui.skin.visible = false\n\tcamera_kick = 18.0\n', '\tui.skin.visible = false\n\tui.settings.visible = false\n\trefresh_settings_ui()\n\tcamera_kick = 18.0\n', 'death settings visibility')

p.write_text(s)
PY2
    NOTE='Added deterministic persistent player-facing settings for sound, haptics, reduced motion and high contrast.' ;;
"""
s2, n = re.subn(pattern, lambda _m: phase, s, flags=re.S)
if n != 1:
    raise SystemExit(f'v3 settings-phase anchor mismatch ({n})')
s = s2

# 3) Final validation must include untracked files too. Intent-to-add makes them visible to diff/scope/secret scans.
final_needle = "# Final scope and secret check after patch application.\nFILES=$(git diff --name-only)"
final_replacement = "# Final scope and secret check after patch application. Include untracked files in every gate.\ngit add -N --all\nFILES=$(git diff --name-only)"
if s.count(final_needle) != 1:
    raise SystemExit('v3 final-scope anchor mismatch')
s = s.replace(final_needle, final_replacement, 1)

# 4) A diagnostic-only cycle has zero source files and is valid. Avoid grep+pipefail treating that as an error.
count_needle = "COUNT=$(printf '%s\\n' \"$FILES\" | grep -v '^docs/AUTONOMOUS_STATE.md$' | sed '/^$/d' | wc -l)"
count_replacement = "COUNT=$(printf '%s\\n' \"$FILES\" | awk 'NF && $0 != \"docs/AUTONOMOUS_STATE.md\" {n++} END {print n+0}')"
if s.count(count_needle) != 1:
    raise SystemExit('v3 source-count anchor mismatch')
s = s.replace(count_needle, count_replacement, 1)

# 5) Empirically benchmark FCC agents in the live Codespace before entrusting Jumpy to one.
# Text completion/tool-probe success is necessary but not sufficient: the winner must perform
# an exact file edit in a disposable git repository using the same BEST_MODEL.
agent_pattern = r'''run_agent\(\) \{\n.*?\n\}\n\ncase \"\$PHASE\" in'''
agent_replacement = r'''run_agent() {
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

  benchmark_agent() {
    local name="$1" dir cmd rc
    dir=$(mktemp -d "/tmp/jumpy-fcc-bench-${name}.XXXXXX")
    pushd "$dir" >/dev/null
    git init -q
    git config user.email benchmark@localhost
    git config user.name 'FCC benchmark'
    printf 'ORIGINAL\n' > TARGET.txt
    git add TARGET.txt && git commit -qm baseline
    printf '%s\n' 'Edit TARGET.txt. Replace its entire contents with exactly FCC_AGENT_OK. Do not create other files. Perform the edit; do not merely explain.' >/tmp/jumpy-fcc-bench-brief.txt
    case "$name" in
      claude-code) cmd='fcc-claude --model "$BEST_MODEL" --permission-mode acceptEdits -p "$(cat /tmp/jumpy-fcc-bench-brief.txt)"' ;;
      opencode) cmd='fcc-opencode run --model "$BEST_MODEL" "$(cat /tmp/jumpy-fcc-bench-brief.txt)"' ;;
      *) popd >/dev/null; rm -rf "$dir"; return 1 ;;
    esac
    set +e
    timeout -k 3s 32s env -u GH_TOKEN -u GITHUB_TOKEN -u CODESPACES_PAT -u NVIDIA_NIM_API_KEY \
      BEST_MODEL="$BEST_MODEL" GIT_TERMINAL_PROMPT=0 SSH_AUTH_SOCK= \
      bash -lc "$cmd" >"/tmp/jumpy-fcc-bench-${name}.log" 2>&1
    rc=$?
    set -e
    local ok=1
    if [ "$rc" -eq 0 ] && [ "$(cat TARGET.txt 2>/dev/null || true)" = 'FCC_AGENT_OK' ] \
       && [ "$(git diff --name-only | paste -sd, -)" = 'TARGET.txt' ]; then
      ok=0
    fi
    popd >/dev/null
    rm -rf "$dir"
    if [ "$ok" -eq 0 ]; then
      echo "FCC_BENCH_PASS=$name MODEL=$BEST_MODEL" | tee -a /tmp/jumpy-agent.log
      return 0
    fi
    echo "FCC_BENCH_FAIL=$name MODEL=$BEST_MODEL RC=$rc" | tee -a /tmp/jumpy-agent.log
    tail -n 10 "/tmp/jumpy-fcc-bench-${name}.log" >>/tmp/jumpy-agent.log 2>/dev/null || true
    return 1
  }

  choose_agent() {
    local cache="$HOME/.cache/ai-dev-server/fcc-agent-winner.txt"
    local model_cache="$HOME/.cache/ai-dev-server/fcc-agent-model.txt"
    mkdir -p "$HOME/.cache/ai-dev-server"
    if [ -s "$cache" ] && [ -s "$model_cache" ] && [ "$(cat "$model_cache")" = "$BEST_MODEL" ]; then
      local cached
      cached=$(cat "$cache")
      if agent_available "$cached"; then
        echo "$cached"
        return 0
      fi
    fi
    local candidate
    for candidate in claude-code opencode; do
      if agent_available "$candidate" && benchmark_agent "$candidate"; then
        printf '%s\n' "$candidate" > "$cache"
        printf '%s\n' "$BEST_MODEL" > "$model_cache"
        echo "$candidate"
        return 0
      fi
    done
    rm -f "$cache" "$model_cache"
    echo none
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
    # A cached winner that stops editing is immediately invalidated so the next route is re-benchmarked.
    rm -f "$HOME/.cache/ai-dev-server/fcc-agent-winner.txt" "$HOME/.cache/ai-dev-server/fcc-agent-model.txt"
    return 1
  }

  ensure_fcc || { echo 'AGENT_SELECTED=none FCC_UNAVAILABLE=1' | tee -a /tmp/jumpy-agent.log; return 0; }
  local winner
  winner=$(choose_agent)
  echo "AGENT_BENCH_WINNER=$winner MODEL=$BEST_MODEL" | tee -a /tmp/jumpy-agent.log

  if [ "$winner" = 'claude-code' ]; then
    run_one_agent "claude-code" "$primary_budget" 'fcc-claude --model "$BEST_MODEL" --permission-mode acceptEdits -p "$(cat /tmp/brief.txt)"' && return 0
    if agent_available opencode && benchmark_agent opencode; then
      run_one_agent "opencode" "$fallback_budget" 'fcc-opencode run --model "$BEST_MODEL" "$(cat /tmp/brief.txt)"' && return 0
    fi
  elif [ "$winner" = 'opencode' ]; then
    run_one_agent "opencode" "$primary_budget" 'fcc-opencode run --model "$BEST_MODEL" "$(cat /tmp/brief.txt)"' && return 0
    if agent_available claude-code && benchmark_agent claude-code; then
      run_one_agent "claude-code" "$fallback_budget" 'fcc-claude --model "$BEST_MODEL" --permission-mode acceptEdits -p "$(cat /tmp/brief.txt)"' && return 0
    fi
  fi

  echo 'AGENT_SELECTED=none' | tee -a /tmp/jumpy-agent.log
  return 0
}

case "$PHASE" in'''
s2, n = re.subn(agent_pattern, agent_replacement, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f'v3 empirical-agent anchor mismatch ({n})')
s = s2

p.write_text(s)
PY

bash -n "$TMP"
exec bash "$TMP"
