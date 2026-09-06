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

STATUS=$(curl -sS --max-time 5 http://127.0.0.1:8082/admin/api/status 2>/dev/null || true)
if [ -n "$STATUS" ]; then
  echo "admin_status: reachable"
else
  echo "admin_status: unavailable"
fi

if [ -n "$MODEL" ]; then
  echo "model_generation_test: running"
  PAYLOAD=$(python - "$MODEL" <<'PY'
import json, sys
print(json.dumps({
  "model": sys.argv[1],
  "max_tokens": 256,
  "messages": [{"role": "user", "content": "Reply exactly with FCC_MODEL_OK"}],
  "stream": False,
}))
PY
)
  RESPONSE=$(curl -sS --max-time 90 -H 'Content-Type: application/json' -X POST http://127.0.0.1:8082/v1/messages --data-binary "$PAYLOAD" 2>/dev/null || true)
  python - "$RESPONSE" <<'PY'
import json, sys
raw=sys.argv[1]
try:
    d=json.loads(raw)
except Exception:
    print("model_generation_test: FAILED (invalid response)")
    raise SystemExit(0)
texts=[]
for item in d.get("content", []):
    if isinstance(item, dict) and item.get("type") == "text":
        texts.append(str(item.get("text", "")))
text=" ".join(texts).strip()
if "FCC_MODEL_OK" in text:
    print("model_generation_test: OK")
    print("model_response: FCC_MODEL_OK")
else:
    err=d.get("error")
    if isinstance(err, dict):
        msg=str(err.get("message", "unknown error"))[:300]
        print("model_generation_test: FAILED")
        print("model_error:", msg)
    else:
        print("model_generation_test: FAILED")
        print("model_response_preview:", text[:300] if text else "empty")
PY
fi
