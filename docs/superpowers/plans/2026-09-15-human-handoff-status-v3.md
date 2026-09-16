# Human Handoff and Project Status V3 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: use superpowers:executing-plans and superpowers:test-driven-development.

**Goal:** Make the exceptional external-prerequisite path safe, persistent and resumable, then expose current autonomous-project state through a read-only CLI.

**Architecture:** Keep `goal_engine` authoritative. Harden `human_input_request.py`, wire it into `autonomous_project.py`, and add a small `project_status.py` reader over `.autonomy/goal.json`, `.autonomy/runtime-state.json`, and handoff files.

**Spec:** `docs/superpowers/specs/2026-09-15-human-handoff-status-v3-design.md`

### Task 1 — TDD contract

- [ ] Add tests proving arbitrary secret env names are extracted by name only.
- [ ] Add a canary secret value and prove neither text nor JSON handoff file contains it.
- [ ] Add wrapper tests proving missing secrets do not invoke the worker.
- [ ] Add wrapper tests proving present named secrets resume a persisted `human_action_required` goal.
- [ ] Add tests proving handoff files are written on a newly detected human action.
- [ ] Add status tests for active, human-action and complete goal states.
- [ ] Run full Python suite and record RED causes before production edits.

### Task 2 — Safe handoff primitives

- [ ] Add deterministic `requested_secret_names(detail)` extraction.
- [ ] Make `prerequisite_satisfied()` require every extracted name and never inspect/persist values.
- [ ] Make `write_request()` store only safe categorized detail and `required_secret_names`.
- [ ] Preserve useful instructions for recognized providers without copying raw secret-bearing detail.

### Task 3 — Persistent wrapper integration

- [ ] On startup, load the sealed goal after `ensure_project_goal()`.
- [ ] If it is `human_action_required` and exact named secrets are now present, call `resume_human_action()` and save before any worker/model call.
- [ ] If prerequisites remain absent/non-machine-verifiable, return the existing terminal state without invoking project work.
- [ ] After `run_goal()`, materialize handoff files for `human_action_required`; clear stale files after verified resume/completion.
- [ ] Never increment attempt budget merely for checking a missing external prerequisite.

### Task 4 — Read-only project status

- [ ] Add `studio/project_status.py` with `read_status(project_out)` and CLI `--project-out`, `--compact`.
- [ ] Validate `goal.json` through `goal_engine.load()`.
- [ ] Include goal status, attempts, missing evidence, missing capabilities, human action, blockers, runtime status, handoff metadata and project-completion evidence.
- [ ] Do not import model/router/verifier execution paths.

### Task 5 — GREEN and integration

- [ ] Run full Python suite.
- [ ] Run all six required GitHub Actions gates on the final head.
- [ ] Merge only when every required gate reports `success`.
