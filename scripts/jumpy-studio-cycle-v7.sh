#!/usr/bin/env bash
set -euo pipefail

# v7 aligns the v4 hardening layer with the catalog-aware v3 runner.
# Keep this compatibility shim deliberately simple: no nested dictionaries or regexes.
python - <<'PY'
from pathlib import Path
p = Path('scripts/jumpy-studio-cycle-v4.sh')
s = p.read_text()

pairs = [
    (
        'echo "FCC_BENCH_PASS=$name MODEL=$BEST_MODEL" | tee -a /tmp/jumpy-agent.log',
        'echo "FCC_BENCH_PASS=$name ROUTE=fcc_catalog PROBE=$BEST_MODEL" | tee -a /tmp/jumpy-agent.log',
    ),
    (
        'echo "FCC_BENCH_FAIL=$name MODEL=$BEST_MODEL RC=$rc" | tee -a /tmp/jumpy-agent.log',
        'echo "FCC_BENCH_FAIL=$name ROUTE=fcc_catalog PROBE=$BEST_MODEL RC=$rc" | tee -a /tmp/jumpy-agent.log',
    ),
    (
        '  winner=$(choose_agent)\\n  echo "AGENT_BENCH_WINNER=$winner MODEL=$BEST_MODEL" | tee -a /tmp/jumpy-agent.log\\n',
        '  local winner; winner=$(choose_agent)\\n  echo "AGENT_BENCH_WINNER=$winner ROUTE=fcc_catalog PROBE=$BEST_MODEL" | tee -a /tmp/jumpy-agent.log\\n',
    ),
]

for old, new in pairs:
    if old in s:
        s = s.replace(old, new)

p.write_text(s)
PY

bash -n scripts/jumpy-studio-cycle-v4.sh
exec bash scripts/jumpy-studio-cycle-v6.sh
