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
phase = r'''  ACCESSIBILITY_SETTINGS_UI)
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

# Death screen must hide the settings button too.
once('\tui.skin.visible = false\n\tcamera_kick = 18.0\n', '\tui.skin.visible = false\n\tui.settings.visible = false\n\trefresh_settings_ui()\n\tcamera_kick = 18.0\n', 'death settings visibility')

p.write_text(s)
PY2
    NOTE='Added deterministic persistent player-facing settings for sound, haptics, reduced motion and high contrast.' ;;
'''
s2, n = re.subn(pattern, phase, s, flags=re.S)
if n != 1:
    raise SystemExit(f'v3 settings-phase anchor mismatch ({n})')
p.write_text(s2)
PY

bash -n "$TMP"
exec bash "$TMP"
