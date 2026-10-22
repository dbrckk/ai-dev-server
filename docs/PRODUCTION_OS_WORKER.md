# Production-OS worker

## Diagnosing delayed worker wake without revealing credentials

On sleeping Render services, the optional diagnostic first waits for `/readyz` through bounded **GET-only** probes (up to 120 seconds) before checking operator access and missing wake settings. Network/gateway errors are retried only for this read-only readiness check. A timeout leaves operator access and worker wake marked unavailable instead of guessing configuration; it never launches a job or edits repositories. This addresses the transient `operator_access=unavailable` seen in live diagnostic run `37989346828` even while model providers were ready.


A successful coding canary with `worker_wake=scheduled_fallback` indicates that the control plane accepted the job but cannot promise an immediate GitHub Actions wake; scheduled polling remains available. The live-diagnostics workflow now performs an optional, authorized **GET-only** `/v1/dashboard/launch-readiness` request after operator authentication and outputs the wake mode plus an allowlisted list of missing **setting names**. It never prints tokens or untrusted error text. The recognized variables are `GITHUB_TOKEN`, `PRODUCTION_OS_ACTIONS_REPOSITORY` and `PRODUCTION_OS_ACTIONS_WORKFLOW`. On Render, the intended non-secret settings are `dbrckk/ai-dev-server` and `production-os-actions-worker.yml`, respectively. GitHub permissions still require a credential provisioned through the service's secret management, not this repository. No scheduling or queue mutation is performed by this diagnostic.


## Canary startup on Render free instances

The `production-os-worker-canary.yml` acceptance workflow now warms the configured Production-OS control plane using a bounded series of **read-only `/readyz` probes** before its one-time authenticated launch. This handles Render cold starts exceeding the operator POST's 30-second request timeout. On a non-transient HTTP failure it fails immediately; if Render never reaches database readiness it stops without creating a project. **The launch POST is never retried after an ambiguous timeout**, avoiding duplicate autonomous work. Real canary #18 (run `37975993803`, 2026-10-09) exposed this: its POST timed out after 30 seconds, while its companion worker later connected and found an empty queue.

## JSON-compliant model routing

Live model diagnostics on 2026-10-09 (Actions runs `37983037858` and `37983251927`) reached two JSON-compliant NVIDIA endpoints, while the other configured fallback returned `invalid_response` repeatedly. Generic Production-OS calls now request NVIDIA NIM `response_format: {"type":"json_object"}` consistently with the existing live diagnostic and still validate the returned object. Fresh hosted diagnosis39703457758 on2026-10-22 verified structured output and AST-checked code from Lightning, while Super returned404 and Poolside was unavailable. Automatic NVIDIA defaults now give the qualified Lightning fallback priority95, ahead of Poolside90, while retaining the explicit primary100. Tiny qualification probes disable supported Nemotron reasoning as described below; this is point-in-time code availability, not a permanent model guarantee. A custom `STUDIO_PROVIDERS_JSON` configuration is never overwritten.

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

The CLI exits successfully only when inference and operator access are both
ready. When `PRODUCTION_OS_DIAGNOSE_WAKE=1`, the wake probe must also report
`immediate` or the supported `scheduled_fallback` mode. Missing credentials,
rejected operator access, or an unavailable/unknown requested wake probe make
`diagnostic_ready` false and return exit code 1 even if a model responds.
These bounded probes do not prove sustained model capacity or delivery of a PR.

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

## Accounting for partial provider token usage

Some OpenAI-compatible APIs report `usage.total_tokens` without input/output subfields, or omit useful usage counters. For capacity and pooled quotas, Production-OS now uses the larger of the reported aggregate and the input/output sum; when there are no positive counters, it conservatively retains the admitted token estimate. Unknown token remainders are conservatively allocated to whichever input/output token type has the higher configured price; quota records and local cost estimates are updated even when the provider omits usage altogether. This is a safety guard against silently counting real work as zero, not a claim that missing usage can be measured exactly. Original prompts, credentials and provider response bodies are not logged.

## GitHub telemetry rejection after a verified code checkpoint

Live Production-OS canary #20 (`37992773915`) generated and structurally verified `.production-os/worker-canary-20.txt` and committed it to `studio/mp-aa8be7dea7e417424da80e41` at `405277e`. It then returned `runner_error` with GitHub HTTP 422 during remote state persistence; the companion canary did **not** constitute a fully successful task completion. GitHub branch history shows project-memory and provider-health checkpoints were committed before the failure, while subsequent provider metrics were not.

