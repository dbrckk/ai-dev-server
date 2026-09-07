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
