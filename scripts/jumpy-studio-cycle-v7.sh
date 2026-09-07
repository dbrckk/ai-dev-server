#!/usr/bin/env bash
set -euo pipefail

# v7 aligns the v4 runtime hardening layer with the catalog-aware v3 runner.
# FCC launchers now own client-compatible model selection instead of receiving raw provider ids.
python - <<'PY'
from pathlib import Path
p=Path('scripts/jumpy-studio-cycle-v4.sh')
s=p.read_text()
repls={
'''    'echo "FCC_BENCH_PASS=$name MODEL=$BEST_MODEL" | tee -a /tmp/jumpy-agent.log':
        'echo "FCC_BENCH_PASS=$name MODEL=$BEST_MODEL" | tee -a /tmp/jumpy-agent.log >&2',
    'echo "FCC_BENCH_FAIL=$name MODEL=$BEST_MODEL RC=$rc" | tee -a /tmp/jumpy-agent.log':
        'echo "FCC_BENCH_FAIL=$name MODEL=$BEST_MODEL RC=$rc" | tee -a /tmp/jumpy-agent.log >&2',''':
'''    'echo "FCC_BENCH_PASS=$name ROUTE=fcc_catalog PROBE=$BEST_MODEL" | tee -a /tmp/jumpy-agent.log':
        'echo "FCC_BENCH_PASS=$name ROUTE=fcc_catalog PROBE=$BEST_MODEL" | tee -a /tmp/jumpy-agent.log >&2',
    'echo "FCC_BENCH_FAIL=$name ROUTE=fcc_catalog PROBE=$BEST_MODEL RC=$rc" | tee -a /tmp/jumpy-agent.log':
        'echo "FCC_BENCH_FAIL=$name ROUTE=fcc_catalog PROBE=$BEST_MODEL RC=$rc" | tee -a /tmp/jumpy-agent.log >&2',''',
'''needle_diag = '''  winner=$(choose_agent)\n  echo "AGENT_BENCH_WINNER=$winner MODEL=$BEST_MODEL" | tee -a /tmp/jumpy-agent.log\n'''
replacement_diag = '''  winner=$(choose_agent)\n  echo "AGENT_BENCH_WINNER=$winner MODEL=$BEST_MODEL" | tee -a /tmp/jumpy-agent.log\n''':
'''needle_diag = '''  local winner; winner=$(choose_agent)\n  echo "AGENT_BENCH_WINNER=$winner ROUTE=fcc_catalog PROBE=$BEST_MODEL" | tee -a /tmp/jumpy-agent.log\n'''
replacement_diag = '''  local winner; winner=$(choose_agent)\n  echo "AGENT_BENCH_WINNER=$winner ROUTE=fcc_catalog PROBE=$BEST_MODEL" | tee -a /tmp/jumpy-agent.log\n'''
}
for old,new in repls.items():
    if old not in s: raise SystemExit('v7 compatibility anchor missing')
    s=s.replace(old,new,1)
p.write_text(s)
PY
bash -n scripts/jumpy-studio-cycle-v4.sh
exec bash scripts/jumpy-studio-cycle-v6.sh
