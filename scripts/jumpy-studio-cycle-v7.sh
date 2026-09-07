#!/usr/bin/env bash
set -euo pipefail

# v7 aligns the current catalog-aware v3 runner with the older v4/v6 hardening layers.
# Compatibility transformations are deliberately simple and idempotent.
python - <<'PY'
from pathlib import Path

# Make the v3 runner tolerate protections already present in the base runtime.
r = Path('scripts/jumpy-studio-cycle-v3-runner.sh')
s = r.read_text()
s = s.replace(
    "if s.count(final_needle) != 1: raise SystemExit('v3 final-scope anchor mismatch')\ns=s.replace(final_needle, final_replacement, 1)",
    "if s.count(final_needle) == 1:\n    s=s.replace(final_needle, final_replacement, 1)\nelif final_replacement not in s:\n    raise SystemExit('v3 final-scope anchor mismatch')",
)
s = s.replace(
    "if s.count(count_needle)!=1: raise SystemExit('v3 source-count anchor mismatch')\ns=s.replace(count_needle,count_replacement,1)",
    "if s.count(count_needle)==1:\n    s=s.replace(count_needle,count_replacement,1)\nelif count_replacement not in s:\n    raise SystemExit('v3 source-count anchor mismatch')",
)
r.write_text(s)

# Align v4 benchmark/diagnostic anchors with the catalog-aware v3 runner.
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

bash -n scripts/jumpy-studio-cycle-v3-runner.sh
bash -n scripts/jumpy-studio-cycle-v4.sh
exec bash scripts/jumpy-studio-cycle-v6.sh
