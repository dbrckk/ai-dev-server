# AI Dev Server — Project Context

> **READ THIS FILE FIRST when resuming work in a new ChatGPT conversation.** Keep it current whenever architecture, priorities, completion status, or the next objective materially changes.

## Repository purpose

`ai-dev-server` is an autonomous mobile-application factory intended to be invoked from a normal ChatGPT conversation. A high-level brief should be enough for the factory to own product definition, research, UX/UI, implementation, graphics/assets, testing, repair, Android QA, performance/accessibility, privacy/security, release engineering and Play Store preparation.

The target is a reusable expert mobile engineering organization implemented as software, not a one-shot code generator.

## Final objective

`ChatGPT conversation -> high-level brief -> ai-dev-server -> autonomous research/planning/design/code/assets/tests/repair -> app-specific QA -> release -> Play Store publication -> finished professional application`

If a project requires a capability the factory lacks, it must detect the gap, research appropriate resources, synthesize an isolated evolution candidate, benchmark it against the current factory, promote only a non-regressing reversible improvement, persist that improvement safely, and resume the blocked app. Human intervention is limited to genuinely irreducible legal, identity, payment, store-agreement or credential actions.

## Non-negotiable quality contract

Compilation or preview is not completion. `finished` requires evidence appropriate to the application: acceptance journeys, polished responsive UI, accessibility, real behavior, tests, independent review, release artifacts, runtime/device QA, capability-specific QA, privacy/Data Safety consistency, security/dependency checks, professional store material and every dynamically required gate.

Fail closed. Self-improvement must never weaken tests, security, privacy, accessibility or definition-of-done merely to obtain a green result.

## Current architecture

Trusted components live primarily under `studio/`:

- `core.py` / `run.py` — bounded Flutter-first generation, product/design/implementation/review/visual loops and trusted patch gates.
- `completion.py` / `stage_registry.py` / `orchestrator.py` — machine-readable definition of done, dynamic trusted stages and provider-neutral completion/adaptation orchestration.
- `github_runner.py` / `ci_runner.py` — GitHub Actions primary runner and CircleCI fallback.
- capability-specific QA includes Android runtime/device, performance, native, notification, Play Billing and platform-view QA.
- `store_package.py`, `privacy_audit.py`, `security_audit.py` — Play Store package, privacy/Data Safety and security/dependency/SBOM evidence.
- `adaptation.py` / `evolution_executor.py` / `evolution_research.py` / `evolution_synthesis.py` — fail-closed gap detection, deterministic work orders, trusted research and bounded synthesis.
- `evolution_candidate.py` — strict generated-file scope plus dangerous-code and protected-policy rejection.
- `evolution_differential.py` / `evolution_isolated_runner.py` / `evolution_benchmark.py` — baseline-red/candidate-green differential evidence, isolated execution, full regression/smoke/integrity/reversibility benchmarking and deterministic promotion decisions.
- `evolution_promotion.py` / `evolution_rollback.py` — trusted dynamic-stage promotion plus hash-bound rollback metadata.
- `evolution_stage_runner.py` — executes promoted code only after stripping production tokens/API keys/secrets.
- `evolution_persist.py` — validates local promotion integrity and persists exactly the approved files to a dedicated GitHub branch + PR; never writes directly to `main`.
- `evolution_pending.py` — detects durable promotion state across runner restarts and prevents duplicate candidate regeneration.
- PR #46 adds `evolution_automerge.py`: immutable local persistence proof, authenticated GitHub Actions checks, exact six-file scope, second head-SHA verification and merge of only the approved commit.
- `project_context.py` — trusted generated root `PROJECT_CONTEXT.md` for managed apps.

GitHub Actions is the primary CI. Android jobs use Ubuntu 24.04, install the Android emulator explicitly and verify KVM acceleration. Never claim CI success without observing it.

## Current state — 2026-09-09

Key completed milestones:

- #17 Actions restore + notification QA.
- #18 unsupported work -> `adaptation_required`.
- #19/#20 durable project-context convention.
- #21 deterministic evolution work orders and research boundary.
- #22 full GitHub provider-neutral completion pipeline + Android emulator/KVM.
- #23 billing QA.
- #27 trusted evolution research.
- #30 platform-view QA.
- #31 candidate scope and benchmark safety gates.
- #33 bounded candidate synthesis.
- #40 differential promotion evidence finalized.
- #43 trusted promotion + dynamic registration + rollback + same-run resume logic merged.
- #44 secure persistence merged: promoted-stage credential scrubbing, integrity-bound GitHub branch/PR persistence, pending-promotion detection and restart-safe duplicate suppression.
- #46 is the current PR: immutable-proof autonomous merge. The orchestrator owns `persist -> wait authenticated CI -> merge exact approved SHA -> stop`; a fresh `main` checkout resumes after the promotion merge. Newly promoted code is not executed from the ephemeral pre-merge checkout.

**Jumpy** remains the first major end-to-end target. Repository `dbrckk/Jumpy` is an existing Godot 4.x/GDScript portrait hybrid-casual game, while the current factory generation core remains Flutter-first. This engine mismatch is now the next architectural blocker.

## Immediate next objective

1. Finish CI and merge #46 only if both trusted validation and real mobile smoke pass on its exact head SHA.
2. Add an explicit engine/project-type abstraction instead of assuming Flutter globally.
3. Add safe detection/support for existing Godot 4.x projects without weakening the Flutter sandbox.
4. Add Godot-specific edit scope, static validation, headless test/build/export smoke and Android release evidence.
5. Create a durable enabled Jumpy request targeting `dbrckk/Jumpy` only after the factory can safely manage an existing Godot repository.
6. Run Jumpy end-to-end and let real missing capabilities drive the next self-evolution cycle.

## Near-term roadmap

- Multi-engine project abstraction: Flutter + Godot first.
- Existing-repository checkout/update path with strict branch/PR boundaries.
- Godot headless/runtime/export QA and Android artifact verification.
- Broader native/hardware QA and stronger semantic capability detection.
- Rich conservative privacy/Data Safety classification for networked apps.
- Professional graphics/asset factory with provenance and visual-consistency QA.
- Stronger license/dependency/provenance/security analysis.
- Autonomous signing and Play Console publication when authorized credentials exist.
- Diverse fixed benchmark suite and full Jumpy completion.

## Mandatory context-file convention for every project

Every repository this factory creates or substantially manages must contain a root **`PROJECT_CONTEXT.md`** describing purpose, current scope, architecture/constraints, evidence-based validation/release status, blockers/risks, immediate next objective, roadmap, long-term objective, decisions/invariants and useful update metadata. Create it early, refresh it after material milestones, and never use it to claim evidence absent from trusted machine state.

## Instructions to any future ChatGPT/agent

1. Read `PROJECT_CONTEXT.md` first.
2. Inspect current `main`, open PRs and CI before trusting this snapshot.
3. Preserve the final objective and quality contract.
4. Perform the next meaningful implementation rather than only proposing it.
5. Use branches/PRs and verify CI before substantial merges.
6. Update this file whenever state, architecture or the next objective materially changes.
7. In user-facing updates, state what will be worked on next and the estimated percentage toward the final objective; do not systematically repeat separate short-term/final-objective headings.
