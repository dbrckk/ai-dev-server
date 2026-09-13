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

The factory is now substantially beyond the 2026-09-09 snapshot.

Completed or materially implemented:

- multi-engine routing exists for Flutter, Godot and a generic repository engine;
- Godot has repository probing, runtime journeys, visual QA, Android export/device QA, privacy/security QA, release artifact QA, store metadata QA and final review stages;
- the generic engine performs repository analysis, planning, implementation, real verification, review, checkpoints and iterative continuation across Node, Python, Go, Rust, Maven, Gradle, .NET and additional detected toolchains;
- provider routing now learns reliability and latency per role, persists health/metrics and uses bounded circuit-breaking;
- external-agent routing learns verified performance by role and can compare direct-model vs agent candidates;
- meta-routing learns verified-success efficiency for model-only, agent-only, model→agent, agent→model and dual strategies;
- strategy learning is recency-aware, uncertainty/risk-adjusted, uses bounded deterministic exploration and detects regime shifts;
- strategy selection now learns by task context and stack, with hierarchical fallback and weighted multi-label contexts;
- execution has predictive difficulty budgeting, explicit phase quotas, active phase timeouts, shared fallback quotas, verification reserves, run-wide cost controls and statistical cost-drift detection;
- verification cost and phase-cost baselines are persisted by toolchain;
- routing history, strategy efficiency, contextual strategy efficiency, provider health/metrics, agent performance, project memory and execution checkpoints survive GitHub runner restarts;
- capability self-evolution, isolated validation, promotion, rollback and persistence machinery are extensive and fail closed;
- privacy, security, SBOM/dependency evidence, store packaging and Godot release/store gates are present;
- the repository currently contains more than 130 Python test modules and nine GitHub Actions workflows.

Current open trust-boundary work:

- PR #118, `Verify exact registry promotion PR before activation`, remains open. Its head `55d23d60fad567c3f5b2357e6ef600e668a557c6` has successful validation/mobile-build evidence, but the PR has not been merged.
- autonomous production signing / keystore lifecycle and direct Play Console publication are not yet implemented as a complete trusted path.
- the full final objective still needs repeated end-to-end proof on real managed repositories, especially Jumpy, rather than relying only on component/unit/smoke coverage.
- graphics/provenance, licensing/dependency policy and privacy/Data Safety classification can still be hardened for broader production use.
- the current weighted contextual strategy routing is implemented but its latest main-head CI should be observed before considering that increment fully proven.

## Progress estimate

Estimated completion toward the repository's stated final objective:

**86%**

This percentage is weighted by end-to-end capability rather than file/commit count. The autonomous engineering core is roughly in the mid-90% range; the remaining percentage is dominated by production publication/signing, capability-promotion closure, and real-world end-to-end evidence.

## Immediate next objective

1. Observe green validation + real-build CI for the current weighted multi-label routing head.
2. Reconcile or merge/replace stale open PR #118 so capability-registry promotion verification is no longer an unresolved branch-level trust boundary.
3. Add a trusted Android signing/keystore abstraction that never exposes signing material to generated/model-controlled code.
4. Add an authorized Play Console publication path with explicit human/legal/payment/store-agreement gates.
5. Run durable end-to-end cycles on Jumpy and at least one Flutter and one generic repository; turn every real failure into a regression test or capability improvement.
6. Harden software-supply-chain evidence: license policy, dependency provenance, SBOM enforcement and artifact provenance.
7. Refresh operator/user documentation once the publication path is stable.

## Remaining roadmap

- Production signing, key rotation and secure keystore integration.
- Play Console upload/release-track automation when authorized credentials and agreements exist.
- Close the registry-promotion verification loop represented by PR #118.
- Repeated Jumpy end-to-end completion, including device/runtime/release evidence.
- A small fixed cross-engine benchmark portfolio used as a release gate for self-evolution and routing changes.
- Stronger asset/license/provenance controls and visual-consistency QA.
- Richer privacy/Data Safety classification for networked/SDK-heavy applications.
- Long-duration soak/fault-injection tests for runner restarts, provider outages, quota exhaustion and partially completed promotions.
- Documentation cleanup so README/docs reflect the current adaptive generic/meta-routing architecture.

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