The runner treats **only an HTTP 422 while writing optional telemetry/caches** as `verified_checkpoint_telemetry_degraded`, noting the first skipped component and avoiding further auxiliary writes in that session. It still *requires* durable autonomous goal state, project memory, and execution checkpoint; these critical failures remain fatal. Validation/schema errors and other HTTP errors remain fatal. An optional telemetry failure cannot silently imply the metrics were persisted or that a PR was created. Use the structured `persistence_status` and `persistence_component` in the retained runner summary, and verify the target branch commit independently.

## Godot preview cycle exhaustion

A restored Godot report retains the authoritative source branch head as
`checkpoint_commit`, including when the preview is already validated or its
cycle budget is exhausted. The stored checkpoint state predates publication
and may omit that field.

An unvalidated preview at `max_cycles` returns an explicit blocked report with
`preview_cycle_budget_exhausted=true`. The native orchestrator stops the goal
with `next_stage=godot_preview_cycle_budget_exhausted`, preserving the committed
SHA and the previous validation blockers in the retained report. The blocked
goal also persists repository-bound checkpoint evidence, so a later worker
that skips the already-blocked goal retains the same SHA without stage calls.
It does not
construct a model or sandbox, repeat active continuations, raise the configured
budget, or claim completion. A validated preview still advances to Android QA
even when its cycle count has reached the limit.

The 2026-10-14 replay used the actual request from worker38569417618 and the
repaired Jumpy checkpoint5b1c32b1f04a7f1190ee8f66bb3abb56a933eeb5. The native
result writer emitted `blocked`, the budget stage, that SHA and `succeeded=false`
after one goal cycle (engine detection and preview only). A fresh worker
directory restored from that sealed goal also retained the SHA and failed
truthfully without rerunning any stage, without provider calls
or repository writes. This replay checks recovery/reporting, not Android or
store readiness.

## Native Godot and Flutter inference accounting

Native model calls use an execution-local counter journal at
`.autonomy/native-model-usage.json`. Reported OpenAI-compatible token counters
replace the admission estimate. Missing or invalid counters and failed HTTP
submissions retain the estimate and increment `estimated_calls`; this is an
approximation, not tokenizer-specific billing evidence. Prompts, replies and
credentials are never stored in this journal.

Managed executions require a valid project capacity plan and share the existing
capacity ledger with generic inference. Admission includes estimated prompt
tokens and a bounded output allowance. Each accounted submission performs at
most one HTTP POST; provider fallback is a separate admission. Exhaustion yields
a capacity stop without burning additional continuation attempts. Journal
counters persist through continuations but start fresh for each claimed server
execution, while the project ledger remains cumulative. Failure reporting keeps
this execution's native counters when available. Historical native calls that
predate this change cannot be reconstructed from missing telemetry.

## Generic inference and execution counters

Generic-project model requests use the same execution-local counter journal as
Godot/Flutter calls. The generic router retains ownership of its existing
reservation and settlement: journaling does not reserve capacity a second time.
Reported counters replace estimates; a transport failure conservatively consumes
the admitted estimate, because a timed-out or failed POST may have reached the
provider. Accounting storage failures stop fallback; pre-submission failures
release the reservation, while failures after submission retain the estimate.
Real API submissions perform one POST per admission and preserve the configured
timeout. The worker also copies validated commit SHAs from result evidence into
the standard `commits.shas` summary consumed by execution analytics.

Live canary27 (2026-10-15, Actions38698376303) created exactly the requested
single file, committed e1d7a4063b5b2581be1c6f334456684aaeec13d9 in
`dbrckk/repo-standards` and opened PR10 automatically. Its successful delivery
exposed zero token/API/commit execution counters before these corrections. This
is proof of a small hosted coding delivery, not an Android or complex-project
release. Historical missing usage cannot be reconstructed.


## Optional Cloudflare Workers Free coding fallback (October 2026)

The scheduled Production-OS Actions worker and the read-only live diagnostics can
use `@cf/zai-org/glm-4.7-flash` through Cloudflare's OpenAI-compatible
`/ai/v1/chat/completions` endpoint as an **optional fallback**. This does not
replace the current NVIDIA primary, does not make claims about sustained
inference capacity, and does not restart any failed star-list v3 integration.

