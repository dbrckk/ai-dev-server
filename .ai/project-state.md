# Project state

Status: active

## Working
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
- At 2026-10-04 18:50 UTC, the live queue had one visual asset job requiring `visual-asset-production`; the Actions worker did not advertise that capability because the remote Asset Forge dispatch probe was unavailable. A real completed coding production and visual asset delivery still need live verification.
- Worker rerun 37197591265 is queued behind scheduled run 37197484353; a successful completed job and repository artifact still need live verification.
- The real worker task has not completed successfully. The remote persistence failure needs a precise safe component/reason diagnosis; a bounded rerun with diagnostics is prepared.
- Live run 37182952933: worker session ready, 1 online worker, 4 failed jobs, 2 failed workflows, no queued candidates. Both implementation tasks exhausted 2/2 attempts with StudioError.
- Its remote Asset Forge dispatch probe failed, so visual capabilities remained disabled.
- Render service verified healthy on merged server fix #250. Direct database connector inspection is unavailable.

## Current priority
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

Generated: 2026-10-04T14:08:19Z

### Git
- Branch: `main`
- Head: `672ee28dfa91`
- Commit date: 2026-10-04T13:35:06+02:00
- Commit: fix(godot): shrink truncated patch retries (#249)
- Tracked files: 849

### Recently changed files
- `studio/godot_model.py`
- `tests/test_godot_model.py`
- `control/production-os-worker-kick.json`
- `studio/github_provider_health_store.py`
- `studio/production_os_worker.py`
- `tests/test_github_provider_health_store.py`
- `tests/test_production_os_worker_recovery.py`
- `.github/workflows/production-os-actions-worker.yml`
- `.github/workflows/production-os-worker-integration.yml`
- `control/production-os-diagnostics-kick.json`
- `studio/production_os_live_diagnostics.py`
- `tests/test_production_os_live_diagnostics.py`

### Project signals
- No common build descriptor detected

> Generated by dbrckk/repo-standards. Keep manual priorities and blockers outside the AUTO markers.
<!-- AUTO:END -->
