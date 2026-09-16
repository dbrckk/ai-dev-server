# Human Handoff and Project Status V3 Design

## Scope

Close the remaining gap between the autonomous-project contract and the current Goal Engine without introducing a second orchestration system.

The existing `goal_engine` remains authoritative. This change only strengthens the exceptional human-handoff path and exposes read-only status from the already persisted state.

## Required behavior

1. A human handoff is materialized as `USER_INPUT_REQUIRED.txt` plus `user-input-required.json` under the project output directory.
2. Secret values are never persisted. For secret prerequisites, only exact environment-variable names and safe instructions are written.
3. Secret names are extracted conservatively from recognized names and environment-style names whose suffix indicates a secret (`KEY`, `TOKEN`, `SECRET`, `PASSWORD`, `CREDENTIAL`, `CREDENTIALS`).
4. A goal waiting on named secrets remains terminal and consumes no model work while any required environment variable is absent.
5. When every named secret is present, the wrapper resumes the sealed Goal Engine state before invoking project work and removes stale handoff files.
6. Non-secret human actions remain paused because they cannot be proven satisfied automatically.
7. A new read-only `project_status.py` reports the sealed Goal Engine status, attempt budget, missing evidence/capabilities, human-action state, runtime summary and completion evidence.
8. The status command never invokes models, verifiers, project code or mutation paths.

## Safety

- Never serialize environment values.
- Never infer that a generic human action is complete.
- Invalid/tampered goal state remains fail-closed through `goal_engine.load()`.
- Stale human-handoff files are cleared only after machine-verifiable resume or non-human terminal completion.
- Status reads persisted files only.

## Verification

TDD must cover secret-value non-persistence, arbitrary secret-name extraction, automatic resume when exact names exist, no worker invocation while names are missing, handoff-file creation, and read-only status for working/human-action/complete goals.
