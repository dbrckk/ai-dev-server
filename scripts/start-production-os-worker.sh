#!/usr/bin/env bash
set -euo pipefail

export PATH="$HOME/.local/bin:$PATH"

python "$(dirname "$0")/preflight-production-os-worker.py"

required=(
  PRODUCTION_OS_URL
  PRODUCTION_OS_WORKER_TOKEN
  PRODUCTION_OS_OPERATOR_TOKEN
)

missing=()
for name in "${required[@]}"; do
  if [[ -z "${!name:-}" ]]; then
    missing+=("$name")
  fi
done

if (( ${#missing[@]} > 0 )); then
  printf 'Missing required environment variables: %s\n' "${missing[*]}" >&2
  exit 2
fi

if ! command -v codex >/dev/null 2>&1; then
  echo "Codex CLI is not installed. Re-run: bash scripts/bootstrap.sh" >&2
  exit 3
fi

worker_id="${PRODUCTION_OS_WORKER_ID:-ai-dev-server-1}"
poll_interval="${PRODUCTION_OS_POLL_INTERVAL:-10}"
output_root="${PRODUCTION_OS_OUTPUT_ROOT:-studio-output/production-os}"

exec python studio/production_os_worker.py \
  --worker-id "$worker_id" \
  --output-root "$output_root" \
  --continuous \
  --poll-interval "$poll_interval"
