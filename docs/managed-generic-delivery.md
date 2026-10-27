# Managed generic delivery

A Production-OS generic objective now completes only after local verification,
publication, an open PR on the published SHA, and independent target CI success.
Standalone generic runs and approved bounded-source lanes retain their own gates.

## Repository prerequisites

- The target has exactly one active GitHub Actions workflow named `CI`.
- Its file under `.github/workflows/` is identical on the source commit and the
  default branch. The generated patch cannot edit `.github`.
- The workflow tests the checked-out project and defines the repository's real
  acceptance checks. Production-OS cannot infer missing product acceptance tests.
- The source credential can publish and create a PR, or the target has the
  supported trusted PR handoff. Existing reserved source-task branches remain
  reserved; this does not broaden those narrowly authorized source lanes.
- CI starts on push/PR, or supports `workflow_dispatch` and the credential has
  permission to dispatch it. A `GITHUB_TOKEN` publication alone may not trigger CI.

This repository's `CI` workflow also accepts `workflow_dispatch`, so delivery can
explicitly start the same validation jobs on its published branch if no automatic
run appears. The dispatched workflow uses read-only contents permission and does
not require model or operator secrets. The source SHA and unchanged workflow
definition are still verified before accepting the result.

CI trust policy v13 explicitly permits this input-free dispatch trigger in
addition to mandatory push/PR triggers. Dispatch inputs, extra triggers,
event-dependent job conditions and write permissions remain rejected. The policy
version and digest change, so attestations bound to an older trust policy must be
collected again; old attestations are not silently reused.

No secret values belong in objectives or reports. Missing permissions, missing
CI, changed workflow definitions and execution problems produce explicit blockers;
they never count as successful delivery.

## Automatic progression

This repository installs the trusted `production_os_review_handoff` receiver for
credentials that can publish a branch but cannot create PRs directly. It runs
only default-branch code, never checks out generated source, verifies the exact
managed branch tip and bounded diff, rejects `.github` edits and opens a draft
PR. Repository settings must permit Actions to create PRs. The receiver then
explicitly dispatches CI after checking that its definition matches main, because
a PR created by GITHUB_TOKEN does not generate automatic PR workflow runs. It
grants no approval or merge authority. Source CI success remains a separate
exact-commit requirement.

1. Generate and locally verify the implementation, then publish it.
2. Seal a delivery checkpoint and confirm the PR at the same SHA.
3. Observe the target's CI. If absent, persist dispatch intent before sending one
   dispatch POST. Do not replay an ambiguous response after restart.
4. While CI runs, yield without invoking the model or republishing source.
   The worker polls every30 seconds with heartbeat and cancellation active;
   waiting does not spend implementation continuations. Delivery-only resumes
   read the branch SHA instead of downloading the source tree again.
5. Require successful jobs from the same run attempt and SHA, executed steps,
   unchanged run identity/status on reread, and an open PR still on the source SHA.
6. A failed CI job returns its run URL, job and step names to the next bounded
   implementation cycle. The existing goal/capacity budgets continue to apply.
7. A repaired publication gets its own CI proof. Success records the observed
   workflow, definition blob, run, attempt, source SHA and URL.

CI waiting expires after one hour instead of silently looping forever. A
separate one-hour deadline also bounds PR handoff waiting. Missing or rejected
handoff configuration stops with an explicit reason; accepted or ambiguous
handoff dispatches are not replayed on resume. CI receives its own wait period
when the PR is confirmed, so a delayed handoff does not consume the CI window.
A
temporary CI read failure remains pending; missing configuration or permission
evidence is surfaced for correction. PR handoff waiting also preserves the
implementation-continuation budget. A definite
dispatch rejection can be attempted again after its permissions/configuration are
fixed; an ambiguous POST is only observed. Cancellation, skipped execution or
unavailable evidence require attention rather than speculative model repairs.

This delivers a qualified PR; it does not automatically merge, deploy the target,
grant permissions, raise budgets, or promise success for arbitrary objectives.

## Evidence

`python studio/generic_smoke.py` exercises generation, actual local verification,
PR recovery, single dispatch, repeated CI waiting, CI rejection, bounded model
repair, new publication and independent confirmation. Model/GitHub responses in
that smoke are deterministic fixtures, not live hosted inference.

The inspector was also executed against public GitHub API responses for real
run `40222698694`, attempt1, source `3d5e617d428d809a9760460e6f22e208f095445e`:
the existing successful CI was accepted without triggering another run.
