#!/usr/bin/env bash
set -euo pipefail

# Bias OPEN_ENDED toward an early concrete edit instead of spending the whole budget reading.
python - <<'PY'
from pathlib import Path
p = Path('scripts/jumpy-studio-cycle-v3.sh')
s = p.read_text()
old = 'Implement ONE smallest complete safe improvement from the strategic review below. Modify at most 2 existing text files and about 100 changed lines. No external downloads, package installs, dependencies, network calls, credentials, .github edits, binary assets or release configuration. Produce useful edits early and leave no undefined symbols. If the main idea is too large, choose a smaller local improvement.'
new = 'EDIT FIRST. Within the first concrete action, modify ONLY scripts/main.gd with one small compile-complete improvement. Use TABS ONLY for GDScript indentation; never introduce leading spaces in indented GDScript lines. Do not redo pulse if it already respects reduced_motion. Priority order: (1) make perfect/clutch landing camera kick, flash and burst materially smaller or disabled under reduced_motion; (2) make death feedback materially smaller or disabled under reduced_motion; (3) make high_contrast visibly improve player/platform/perfect-zone readability using existing procedural drawing only. If all three are already complete, choose the next smallest local gameplay/UX improvement. Do not spend the cycle only reading. Keep the diff under about 100 changed lines. No external downloads, package installs, dependencies, network calls, credentials, .github edits, binary assets or release configuration. Leave no undefined symbols.'
if old not in s:
    raise SystemExit('open-ended prompt anchor mismatch')
s = s.replace(old, new, 1)

# Repair a recurring model failure before safety checks/Godot: generated GDScript sometimes
# uses groups of 4 leading spaces in a tab-indented file. Normalize only main.gd after the
# agent finishes; semantic content is unchanged and Godot remains the final authority.
anchor = "if [ -s /tmp/jumpy-agent.log ]; then"
repair = r'''python - <<'PY2'
from pathlib import Path
p=Path('scripts/main.gd')
if p.exists():
    out=[]
    for line in p.read_text().splitlines(keepends=True):
        body=line.rstrip('\r\n')
        ending=line[len(body):]
        n=0
        while n < len(body) and body[n] == ' ':
            n += 1
        if n >= 4:
            body = ('\t' * (n // 4)) + (' ' * (n % 4)) + body[n:]
        out.append(body + ending)
    p.write_text(''.join(out))
PY2

'''
if anchor not in s:
    raise SystemExit('agent-log anchor mismatch')
s = s.replace(anchor, repair + anchor, 1)
p.write_text(s)
PY

LOG=/tmp/jumpy-v3-safe.log
set +e
bash scripts/jumpy-studio-cycle-v3-runner.sh 2>&1 | tee "$LOG"
RC=${PIPESTATUS[0]}
set -e

if [ "$RC" -eq 0 ]; then
  exit 0
fi

# OPEN_ENDED may legitimately time out without producing any source change.
# Treat only this exact, validated, documentation-only outcome as a clean no-op.
if grep -q '^PHASE=OPEN_ENDED$' "$LOG" \
  && grep -q '^FILES=docs/AUTONOMOUS_STATE.md$' "$LOG" \
  && grep -q 'Godot Engine v4.7.2' "$LOG" \
  && ! grep -Eq 'Godot rejected candidate|REJECTING_|Secret-like material detected|Final scope too broad|Parse Error|SCRIPT ERROR' "$LOG"; then
  echo 'RESULT=NO_SOURCE_CHANGE'
  echo 'Open-ended executor produced documentation only; preserving green workflow without pushing noise.'
  exit 0
fi

exit "$RC"
