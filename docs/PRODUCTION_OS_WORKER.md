# Production-OS worker

## Diagnosing delayed worker wake without revealing credentials

On sleeping Render services, the optional diagnostic first waits for `/readyz` through bounded **GET-only** probes (up to 120 seconds) before checking operator access and missing wake settings. Network/gateway errors are retried only for this read-only readiness check. A timeout leaves operator access and worker wake marked unavailable instead of guessing configuration; it never launches a job or edits repositories. This addresses the transient `operator_access=unavailable` seen in live diagnostic run `37989346828` even while model providers were ready.


A successful coding canary with `worker_wake=scheduled_fallback` indicates that the control plane accepted the job but cannot promise an immediate GitHub Actions wake; scheduled polling remains available. The live-diagnostics workflow now performs an optional, authorized **GET-only** `/v1/dashboard/launch-readiness` request after operator authentication and outputs the wake mode plus an allowlisted list of missing **setting names**. It never prints tokens or untrusted error text. The recognized variables are `GITHUB_TOKEN`, `PRODUCTION_OS_ACTIONS_REPOSITORY` and `PRODUCTION_OS_ACTIONS_WORKFLOW`. On Render, the intended non-secret settings are `dbrckk/ai-dev-server` and `production-os-actions-worker.yml`, respectively. GitHub permissions still require a credential provisioned through the service's secret management, not this repository. No scheduling or queue mutation is performed by this diagnostic.


## Canary startup on Render free instances

The `production-os-worker-canary.yml` acceptance workflow now warms the configured Production-OS control plane using a bounded series of **read-only `/readyz` probes** before its one-time authenticated launch. This handles Render cold starts exceeding the operator POST's 30-second request timeout. On a non-transient HTTP failure it fails immediately; if Render never reaches database readiness it stops without creating a project. **The launch POST is never retried after an ambiguous timeout**, avoiding duplicate autonomous work. Real canary #18 (run `37975993803`, 2026-10-09) exposed this: its POST timed out after 30 seconds, while its companion worker later connected and found an empty queue.

## JSON-compliant model routing

Live model diagnostics on 2026-10-09 (Actions runs `37983037858` and `37983251927`) reached two JSON-compliant NVIDIA endpoints, while the other configured fallback returned `invalid_response` repeatedly. Generic Production-OS calls now request NVIDIA NIM `response_format: {"type":"json_object"}` consistently with the existing live diagnostic and still validate the returned object. In automatic default NVIDIA configuration, the compliant Poolside fallback has priority 90 and the unreliable Lightning fallback has priority 70. A custom `STUDIO_PROVIDERS_JSON` configuration is never overwritten.

This only changes routing preference and structured-output requests: the health circuit breaker, token reservations, free/paid budgets, remaining fallback, and fail-closed verification are unchanged. A valid diagnostic JSON response is not proof that a complex coding task will succeed; verify a real implementation before declaring full production readiness.

## Delivery proof and restricted GitHub credentials

A successful canary demonstrates a verified **commit on a checkpoint branch**, not necessarily a pull request or a merged release. Live canary 17 (2026-10-09) produced an actual commit in `dbrckk/repo-standards` but PR creation failed with GitHub HTTP 403. The coding result was successful; **review delivery remains blocked** until a PR can be opened.

For ordinary target repositories, grant the worker GitHub credential **Contents: write** and **Pull requests: write** on the *target repository* (fine-grained PAT or equivalent). Set the credential only in GitHub Actions secrets, never source files. If PR creation remains unavailable, the result retains a structured `pull_request.state=unavailable`, a fixed `reason` (without raw API text), and, when the default branch is known, `head`, `base` and an actionable GitHub `compare_url`. An operator can open this comparison and create a PR manually. The result also distinguishes `delivery_status=review_blocked` from a successful implementation checkpoint and exposes the changed file list from verified rounds when available. The release status is `verified_branch_review_blocked` until a PR can be created. A completed implementation is **not** proof of deployment.


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

## Resume after a bounded GitHub Actions session

Production-OS queues a **new job key** for every retry of a workflow task.
The worker must not derive its durable autonomous state solely from this
ephemeral job key. For workflow dispatches with a positive integer
`workflow_attempt`, the project ID is now derived from the repository,
workflow ID and task ID. That identity is stable across attempts of the same
logical task and isolated between distinct tasks, workflows and repositories.
Legacy non-workflow jobs continue to use a job-scoped project ID.

The short-lived GitHub Actions worker sets `STUDIO_PERSIST_REMOTE=1`. The
native runner restores the goal, capability registry, improvement backlog and
generic execution checkpoint from the protected `studio-autonomy-state` GitHub
branch before doing more work. It now also **persists the sealed goal and
generic execution checkpoint after each completed autonomous goal cycle**,
immediately after the goal is written locally. A final flush at the end of
the native invocation persists terminal status, memory, and related metadata.
Each intermediate checkpoint can truthfully remain `active` even when it
already contains final evidence, because terminal finalization happens next.

