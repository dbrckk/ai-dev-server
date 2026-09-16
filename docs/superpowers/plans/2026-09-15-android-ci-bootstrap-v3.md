# Android CI Bootstrap V3 Implementation Plan

> **For agentic workers:** use superpowers:executing-plans and superpowers:test-driven-development.

**Goal:** Make required Android CI gates resilient to transient corrupted SDK package downloads without weakening validation.

**Architecture:** Add one tested shell bootstrap helper for host SDK packages, call it from both required Android workflows, and permit one disposable Flutter-fixture retry only for exact Android archive-corruption signatures.

**Spec:** `docs/superpowers/specs/2026-09-15-android-ci-bootstrap-v3-design.md`

### Task 1 — RED tests

- [x] Add a unit test with a fake `sdkmanager` that fails once, then succeeds; expect bootstrap success and two install attempts.
- [x] Add a unit test with a fake `sdkmanager` that always fails; expect bootstrap failure after exactly three attempts.
- [x] Add a static workflow test proving both `studio-smoke.yml` and `multi-engine-benchmark.yml` call `scripts/bootstrap-android-ci.sh`.
- [x] Add a signature test distinguishing exact Android archive corruption from ordinary Flutter/test failures.
- [x] Run the full Python suite and capture the four expected RED failures before production edits.

### Task 2 — Bootstrap helper

- [x] Add `scripts/bootstrap-android-ci.sh` with strict shell mode.
- [x] Validate Android SDK paths and export runtime paths through `GITHUB_PATH` when set.
- [x] Accept licenses without treating the normal `yes` broken-pipe exit as failure.
- [x] Retry `sdkmanager` acquisition of platform-tools, emulator and the current Flutter-template NDK at most three times.
- [x] Between failures remove only known temporary/cache download directories.
- [x] Exit non-zero after the final failure.

### Task 3 — Fixture recovery and workflow wiring

- [x] Recognize only `Archive is not a ZIP archive` and `ZipFile unknown archive` as transient Android SDK corruption.
- [x] Retry a disposable sequential Flutter fixture at most once after one of those exact signatures.
- [x] Keep ordinary Flutter/test/build failures immediately blocking.
- [x] Replace duplicated bootstrap blocks in both Android workflows with the shared script.
- [x] Keep acceleration validation and all build/test steps unchanged.

### Task 4 — GREEN

- [ ] Run the targeted tests.
- [ ] Run the full Python suite.
- [ ] Require all six GitHub Actions gates on final head before merge.
