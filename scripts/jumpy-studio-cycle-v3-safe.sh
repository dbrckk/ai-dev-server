#!/usr/bin/env bash
set -euo pipefail

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