**Generic projects have a finer-grained boundary:** after every repository
round is published to its work branch, the sealed
`generic-execution-checkpoint.json` is mirrored immediately to the
GitHub-backed autonomy-state branch, even when the entire goal cycle still
has more rounds to execute. The published SHA, round number, verification
result and phase are recorded; a mere planned or uncommitted stage must
never be treated as a published checkpoint. GitHub persistence errors
halt further rounds **and bypass the ordinary retryable model/goal loop**:
the failed remote write cannot be interpreted as an ordinary provider
error and silently spend another attempt. Only the exception type is
reported; API error bodies (which may contain credentials) are not
included. This does not increase model budgets and does not
turn unsuccessful verification into successful completion. The goal state
is still flushed at the completed goal-cycle boundary.

The target-repository work branch and the remote autonomy checkpoint are
**different** stores and must not be confused.

One interrupted/retried task is expected to follow this sequence:

1. The first worker claims and acknowledges attempt 1, completes some
   verifiable work and saves the sealed goal/partial evidence remotely.
2. The runner reports `continuation_limit` or `runtime_limit` as a
   **failure**, not fabricated completion.
3. If the workflow has remaining `max_attempts`, Production-OS enqueues the
   next attempt with a new job key. The server checks whether a worker wake
   is needed after the workflow transition.
4. A fresh Actions runner uses the same project ID, restores the saved goal
   and continues from the missing evidence. It must still run and verify the
   remaining work before reporting success.

The worker allows up to **16** autonomous continuations by default, with a
70-minute total runtime limit and a finalization reserve. Adjust these with
`--max-continuations` (0–32) and `--max-runtime-seconds` (60–4800). Those
limits bound consumption; they do not guarantee that enough inference
capacity exists to complete a job.

**Limits and failure modes:** Workers cannot recover steps that never reached
the remote store. An abrupt runner termination **within** a goal cycle may lose
work since its last persisted boundary; a crash after a finished cycle should
preserve its evidence through the new intermediate remote checkpoint.
Previously committed GitHub artifacts remain independently durable.
Intermediate checkpoint persistence failures are treated as errors instead
of silently executing additional cycles with uncommitted state.
Generic project model calls now right-size their requested `max_tokens` to
the available pooled provider quota and, where configured, the remaining
project token envelope. Admission reserves the estimated prompt plus a
tokenization safety margin and the actual bounded maximum output. Routine
work still preserves the critical-call quota reserve and code-generation
responses retain a minimum useful output budget. If no eligible provider
has enough tokens to answer safely, the call fails instead of pretending
that the task is complete; this optimization cannot restore a genuinely
exhausted API account.

When Production-OS supplies a finite project envelope, each generic model
call now requests at most one quarter of that envelope (with a 4096-token
minimum cap, still bounded by the original role limit and remaining quota).
For a 30,000-token project, a single completion is capped at 7,500 tokens
instead of 16,000. This preserves capacity for subsequent coding and
verification calls, especially if a provider omits usage metadata and the
ledger conservatively charges the full reserved amount. It does not
override the total project envelope or the provider's actual quota.
A successful workflow must still produce verified repository evidence.

Generic repository snapshots are also bounded for projects with a token
envelope: each snapshot includes at most half the project's token envelope
measured in **source bytes**, floored at 16 KiB and capped at 128 KiB. For a
30,000-token project, that means up to 16,000 bytes of source instead of the
usual 420,000-byte default. `AGENTS.md`, README and primary package manifests
are considered first. This source-byte heuristic reduces context waste but
does not claim to measure tokenizer-specific tokens exactly. Unbounded local
projects keep their existing snapshot limit.

After an HTTP 429 rate-limit response has exhausted its bounded transport retries,
both generic and Flutter model routers immediately open the affected provider's
temporary health circuit. They can use a separately configured eligible model
without replaying the same failing provider in the next coding call. The
mobile model engine also binds each request to the currently selected
provider's own endpoint and credentials after health filtering or reranking,
rather than incorrectly reusing its startup primary client. This
cooldown expires automatically and is **not** treated as proof of permanent
monthly quota exhaustion; HTTP 503 and ordinary model failures keep their
existing multi-failure circuit threshold.

An exhausted token quota is not bypassed. A failed GitHub Actions dispatch
leaves durable work queued for the scheduled fallback (currently every five
minutes), and operator pause/drain continues to apply. The immediate wake
path needs a Render-side GitHub token authorized to dispatch Actions on
`dbrckk/ai-dev-server`; a successful canary with
`worker_wake=scheduled_fallback` does **not** prove immediate dispatch.

The deterministic regression test
`tests/test_production_os_local_e2e.py::ProductionOSLocalE2ETests::test_two_separate_worker_sessions_restore_verified_partial_progress`
runs two authenticated worker sessions against a local HTTP fixture, with
**different queue keys and empty disks**. It persists the first session's
sealed goal through the real GitHub goal-store API using a fake GitHub
Git-object protocol, restores it on the second session and verifies that
completed build evidence is not lost or re-executed. This validates the
cross-session contract in CI but is **not** itself a live, quota-consuming
two-run Actions test.
