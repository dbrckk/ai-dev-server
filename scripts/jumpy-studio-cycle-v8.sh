#!/usr/bin/env bash
set -euo pipefail

# Temporary hardening for the legacy Jumpy autocycle while it is being absorbed into
# the generic multi-engine factory. Godot executes repository scripts, so validation
# must never inherit GitHub/provider credentials from the privileged outer workflow.
python - <<'PY'
from pathlib import Path

files = [Path('scripts/jumpy-studio-cycle-v3.sh'), Path('scripts/jumpy-studio-cycle-v5.sh')]
replacements = {
    '/tmp/godot-jumpy/godot --headless --path . --editor --quit':
        'env -u GH_TOKEN -u GITHUB_TOKEN -u CODESPACES_PAT -u NVIDIA_NIM_API_KEY /tmp/godot-jumpy/godot --headless --path . --editor --quit',
    '/tmp/godot-v5/godot --headless --path . --editor --quit':
        'env -u GH_TOKEN -u GITHUB_TOKEN -u CODESPACES_PAT -u NVIDIA_NIM_API_KEY /tmp/godot-v5/godot --headless --path . --editor --quit',
}
seen = set()
for path in files:
    text = path.read_text()
    for old, new in replacements.items():
        if old in text:
            text = text.replace(old, new)
            seen.add(old)
    path.write_text(text)
missing = set(replacements) - seen
if missing:
    raise SystemExit('v8 credential-scrub anchor missing: ' + ','.join(sorted(missing)))
PY

bash -n scripts/jumpy-studio-cycle-v3.sh
bash -n scripts/jumpy-studio-cycle-v5.sh
exec bash scripts/jumpy-studio-cycle-v7.sh
