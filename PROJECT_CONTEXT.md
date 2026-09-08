# AI Dev Server — Project Context

> **READ THIS FILE FIRST when resuming work in a new ChatGPT conversation.** Keep it current whenever architecture, priorities, completion status, or the next objective materially changes.

## Repository purpose

`ai-dev-server` is an autonomous mobile-application factory intended to be invoked from a normal ChatGPT conversation. A high-level brief should be enough for the factory to own product definition, research, UX/UI, implementation, graphics/assets, testing, repair, Android QA, performance/accessibility, privacy/security, release engineering and Play Store preparation.

The target is not a code generator but a reusable expert mobile engineering organization implemented as software.

## Final objective

`ChatGPT conversation -> high-level brief -> ai-dev-server -> autonomous research/planning/design/code/assets/tests/repair -> app-specific QA -> release -> Play Store publication -> finished professional application`

If a project requires a capability the factory lacks, it must detect the gap, research appropriate resources, create an isolated evolution candidate, benchmark it against the current factory, promote only a non-regressing reversible improvement, and resume the blocked app. Human intervention is limited to genuinely irreducible legal, identity, payment, store-agreement or credential actions.

## Non-negotiable quality contract

Compilation or preview is not completion. `finished` requires evidence appropriate to the application: acceptance journeys, polished responsive UI, accessibility, real behavior, tests, independent review, release artifacts, runtime/device QA, capability-specific QA, privacy/Data Safety consistency, security/dependency checks, professional store material and every dynamically required gate.

Fail closed. Self-improvement must never weaken tests, security, privacy, accessibility or definition-of-done merely to obtain a green result.

## Current architecture

Trusted components live primarily under `studio/`:

- `core.py` — bounded Flutter generation sandbox and trusted gates.
- `run.py` — product/design/implementation/review/visual loop and checkpoints.
- `completion.py` — machine-readable definition of done and dynamic stages.
- `stage_registry.py` — trusted post-preview stage registry.
- `orchestrator.py` — provider-neutral preview -> release -> QA -> completion/adaptation orchestration.
- `github_runner.py` / `ci_runner.py` — GitHub Actions and CircleCI adapters.
- `capability_qa.py` — capability classification and specialized-QA requirements.
- Android runtime/device QA plus performance, native, notification and Play Billing QA.
- `store_package.py` — Play Store listing/assets package.
- `privacy_audit.py` — privacy/Data Safety evidence.
- `security_audit.py` — security/dependency/SBOM evidence.
- `adaptation.py` — fail-closed capability-gap detection and `evolution-request.json`.
- `evolution_executor.py` — deterministic `evolution-work-order.json`, isolated candidate identity, baseline and rollback contract.
- `evolution_evidence.py` — allowlisted research-evidence boundary; current work adds hash-bound evidence v2.
- `evolution_research.py` — current branch adds bounded official-doc/package/GitHub/runtime research adapters that never execute discovered code.
- `project_context.py` — trusted generated root `PROJECT_CONTEXT.md` for managed apps.

GitHub Actions is the primary CI; CircleCI remains fallback. GitHub Android jobs use Ubuntu 24.04, explicitly install the Android emulator, and verify KVM acceleration. Never claim CI success without observing it.

## Current state — 2026-09-08

- PR #17 `177153db2eb31b4a1a09c7b22cd16ad527065bfc`: GitHub Actions restored; notification QA.
- PR #18 `0fc68b14a71ce335e753c238cda17e9e4d5764eb`: unsupported work becomes `adaptation_required`.
- PR #19 `a48b22830a3499c40bd8b4fdf139821a8db7ac46`: durable project-context convention.
- PR #20 `2ff07231b7eac692c564d465e4ea7514d8843e58`: generated apps receive trusted context files at checkpoints.
- PR #21 `ab24ae71f67d6dfba1c43e39444cfb8268b87c28`: deterministic evolution work orders and research-evidence boundary.
- PR #22 `d973269253ba90dfbd3fdc257376071cf8760108`: GitHub Actions runs the full provider-neutral completion pipeline; Android emulator/KVM bootstrap verified.
- PR #23 `94250b982113cf222f0b3a238e6ffd8400f934b2`: fail-closed `billing_qa`; Play purchase success requires matching Google Play tester/sandbox evidence bound to exact package and release APK hash.
- Current branch `codex/evolution-research-rebased` adds automatic trusted research after an evolution work order: official documentation, bounded `pub.dev` metadata, bounded GitHub repository metadata and local Android runtime fingerprints. Responses are allowlisted, size/time bounded, provenance-recorded and hash-bound. Discovered code is never executed.
- PR #25 separately implements `platform_view_qa` for WebView/maps/video and must be rebased after current work before merge.
- **Jumpy** remains the first major end-to-end target application.

## Immediate next objective

1. Validate and merge trusted research execution on top of the billing-enabled main branch.
2. Rebase and merge `platform_view_qa`.
3. Implement candidate synthesis + benchmark/promotion:
   - consume `evolution-work-order.json` and `evolution-research.json`;
   - create the isolated candidate from the pinned baseline;
   - synthesize only the missing factory capability;
   - run candidate work without production secrets;
   - require new trusted unit tests and a capability-specific benchmark;
   - compare with baseline across regression/security/smoke gates;
   - reject gate weakening or test removal;
   - promote only a passing reversible candidate;
   - resume the blocked application automatically.

## Near-term roadmap

- Candidate synthesis, benchmark, promotion/rollback and automatic resume.
- Complete platform-view and broader native/hardware QA.
- Stronger semantic capability detection, including built artifacts.
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
