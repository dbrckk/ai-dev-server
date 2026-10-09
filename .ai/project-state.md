# Project state

Status: active

## Working
- **2026-10-09 latest:** live worker/canary #17 (`37968265692`, `37968265772`) succeeded after bounded-context fix #276; artifact `11634630863` shows checkpoint `b82a9e275ba487f3176c76dddbdc7da8156f16b5`, adding `.production-os/worker-canary-17.txt` to a studio branch. GitHub PR creation returned HTTP 403 and the final result incorrectly concealed changed files; work on `fix/pos-delivery-evidence-review-link` now makes review blockage actionable and reports changed-file evidence. Production deployment is NOT proven.
- A real worker run reached a committed Godot checkpoint but returned `active` with `next_stage=preview`. The worker now continues that same claimed job through bounded runner invocations and only completes the Production-OS task when the Studio result is finished. Exhaustion reports `continuation_limit` explicitly.
- A live Godot checkpoint at 2026-10-04 11:21 UTC showed an implementation response cut at the output token limit. On that precise protocol error, the model retry now asks for a complete, smaller two-file patch so a subsequent round can continue without repeating the oversized response.
- The live persistence failure can be reproduced locally: `provider_health.record_success` writes seven aggregate fields, while `github_provider_health_store` accepted only four. The remote store now validates all seven, supplies defaults for older rows, and retains latency and recent outcome data.
- PR #246 makes the primary and third NVIDIA providers return structured JSON in live diagnostics 37185440546; the second fallback still returned invalid JSON.
- Real worker run 37184922962 claimed a recovered Jumpy task and checkpointed a branch, proving queue registration, claim, and source execution. Its final result was runner_error because remote state persistence failed; autonomy state committed at 07:17:15 UTC, while the project-memory branch did not advance.
- Both original legacy goals relaunched through idempotent dashboard API; real worker run 37184922962 claimed work and checkpointed product/design to Jumpy.
- Live diagnostics 37184194436: all three configured model endpoints responded; existing operator access verified after control-plane startup.
- Production-OS optional skill_learning contracts now pass the Studio validator; reproduced historical artifact 11276785062 now validates.
- Worker forwards its pinned Git baseline and preserves fixed runner error codes/HTTP status without raw messages.
- A separate trusted-main live diagnostic workflow checks bounded inference and existing operator access.
- Worker setup/result failures are reported to Production-OS rather than leaving acknowledged jobs active.
- Correlated result validation prevents completing a different workflow/task/project/repository.
- Bounded invocations signal failed work with exit code 1; paused/draining continuous workers back off.
- Dedicated worker CI covers pytest function tests and real authenticated Production-OS HTTP integration.

## Broken / blockers
- **Current:** GitHub token used by the AI Dev Server worker can push checkpoint branches but failed creating a target pull request (`API HTTP 403`); target repo Pull requests:write access still requires operational configuration or an operator review link. Do not mistake worker `succeeded` for PR/merged release.
- Live worker canary sequence 16 (worker 37967390363, canary 37967390403) again failed `capacity_exhausted` after the per-call cap fix. Artifact 11634067913 shows 22,309 capacity-ledger tokens charged in a 30,000-token envelope, no changed files and checkpoint phase `planned`. Source inspection found that generic project snapshots could still include 420,000 source bytes per call; the targeted context cap is now proposed in `fix/generic-context-envelope` and awaits CI and a real canary.
- Live 2026-10-09 worker canary sequence 15 (Actions worker run 37965833843, canary 37965833971) was claimed and executed against the ready Render server but failed with structured `capacity_exhausted`. Artifact 11634035810 shows a 30,000-token project envelope, 20,664 tokens charged in the capacity ledger, no changed files and no commit. The runner completed the service/queue probes successfully. Per-call completion cap is reduced on branch `fix/bounded-generic-completion-envelopes` to avoid allocating up to 16,000 output tokens in one bounded project call; this remains unverified on a real follow-up canary.
- Live worker run 37298981754 exhausted its Godot continuation budget on Jumpy; validation evidence showed the container could not create `.godot` in its disposable project copy, plus a GDScript parse error and missing generated textures on the project branch. The sandbox copy permission repair is prepared; project code/assets still require a separate repair.
- At 2026-10-04 18:50 UTC, the live queue had one visual asset job requiring `visual-asset-production`; the Actions worker did not advertise that capability because the remote Asset Forge dispatch probe was unavailable. A real completed coding production and visual asset delivery still need live verification.
- Worker rerun 37197591265 is queued behind scheduled run 37197484353; a successful completed job and repository artifact still need live verification.
- The real worker task has not completed successfully. The remote persistence failure needs a precise safe component/reason diagnosis; a bounded rerun with diagnostics is prepared.
- Live run 37182952933: worker session ready, 1 online worker, 4 failed jobs, 2 failed workflows, no queued candidates. Both implementation tasks exhausted 2/2 attempts with StudioError.
- Its remote Asset Forge dispatch probe failed, so visual capabilities remained disabled.
- Render service verified healthy on merged server fix #250. Direct database connector inspection is unavailable.

