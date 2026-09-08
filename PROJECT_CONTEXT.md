# AI Dev Server — Project Context

> **Read this file first when resuming work in a new ChatGPT conversation.**
> It is the durable handoff contract for this repository. Keep it current whenever architecture, priorities, completion status, or the next objective materially changes.

## What this repository is

`ai-dev-server` is an autonomous mobile-application factory and control plane. Its intended entry point is a normal ChatGPT conversation: the user gives a high-level product brief, ChatGPT dispatches it to this system, and the factory owns the work from product definition through a production-quality Android application and Play Store release package.

The system is not meant to be a one-off code generator. It must become a reusable engineering organization in software: product, UX/UI, implementation, graphics/assets, testing, device QA, performance, accessibility, privacy, security, release engineering, store preparation, repair, and controlled self-improvement.

## Final objective

The long-term contract is:

`ChatGPT conversation -> high-level brief -> ai-dev-server -> autonomous planning/research/design/code/assets/tests/repair -> capability-specific QA -> release -> Play Store package/submission -> finished professional application`

The factory should accept essentially any reasonable mobile-app project within supported platform/policy constraints. When a project requires a capability the factory does not yet possess, it must not fake success or permanently stop. It must identify the gap, acquire/research appropriate resources, develop the missing capability in isolation, validate it against trusted benchmarks and regression gates, promote it only if non-regressing, then resume the original project.

Human intervention should be limited to genuinely irreducible external actions such as legal attestations, identity/payment/store agreements, or credentials that cannot safely be generated or delegated. These external blockers must never be fabricated or silently bypassed.

## Non-negotiable quality bar

A project is not `finished` merely because it compiles or has a preview. Completion requires evidence appropriate to the app, including product acceptance, professional responsive design, accessibility, real behavior, tests, independent review, release artifacts, runtime/device QA, capability-specific QA, privacy/data-safety consistency, security/dependency checks, professional store assets and listing material, and all other dynamically required gates.

The system must fail closed. Self-improvement must never weaken tests, security boundaries, privacy requirements, accessibility requirements, or the definition of done in order to obtain a green result.

## Current architecture

Core trusted components live under `studio/`.

- `core.py`: bounded Flutter generation sandbox and trusted gates.
- `run.py`: product/design/implementation/review/visual generation loop and checkpoints.
- `completion.py`: machine-readable definition of done and dynamic release stages.
- `stage_registry.py`: trusted post-preview stage executors.
- `ci_runner.py`: bounded queue/stage orchestration.
- `capability_qa.py`: classifies generated app capabilities and derives specialized QA.
- `device_qa.py` / `device_stage.py`: Android release runtime validation.
- `performance_qa.py`: performance/game runtime evidence.
- `notification_qa.py`: notification permission/lifecycle/delivery validation.
- `store_package.py`: Play Store listing/assets package.
- `privacy_audit.py`: privacy/Data Safety evidence.
- `security_audit.py`: source/dependency/security/SBOM evidence.
- `adaptation.py`: fail-closed capability-gap detection and machine-readable evolution requests.

CI currently uses GitHub Actions as primary validation with a real Flutter smoke build. CircleCI is retained as fallback. Never claim CI success without observing it.

## Current state — 2026-09-08

PR #17 (`Restore GitHub Actions and add notification QA`) was validated by both `Validate AI Dev Server` and `Mobile Studio Real Build` and merged as `177153db2eb31b4a1a09c7b22cd16ad527065bfc`.

PR #18 (`Fail closed into autonomous adaptation requests`) was validated by both GitHub Actions workflows and squash-merged as `0fc68b14a71ce335e753c238cda17e9e4d5764eb`.

The factory now turns unsupported completion work into `adaptation_required` and writes `evolution-request.json` rather than treating an unfinished project as acceptable progress. Evolution requests describe gaps, bounded research/resource targets, isolated-candidate policy, rollback requirements, and promotion gates.

Implemented or substantially present QA/release capabilities include standard Flutter validation, real Android release/device QA, capability classification, performance QA, notification QA, store packaging, privacy audit and security/SBOM gates. Some specialized capabilities remain incomplete or absent, notably robust billing QA, platform-view QA, broader native/hardware QA, richer privacy classification for networked apps, and full automated Play Store publication when credentials/legal prerequisites exist.

The first important target application for exercising the factory is **Jumpy**, a mobile game. The factory itself should continue improving before it is described as 100% autonomous.

## Immediate objective

Build the **consumer/executor for `evolution-request.json`**. The intended controlled loop is:

1. detect a missing capability;
2. formulate a bounded research request;
3. prefer authoritative official documentation and maintained resources;
4. evaluate candidate SDKs/packages/tools/reference implementations for maintenance, licensing, security and compatibility;
5. create the capability implementation on an isolated branch;
6. add trusted tests and a benchmark scenario that proves the capability;
7. run the full existing regression suite and real Flutter smoke;
8. reject regressions or attempts to weaken the definition of done;
9. promote only a passing, reversible candidate;
10. resume the blocked application automatically.

Do not allow arbitrary downloaded code to execute merely because research found it. External dependencies/actions must be reviewed, version-pinned where applicable, policy-compatible and validated before becoming trusted factory resources.

## Near-term roadmap

After the evolution executor:

- implement/strengthen `billing_qa`, `platform_view_qa` and general `native_qa`;
- improve capability detection beyond direct dependencies/simple source markers;
- make privacy/Data Safety classification sufficiently rich for legitimate networked apps without inventing claims;
- build a professional graphics/asset factory with provenance and automated visual consistency QA;
- strengthen dependency/license/provenance/security analysis;
- make release signing and Play Console publication autonomous when authorized credentials exist;
- maintain a representative benchmark suite of diverse mobile briefs;
- let factory improvements compete against the current baseline and promote only measured non-regressions;
- exercise the complete pipeline on Jumpy and then increasingly diverse applications.

## Rule for every generated/managed project

This repository establishes a project-wide convention: **every project the factory creates or substantially manages must contain a root `PROJECT_CONTEXT.md`.**

That file must be useful without access to the previous ChatGPT conversation and must contain at minimum:

1. what the project/application is;
2. target users and core product value;
3. present scope and implemented features;
4. architecture/technology and important constraints;
5. current validation/release status with evidence, not guesses;
6. known blockers, risks and technical debt;
7. immediate next objective;
8. near-term roadmap;
9. long-term/final objective;
10. key decisions that a future agent must preserve;
11. last meaningful update date and, when useful, relevant commit/PR references.

The factory must create this file early, update it as milestones change, and include it in checkpoints. A future ChatGPT/agent should read it before making substantial changes. It is a handoff document, not marketing copy and not a replacement for README/user documentation.

## Rules for a future ChatGPT conversation

When asked to continue this repository:

1. read `PROJECT_CONTEXT.md` first;
2. inspect current `main`, open PRs and CI rather than assuming this snapshot is still current;
3. preserve the final objective above;
4. perform the next meaningful implementation rather than only proposing it;
5. work through branches/PRs and verify CI before merging substantial changes;
6. update this file whenever the repository state or next objective materially changes;
7. report both **Objectif court terme** and **Objectif final** to the user.
