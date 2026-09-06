#!/usr/bin/env bash
set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"

BASE="$HOME/.cache/ai-dev-server"
LOGDIR="$BASE/logs"
WORK=/tmp/jumpy-autonomous-cycle
mkdir -p "$LOGDIR"

if ! curl -fsS --max-time 3 http://127.0.0.1:8082/health >/dev/null 2>&1; then
  nohup fcc-server >"$LOGDIR/fcc.log" 2>&1 &
  for i in {1..30}; do
    curl -fsS --max-time 2 http://127.0.0.1:8082/health >/dev/null 2>&1 && break
    sleep 1
  done
fi
curl -fsS --max-time 3 http://127.0.0.1:8082/health >/dev/null

rm -rf "$WORK"
git clone --depth 1 https://github.com/dbrckk/Jumpy.git "$WORK" >/dev/null 2>&1
cd "$WORK"

PROMPT=$(cat <<'EOF'
You are the autonomous lead developer of Jumpy, a Godot 4.7 mobile arcade game whose goal is exceptional replayability, retention, shareability, polish and technical quality. Work directly in this repository.

Perform exactly ONE high-impact, coherent evolution cycle. First inspect README.md, docs/GAME_DESIGN.md, docs/PRODUCTION_ROADMAP.md, SETUP_REQUIRED.txt, project.godot and the current implementation. Choose the highest-value improvement that is safe to implement without external credentials or paid services. Prefer core feel, retention, social/viral mechanics, UX, accessibility, performance, robustness and production polish over feature bloat.

Rules:
- Actually edit the repository; do not only explain.
- Keep the game instantly understandable and one-touch-first.
- Do not add secrets, credentials, paid dependencies, telemetry endpoints, store publishing, destructive migrations or copyrighted third-party assets.
- If any external API/account/credential/store action becomes necessary, update SETUP_REQUIRED.txt with concise exact instructions BEFORE code depends on it; otherwise avoid that dependency.
- Preserve Godot 4.7 compatibility, portrait mobile scaling and deterministic Daily mode.
- Preserve or improve 60 FPS suitability on mid-range Android.
- Do not edit .github workflows in this cycle.
- Do not commit or push; the outer automation handles version control.
- Finish by ensuring edits are internally consistent.
EOF
)

# Agent runs in a credential-free disposable clone, so write permissions are safe here.
set +e
AGENT_OUT=$(timeout 210s fcc-claude -p --dangerously-skip-permissions "$PROMPT" 2>&1)
AGENT_RC=$?
set -e
printf '%s\n' "$AGENT_OUT" > /tmp/jumpy-agent-output.txt

if [ "$AGENT_RC" -ne 0 ] && [ "$AGENT_RC" -ne 124 ]; then
  echo "CYCLE_STATUS=AGENT_FAILED"
  echo "AGENT_RC=$AGENT_RC"
  tail -n 40 /tmp/jumpy-agent-output.txt | sed 's/^/AGENT: /'
  exit 0
fi

# Never allow the agent to alter automation or hidden Git metadata.
git checkout -- .github 2>/dev/null || true

if git diff --quiet && [ -z "$(git ls-files --others --exclude-standard)" ]; then
  echo "CYCLE_STATUS=NO_CHANGE"
  tail -n 20 /tmp/jumpy-agent-output.txt | sed 's/^/AGENT: /'
  exit 0
fi

# Reject accidental credential-looking material before exporting the patch.
if git diff -- . ':!.github' | grep -Eiq '(github_pat_|ghp_|ghu_|nvapi-|BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY|api[_-]?key[[:space:]]*=[[:space:]]*["'"'][A-Za-z0-9_-]{16,})'; then
  echo "CYCLE_STATUS=REJECTED_SECRET_PATTERN"
  exit 0
fi

git diff --check

# Include tracked and untracked text files in a temporary index, then emit one binary-safe patch.
git add -A -- ':!.github'
git diff --cached --binary > /tmp/jumpy-cycle.patch

CHANGED=$(git diff --cached --name-only | tr '\n' ',' | sed 's/,$//')
echo "CYCLE_STATUS=PATCH_READY"
echo "CHANGED_FILES=$CHANGED"
echo "PATCH_B64_BEGIN"
base64 -w0 /tmp/jumpy-cycle.patch
echo
echo "PATCH_B64_END"