## Current priority
- Validate and merge finite-envelope repository snapshot limits, then run a canary that verifies real source delivery before any further quota increases.
- Validate the constrained single-call token cap with existing model/capacity tests and complete CI, then run a new real worker canary. Verify output branch and file instead of accepting Actions success alone.
- Verify the currently running worker exits cleanly, then observe the queued persistence-fixed run. Keep the bounded Godot truncation repair in future worker runs.
- Merge the provider-health persistence fix with a new bounded kick, then verify both the remote memory branch and Production-OS job result.
- Publish the persistence diagnosis, run the worker with the structured JSON fix, repair the failing store, and verify a successful real task and saved artifact.
- Real source generation returned invalid structured JSON. Enable NVIDIA JSON response mode and validate structured inference in live diagnostics before the next execution.
- The selected failed workflows are legacy jobs without current managed-project association. Recover them through the normal dashboard launch API using stable request IDs, preserving their original final goals and exhausted attempts.
- Safely resume only the two explicitly selected failed managed objectives through existing operator instruction controls, then verify real worker execution.
- Verify shared provider fallbacks with live diagnostics, then resume exhausted objectives through authorized operator controls.
- Diagnostics #241/#251 and startup recovery #242 are deployed. Resume exhausted objectives through existing operator controls, investigate StudioError during a real run and verify its artifact.
- Investigate live queue eligibility and remote Asset Forge dispatch permissions without exposing secrets.

## Validation
- Active-checkpoint regression: failed before the worker fix and passed after; 1721 unit tests and 6 authenticated Production-OS HTTP integrations passed locally.
- Godot model, preview, and persistent runner checks: 18 selected tests passed; the truncation regression failed before the change and passed after.
- Provider-health persistence and worker recovery selected checks: 41 tests and 19 subtests passed locally.
- New regression suite: 87 tests and 22 subtests passed; both historical requests validate.
- Three authenticated server integrations pass with the actual skill_learning contract and Studio request validation.
- Selected worker suite: 99 tests passed, including recovery regressions.
- Real Production-OS server integration: 2 tests passed, also against qualified revision 7e0d47a in an isolated installed environment.
- Full unit suite: 1700 tests passed; compilation and existing CI trust policy passed.

## Last verified
- 2026-10-04

<!-- AUTO:START -->
## Automatic repository state

Generated: 2026-10-09T18:35:36Z

### Git
- Branch: `main`
- Head: `8ab8232b99c3`
- Commit date: 2026-10-09T20:35:25+02:00
- Commit: fix(production-os): expose blocked GitHub PR delivery and file evidence (#278)
- Tracked files: 863

### Recently changed files
- `docs/PRODUCTION_OS_WORKER.md`
- `studio/generic_project.py`
- `studio/generic_repository.py`
- `studio/github_runner.py`
- `control/production-os-worker-canary.json`
- `studio/generic_model.py`

### Project signals
- No common build descriptor detected

> Generated by dbrckk/repo-standards. Keep manual priorities and blockers outside the AUTO markers.
<!-- AUTO:END -->
