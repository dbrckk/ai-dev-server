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