**Safe enablement on `dbrckk/ai-dev-server`:**

- Repository Actions secret `CLOUDFLARE_API_TOKEN`: an appropriately scoped
  Workers AI token; never paste the token into a variable, issue, or log.
- Repository Actions variable `CLOUDFLARE_ACCOUNT_ID`: the 32-character
  hexadecimal account ID.
- Repository Actions variable `STUDIO_CLOUDFLARE_FREE_TIER_ONLY=1` **only after
  confirming that the account is on Workers Free**, rather than Workers Paid
  where consumption beyond the free allowance can incur charges.
- Keep `STUDIO_PROVIDERS_JSON` empty to use the built-in default fallback
  chain. If it contains a custom provider list, it is authoritative and is
  **not** modified automatically.

No fallback is injected if any opt-in requirement is absent or malformed;
only the specific Free-eligible GLM model is configured (not a paid-only
frontier model). The API token is referenced by its environment-variable name
and never serialized into `STUDIO_PROVIDERS_JSON`.

Cloudflare [documents](https://developers.cloudflare.com/workers-ai/platform/pricing/)
10,000 free Neurons/day, resetting at 00:00 UTC; Neurons are **not** code-task
tokens. Free allowance exhaustion and model availability failures are possible.
See the [official model eligibility notice](https://developers.cloudflare.com/changelog/post/2026-07-28-models-require-workers-paid/)
and [OpenAI-compatible API configuration](https://developers.cloudflare.com/workers-ai/configuration/open-ai-compatibility/).
The fallback is not marked `unmetered` or assigned a fictional monthly quota.

After the variables are configured, execute
**Actions > Production-OS Live Diagnostics > Run workflow**. The probe sends
a bounded, non-mutating inference request and checks operator connectivity;
the output is intentionally redacted. A successful probe proves only a small
request worked at that time. It does **not** establish an available 90,000-token
portfolio envelope, a stable authenticated quota, valid coding patches, or a
finished target integration. Keep the star-list final-v3 fleet pause until
capacity, worker execution, source delivery, target tests and CI are separately
verified. Do not bypass stop markers or enable an automatic production merge.


## Bounded configured-provider coding qualification

Real generic-project fallback also refreshes its output reservation from the current project ledger before each provider. A failed POST retains its conservative charge; the next provider can use the useful remaining capacity with a smaller response cap instead of attempting the original stale reservation. Actual loopback inference within a6000-token project:503 leaves1758 tokens; the second provider succeeds with a1612-token output cap, leaving total charged capacity4292/6000. The minimum useful completion size and all project/provider admission checks still apply.

The live diagnostic uses a shared ceiling of384 code-output tokens and40 seconds across responsive configured providers, with exactly one POST per candidate and no opaque retry. Failed attempts remain in `coding_smoke.attempts`; success means that at least one configured provider produced AST-verified synthetic code, never that every provider is healthy. The Cloudflare Free opt-in retains preference when present. Only the fixed synthetic exercise is submitted, and generated code is interpreted by the existing restricted AST checker, never executed.

Tiny NVIDIA Nemotron3/3.5 probes explicitly set `chat_template_kwargs.enable_thinking=false`: their128-token readiness cap should measure the answer, not consume it in reasoning. This is supported by [NVIDIA's Lightning model card](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-NVFP4). Production model reasoning, providers, quota accounting and project budgets are unaffected. Readiness records add only allowlisted public model-profile and finish-reason labels; raw model IDs, remote bodies and generated source are not logged.

A loopback HTTP reproduction of the old diagnostic observed one code503 and an incorrectly unusable thinking-heavy fallback. The corrected diagnostic recovered on its second provider within the same384-token total allowance. Actual NVIDIA availability still requires the trusted-main hosted diagnostic; a model catalog entry alone is not inference availability. Kilo's separate one-request public synthetic probe passed with75 completion tokens and reported zero cost on2026-10-22; it does not activate a project-data fallback.

## Redacted coding smoke for free-provider qualification

The live diagnostics workflow sets `PRODUCTION_OS_DIAGNOSE_CODE_SMOKE=1` and
issues **at most one additional 384-output-token coding request** after its
existing provider JSON readiness checks. It prefers a verified
`cloudflare_workers_free` provider when enabled and responsive, otherwise
a ready configured provider. Model-generated Python is parsed and evaluated
through a tiny restrictive AST interpreter with deterministic examples; the
source is **never executed** in the trusted Actions process. The report shows
only public provider families (`cloudflare_workers_free`, `nvidia_nim`,
`other`) and bounded statuses, never account IDs, endpoints, token values,
model responses or generated source. `cloudflare_free_configured=false` means
that Cloudflare has **not** been registered for this workflow, regardless of
other successful inference checks.

A passing `coding_smoke.status=ready` verifies a very small code-generation
behavior at that moment, **not** autonomous repository modification, a
persistent token budget, compatibility with large contexts, or a verified
PR/integration. A failed code smoke makes `diagnostic_ready=false` only when
explicitly enabled. No production job is claimed and the fleet pause remains
in force until actual implementation, tests, CI and quota checks succeed.

## Optional DSH local model gateway

See [DSH gateway setup and qualification](DSH_FREE_MODEL.md) for the optional
`dsh-our-free-model` integration, credential requirements and explicit external
quota accounting. It is not enabled automatically on hosted workers.

## Source-canary applicability and launch preflight

Before enqueueing either historical Jumpy source scenario, the canary reads
`scripts/main.gd` from public `main` through a bounded GitHub GET, with redirects
refused. It records the observed source blob SHA. The settings scenario requires
the known unguarded READY/start_run block; the landing scenario requires the
original judgement code and no existing landing-cue machinery. Unrecognized or
already modified source returns `result.status=blocked`, reason
`scenario_no_longer_applicable`, and `succeeded=false`, without queue submission,
worker dispatch, or model calls. Unreadable/malformed source also prevents launch.

This is a conservative applicability check, not proof that the target product
works. Source can change after the GET; ordinary worker validation and exact-SHA
review remain required. Select a new, independently verified source objective
when a historical scenario is no longer applicable. On 2026-10-20 both old Jumpy
scenarios were blocked against blob `1f4c52618356fe1bbd684a1a3f4d0b717073501e`.
Marker-only scenarios need no source GET.

Polling durations are also validated before submission: wait 0–7200 seconds,
poll 1–60 seconds, finite numeric values. Invalid durations must never leave a
real queued task behind a failed CLI invocation.

## Resuming an approved published source repair

The two approved source lanes retain the published commit while their draft PR
or independent CI is pending. A new worker invocation can recheck that delivery
without another model request or source commit. It requires an integrity-sealed
checkpoint bound to the same project, operator instruction, workflow task,
repository, review branch, commit SHA and source hash. A moved branch, modified
source or different request blocks resumption. Older checkpoints without the
request binding require reviewed recovery; they never trigger a replacement edit.

Only the source-review blocker can reopen for this check. Each pending check
consumes one existing goal attempt, stops again when review is pending or failed,
and preserves the original attempt ceiling. Other terminal goals stay immutable.
The report records `delivery_resumed=true`; completion still requires a verified
draft PR and passing independent CI for the exact commit.

Source API failures identify one bounded operation: `restore`, `publish`,
`review`, or `target_ci`. HTTP 401/403 blocks the goal on its first attempt and
records the operation/status under `source_delivery_error` in the goal evidence.
Worker exception diagnostics expose `error_stage` and `error_http_status` without
remote response bodies, request URLs or credentials.

### Publication proof when source delivery is blocked

If approved source delivery is blocked after publication, its result retains the
published commit and approved changed file even when no source report was returned.
The reporter accepts only the sealed published checkpoint bound to the same project,
repository, review branch, operator instruction and workflow task. Unbound, changed,
corrupt or unreadable checkpoints contribute no publication proof.

This is the retained publication checkpoint, not a claim that the remote branch is
still unchanged or that its review/CI passed. The goal remains blocked, the native
result stays unsuccessful, and stale checkpoint validation/CI success is not copied.
Reporting does not reopen a goal, rewrite the checkpoint, regenerate source or publish
another commit. Legacy recovery still requires reviewed evidence.

### Canary read deadlines

Readiness and workflow-status probes cap each GET timeout at the remaining wait
budget (up to the existing 30-second default). They do not begin a transport call
when less than the API client's one-second minimum remains. Warmup uses the same
finite timeout/poll validation as workflow monitoring.

Transient gateway and connection failures during workflow monitoring may retry
GETs within that budget. Authorization errors and malformed responses still stop
the monitor. The launch POST remains a single submission, and monitoring timeout
reports the last observed workflow state without claiming completion or creating
another task. This changes no inference or project token budget.
