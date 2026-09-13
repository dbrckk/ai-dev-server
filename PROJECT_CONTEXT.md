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

## Current state — 2026-09-13

The factory now has a mature autonomous engineering core across Flutter, Godot and generic repositories.

Completed or materially implemented:

- multi-engine routing for Flutter, Godot and generic repositories;
- generic repository analysis, planning, implementation, verification, review, checkpointing and bounded continuation across Node, Python, Go, Rust, Maven, Gradle, .NET and additional detected toolchains;
- Godot repository import/probing, runtime journeys, visual QA, Android export/device QA, release artifact QA, store metadata, privacy/security QA, final release review and opt-in trusted Google Play publication;
- Flutter real-device/release pipeline, trusted Android artifact-only production signing, Play metadata/privacy/security gates and opt-in trusted Google Play publication;
- shared Android AAB signer strips prior JAR signatures, keeps keystores outside the project workspace, passes passwords only through trusted process environment and verifies the signed bundle/certificate;
- Android Publisher v3 edit workflow implemented as validate-first by default: create edit, upload AAB, update track, validate, optional explicit commit;
- explicit human-action states for missing keystore/token/commit approval, without regenerating an already validated application;
- provider routing with reliability, latency, circuit breaking and bounded transport timeouts;
- external-agent routing and verified candidate comparison;
- meta-routing that learns verified-success efficiency for model-only, agent-only, model→agent, agent→model and dual strategies;
- recency-aware, uncertainty-adjusted, bounded explore/exploit strategy learning with regime-shift detection;
- hierarchical and weighted multi-label task-context strategy learning;
- predictive difficulty budgeting, explicit phase quotas, active timeouts, verification reserves, shared fallback budgets, run-wide cost controls and statistical cost-drift detection;
- persisted provider health/metrics, routing history, verification costs, phase-cost baselines, strategy efficiency, contextual strategy efficiency, agent performance, project memory and execution checkpoints;
- capability self-evolution, isolated validation, promotion, rollback and persistence machinery;
- exact registry-promotion PR identity verification ported directly onto current main; stale PR #118 was closed without merge after its guarantees were superseded and validated on modern main;
- stronger Flutter software-supply-chain evidence: hosted registry provenance, package content hashes, dependency-type evidence, cached license classification, strong-copyleft/unknown-license fail-closed behavior and enriched SBOM;
- richer privacy/Data Safety classification for analytics, advertising, auth, crash reporting, location, payments, push notifications and remote backends;
- a fixed multi-engine E2E benchmark workflow covering Flutter real sandbox build, pinned Godot runtime + real Jumpy probe, and a trusted generic Python fixture;
- an integrated fault-injection CI gate covering provider outage, circuit breaker, checkpoint tampering, run-cost exhaustion, adaptation-state tampering and registry-promotion identity changes;
- 141 Python test modules, 170 studio Python modules and 11 GitHub Actions workflows.

Current open trust-boundary / production work:

- PR #118 is stale/unmergeable but its guarantees have been ported to current main; close it after the current HEAD CI is green.
- current HEAD CI for unit validation, real Flutter build, multi-engine benchmark and fault-injection gate should still be observed before treating the latest artifact-handoff increment as fully proven.
- Google Play publication code is implemented, but live end-to-end publication still requires real authorized credentials, Play account agreements and explicit trusted commit approval.
- signed AAB handoff now survives runner restarts through project-scoped GitHub Actions artifacts, with deterministic prior-artifact selection and exact SHA-256 verification before trusted reuse.
- full repeated end-to-end proof is still needed on real managed repositories, especially Jumpy, plus at least one Flutter and one generic repository.
- iOS production build/signing/publication remains outside the current production path.
- broader asset provenance/license QA and long-duration soak/fault scenarios can still be expanded.

## Progress estimate

Estimated completion toward the repository's stated final objective:

**94%**

This is weighted by end-to-end production capability rather than file or commit count.

Approximate subsystem maturity:

- autonomous orchestration / persistence / recovery: 97%
- generic engine: 96%
- Flutter engineering/release pipeline: 96%
- Godot engineering/release pipeline: 95%
- adaptive routing / agents / provider learning: 98%
- budgeting / drift / cost control: 98%
- self-evolution / capability promotion: 92%
- security / SBOM / dependency provenance: 92%
- privacy / Data Safety preclassification: 91%
- Android production signing: 90%
- Google Play API publication path: 86%
- repeated live end-to-end proof on real repositories: 76%
- iOS production delivery: 35%

## Immediate next objective

1. Observe green CI on current main for:
   - Validate AI Dev Server
   - Mobile Studio Real Build
   - Multi-Engine E2E Benchmark
   - Fault Injection Gate
2. Run durable end-to-end completion on Jumpy and one real Flutter + one generic repository.
3. Exercise the Play validate-only path against a real authorized Play application; only then test an explicitly approved internal-track commit.
4. Harden remaining asset provenance/visual-consistency controls and long-duration restart/provider-failure soak tests.
5. Refresh README/operator docs after live Play validation is proven.

## Remaining roadmap

- Real Jumpy completion cycle with release evidence retained.
- Real Flutter repository completion through signed AAB and Play edit validation.
- Real generic repository completion through learned routing + verification.
- Live Android Publisher API validation with authorized short-lived credentials.
- Explicitly approved internal-track publication test.
- Stronger asset provenance/license policy and visual-consistency QA.
- Longer soak tests across runner restarts, provider outages, quota exhaustion and partially completed promotions.
- Optional future iOS build/signing/App Store production path.
- Documentation cleanup so README/docs reflect the current adaptive multi-engine architecture.

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
