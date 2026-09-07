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
