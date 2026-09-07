#!/usr/bin/env bash
set -euo pipefail

# v6 removes regex backreferences from the nested runtime diagnostic filter before
# delegating to v5. This keeps diagnostics sanitized without breaking Python re.sub.
python - <<'PY'
from pathlib import Path
p=Path('scripts/jumpy-studio-cycle-v4.sh')
s=p.read_text()
old="s/(Bearer[[:space:]]+)[A-Za-z0-9._-]+/\\\\1[REDACTED]/g; s/([Aa][Pp][Ii][_-]?[Kk][Ee][Yy][[:space:]]*[:=][[:space:]]*)[^[:space:]]+/\\\\1[REDACTED]/g"
new="s/Bearer[[:space:]]+[A-Za-z0-9._-]+/Bearer [REDACTED]/g; s/[Aa][Pp][Ii][_-]?[Kk][Ee][Yy][[:space:]]*[:=][[:space:]]*[^[:space:]]+/API_KEY=[REDACTED]/g"
if old not in s:
    raise SystemExit('v6 redaction anchor missing')
p.write_text(s.replace(old,new,1))
PY

bash -n scripts/jumpy-studio-cycle-v4.sh
exec bash scripts/jumpy-studio-cycle-v5.sh
