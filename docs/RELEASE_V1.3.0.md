# AI Dev Server v1.3.0

v1.3.0 is the stable consolidation release for the current autonomous multi-engine architecture.

## Stability contract

The release is accepted only when the exact release revision passes **6/6** hard gates:

- CI
- Validate AI Dev Server
- Fault Injection Gate
- Resilience Soak
- Mobile Studio Real Build
- Multi-Engine E2E Benchmark

After merge and final verification on `main`, the validated revision is preserved by the immutable release anchor `release/validated-v1.3.0`.

## Finalized guarantees

- Finite shared model capacity is **work-conserving**: unused ordinary capacity is redistributed while critical reserve, pause, stagnation, recovery and total-capacity limits remain enforced.
- Human prerequisites are explicit. A real external prerequisite produces `USER_INPUT_REQUIRED.txt` and `user-input-required.json` without persisting the secret value.
- Named environment prerequisites can resume a sealed terminal goal only when the required variable is actually present.
- `studio.project_status` reads persisted project/goal/handoff state without invoking models, project code or verifiers.
- Android CI retries only bounded SDK/NDK package-download corruption. Application, Flutter, test and validation failures remain hard failures.
- Adaptive planning/review decisions expose stable telemetry while trusted verification remains authoritative.

## Operator commands

```bash
python studio/v1_gate.py
python -m studio.project_status --project-out studio-output/<project-id>
python studio/fleet_dashboard.py --root studio-output
python studio/fleet_daemon.py --root studio-output --once
```

## Security note

Do not put secret values in `USER_INPUT_REQUIRED.txt`, `user-input-required.json`, briefs, repository files or command arguments. Supply only the named prerequisite through the approved environment/secret mechanism.

## Release rule

No release claim is made from partial or stale evidence. All six gates must refer to the final exact candidate revision before merge, and the merged `main` revision is rechecked before `release/validated-v1.3.0` is created.
