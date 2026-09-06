#!/usr/bin/env bash
set -u
export PATH="$HOME/.local/bin:$PATH"
BASE="$HOME/.cache/ai-dev-server"
mkdir -p "$BASE/logs"

if ! curl -fsS --max-time 3 http://127.0.0.1:8082/health >/dev/null 2>&1; then
  nohup fcc-server >"$BASE/logs/fcc.log" 2>&1 &
  for i in {1..20}; do
    curl -fsS --max-time 2 http://127.0.0.1:8082/health >/dev/null 2>&1 && break
    sleep 1
  done
fi
curl -fsS --max-time 3 http://127.0.0.1:8082/health >/dev/null 2>&1 || { echo 'fcc_service: FAILED'; exit 0; }

echo 'fcc_service: OK'
WORK=/tmp/jumpy-fcc-audit
rm -rf "$WORK"
git clone --depth 1 https://github.com/dbrckk/Jumpy.git "$WORK" >/dev/null 2>&1 || { echo 'clone: FAILED'; exit 0; }
cd "$WORK"

MODEL=$(grep -E '^MODEL=' "$HOME/.fcc/.env" | tail -n1 | cut -d= -f2-)
CODE=$(python - <<'PY'
from pathlib import Path
files=['project.godot','scripts/main.gd','scripts/profile.gd','scripts/integrations.gd','export_presets.cfg']
for f in files:
    p=Path(f)
    if p.exists():
        print(f'\n### FILE {f}\n')
        print(p.read_text(errors='replace'))
PY
)
PROMPT="You are the release-blocker reviewer for a Godot 4.7 portrait mobile game. Review only blocking/high-impact correctness issues in the supplied files: parse/runtime errors, broken Godot APIs, impossible gameplay, save corruption, nondeterministic daily level generation, mobile input blockers, or unsafe credential handling. Ignore stylistic/nice-to-have concerns. Godot CI already imports/parses the project successfully. Reply on ONE line only: AUDIT_OK: <short assessment> OR AUDIT_ISSUES: <up to 4 concise issues with file/function and fix>.\n\n$CODE"
PAYLOAD=$(python - "$MODEL" "$PROMPT" <<'PY'
import json,sys
print(json.dumps({'model':sys.argv[1],'max_tokens':900,'messages':[{'role':'user','content':sys.argv[2]}],'stream':False}))
PY
)
RESPONSE=$(curl -sS --max-time 150 -H 'Content-Type: application/json' -X POST http://127.0.0.1:8082/v1/messages --data-binary "$PAYLOAD" || true)
python - "$RESPONSE" <<'PY'
import json,sys,re
try:
    d=json.loads(sys.argv[1])
    text=' '.join(str(x.get('text','')) for x in d.get('content',[]) if isinstance(x,dict) and x.get('type')=='text')
    m=re.search(r'(AUDIT_(?:OK|ISSUES):.*)', text, re.S)
    if m:
        print('fcc_release_audit:', re.sub(r'\s+',' ',m.group(1))[:3000])
    else:
        print('fcc_release_audit: NO_VERDICT', re.sub(r'\s+',' ',text)[:1200])
except Exception as e:
    print('fcc_release_audit: INVALID_RESPONSE', str(e))
PY
exit 0
