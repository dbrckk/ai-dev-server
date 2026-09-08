# AI Dev Server — Project Context

> **READ THIS FILE FIRST when resuming work in a new ChatGPT conversation.** Keep it current whenever architecture, priorities, completion status, or the next objective materially changes.

## Repository purpose

`ai-dev-server` is an autonomous mobile-application factory intended to be invoked from a normal ChatGPT conversation. The user supplies a high-level brief; the factory should own product definition, research, UX/UI, implementation, original/provenance-tracked graphics, testing, repair, device QA, performance/accessibility, privacy/security, release engineering and Play Store preparation.

It is not merely a code generator. The target is a reusable expert mobile engineering organization implemented as software.

## Final objective

`ChatGPT conversation -> high-level brief -> ai-dev-server -> autonomous research/planning/design/code/assets/tests/repair -> app-specific QA -> release -> Play Store publication -> finished professional application`

The factory should handle essentially any reasonable mobile project within platform/policy constraints. If a project needs a capability the factory lacks, it must detect the gap, research/acquire appropriate resources, implement the missing capability on an isolated candidate branch, benchmark it against trusted regression/quality gates, promote only a non-regressing reversible improvement, and then resume the blocked project.

Human intervention is reserved for genuinely irreducible external actions such as legal attestations, identity/payment/store agreements, or credentials that cannot safely be generated/delegated. Never fabricate these prerequisites.

## Non-negotiable quality contract

A preview or successful compilation is not completion. `finished` requires evidence appropriate to the application: acceptance journeys, polished responsive UI, accessibility, real behavior, tests, independent review, release artifacts, runtime/device QA, capability-specific QA, privacy/Data Safety consistency, security/dependency checks, professional store assets/listing and every dynamically required gate.

Fail closed. Self-improvement must never weaken tests, security, privacy, accessibility or the definition of done merely to obtain a green result.

## Current architecture

Trusted components are primarily under `studio/`:

- `core.py` — bounded Flutter generation sandbox and trusted gates.
- `run.py` — product/design/implementation/review/visual loop and checkpoints.
- `completion.py` — machine-readable definition of done and dynamic stages.
- `stage_registry.py` / `ci_runner.py` — trusted post-preview orchestration.
- `capability_qa.py` — capability classification and specialized-QA requirements.
- Android runtime/device QA plus specialized performance and notification QA.
- `store_package.py` — Play Store listing/assets package.
- `privacy_audit.py` — privacy/Data Safety evidence.
- `security_audit.py` — security/dependency/SBOM evidence.
- `adaptation.py` — fail-closed capability-gap detection and evolution requests.

GitHub Actions is currently the primary CI and includes a real Flutter smoke build. CircleCI remains fallback. Never claim CI success without observing it.

## Current state — 2026-09-08

- PR #17, `Restore GitHub Actions and add notification QA`, passed both GitHub Actions workflows and merged as `177153db2eb31b4a1a09c7b22cd16ad527065bfc`.
- PR #18, `Fail closed into autonomous adaptation requests`, passed both workflows and squash-merged as `0fc68b14a71ce335e753c238cda17e9e4d5764eb`.
- Unsupported completion work now becomes `adaptation_required` with `evolution-request.json`; it is no longer accepted as ambiguous progress.
- Evolution requests describe gaps, bounded research/resource targets, isolated-candidate policy, rollback and promotion gates.
- Important incomplete areas include the executor that consumes evolution requests, robust billing/platform-view/general native QA, richer networked-app privacy classification, professional graphics automation, stronger dependency/license provenance and authorized Play Console publication.
- **Jumpy** is the first important target app for exercising the complete factory. Do not describe the factory as 100% autonomous yet.

## Immediate objective

Implement the **evolution-request executor**:

1. consume `evolution-request.json`;
2. research authoritative and maintained resources for the missing capability;
3. assess compatibility, security, licensing and maintenance;
4. create an isolated candidate implementation;
5. add trusted capability tests and benchmark cases;
6. run all existing regression gates and real Flutter smoke;
7. reject regressions or any weakening of the completion contract;
8. promote only a passing, reversible candidate;
9. resume the blocked application automatically.

External code discovered during research must not become trusted/executable merely because it was found. Dependencies/actions must be reviewed, pinned where applicable, policy-compatible and validated.

## Near-term roadmap

- Evolution executor and benchmark/promotion engine.
- Complete `billing_qa`, `platform_view_qa` and broad `native_qa`.
- Stronger semantic capability detection.
- Rich but conservative privacy/Data Safety classification for networked apps.
- Professional graphics/asset factory with provenance and visual-consistency QA.
- Stronger license/dependency/provenance/security analysis.
- Autonomous signing and Play Console publication when authorized credentials exist.
- Diverse fixed benchmark suite for measuring factory changes.
- End-to-end Jumpy completion, followed by increasingly diverse applications.

## Mandatory context-file convention for every project

Every repository this factory creates or substantially manages must contain a root **`PROJECT_CONTEXT.md`**. It is a durable handoff for a future ChatGPT conversation/agent with no access to prior chat history.

It must contain at minimum:

1. project/app purpose and target users;
2. current product scope and implemented features;
3. architecture, technology and important constraints;
4. current validation/release status based on evidence;
5. blockers, risks and technical debt;
6. immediate next objective;
7. near-term roadmap;
8. long-term/final objective;
9. key decisions/invariants to preserve;
10. last meaningful update date and useful commit/PR references.

Create it early, update it after material milestones, and include it in checkpoints. It is not marketing copy and does not replace README/user documentation.

## Instructions to any future ChatGPT/agent

1. Read `PROJECT_CONTEXT.md` first.
2. Inspect current `main`, open PRs and CI before assuming this snapshot is current.
3. Preserve the final objective and quality contract above.
4. Perform the next meaningful implementation rather than only proposing it.
5. Use branches/PRs and verify CI before merging substantial changes.
6. Update this file whenever state, architecture or the next objective materially changes.
7. Report **Objectif court terme** and **Objectif final** to the user.
