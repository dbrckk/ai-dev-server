# Android CI Bootstrap V3 Implementation Plan

> **For agentic workers:** use superpowers:executing-plans and superpowers:test-driven-development.

**Goal:** Make required Android CI gates resilient to transient corrupted SDK package downloads without weakening validation.

**Architecture:** Add one tested shell bootstrap helper and call it from both required Android workflows.

**Spec:** `docs/superpowers/specs/2026-09-15-android-ci-bootstrap-v3-design.md`

### Task 1 — RED tests

- [ ] Add a unit test with a fake `sdkmanager` that fails once, then succeeds; expect bootstrap success and two install attempts.
- [ ] Add a unit test with a fake `sdkmanager` that always fails; expect bootstrap failure after exactly three attempts.
- [ ] Add a static workflow test proving both `studio-smoke.yml` and `multi-engine-benchmark.yml` call `scripts/bootstrap-android-ci.sh`.
- [ ] Run the targeted tests and capture RED before production edits.

### Task 2 — Bootstrap helper

- [ ] Add `scripts/bootstrap-android-ci.sh` with strict shell mode.
- [ ] Validate Android SDK paths and export runtime paths through `GITHUB_PATH` when set.
- [ ] Accept licenses without treating the normal `yes` broken-pipe exit as failure.
- [ ] Retry `sdkmanager platform-tools emulator` at most three times.
- [ ] Between failures remove only known temporary/cache download directories.
- [ ] Exit non-zero after the final failure.

### Task 3 — Workflow wiring

- [ ] Replace duplicated bootstrap blocks in both Android workflows with the shared script.
- [ ] Keep acceleration validation and all build/test steps unchanged.

### Task 4 — GREEN

- [ ] Run the targeted tests.
- [ ] Run the full Python suite.
- [ ] Require all six GitHub Actions gates on final head before merge.
