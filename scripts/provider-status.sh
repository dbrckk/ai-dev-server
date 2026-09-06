#!/usr/bin/env bash
set -u
export PATH="$HOME/.local/bin:$PATH"
ENVFILE="$HOME/.fcc/.env"

echo "=== FCC provider status ==="
if [ ! -f "$ENVFILE" ]; then
  echo "config_file: missing"
  exit 0
fi

echo "config_file: present"
MODEL=$(grep -E '^MODEL=' "$ENVFILE" 2>/dev/null | tail -n1 | cut -d= -f2- || true)
[ -n "$MODEL" ] && echo "model: $MODEL" || echo "model: not configured"

echo "configured_credentials:"
FOUND=0
while IFS='=' read -r key value; do
  case "$key" in
    *_API_KEY|*_TOKEN|ANTHROPIC_AUTH_TOKEN|AWS_BEARER_TOKEN_BEDROCK)
      if [ -n "$value" ]; then
        echo "  $key"
        FOUND=1
      fi
      ;;
  esac
done < "$ENVFILE"
[ "$FOUND" -eq 1 ] || echo "  none"

# This endpoint is loopback-only and reports runtime health, without printing secrets.
STATUS=$(curl -sS --max-time 5 http://127.0.0.1:8082/admin/api/status 2>/dev/null || true)
if [ -n "$STATUS" ]; then
  echo "admin_status: reachable"
else
  echo "admin_status: unavailable"
fi
