# AI Dev Server — Project Context

> **READ THIS FILE FIRST when resuming work in a new ChatGPT conversation.** Keep it current whenever architecture, priorities, completion status, or the next objective materially changes.

## Repository purpose

`ai-dev-server` is an autonomous mobile-application factory intended to be invoked from a normal ChatGPT conversation. The user supplies a high-level brief; the factory should own product definition, research, UX/UI, implementation, original/provenance-tracked graphics, testing, repair, device QA, performance/accessibility, privacy/security, release engineering and Play Store preparation.

It is not merely a code generator. The target is a reusable expert mobile engineering organization implemented as software.

## Final objective

`ChatGPT conversation -> high-level brief -> ai-dev-server -> autonomous research/planning/design/code/assets/tests/repair -> app-specific QA -> release -> Play Store publication -> finished professional application`

If a project needs a capability the factory lacks, it must detect the gap, research/acquire appropriate resources, implement the missing capability on an isolated candidate branch, benchmark it against trusted regression/quality gates, promote only a non-regressing reversible improvement, and then resume the blocked project. Human intervention is reserved for genuinely irreducible legal, identity, payment, store-agreement or credential actions.

## Non-negotiable quality contract

A preview or successful compilation is not completion. `finished` requires evidence appropriate to the application: acceptance journeys, polished responsive UI, accessibility, real behavior, tests, independent review, release artifacts, runtime/device QA, capability-specific QA, privacy/Data Safety consistency, security/dependency checks, professional store assets/listing and every dynamically required gate.

Fail closed. Self-improvement must never weaken tests, security, privacy, accessibility or the definition of done merely to obtain a green result.

## Current architecture

Trusted components are primarily under `studio/`:

- `core.py` — bounded Flutter generation sandbox and trusted gates.
- `run.py` — product/design/implementation/review/visual loop and checkpoints.
- `completion.py` — machine-readable definition of done and dynamic stages.
- `stage_registry.py` — trusted post-preview stage registry.
- `ci_runner.py` — CircleCI adapter.
- `capability_qa.py` — capability classification and specialized-QA requirements.
- Android runtime/device QA plus specialized performance, native and notification QA.
- `store_package.py` — Play Store listing/assets package.
- `privacy_audit.py` — privacy/Data Safety evidence.
- `security_audit.py` — security/dependency/SBOM evidence.
- `adaptation.py` — fail-closed capability-gap detection and `evolution-request.json` generation.
- `evolution_executor.py` — validates adaptation requests and creates deterministic isolated `evolution-work-order.json` candidates tied to a baseline SHA and rollback policy.
- `evolution_evidence.py` — trusted boundary for research metadata from official/allowlisted sources; arbitrary discovered code is not accepted as evidence.
- `project_context.py` — trusted root `PROJECT_CONTEXT.md` generation from factory state for managed applications.
- Current branch adds `orchestrator.py` and `github_runner.py` so GitHub Actions and CircleCI share the same full completion semantics.

GitHub Actions is the primary CI; CircleCI remains fallback. Never claim CI success without observing it.

## Current state — 2026-09-08

- PR #17 merged as `177153db2eb31b4a1a09c7b22cd16ad527065bfc`: GitHub Actions restored; notification QA added.
- PR #18 merged as `0fc68b14a71ce335e753c238cda17e9e4d5764eb`: unsupported work becomes `adaptation_required` with an evolution request.
- PR #19 merged as `a48b22830a3499c40bd8b4fdf139821a8db7ac46`: durable root `PROJECT_CONTEXT.md` standard established.
- PR #20 merged as `2ff07231b7eac692c564d465e4ea7514d8843e58`: generated applications now receive trusted `PROJECT_CONTEXT.md` files at studio checkpoints, outside model-editable scope.
- PR #21 merged as `ab24ae71f67d6dfba1c43e39444cfb8268b87c28`: evolution requests become deterministic candidate work orders and research evidence has an allowlisted trusted schema.
- Current branch is converting GitHub Actions from preview-only generation to the full preview -> release -> device/capability QA -> specialized QA -> store/privacy/security -> adaptation pipeline, while making CircleCI reuse the same stage orchestrator.
- Important incomplete areas include actual research-task execution/candidate synthesis/benchmark promotion, `billing_qa`, `platform_view_qa`, broader native QA, richer networked-app privacy classification, professional graphics automation, stronger dependency/license provenance and authorized Play Console publication.
- **Jumpy** remains the first important target app for exercising the complete factory.

## Immediate next objective

Validate and merge the provider-neutral full pipeline. Then implement the next evolution layer:

1. execute `evolution-work-order.json` research tasks through trusted adapters / orchestrating ChatGPT;
2. store allowlisted research evidence;
3. synthesize the missing factory capability on the isolated evolution branch;
4. require new trusted tests and a capability benchmark;
5. compare the candidate with the pinned baseline;
6. reject regressions or weakened gates;
7. promote a passing candidate and automatically resume the blocked application.

## Near-term roadmap

- Full GitHub Actions completion pipeline and adaptation handoff.
- Research execution + candidate synthesis + benchmark/promotion engine.
- Complete `billing_qa`, `platform_view_qa` and broad `native_qa`.
- Stronger semantic capability detection.
- Rich conservative privacy/Data Safety classification for networked apps.
- Professional graphics/asset factory with provenance and visual-consistency QA.
- Stronger license/dependency/provenance/security analysis.
- Autonomous signing and Play Console publication when authorized credentials exist.
- Diverse fixed benchmark suite and end-to-end Jumpy completion.

## Mandatory context-file convention for every project

Every repository this factory creates or substantially manages must contain a root **`PROJECT_CONTEXT.md`** describing purpose, current scope, architecture/constraints, evidence-based validation/release status, blockers/risks, immediate next objective, roadmap, long-term objective, decisions/invariants and useful update metadata. Create it early, refresh it after material milestones, and never use it to claim evidence that the machine state does not contain.

## Instructions to any future ChatGPT/agent

1. Read `PROJECT_CONTEXT.md` first.
2. Inspect current `main`, open PRs and CI before assuming this snapshot is current.
3. Preserve the final objective and quality contract above.
4. Perform the next meaningful implementation rather than only proposing it.
5. Use branches/PRs and verify CI before merging substantial changes.
6. Update this file whenever state, architecture or the next objective materially changes.
7. In user-facing progress updates, state what will be worked on next and the estimated percentage toward the final objective; do not systematically repeat separate short-term/final-objective headings.
