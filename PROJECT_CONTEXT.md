# AI Dev Server — Project Context

> **READ THIS FILE FIRST when resuming work in a new ChatGPT conversation.** Keep it current whenever architecture, priorities, completion status, or the next objective materially changes.

## Repository purpose

`ai-dev-server` is an autonomous mobile-application factory intended to be invoked from a normal ChatGPT conversation. A high-level brief should be enough for the factory to own product definition, research, UX/UI, implementation, graphics/assets, testing, repair, Android QA, performance/accessibility, privacy/security, release engineering and Play Store preparation.

The target is a reusable expert mobile engineering organization implemented as software, not a one-shot code generator.

## Final objective

`ChatGPT conversation -> high-level brief -> ai-dev-server -> autonomous research/planning/design/code/assets/tests/repair -> app-specific QA -> release -> Play Store publication -> finished professional application`

If a project requires a capability the factory lacks, it must detect the gap, research appropriate resources, synthesize an isolated evolution candidate, benchmark it against the current factory, promote only a non-regressing reversible improvement, and resume the blocked app. Human intervention is limited to genuinely irreducible legal, identity, payment, store-agreement or credential actions.

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
- Android runtime/device QA plus performance, native, notification, Play Billing and platform-view QA.
- `store_package.py` — Play Store listing/assets package.
- `privacy_audit.py` — privacy/Data Safety evidence.
- `security_audit.py` — security/dependency/SBOM evidence.
- `adaptation.py` — fail-closed capability-gap detection and promotion-gate contract.
- `evolution_executor.py` — deterministic `evolution-work-order.json`, isolated candidate identity, baseline and rollback contract.
- `evolution_evidence.py` / `evolution_research.py` — allowlisted, hash-bound trusted research evidence; discovered code is never executed.
- `evolution_candidate.py` — strict synthesized-candidate file scope and dangerous-code rejection.
- `evolution_synthesis.py` — converts completed trusted research into a candidate artifact; model output remains data until validation.
- `evolution_benchmark.py` — deterministic baseline/candidate promotion evaluator.
- Current branch adds `evolution_differential.py` and makes `differential_improvement_proved` a mandatory promotion gate: candidate tests must fail on the pinned baseline and pass on the candidate before promotion can succeed.
- `project_context.py` — trusted generated root `PROJECT_CONTEXT.md` for managed apps.

GitHub Actions is the only active CI (owner decision, 2026-09-10). CircleCI is not a fallback: do not trigger it, maintain it, or treat its statuses as project blockers. Legacy CircleCI files may remain until a separate cleanup removes them. GitHub Android jobs use Ubuntu 24.04, explicitly install the Android emulator, and verify KVM acceleration. Never claim CI success without observing it.

## Current state — 2026-09-09

- PR #17 `177153db2eb31b4a1a09c7b22cd16ad527065bfc`: GitHub Actions restored; notification QA.
- PR #18 `0fc68b14a71ce335e753c238cda17e9e4d5764eb`: unsupported work becomes `adaptation_required`.
- PR #19 `a48b22830a3499c40bd8b4fdf139821a8db7ac46`: durable project-context convention.
- PR #20 `2ff07231b7eac692c564d465e4ea7514d8843e58`: generated apps receive trusted context files at checkpoints.
- PR #21 `ab24ae71f67d6dfba1c43e39444cfb8268b87c28`: deterministic evolution work orders and research-evidence boundary.
- PR #22 `d973269253ba90dfbd3fdc257376071cf8760108`: GitHub Actions runs the full provider-neutral completion pipeline; Android emulator/KVM bootstrap verified.
- PR #23 `94250b982113cf222f0b3a238e6ffd8400f934b2`: fail-closed `billing_qa`.
- PR #27 `3b06636aaa194a547b1730608d8659df90dcbb96`: automatic trusted evolution research execution.
- PR #30 `f671ba2500d8025f8d5ab64e63a8566400a3adec`: `platform_view_qa` for WebView/maps/video release runtime validation.
- PR #31 `568ba372225dbbac34b78b7617f92719013f9053`: synthesized candidate scope and benchmark/promotion safety gates.
- PR #33 `be2164d114d8467d0f541c50fe2ad17f1b00d996`: bounded candidate synthesis is merged; research can now produce a validated candidate artifact without executing it.
- Current branch hardens promotion against vacuous candidate tests by requiring baseline-red/candidate-green differential evidence.
- **Jumpy** remains the first major end-to-end target application.

## Immediate next objective

1. Validate and merge the mandatory differential-improvement gate.
2. Materialize a validated candidate on its isolated `evolution/<candidate>` branch from the pinned baseline.
3. Run the candidate-specific differential test on baseline and candidate with production credentials removed and network isolated.
4. Run the full trusted regression suite + Flutter smoke + capability benchmark on both sides.
5. Feed all machine evidence into `evolution_benchmark.py`.
6. Promote only an approved candidate, register the new trusted stage through a trusted promotion step, retain rollback metadata, then resume the blocked application automatically.

## Near-term roadmap

- Isolated candidate materialization + execution + promotion/rollback + automatic resume.
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
