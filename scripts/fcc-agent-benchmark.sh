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
