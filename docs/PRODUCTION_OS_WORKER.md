# Production-OS worker

The AI Dev Server can run as a long-lived Production-OS worker and dispatch coding work to Codex CLI or the existing agent router.

## Required environment

```bash
export PRODUCTION_OS_URL="https://your-production-os.example"
export PRODUCTION_OS_WORKER_TOKEN="..."
export PRODUCTION_OS_OPERATOR_TOKEN="..."
```

Optional OmniRoute capacity routing:

```bash
export OMNIROUTE_URL="https://your-omniroute.example"
export OMNIROUTE_API_KEY="..."
```

Optional worker tuning:

```bash
export PRODUCTION_OS_WORKER_ID="ai-dev-server-1"
export PRODUCTION_OS_POLL_INTERVAL="10"
export PRODUCTION_OS_OUTPUT_ROOT="studio-output/production-os"
```

Do not commit token values. Put them in Codespaces secrets or another secret manager.

## Codespaces

Codex CLI is installed by `scripts/bootstrap.sh`.

Before starting the worker, run the non-mutating readiness check:

```bash
python scripts/preflight-production-os-worker.py
```

It validates required configuration, secure service URLs, OmniRoute pairing, polling interval, output-directory writability, and a real `codex --version` probe. Secret values are never printed. The launcher runs the same preflight automatically.

The bootstrap installs Asset Forge from the E2E-verified immutable revision `c96b87faa5c1a52d2b785cd7c6c3de2da4d16efa` by default. Set `ASSET_FORGE_REF` only when intentionally testing another revision.

Visual production readiness is delegated to the installed Asset Forge CLI:

```bash
asset-forge operational-status
```

The worker advertises `visual-asset-production` only when Asset Forge and an authenticated generation backend are actually ready. Generated 3D additionally advertises `visual-asset-3d-production` only when the server-side API-key path is available. Visual Production-OS handoffs are translated into the `asset-forge/production-request/v1` contract and executed end to end with `asset-forge fulfill <request.json>`.

Start the persistent worker with:

```bash
bash scripts/start-production-os-worker.sh
```

The worker registers itself, polls for jobs, acknowledges claimed jobs, emits periodic heartbeats while work is active, refreshes capacity between polls, and reports either completion or failure back to Production-OS.

## Authentication

If OmniRoute has authenticated free capacity, Codex is routed through the isolated OmniRoute provider configuration.

Otherwise the worker falls back to the normal Codex invocation, which requires the Codex CLI environment to already be authenticated. No paid provider is enabled automatically.

## Output

Per-job state is written below:

```text
studio-output/production-os/<project-id>/
```

including the correlated request and `production-os-result.json` envelope.

## Operational acceptance test

A production deployment is considered usable only after one real job completes this path:

```text
Production-OS
  -> worker register
  -> claim
  -> ack
  -> active heartbeat(s)
  -> Codex execution
  -> production-os-result.json
  -> complete/fail
  -> inactive heartbeat
```

Verify that the target repository actually contains the expected commit or PR and that Production-OS records the same workflow/task correlation and token usage.
