# Production-OS worker

The AI Dev Server can run as a long-lived Production-OS worker and dispatch coding work to Codex CLI or the existing agent router.

## Required environment

```bash
export PRODUCTION_OS_URL="https://your-production-os.example"
export PRODUCTION_OS_WORKER_TOKEN="..."
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

The bootstrap installs Asset Forge from the E2E-verified immutable revision `7cd615b9b42956b9b3d0d44992ac3e45e1764b6b` by default. Set `ASSET_FORGE_REF` only when intentionally testing another revision.

Visual production readiness is delegated to the installed Asset Forge CLI. Raster generation can use Pollinations when authenticated, or the installed imagen Codex fallback when `CODEX_ACCESS_TOKEN` or `CHATGPT_ACCESS_TOKEN` is present. Backend selection is automatic; SVG and 3D remain fail-closed when their required backend is unavailable.

```bash
asset-forge operational-status
```

The worker advertises `visual-asset-production` only when Asset Forge and an authenticated generation backend are actually ready. Generated 3D additionally advertises `visual-asset-3d-production` only when the server-side API-key path is available. Visual Production-OS handoffs are translated into the `asset-forge/production-request/v1` contract and executed end to end with `asset-forge fulfill <request.json>`.

### Live visual E2E ownership

The canonical real-generation acceptance test is owned by `dbrckk/asset-forge` in `.github/workflows/production-os-ai-dev-server-live-e2e.yml`. Asset Forge owns the provider credentials, checks out the current AI Dev Server and Deadline Zero revisions, materializes the Production-OS handoff through this repository, generates and validates a real asset, injects it into Deadline Zero, and compiles/tests the target. Provider credentials therefore remain inside Asset Forge.

For the runtime remote bridge (`production-os asset-forge-batch --mode github`), `STUDIO_GITHUB_TOKEN` or the `CODESPACES_PAT` fallback must be able to access `dbrckk/asset-forge` and dispatch GitHub Actions workflows there. For a fine-grained PAT, grant the target repository **Actions: Read and write** and the minimum repository metadata/content access required by GitHub. Do not add Cloudflare, Kaggle, or Pollinations credentials to AI Dev Server.

Remote visual readiness is fail-closed and can be checked without creating a workflow run:

```bash
env -u PYTHONPATH production-os asset-forge-batch --probe
```

The probe returns success only when cross-repository workflow dispatch is authorized. If it fails, the worker remains available for non-visual work but does not advertise `visual-asset-production`, so visual jobs remain queued instead of consuming an execution attempt.

Start the persistent worker with:

```bash
bash scripts/start-production-os-worker.sh
```

The worker registers itself, polls for jobs, acknowledges claimed jobs, emits periodic heartbeats while work is active, refreshes capacity between polls, and reports either completion or failure back to Production-OS.

## Authentication

The worker token is sufficient for registration through `/v1/workers/session`.
The configured worker ID must match that token's principal name on Production-OS
(for the Actions worker, `github-actions-worker`). `PRODUCTION_OS_OPERATOR_TOKEN`
is optional and enables legacy operator registration; do not grant operator access
just to run a worker.


If OmniRoute has authenticated free capacity, Codex is routed through the isolated OmniRoute provider configuration.

Otherwise the worker falls back to the normal Codex invocation, which requires the Codex CLI environment to already be authenticated. No paid provider is enabled automatically.

## Output

Per-job state is written below:

```text
studio-output/production-os/<project-id>/
```

including the correlated request and `production-os-result.json` envelope.

The worker accepts Production-OS's optional `skill_learning` contract. It preserves
that metadata without making skill publication a condition for completing work.
Runner failures retain a fixed error code and optional HTTP status in their local
result and server evidence; raw exception messages are never published.

The CLI forwards `GITHUB_SHA` to the autonomous runner as its pinned baseline.
Outside Actions, use `--baseline-sha <full-commit-sha>` when the project needs
capability research or promotion.

## Live provider diagnostics

Run the `Production-OS Live Diagnostics` workflow manually, or increment
`control/production-os-diagnostics-kick.json` on main. It checks up to three
configured providers with small, bounded inference requests, using the same
fallback defaults as the worker. It also checks an existing
`PRODUCTION_OS_OPERATOR_TOKEN` secret with a read-only operator endpoint.
It does not claim jobs, retry objectives, modify repositories, print credentials,
or print generated responses. This check is separate from the scheduled worker
and runs only when explicitly triggered.

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

## Failure recovery and automated verification

Local request/output preparation failures and unreadable or mismatched result
files are reported through `/v1/jobs/fail`, followed by an inactive heartbeat.
The worker checks the schema, workflow, task, project and repository correlation
before reporting completion. Transport errors while reporting completion remain
errors; the worker does not send a contradictory failure when completion may
already have reached the server.

A bounded invocation (`--once` or `--cycles`) returns exit code 1 if any job fails,
while preserving the status JSON artifact. Continuous workers wait between idle,
paused and draining polls. Invalid heartbeat/retry timing is rejected before a
job is claimed.

`.github/workflows/production-os-worker-integration.yml` runs all selected worker
tests, including pytest function tests, plus authenticated HTTP integration with
the pinned qualified Production-OS revision. The integration runner executes a
deterministic Python artifact and verifies both completion and result-file failure.
This proves the bridge and server contract; it does not replace the live Codex
acceptance test above.

## Diagnosing an idle Actions worker

The queue preflight prints separate base/mobile `queue_diagnostics` from the
server. `queue_empty` means no queued candidate is assigned to this worker or
unassigned within the bounded scan. `missing_capabilities` includes the required
capabilities this worker cannot provide. `no_actionable_jobs` reports filtered
cancelled or stale generations. `worker_paused` and `worker_draining` reflect an
operator control state and do not scan or claim the queue. Older servers report
`server_diagnostics_unavailable`; an idle run alone does not establish an empty
queue. These diagnostics never claim a job or expose repository briefs.

The preflight also prints aggregate `/v1/stats` job/workflow counts using the
worker token. This separates a worker-specific empty candidate window from
unfinished work assigned elsewhere or workflows which have not queued tasks.
Inventory inspection is read-only and diagnostic failures do not override the
mandatory authenticated availability check.

## Actions restart recovery

Each new Actions process opens its worker-only session before testing queue
availability. The single-flight workflow reports no active jobs at startup,
allowing the server to recover the same worker's interrupted claimed/acknowledged
jobs. Registration happens even when the candidate queue appears empty; otherwise
the preflight would skip the process needed to recover those jobs. Operator pause
and draining states still prevent claiming work.

The preflight also reads at most five failed workflows and prints only task IDs,
attempt counters, pipeline status/stage and exception type. It omits request
briefs, repository metadata, raw exceptions and tokens. Terminal failed tasks
are not automatically retried by this diagnostic; retry/continue remains an
operator action with the existing attempt limits.
