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

# 0) Strategy is advisory. Provider stalls must never consume a deterministic cycle.
# For known repository-derived phases, skip the model review entirely and use a concise local snapshot.
strategy_start = "MODEL=$(grep -E '^MODEL=' \"$HOME/.fcc/.env\" | tail -n1 | cut -d= -f2-)\nCONTEXT=$(python - <<'PY'"
strategy_end = "PY\n)\n\nPHASE=$(python - <<'PY'"
if strategy_start not in s or strategy_end not in s:
    raise SystemExit('v3 strategy block anchors missing')
pre, rest = s.split(strategy_start, 1)
strategy_body, post = rest.split(strategy_end, 1)
replacement = r'''# Resolve deterministic phase before spending model budget.
PRE_PHASE=$(python - <<'PY'
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

if [ "$PRE_PHASE" = OPEN_ENDED ] || [ "$PRE_PHASE" = ACCESSIBILITY_VISUAL_BEHAVIOR ]; then
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
  RESP=$(curl -sS --max-time 20 -H 'Content-Type: application/json' -X POST http://127.0.0.1:8082/v1/messages --data-binary "$PAYLOAD" || true)
  python - "$RESP" <<'PY' >/tmp/jumpy-strategy.txt
import json,sys
try:
    d=json.loads(sys.argv[1]); t='\n'.join(str(x.get('text','')) for x in d.get('content',[]) if isinstance(x,dict) and x.get('type')=='text').strip()
except Exception: t=''
print((t or 'Strategic review unavailable; use repository evidence and living state.')[-4500:])
PY
else
  printf 'Deterministic phase %s selected from current repository evidence; no model call required.\n' "$PRE_PHASE" >/tmp/jumpy-strategy.txt
fi

PHASE=$(python - <<'PY' '''
s = pre + replacement + post

# The original phase resolver body now starts after our replacement. Keep it, but force agreement with PRE_PHASE.
resolver_end = "PY\n)\n\necho \"PHASE=$PHASE\""
if resolver_end not in s:
    raise SystemExit('v3 resolver end anchor missing')
s = s.replace(resolver_end, "PY\n)\nPHASE=\"$PRE_PHASE\"\n\necho \"PHASE=$PHASE\"", 1)

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

p.write_text(s)
PY

bash -n "$TMP"
exec bash "$TMP"
