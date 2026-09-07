#!/usr/bin/env bash
set -euo pipefail

SRC="scripts/jumpy-studio-cycle-v3.sh"
TMP="/tmp/jumpy-studio-cycle-v3-runtime.sh"
cp "$SRC" "$TMP"

python - "$TMP" <<'PY'
from pathlib import Path
import sys
p = Path(sys.argv[1])
s = p.read_text()
needle = "subprocess.run(['git','diff','--check'],check=True)"
replacement = r'''# Normalize harmless trailing spaces/tabs in changed text files before strict diff validation.
for x in source:
    try:
        data=open(x,'r',encoding='utf-8').read()
    except (OSError, UnicodeDecodeError):
        continue
    had_nl=data.endswith('\n')
    cleaned='\n'.join(line.rstrip(' \t') for line in data.splitlines())
    if had_nl:
        cleaned += '\n'
    if cleaned != data:
        open(x,'w',encoding='utf-8',newline='').write(cleaned)
subprocess.run(['git','diff','--check'],check=True)'''
if s.count(needle) != 1:
    raise SystemExit('v3 diff-check anchor mismatch')
p.write_text(s.replace(needle, replacement, 1))
PY

bash -n "$TMP"
exec bash "$TMP"
